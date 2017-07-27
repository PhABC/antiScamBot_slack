#!/usr/bin/python

# -*- coding: utf-8 -*-
import re, sys, time, os, subprocess
from rtmbot.bin.run_rtmbot import main

if __name__ == '__main__':

    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    # sys.exit(main())
    try:
        while True: # super hacky, added this to reboot if connection fails

            #If source ~/.bashrc is currently required
            needToSource = False

            if not 'SLACK_ADMIN_TOKEN' in os.environ:        
               
               #Adding slack Admin Token if not existent
               SLACK_ADMIN_TOKEN = input("Specify admin (OAuth) access token: ")
                             
               #Adding SLACK_ADMIN_TOKEN in ~/.bashrc
               with open(os.path.expanduser('~') + "/.bashrc", "a") as outfile:
                 outfile.write("\nexport SLACK_ADMIN_TOKEN=\"{}\"".format(SLACK_ADMIN_TOKEN))
            
               #Reminder to run source .bashrc
               print(['Admin Token added to environment as SLACK_ADMIN_TOKEN.'   + 
                      '\n\nPLEASE RUN \"source ~/.bashrc\" in the current shell' +
                      ' terminal to update your local environment.\n'][0])            

               #Quit trigger
               needToSource = True   

            if not 'SLACK_BOT_TOKEN' in os.environ:

               #Adding slack Admin bot if not existent
               SLACK_BOT_TOKEN = input("Specify bot access token: ")
                             
               #Adding SLACK_BOT_TOKEN in ~/.bashrc
               with open(os.path.expanduser('~') + "/.bashrc", "a") as outfile:
                 outfile.write("\nexport SLACK_BOT_TOKEN=\"{}\"".format(SLACK_BOT_TOKEN)) 

               #Reading lines of rtmbot.conf              
               with open('rtmbot.conf',"r") as outfile:
                 conf = outfile.readlines()            
     
               #Chaging 3rd line to add current token 
               conf[2] = " SLACK_TOKEN: \"{}\"\n".format(SLACK_BOT_TOKEN)
               
               #Editing rtmbot.conf with SLACK_BOT_TOKEN as SLACK_TOKEN   
               with open('rtmbot.conf',"w") as outfile:
                 outfile.writelines(conf)                

               #Reminder to run source .bashrc
               print(['Bot Token added to environment as SLACK_BOT_TOKEN.'   + 
                      '\n\nPLEASE RUN \"source ~/.bashrc\" in the current shell' +
                      ' terminal to update your local environment.\n'][0])               
               
               #Quit trigger
               needToSource = True

            else:
               #Still overwrite rtmbot incase of git pull 

               #Reading lines of rtmbot.conf              
               with open('rtmbot.conf',"r") as outfile:
                 conf = outfile.readlines()            
     
               #Chaging 3rd line to add current token 
               conf[2] = " SLACK_TOKEN: \"{}\"\n".format(SLACK_BOT_TOKEN)
               
               #Editing rtmbot.conf with SLACK_BOT_TOKEN as SLACK_TOKEN   
               with open('rtmbot.conf',"w") as outfile:
                 outfile.writelines(conf)
               
            if not 'SLACK_BOT_EMOJI' in os.environ:

               #Adding slack Admin bot if not existent
               SLACK_BOT_EMOJI = input("Specify bot emoji avatar ( e.g. :joy: ): ")
                             
               #Adding SLACK_BOT_TOKEN in ~/.bashrc
               with open(os.path.expanduser('~') + "/.bashrc", "a") as outfile:
                 outfile.write("\nexport SLACK_BOT_EMOJI=\"{}\"".format(SLACK_BOT_EMOJI))              

               #Reminder to run source .bashrc
               print(['Bot Emoji added to environment as SLACK_BOT_EMOJI.'   + 
                      '\n\nPLEASE RUN \"source ~/.bashrc\" in the current shell' +
                      ' terminal to update your local environment.\n'][0]) 

               #Quit trigger
               needToSource = True 
            
            #Quitting if source ~/.bashrc is required
            if needToSource :
              quit()

            #Printing token used                
            print('Bot token   : {}'.format(os.environ['SLACK_BOT_TOKEN']))
            print('Admin token : {}'.format(os.environ['SLACK_ADMIN_TOKEN']))
            
            #Launching bot
            print('AntiScam bot initiation.')
            main()
             
    except KeyboardInterrupt:
        pass
