#!/usr/bin/python

# -*- coding: utf-8 -*-
import re
import sys
import time

from rtmbot.bin.run_rtmbot import main

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    # sys.exit(main())
    try:
        while True: # super hacky, added this to reboot if connection fails
                print('AntiScam bot initiation.')
                main()
             
    except KeyboardInterrupt:
        pass
