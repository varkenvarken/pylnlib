# capture and replay
The `Interface` class can write every incoming and outgoing message as raw bytes to a file.
It can also read from this file instead of from a serial port.

Not only is this a great help during development because it spares us the effort of running trains again and again just to see activity on the LocoNet bus, 
it can also help for the same reason when developing scripts that use the library.

## options
The monitoring program has options to enable capturing or replay

Capture:
```bash
python -m pylnlib -c -f capturefile
```
Replay:
```bash
python -m pylnlib -r -f capturefile
```

Output messages are captured as well but during replay no output is generated. Instead, any captured output is shown as is.
This means that we can replay without being connected to a command station.

## timestamps
When capturing you also specify the -t option:
```bash
python -m pylnlib -c -t -f capturefile
```
This will write a timestamp before every message that is written to the capture file.
During replay this timestamp is used to replay the messages in the exact same tempo as they were recorded.

The timestamps are written to the capture file as an unused but valid, 6-byte LocoNet message with opcode 0xc0.
A corresponding `CaptureTimeStamp` class is defined to represent this.

The 6 bytes of the message are, C0 hh mm ss ff checksum. Where hh, mm and ss represent the hour, minutes and seconds espectively,
and ff the fraction of the seconds in hundredths.

Without timestamps present, replay will process captured messages as fast as possible.
