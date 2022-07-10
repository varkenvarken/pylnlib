# pylnlib : a package to communicate with a model railroad controller using the LocoNet® protocol
#
# (c) 2022 Michel Anders (varkenvarken)
#
# License: GPL 3, see file LICENSE
#
# Version: 20220710112411

"""
Module to allow pylnlib to be invoked as a module.

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

from threading import Thread
from time import sleep

from .Utils import Args, createInterface, createScrollkeeper, reporter

if __name__ == "__main__":

    args = Args().args

    # create an interface, possibly pointing to a file with previously captured input
    interface = createInterface(args)

    # create a Scrollkeeper instance and let it process messages
    scrollkeeper = createScrollkeeper(interface, args)

    if args.reportinterval > 0:
        Thread(
            target=reporter(scrollkeeper, args.reportinterval),
            name="scrollkeeper dump",
            daemon=True,
        ).start()  # no need to join a daemon thread later

    interface.run()

    if args.replay and args.reportinterval > 0:
        print(
            f"waiting {args.reportinterval + 2} seconds so the final scrollkeeper report will be produced."
        )
        sleep(args.reportinterval + 2)
