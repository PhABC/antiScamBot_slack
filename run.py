#!/usr/bin/python

# -*- coding: utf-8 -*-
import re, sys, time, os, subprocess
import pickle as pk

from rtmbot.bin.run_rtmbot import main
from Settings              import initSettings

if __name__ == '__main__':

    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    # sys.exit(main())

    try:
        while True: # super hacky, added this to reboot if connection fails
               
          #If settings not instantiated
          if not os.path.isfile('Settings.txt'):
            initSettings()

          else:

            #Checking if Settings.txt is empty or bad
            try:
              with open('Settings.txt', 'rb') as f:
                Settings = pk.loads(f.read())

            except:
              cont = input(['\nIt seems like your Settings.txt file is bad. Press 1 if you ' + 
                            'want to create a new Settings.txt file, otherwise press 0 : '  ][0])

              if cont == '1':
                initSettings()
              else:
                print('Aborting.')
                quit()

          #Running bot
          print('\nAntiscam Bot Initiation.')
          main()
             
    except KeyboardInterrupt:
        pass
