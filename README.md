# pylnlib
A python library to monitor LocoNet traffic on a usb/serial bus.

# intro
I am automating my layout with several Digikeijs components (DR5000, DR4024, DR4088) and I want to be able to script part of the running operation.

Now JMRI works fine and even allows for Python scripting, but I find it a bit top heavy on a RaspberryPi 3B+ and also, although this may be a matter of taste, the Python bindings are not very pythonic nor very logical IMHO.

Still, a lot of effort went into JMRI and otherwise it is a fine piece of software, but writing my own LocoNet Python library from scratch is not only a nice personal learning experience, but also might allow me to move some of it to microcontrollers with micro Python.

# architecture

Pylnlib is designed around the `Message` and `Interface` classes.

## Message and Interface classes
`Message` is subclassed for every implemented LocoNet message (a.k.a. opcode) and `Interface` communicates over a pyserial interface with the command station. `Interface` converts incoming raw bytes to (subclasses of) `Message` instances and converts outgoing `Message` instance to raw bytes.

`Interface` is thread safe and manages all input and output through two queues.

Other class instances, like the `Scrollkeeper`, can register a callback with an instance of an `Interface` that will be called for every incoming message.

![Class diagram and architecture overview](drawings/pylnlib.drawio.svg)

## The Scrollkeeper class
The `Scrollkeeper` class is designed to keep track of the layout status. It does this by registering a callback function with an instance of `Interface` and look at every incoming `Message` for changes in the status of sensors, switches and slots.

Status reply messages are used to update information about the item, just like commands. However if a command (like throwing a switch or changing the contents of a slot to for example change a locomotive's speed) references an unknow item, the `Scrollkeeper` instance will send an appropriate status request message. The reply to this message will then be processed as normal.

The `Scrollkeeper` class also offers method to provide information about the status of the items it keeps updated and to forward an outgoing `Message` to an `Interface`.

## The Script class
The `Script` class is used to automate operations on a layout.

It holds a reference to a `Scrollkeeper` instance and provides methods to change locomotive speed, directions and functions, throw swithces as well as wait for a sensor to change to a certain state.

