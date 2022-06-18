import sys
import signal
import threading
import time
import serial
from queue import Queue

class LocoNet:
  # Global power state
  POWER_ON = 0
  POWER_OFF = 1

  # Switch (turnout) state
  SWITCH_CLOSED = 2
  SWITCH_THROWN = 3

  # Signal aspect
  SIGNAL_RED = 4
  SIGNAL_GREEN = 5
  SIGNAL_YELLOW = 6
  SIGNAL_FLASHING_YELLOW = 7

  # sensor state
  SENSOR_HI = 8
  SENSOR_LO = 9

  # LocoNet message type
  MSG_UNKNOWN = -1
  MSG_POWER_ON = -2
  MSG_POWER_OFF = -3
  MSG_SWITCH_STATE = -4
  MSG_SENSOR_STATE = -5


  def __init__(self, port, baud):
    signal.signal(signal.SIGTERM, self.term_handler)
    signal.signal(signal.SIGINT, self.term_handler)

    self.exit = False

    self.recv = threading.Thread(name = 'recv', target = self.receiver_thread)
    self.recv.setDaemon(True)

    self.receiver_handler = None

    # Event that is signaled when data arrives over LocoNet
    self.rd_event = threading.Event()

    self.msg_queue = Queue()

    try:
      # 8 bits, 1 stop bit, 1 start bit
      self.com = serial.Serial(
        port = port,
        baudrate = baud,
        stopbits = serial.STOPBITS_ONE,
        bytesize = serial.EIGHTBITS,
        timeout = None)
    except serial.SerialException as e:
      exit(e)


  '''
  Signal handler for termination
  '''
  def term_handler(self, signum, frame):
    self.exit = True


  def run(self):
    self.recv.start()
    # main loop that pulls messages from msg_queue
    while not self.exit:
      n = self.rd_event.wait(1)
      if n:
        self.rd_event.clear()

        if not self.msg_queue.empty():
          msg = self.msg_queue.get()
          self.on_receive(msg)

    self.recv.join()

    self.com.close()

    print("Done...", file=sys.stderr)


  '''
  Receiver Thread

  It reads from the serial port and calls on_receive() when data arrived
  '''
  def receiver_thread(self):
    while not self.exit:
      if self.com != None:
        n = self.com.inWaiting()
        if (n > 0):
          opcode = self.com.read(1)
          opchi = ord(opcode) >> 5
          if opchi == 0x4:
            data = ""
            chksum = self.com.read(1)
          elif opchi == 0x5:
            data = self.com.read(2)
            chksum = self.com.read(1)
          elif opchi == 0x6:
            data = self.com.read(4)
            chksum = self.com.read(1)
          elif opchi == 0x7:
            n = ord(self.com.read(1))
            data = self.com.read(n - 3)
            chksum = self.com.read(1)
          else:
            pass

          msg = self.decode(opcode, data, chksum)
          self.msg_queue.put(msg)
          self.rd_event.set()
        time.sleep(0.1)


  '''
  This is called when data arrives over LocoNet

  @param msg Decoded LocoNet message
  '''
  def on_receive(self, msg):
    if self.receiver_handler != None:
      self.receiver_handler(msg)


  '''
  Decode the raw LocoNet message

  @param data Raw data from LocoNet
  @return Decoded message
  '''
  def decode(self, opcode, data, checksum):
    # we should check if the message is valid by testing the checksum, but we
    # trust what comes in over the wire
    opc = ord(opcode)
    msg = { 'raw' : f"{opcode}{data}{checksum}"}
    if opc == 0x83:
      msg['type'] = LocoNet.MSG_POWER_ON
    elif opc == 0x82:
      msg['type'] = LocoNet.MSG_POWER_OFF
    elif opc == 0xB0:
      msg['type'] = LocoNet.MSG_SWITCH_STATE
      msg['id'] = 'DECODE ME'
      msg['state'] = 'DECODE ME'
    elif opc == 0xB2:
      byte1 = ord(data[0])
      byte2 = ord(data[1])
      msg['type'] = LocoNet.MSG_SENSOR_STATE
      msg['id'] = ((((byte2 & 0xF) << 8) | byte1) << 1) | ((byte2 >> 5) & 0x1);
      if (byte2 >> 4) & 0x1 == 0x1:
        msg['state'] = LocoNet.SENSOR_HI
      else:
        msg['state'] = LocoNet.SENSOR_LO
    else:
      msg['type'] = LocoNet.MSG_UNKNOWN
    return msg


  '''
  Build the message for LocoNet

  @param data Array of data bytes for the message
  @return LocoNet message bytes
  '''
  def build_message(self, data):
    opcode = data[0]
    opcodehi = opcode >> 4
    if opcodehi == 0x8:
      # 2-byte message
      msg = chr(opcode)
    elif (opcodehi == 0xA) or (opcodehi == 0xB):
      # 4-byte message
      n = len(data)
      if n == 3:
        msg = chr(opcode)
        for i in range(1, 3):
          msg += chr(data[i])
      else:
        print("WARNING: trying to send message that does not have 2 data bytes in 2-byte message. Not sending...", file=sys.stderr)
    elif (opcodehi == 0xE):
      print("WARNING: multiple byte messages not implemented.", file=sys.stderr)

    if len(msg) > 0:
      checksum = 0
      for c in msg:
        checksum = checksum ^ (ord(c) ^ 0xFF)
      msg += chr(checksum)
      return msg
    else:
      return None


  '''
  Compute the checksum for a message

  @param msg The byte array of the message
  @return The checksum byte
  '''
  def checksum(self, msg):
    chksum = 0
    for c in msg:
      chksum = chksum ^ (c ^ 0xFF)
    return chksum


  '''
  Send message to the LocoNet
  '''
  def send_message(self, msg):
    chksum = self.checksum(msg)
    if self.com != None:
      data = ""
      for c in msg:
        data += chr(c)
      self.com.write(data)
      self.com.write(chr(chksum))


  '''
  Set the global power on the LocoNet

  @param state Either POWER_ON or POWER_OFF to turn power on/off respectively
  '''
  def set_global_power(self, state):
    if (state == LocoNet.POWER_ON):
      self.send_message([ 0x83 ])
    elif (state == LocoNet.POWER_OFF):
      self.send_message([ 0x82 ])
    else:
      print("WARNING: set_global_power(): unknown state = " + str(state), file=sys.stderr)


  '''
  Set the state on a turnout

  @param id ID of the switch
  @param state { SWITCH_THROWN | SWITCH_CLOSED }
  '''
  def set_switch_state(self, id, state):
    # IDs on LocoNet are 0-based, but people work with 1-based numbers
    lnid = id - 1
    byte1 = lnid & 0xFF
    byte2 = (lnid & 0xF00) >> 7
    if state == LocoNet.SWITCH_CLOSED:
      byte2 = byte2 | 0x20
    self.send_message([ 0xB0, byte1, byte2 | 0x10 ])
    self.send_message([ 0xB0, byte1, byte2 ])
