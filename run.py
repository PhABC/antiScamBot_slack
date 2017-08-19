#!/usr/bin/python

# -*- coding: utf-8 -*-
import re, sys, time, os, subprocess
import pickle as pk

from rtmbot.bin.run_rtmbot import main
from Settings              import initSettings


def editConf(Settings):
   'Will edit the rtmbot.con'

   #Reading lines of rtmbot.conf              
   with open('rtmbot.conf',"r") as outfile:
     conf = outfile.readlines()            

   #Chaging 3rd line to add current token 
   conf[2] = " SLACK_TOKEN: \"{}\"\n".format(Settings['SLACK_BOT_TOKEN'])
   
   #Editing rtmbot.conf with SLACK_BOT_TOKEN as SLACK_TOKEN   
   with open('rtmbot.conf',"w") as outfile:
     outfile.writelines(conf)  


if __name__ == '__main__':

    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    # sys.exit(main())

    try:
        while True: # super hacky, added this to reboot if connection fails
          
          try: #Will restart after 5 seconds if goes down

              #If settings not instantiated
              if not os.path.isfile('Settings.txt'):
                Settings = initSettings()

                #Ediit rtmbot.conf file to add bot token
                editConf(Settings)

              else:

                #Checking if Settings.txt is empty or bad
                try:
                  with open('Settings.txt', 'rb') as f:
                    Settings = pk.loads(f.read())

                except:
                  cont = input(['\nIt seems like your Settings.txt file is bad. Press 1 if you ' + 
                                'want to create a new Settings.txt file, otherwise press 0 : '  ][0])

                  if cont == '1':
                    Settings = initSettings()
                    editConf(Settings)
                  else:
                    print('Aborting.')
                    quit()

              #Running bot
              print('\nAntiscam Bot Initiation.')
              main()

          except Exception as ex: 

              #Printing error and restart message
              print('\nError : ') ; print(ex)
              print('\nRESTARTING IN 5 SECONDS.\n')

              #Restart after 5 seocnds
              time.sleep(5) 
             
    except KeyboardInterrupt:
        pass
