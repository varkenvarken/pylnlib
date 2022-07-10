# pylnlib : a package to communicate with a model railroad controller using the LocoNet® protocol
#
# (c) 2022 Michel Anders (varkenvarken)
#
# License: GPL 3, see file LICENSE
#
# Version: 20220710113704

"""
This package can be invoked as a module.

Example:
```
python -m pylnlib
```

If invoked this way, it will start listening for data on a serial interface 
and will report any incoming messages. Incoming messages related to unknown
slots, switches or sensors will trigger outgoing status request messages.

It can both capture and replay messages. For more info run it with the -- help option

```
python -m pylnlib --help
```

"""
