# pylnlib : a package to communicate with a model railroad controller using the LocoNet® protocol
#
# (c) 2022 Michel Anders (varkenvarken)
#
# License: GPL 3, see file LICENSE
#
# Version: 20220710113627

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
