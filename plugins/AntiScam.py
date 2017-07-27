#Imports
import re, os
import pickle as pk

from rtmbot.core import Plugin
from slackclient import SlackClient


class AntiScam(Plugin):

    #Admin token ( OAuth Access Token ) and client
    adminToken = os.environ['SLACK_ADMIN_TOKEN']
    scAdmin    = SlackClient(adminToken)

    #Bot token and client
    botToken = os.environ['SLACK_BOT_TOKEN']
    scBot    = SlackClient(botToken)
    
    #Whitelist
    whitelist_chan = [] # List of channels to be whitelisted

    #Regular Expressions for ETH and BTC addresses
    eth_prog = re.compile(r'((0x)?[0-9a-fA-F]{40})')
    btc_prog = re.compile(r'([13][a-km-zA-HJ-NP-Z1-9]{25,34})')

    #List of users with information
    UserList = scBot.api_call("users.list")

    #Mapping between names and user IDs
    NameID_mapping = { i['name']:i['id'] for i in UserList['members']}


    def delete(self, data, msg, warning = False):
        '''
        Will delete a msg and post a warning message in the respective channel
        '''

        #Deleting message
        self.scAdmin.api_call("chat.delete", channel = data['channel'],
                               ts=data['ts'], as_user = True)

        #Adding warning wrapper if true
        if warning:
            warningWrap = ':exclamation::warning::exclamation:'
            msg = warningWrap + msg + warningWrap

        #Posting warning
        Z = self.postMessage(data, msg)        

        return

    def postMessage(self, data, msg, chan = ''):
        'Will post a message in the current channel'

        if not chan:
            chan = data['channel']
        
        self.scBot.api_call('chat.postMessage', channel= chan, 
                              text = msg, icon_emoji=":exclamation:")    

    def process_message(self, data):
        'Will process all posts on watched channels.'

        #Printing message to console
        print(data)

        #Name of the user
        userinfo = self.slack_client.api_call('users.info', user=data['user'])
        username = userinfo['user']['name']

        #Returning if whitelisted user
        if self.isAdmin(userinfo):
            print('User is Admin')
            return     

        #Returning if whitelisted channel
        if data['channel'] in self.whitelist_chan:
            print('Whitelisted channel')
            return

        #Deleting if message contains a call to all
        if '@channel' in data['text'] or '@here' in data['text']:

            msg = ''' @{0}, please refrain from using @ channel or @ here tags, 
                      as they are reserved for the team.'''.format(username) 

            self.delete(data, msg)
            return

        #Deleting if containg ETH or BTC address
        self.isETH_BTC(data)


    def isETH_BTC(self, data):
        'Will verify and delete messages that contain ETH/BTC addresses'

        #Name of user
        userinfo = self.slack_client.api_call('users.info', user=data['user'])
        username = userinfo['user']['name']

        #Delete anything that remotely looks like an eth or btc address, except etherscan.
        eth_result = self.eth_prog.search(data['text'])
        btc_result = self.btc_prog.search(data['text'])

        #Allow if etherscan address
        if 'etherscan.io/' in data['text']:
            print('Etherscan address')
            return 

        #ETH address detection
        if eth_result and eth_result.group(1):
            print('ETH address detected.')

            #Message to post in channel
            msg  = [' @{0} posted an ETH address and'.format(username) + 
                    ' the message was deleted. *Do NOT trust any '     +
                    ' address posted on slack*.']

            #Deleting message
            self.delete(data, msg[0], warning = True)
            return

        #BTC address detection
        if btc_result and btc_result.group(1):
            print('BTC address detected.')

            #Message to post in channel
            msg  = [' @{0} posted an BTC address and'.format(username) + 
                    ' the message was deleted. *Do NOT trust any '     +
                    ' address posted on slack.']

            #Deleting message
            self.delete(data, msg[0], warning = True)
            return

    def isAdmin(self, userinfo):
        'Verify if user if admin'

        if userinfo['user']['is_admin']:
            return True
        else:
            return False



class Moderation(Plugin):
    '''
    Will allow admins to add/remove "trap" users, who can report
    to the antiscam_bot whether an user is sending scam messages.

    LIST OF $mods COMMANDS:

        '$mods add USERNAME'    : Will add USERNAME to the list of moderators
        '$mods remove USERNAME' : Will remove USERNAME from the list of moderators
        '$mods list'            : Will show the current list of moderators
        '$mods help'            : Will list the possible $mods commands
    
    LIST OF $flag COMMANDS:

        '$flag add USERNAME'      : Will flag USERNAME for scamming
        '$unflag remove USERNAME' : Will remove the flag on a user
        '$flag list'              : Will show the current list of flagged users
        '$flag helo'              : Will list flag commands

    '''

    #Admin token ( OAuth Access Token )
    adminToken = os.environ['SLACK_ADMIN_TOKEN']
    scAdmin    = SlackClient(adminToken)

    #Bot token and client
    botToken = os.environ['SLACK_BOT_TOKEN']
    scBot    = SlackClient(botToken)

    #Loading Moderators list
    if os.path.isfile('Moderators.txt'):
        with open('Moderators.txt', 'r') as f:
            Moderators = f.read().split(',')[:-1]
    else:
        Moderators = []

    #Loading Flagged users list
    if os.path.isfile('Flagged.txt'):
        with open('Flagged.txt', 'rb') as f:
            Flagged = pk.loads(f.read())-tests-tests
    else:
        Flagged = {}

    #List of users with information
    UserList = scBot.api_call("users.list")

    #Mapping between names and user IDs
    NameID_mapping = { i['name']:i['id'] for i in UserList['members']}


    def postMessage(self, data, msg, chan = ''):
        'Will post a message in the current channel'

        if not chan:
            chan = data['channel']
        
        self.scBot.api_call('chat.postMessage', channel= chan, 
                              text = msg, icon_emoji=":exclamation:")  


    def process_message(self, data):
        'Will process all posts on watched channels.'

        userinfo = self.scBot.api_call('users.info', user=data['user'])
        username = userinfo['user']['name']

        #Moderation commands
        if '$mods ' in data['text'] and self.isAdmin(userinfo):
            self.ModeratorControl(data)

        #Flag scam commands
        if '$flag ' in data['text'] and (self.isAdmin(userinfo) or username in self.Moderators):
            self.FlagControl(data)


    def ModeratorControl(self, data):
        '''
        Will control the moderator list and commands.

        '''

        #Name of the user
        userinfo = self.scBot.api_call('users.info', user=data['user'])
        username = userinfo['user']['name']

        #Text contained in data
        text = data['text']

        #Splitting text
        splitText = text.split()


        if '$mods remove ' in text:

            #Name of specified moderator
            modName = splitText[splitText.index('remove')+1]
            modID   = self.NameID_mapping[modName]

            #Removing moderator
            if modName in self.Moderators:        
                del self.Moderators[self.Moderators.index(modName)]
                #Log message
                self.postMessage(data, 'Removed *{}* as a moderator'.format(modName))

                #Channel with new moderator
                contactChan = self.scBot.api_call('im.open', user = modID)['channel']['id']

                #Contacting ex-moderator
                self.postMessage(data, 'You have lost your moderator powers. Sorry!', chan = contactChan)

            else:
                self.postMessage(data, '*{}* is not a moderator'.format(modName))

        elif '$mods add ' in text:

            #Name of specified moderator
            modName = splitText[splitText.index('add')+1]
            modID   = self.NameID_mapping[modName]

            #Adding new moderator
            if not modName in self.Moderators:
                self.Moderators.append(modName)

                #Log message
                self.postMessage(data, 'Added *{}* as a moderator'.format(modName))

                #Channel with new moderator
                contactChan = self.scBot.api_call('im.open', user = modID)['channel']['id']

                #Contacting new moderator
                msg = ['Hello,\n\n You just gained new powers ... as a moderator! Your role will'        + 
                       ' consists of flagging scammers as soon as possible. *We DO NOT want the'         +
                       ' scammers to know who the moderators are, so please only use the commands'       +
                       ' here, in this private chat*. \n\n Here is a list of commands available to you:' + 
                       '\n     *$flag add USERNAME*        : Will flag USERNAME for scamming'            +
                       '\n     *$flag remove USERNAME* : Will remove USERNAME for flag list'             +
                       '\n     *$flag list*    : Will show the current list of flagged users'            +
                       '\n     *$flag help* : Will list the flag commands\n\n'                           +
                       'Flagging a user (if concensus is achieved) will result in certain actions such as ' +
                       'immediate public message and eventual ban of the flagged user.\n\n'              + 
                       'Thank you for your help!']

                self.postMessage(data, msg[0], chan = contactChan)


            else:
                self.postMessage(data, '*{}* is already a moderator'.format(modName))


        elif '$mods list' in text:

            #Printing list of moderators
            self.postMessage(data, 'Moderators list : ' + '*' + '*, *'.join(self.Moderators) + '*')

        elif '$mods help' in text :

            self.postMessage(data, 'List of mods commands : *$mods add USER* ~|~ *$mods remove USER* ~|~ *$mods list*')


        #Writing self.Moderator list to Moderators.txt
        with open('Moderators.txt', 'w') as f:
            for item in self.Moderators:
                f.write("%s," % item)

    def FlagControl(self, data):
        '''
        Will control flag commands

        '''

        #Name of the user
        userinfo = self.slack_client.api_call('users.info', user=data['user'])
        modName  = userinfo['user']['name']

        #Text contained in data
        text = data['text']

        #Splitting text
        splitText = text.split()

        if '$flag list' in text:

            #Build list of flag users and number of flags
            FlaggedList = [[k + ': ' + str(len(self.Flagged[k]))] for k in self.Flagged.keys()]
            FlaggedList = [i[0] for i in FlaggedList]

            #Printing list of moderators
            self.postMessage(data, ['Flagged users list (name : unique flags):\n' + 
                                    '     *' + '*\n     *'.join(FlaggedList) + '*'][0])

        elif '$flag help' in text :

            self.postMessage(data, 'List of flag commands : *$flag add USER* ~|~ *$flag remove USER* ~|~ *$flag list*')

        elif '$flag add ' in text :

            #Name of flagged user
            flaggedName = splitText[splitText.index('add')+1]
            flaggedID   = self.NameID_mapping[flaggedName]

            #Information of flagged user
            flaggedInfo = self.scBot.api_call('users.info', user=flaggedID)

            #Removing moderator
            if not flaggedName in self.Flagged:

                if flaggedInfo['user']['is_admin']:

                    self.postMessage(data, 'Admins cannot be flagged :)')
                    return

                self.Flagged[flaggedName] = [modName]
                self.postMessage(data, 'Flagged *{}* '.format(flaggedName))

            #If already reported by current mod/admin
            elif not modName in self.Flagged[flaggedName]:
                self.Flagged[flaggedName].append(modName)
                self.postMessage(data, 'Flagged *{}* '.format(flaggedName))

            else:
                self.postMessage(data, 'You already flagged *{}* '.format(flaggedName))

        elif '$flag remove ' in text:

            #Name of specified moderator
            flaggedName = splitText[splitText.index('remove')+1]

            #Removing moderator
            if not flaggedName in self.Flagged:

                self.postMessage(data, '*{}* is not flagged.'.format(flaggedName))

            else:

                del self.Flagged[flaggedName]
                self.postMessage(data, '*{}* has been unflagged.'.format(flaggedName))

        #Writing self.Flagged list to Flagged.txt
        with open('Flagged.txt', 'wb') as f:
            pk.dump(self.Flagged, f)


    def isAdmin(self, userinfo):
        'Verify if user if admin'

        if userinfo['user']['is_admin']:
            return True
        else:
            return False