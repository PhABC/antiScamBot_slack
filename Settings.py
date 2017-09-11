import os
import pickle as pk


def initSettings():

    'Will initialize the Settings.txt file'

    #Generating Empty Settings
    Settings = { 'Moderators'     : [], 'MutedChannels' : [], 'RemindedChannels' : [],
                 'ChannelsTopics' : {}, 'Flagged'       : {} }
                

    #Defaults URL
    Settings['URL_WhiteList'] = ['github.com','reddit.com','etherscan.io','myetherwallet.com',
                                 '0xproject.com','numer.ai','twitter.com','slack.com',
                                 'medium.com', 'ethplorer.io', 'metamask.io', 'steemit.com', 
                                 'youtube.com','hackingdistributed.com','ens.domains','bittrex.com',
                                 'consensys.net','forbes.com','coinmarketcap.com','liqui.io',
                                 'hitbtc.com']

    #Registering Parameters
    Settings['SLACK_ADMIN_TOKEN'] = input("Specify admin (OAuth) access token: ")       # SLACK_ADMIN_TOKEN
    Settings['SLACK_BOT_TOKEN']   = input("Specify bot access token: ")                 # SLACK_BOT_TOKEN
    Settings['SLACK_BOT_EMOJI']   = input("Specify bot emoji avatar ( e.g. :joy: ): ")  # SLACK_BOT_EMOJI

    #Consensus
    Settings['CONSENSUS'] = int(input("\nNumber of moderator required for concensus (2 or more is recommended): "))  

    while Settings['CONSENSUS'] < 1:
        Settings['CONSENSUS'] = int(input('Please put at least 1'))


    #If URL filter or not
    Settings['URLFILTER'] = input("\nDo you want the bot to filter URLs (y or n)? y is recommended: ")

    while not Settings['URLFILTER'] == 'y' and not Settings['URLFILTER'] == 'n':
        Settings['URLFILTER'] = input("Please answer with y or n: ")

    #Putting in binary
    if Settings['URLFILTER'] == 'y': 
        Settings['URLFILTER'] = True
    else:
        Settings['URLFILTER'] = False

    """

    #If paranoid reminder or not
    Settings['REMINDER'] = input("Do you want the bot to give security reminders in certain channels (y or n)? : ")

    while not Settings['REMINDER'] == 'y' and not Settings['REMINDER'] == 'n':
        Settings['REMINDER'] = input("Please answer with y or n")

    if Settings['REMINDER'] == 'y':

        #Putting in binary
        Settings['REMINDER'] = 0

        #Reminder frequency
        Settings['REMINDER_FRQ'] = float(input( ["At what frequency (in hour) would you like the bot to " +
                                                 "send security reminder? 1.5 would mean a reminder every 1 h 30 mins) : "]))
        
        #Reminder Channels note
        x = input(['\nYou will be able to specify which channel(s) you want the bot to post ' + 
               'the reminders with the command "$reminder add #CHANNEL" in Slack.'][0])
    else:

        Settings['REMINDER'] = 0
        Settings['REMINDER_FRQ'] = -1

    """

    input(['\nNote that you can customize your welcoming message for new users ' +
           ' by modifying the Welcome.txt file. \n~> Press ENTER to launch bot.'][0])

    #LOADING TXT FILES FOR BACKWARD COMPATIBILITY 

    #Loading Moderators list
    if os.path.isfile('Moderators.txt'):
        with open('Moderators.txt', 'r') as f:
            Settings['Moderators'] = f.read().split(',')[:-1]

    #Loading URL_WhiteList.txt
    if os.path.isfile('URL_WhiteList.txt'):
        with open('URL_WhiteList.txt', 'r') as f:
            Settings['URL_WhiteList'] = f.read().split(',')[:-1]

    #Loading Flagged users list
    if os.path.isfile('Flagged.txt'):
        with open('Flagged.txt', 'rb') as f:
            Settings['Flagged'] = pk.loads(f.read())

    #Loading censored channels list
    if os.path.isfile('MutedChannels.txt'):
        with open('MutedChannels.txt', 'r') as f:
            Settings['MutedChannels'] = f.read().split(',')[:-1]

    # Saving SetTings to Settings.txt
    with open('Settings.txt', 'wb') as f:
        pk.dump(Settings, f)

    return Settings

