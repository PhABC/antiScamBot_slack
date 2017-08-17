 #Imports
import re, os, time
import pickle as pk

from rtmbot.core import Plugin
from slackclient import SlackClient

try:
    from urlparse     import urlparse
except:
    from urllib.parse import urlparse

class AddrDetection(Plugin):
    '''
    Will filter ETH/BTC adddresses and URL domains.

    LIST OF $url COMMANDS:

        '$url add DOMAIN'     : Will whitelist DOMAIN
        '$url remove DOMAIN ' : Will remove DOMAIN from whitelist
        '$url list'           : Will show the current list of whitelisted domains
        '$url help'           : Will list the possible $url commands
    
    '''

    #Admin token ( OAuth Access Token ) and client
    adminToken = os.environ['SLACK_ADMIN_TOKEN']
    scAdmin    = SlackClient(adminToken)

    #Bot token and client
    botToken = os.environ['SLACK_BOT_TOKEN']
    scBot    = SlackClient(botToken)

    #Bot avatar emoji
    botAvatar = os.environ['SLACK_BOT_EMOJI']
    
    #Whitelist
    whitelistUsers = ['USLACKBOT']

    #Regular Expressions for ETH and BTC addresses
    eth_prog = re.compile(r'((0x)?[0-9a-fA-F]{40})')
    btc_prog = re.compile(r'([13][a-km-zA-HJ-NP-Z1-9]{25,34})')

    #List of users with information
    UserList = scBot.api_call("users.list")

    #Mapping between names and user IDs
    UserNameID_mapping = { i['name']:i['id'] for i in UserList['members']}

    #Hack to reload mods after they are modified in other plugin
    reloadMods = False

    #Loading URL_WhiteList.txt
    if os.path.isfile('URL_WhiteList.txt'):
        with open('URL_WhiteList.txt', 'r') as f:
            URL_WhiteList = f.read().split(',')[:-1]
    else:
        URL_WhiteList = []

    #Loading Moderators list
    if os.path.isfile('Moderators.txt'):
        with open('Moderators.txt', 'r') as f:
            Moderators = f.read().split(',')[:-1]
    else:
        Moderators = []


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

    def postMessage(self, data, msg, chan = '', SC = ''):
        'Will post a message in the current channel'

        if not chan:
            chan = data['channel']

        #Slack client control
        if not SC:
            SC = self.scBot
        
        SC.api_call('chat.postMessage', channel= chan, 
                     text = msg, icon_emoji = self.botAvatar,
                     username = 'Anti-Scam Bot')   
   

    def catch_all(self, data):
        'Catching all events (like joined team)'

        if data['type'] == 'team_join':
            self.UserList['members'].append(data['user']['id'])
            self.UserNameID_mapping[data['user']['name']] = data['user']['id']


    def process_message(self, data):
        'Will process all posts on watched channels.'

        #Printing message to console
        print(data)

        #Name of the user
        userinfo = self.scBot.api_call('users.info', user=data['user'])
        username = userinfo['user']['name']
        userID   = self.UserNameID_mapping[username]

        #Will reload mods if was changed last message
        if self.reloadMods:
            #Loading new moderator list
            with open('Moderators.txt', 'r') as f:
                self.Moderators = f.read().split(',')[:-1]

            self.reloadMods = False

        #Check if current user is and admin or mod
        isAdminOrMod = (self.isAdmin(userinfo) or userID in self.Moderators)

        #Reloading moderators if change
        if self.isAdmin(userinfo) and '$mods' in data['text']:

            #Will reload next messgae
            self.reloadMods = True

        #URL control
        if '$url ' in data['text']:
            if isAdminOrMod:
                self.URLControl(data, admin = True)
            else: 
                self.URLControl(data, admin = False)

        #Returning if admin or moderator
        if isAdminOrMod:
            print('User is Admin/Mod')
            return    

        #Deleting if containg ETH or BTC address
        if self.isETH_BTC(data):
            return

        #Deleting if contains non-allowed URL
        if self.isBadURL(data):
            return

        return


    def URLControl(self, data, admin = False):
        '''
        Will control url commands
        '''

        #Name of user
        userinfo = self.scBot.api_call('users.info', user=data['user'])
        username = userinfo['user']['name']
        userID   = self.UserNameID_mapping[username]

        #Text contained in data
        text = data['text']

        if '$url list' in text:

            #Printing list of whitelisted domains
            self.postMessage(data, '*Whitelisted URL Domains* : ' + '\n\n>>>' + '\n'.join(self.URL_WhiteList))

        #Commands accessible only to admins
        if admin:

            #Regular expression for URLs
            urls = re.findall([ 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|' + 
                                 '[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+' ][0], text)
            if urls:
                #Domain name
                domain = urlparse(urls[0]).netloc
                
                #Removing www.
                domain = domain.replace('www.', '')

            #Whitelisting new url
            if '$url add' in text:


                #Adding new url to whitelist
                if not domain in self.URL_WhiteList:

                    self.URL_WhiteList.append(domain)

                    #Notification message
                    self.postMessage(data, 'Whitelisted *{}*'.format(domain))

                else:

                    #Notification message
                    self.postMessage(data, '*{}* is already whitelisted.'.format(domain))

            #Removing url from whitelist
            elif '$url remove' in text :

                if domain in self.URL_WhiteList:

                    #Deleting
                    del self.URL_WhiteList[self.URL_WhiteList.index(domain)]

                    #Log message
                    self.postMessage(data, 'Removed *{}* from URL whitelist.'.format(domain))

                else:
                    self.postMessage(data, '*{}* is not whitelisted.'.format(domain))

            #Printing url commands
            elif '$url help' in text :

                self.postMessage(data, 'List of url commands : *$url add DOMAIN* ~|~ *$url remove DOMAIN* ~|~ *$url list*')


            #Writing self.URL_WhiteList list to URL_WhiteList.txt
            with open('URL_WhiteList.txt', 'w') as f:
                for item in self.URL_WhiteList:
                    f.write("%s," % item)

            return

        else:
            return


    def isBadURL(self, data):

        #Name of user
        userinfo = self.scBot.api_call('users.info', user=data['user'])
        username = userinfo['user']['name']
        userID   = self.UserNameID_mapping[username]

        #Regular expression for URLs
        urls = re.findall([ 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|' + 
                            '[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+' ][0], data['text'])

        #If URL is found
        if urls:

            #Domain of URL
            domain = urlparse(urls[0]).netloc

            #Removing www.
            domain = domain.replace('www.', '')

            #URL log
            print('URL detected at {}'.format(domain))

            #If domain is not in whitelist
            if not domain in self.URL_WhiteList:

                #Channel with new moderator
                contactChan = self.scBot.api_call('im.open', user = userID)['channel']['id']

                #Message to user
                msg = [ 'Hello,\n\n You posted a message containing a non-approved domain ' +
                        '({}). Please contact an admin or moderator to add '.format(domain) +
                        'this domain to the URL whitelist if you consider it to be safe.\n' +
                        '\nYou can see the whitelisted domains by typing `$url list`.' ]

                #Sending warning message to user
                self.postMessage(data, msg[0], chan = contactChan)
                
                #Deleting message
                self.delete(data, msg[0])

                return True


        return False


    def isETH_BTC(self, data):
        'Will verify and delete messages that contain ETH/BTC addresses'

        #Name of user
        userinfo = self.scBot.api_call('users.info', user=data['user'])
        username = userinfo['user']['name']
        userID   = self.UserNameID_mapping[username]

        #Delete anything that remotely looks like an eth or btc address, except etherscan.
        eth_result = self.eth_prog.search(data['text'])
        btc_result = self.btc_prog.search(data['text'])

        #Allow if etherscan address
        if 'etherscan.io/' in data['text']:
            print('Etherscan address')
            return False

        #ETH address detection
        if eth_result and eth_result.group(1):
            print('ETH address detected.')

            #Message to post in channel
            msg  = [' *<@{}>* posted an ETH address and'.format(userID) + 
                    ' the message was deleted. *Do NOT trust any '      +
                    ' address posted on slack*.']

            #Deleting message
            self.delete(data, msg[0], warning = True)
            return True

        #BTC address detection
        if btc_result and btc_result.group(1):
            print('BTC address detected.')

            #Message to post in channel
            msg  = [' *<@{}>* posted an ETH address and'.format(userID) + 
                    ' the message was deleted. *Do NOT trust any '      +
                    ' address posted on slac*.']

            #Deleting message
            self.delete(data, msg[0], warning = True)
            return True

        return False


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

        '$mods add (@)USERNAME'    : Will add USERNAME to the list of moderators ( @ is optional )
        '$mods remove (@)USERNAME' : Will remove USERNAME from the list of moderators 
        '$mods list'               : Will show the current list of moderators
        '$mods msg MESSAGE'        : Will send a message to all mods
        '$mods help'               : Will list the possible $mods commands
    
    LIST OF $flag COMMANDS:

        '$flag (@)USERNAME'   : Will flag USERNAME for scamming 
        '$unflag (@)USERNAME' : Will remove the flag on a user 
        '$flag list'          : Will show the current list of flagged users
        '$flag help'          : Will list flag commands

    '''
    #Number of required mod concensus to report scammer (No concensus needed for admins)
    flagConcensus = 2

    #Admin token ( OAuth Access Token )
    adminToken = os.environ['SLACK_ADMIN_TOKEN']
    scAdmin    = SlackClient(adminToken)

    #Bot token and client
    botToken = os.environ['SLACK_BOT_TOKEN']
    scBot    = SlackClient(botToken)

    #Bot avatar emoji
    botAvatar = os.environ['SLACK_BOT_EMOJI']

    #Loading Moderators list
    if os.path.isfile('Moderators.txt'):
        with open('Moderators.txt', 'r') as f:
            Moderators = f.read().split(',')[:-1]
    else:
        Moderators = []

    #Loading Flagged users list
    if os.path.isfile('Flagged.txt'):
        with open('Flagged.txt', 'rb') as f:
            Flagged = pk.loads(f.read())
    else:
        Flagged = {}

    #List of users with information
    UserList = scBot.api_call("users.list")

    #Mapping between names and user IDs
    UserNameID_mapping = { i['name']:i['id'] for i in UserList['members']}


    def postMessage(self, data, msg, chan = '', SC = ''):
        'Will post a message in the channel chan (current channel is default)'

        if not chan:
            chan = data['channel']

        #Botname for scam-alert posting
        if chan == '#-scam-alert-':
            botName = 'Anti-Scam Bot'
        else:
            botName = 'Moderator Bot'

        #Slack client control
        if not SC:
            SC = self.scBot
        
        #Posting message
        SC.api_call('chat.postMessage', channel = chan, 
                     text = msg, icon_emoji = self.botAvatar,
                     username = botName)   

    def catch_all(self, data):
        'Catching all events (like joined team)'

        #Adding new users to the userlist
        if data['type'] == 'team_join':
            self.UserList['members'].append(data['user']['id'])
            self.UserNameID_mapping[data['user']['name']] = data['user']['id']

            #Send welcoming message



    def process_message(self, data):
        'Will process all posts on watched channels.'

        userinfo = self.scBot.api_call('users.info', user=data['user'])
        username = userinfo['user']['name']
        userID   = self.UserNameID_mapping[username]

        #Moderation commands
        if '$mods ' in data['text'] and self.isAdmin(userinfo):
            self.ModeratorControl(data)

        #Flag scam commands
        if 'flag ' in data['text'] and (self.isAdmin(userinfo) or userID in self.Moderators):
            self.FlagControl(data)


    ### --------------------------- MODIFIERS -------------------------- ###

    def isAdmin(self, userinfo):
        'Will return True if user is admin'

        if userinfo['user']['is_admin']:
            return True
        else:
            return False

    def isTag(self, user):
        ''' 
            Will verify if the provided user information is the name of 
            the user or whether it is their ID. Will return the ID if tag
            (e.g. <@USERID> ) or false if name (e.g. USERNAME).
        '''

        if '<@' in user:

            ID = user[2:-1] #ID of user, removing '<@ >'
            return ID 

        else:
            return False


    ### ----------------------- COMMANDS CONTROL ----------------------- ###

    def ModeratorControl(self, data):
        '''
        Will control the moderator list and commands.

        '''

        #Name of the user
        userinfo = self.scBot.api_call('users.info', user=data['user'])
        username = userinfo['user']['name']
        userID   = self.UserNameID_mapping[username]

        #Text contained in data
        text = data['text']

        #Splitting text
        splitText = text.split()


        if '$mods remove ' in text:

            #Name of specified moderator
            modName = splitText[splitText.index('remove')+1]
            modID   = self.isTag(modName) #Will check is user was tagged or not

            #If user was not tagged
            if not modID:
                modID = self.UserNameID_mapping[modName]

            #Removing moderator
            if modID in self.Moderators:        
                del self.Moderators[self.Moderators.index(modID)]
                #Log message
                self.postMessage(data, 'Removed *<@{}>* as a moderator'.format(modID))

                #Channel with new moderator
                contactChan = self.scBot.api_call('im.open', user = modID)['channel']['id']

                #Contacting ex-moderator
                self.postMessage(data, 'You have lost your moderator powers. Sorry!', chan = contactChan)

            else:
                self.postMessage(data, '*<@{}>* is not a moderator'.format(modID))


        elif '$mods add ' in text:

            #Name of specified moderator
            modName = splitText[splitText.index('add')+1]
            modID   = self.isTag(modName) #Will check is user was tagged or not

            #If user was not tagged
            if not modID:
                modID = self.UserNameID_mapping[modName]

            #Adding new moderator
            if not modID in self.Moderators:
                self.Moderators.append(modID)

                #Log message
                self.postMessage(data, 'Added *<@{}>* as a moderator'.format(modID))

                #Channel with new moderator
                contactChan = self.scBot.api_call('im.open', user = modID)['channel']['id']

                #Contacting new moderator
                msg = ['Hello,\n\n You were just promoted as a moderator, a gift from *<@{}>*! '.format(userID) +
                       'Your role will consist of flagging scammers/spammers as soon as possible. *We DO '      +
                       'NOT want the scammers to know who the moderators are, so please only '                  +
                       'use the commands here, in this private chat*. \n\n Here is a list of commands '         +
                       'available to you:\n>     `$flag USERNAME`       : Will flag USERNAME for scamming'      +
                       '\n>     `$unflag USERNAME`   : Will remove USERNAME from flagged list'                  +
                       '\n>     `$flag list`             : Will show the current list of flagged users'         +
                       '\n>     `$flag help`             : Will list the flag commands'                         +
                       '\n>     `$url add DOMAIN`      : Will whitelist DOMAIN'                                 +
                       '\n>     `$url remove DOMAIN` : Will remove DOMAIN from whitelist'                       +
                       '\n>     `$url list`               : Will list the whitelisted domains'                  +
                       '\n>     `$url help`               : Will list the url commands\n\n'                     +
                       'Flagging a user (if consensus is achieved) will result in certain actions such '        +
                       'as immediate public message and eventual ban of the flagged user.'                      +
                       'You can also allow or disallow certain website domains using the `url` commands.\n\n'   +
                       'Thank you for your help!']

                self.postMessage(data, msg[0], chan = contactChan)


            else:
                self.postMessage(data, '*<@{}>* is already a moderator'.format(modID))


        elif '$mods list' in text:

            #Printing list of moderators
            self.postMessage(data, 'Moderators list : ' + '*<@' + '>*, *<@'.join(self.Moderators) + '>*')


        elif 'mods msg' in text:

            #Formatting message to send to mods
            msgSplit = splitText[splitText.index('msg')+1:]

            #Replacing double slash to allow multiple lines
            msg = " ".join(msgSplit)

            #Replacing bad characters
            msg = msg.replace('\\n', '\n')

            for modID in self.Moderators:

                try:
                    #Channel with current moderator
                    contactChan = self.scBot.api_call('im.open', user = modID)['channel']['id']

                    #Contacting current mod
                    self.postMessage(data, msg, chan = contactChan)

                except ValueError:
                    print("Error with moderator {}".format(modID))


        elif '$mods help' in text :

            self.postMessage(data, ['List of mods commands : *$mods add USER* ~|~ *$mods remove USER* ' + 
                                    '~|~ *$mods list* ~|~ *$mods msg MESSAGE*'])

        #Writing self.Moderator list to Moderators.txt
        with open('Moderators.txt', 'w') as f:
            for item in self.Moderators:
                f.write("%s," % item)


    def FlagControl(self, data):
        '''
        Will control flag commands

        '''

        #Name of the user
        modinfo = self.slack_client.api_call('users.info', user=data['user'])
        modName = modinfo['user']['name']

        #Text contained in data
        text = data['text']

        #Splitting text
        splitText = text.split()

        if '$flag list' in text:

            #Build list of flag users and number of flags
            FlaggedList = [[k + ': ' + str(len(self.Flagged[k]))] for k in self.Flagged.keys()]
            FlaggedList = [i[0] for i in FlaggedList]

            #Forming list of flagged users
            msg = 'Flagged users list (name : unique flags):\n>>>'
            for i in self.Flagged.keys():
                msg += ['*<@' + i + '>* : *' + str(len(self.Flagged[i])) + '*\n'][0]

            #Printing list of flagged users
            self.postMessage(data, msg)

        elif '$flag help' in text :

            self.postMessage(data, 'List of flag commands : *$flag USER* ~|~ *$unflag USER* ~|~ *$flag list*')

        elif '$unflag ' in text:

            #Name of specified flagged user
            flaggedName = splitText[splitText.index('$unflag')+1]
            flaggedID   = self.isTag(flaggedName) #Will check is user was tagged or not

            #If user was not tagged
            if not flaggedID:
                flaggedID = self.UserNameID_mapping[flaggedName]

            #Removing flagged user
            if not flaggedID in self.Flagged:

                self.postMessage(data, '*<@{}>* is not flagged.'.format(flaggedID))

            else:

                del self.Flagged[flaggedID]
                self.postMessage(data, '*<@{}>* has been unflagged.'.format(flaggedID))

        elif '$flag ' in text :

            #Name of flagged user
            flaggedName = splitText[splitText.index('$flag')+1]
            flaggedID   = self.isTag(flaggedName) #Will check is user was tagged or not

            #If user was not tagged
            if not flaggedID:
                flaggedID = self.UserNameID_mapping[flaggedName]

            #Information of flagged user
            flaggedInfo = self.scBot.api_call('users.info', user=flaggedID)

            #Removing flagged user
            if not flaggedID in self.Flagged:

                if flaggedInfo['user']['is_admin']:

                    self.postMessage(data, 'Admins cannot be flagged :)')
                    return

                #If mod is admin, report right away
                if self.isAdmin(modinfo):

                    #Flagging
                    self.Flagged[flaggedID] = [modName]
                    self.postMessage(data, 'Flagged *<@{}>* '.format(flaggedID))

                    #Reporting without concensus
                    self.reportFlagged(data, flaggedID)
                else:
                    #Flagging
                    self.Flagged[flaggedID] = [modName]
                    self.postMessage(data, 'Flagged *<@{}>* '.format(flaggedID))

            #If already reported by current mod/admin
            elif not modName in self.Flagged[flaggedID]:

                self.Flagged[flaggedID].append(modName)
                self.postMessage(data, 'Flagged *<@{}>* '.format(flaggedID))

                #Report if concensus is reached (or automatic if Admin)
                if ( (len(self.Flagged[flaggedID]) >= self.flagConcensus or self.isAdmin(modinfo))  and 
                    '$reported' not in self.Flagged[flaggedID] ):

                    #Reporting
                    self.reportFlagged(data, flaggedID)
            else:

                self.postMessage(data, 'You already flagged *<@{}>* '.format(flaggedID))

        #Writing self.Flagged list to Flagged.txt
        with open('Flagged.txt', 'wb') as f:
            pk.dump(self.Flagged, f)



    ### ----------------------- EXTRA FUNCTIONS ----------------------- ###

    def reportFlagged(self, data, flaggedID):
        'Will report the flagged user to #-scam-alert- channel'

        #Reporting scammer
        msg  = ['<!channel>,\n\n*<@{}>* has been reported by multiple Moderators'.format(flaggedID)   +
                ' and Admins as being a scammer/spammer. *Please ignore every message from this user' +
                ' as their intentions are bad.* The user will be banned as soon as possible.']

        #Channel where to report scammer
        scamAlertChan = '#-scam-alert-'

        #Posting warning
        self.postMessage(data, msg[0], scamAlertChan, SC = self.scAdmin)

        #Reported
        self.Flagged[flaggedID].append('$reported')



class Channels(Plugin):
    '''
    Will allow admins to "censore" (or mute or freeze) certain channels, where only
    admins will be able to post. Will also allow automatic history 
    deletion.

    COMMANDS:

        $mute (#)CHANNEL   : Will prevent non-admin, non-bot from posting in CHANNEL 
        $unmute (#)CHANNEL : Will unmute a muted channel
        $mute list         : Will show which channels are muted
        $mute help         : Will show the list of mute commands

    $inviteAll CHANNEL

    '''

    #Admin token ( OAuth Access Token )
    adminToken = os.environ['SLACK_ADMIN_TOKEN']
    scAdmin    = SlackClient(adminToken)

    #Bot token and client
    botToken = os.environ['SLACK_BOT_TOKEN']
    scBot    = SlackClient(botToken)

    #Bot avatar emoji
    botAvatar = os.environ['SLACK_BOT_EMOJI']

    #List of users with information
    UserList = scBot.api_call("users.list")

    #Mapping between names and user IDs
    UserNameID_mapping = { i['name']:i['id'] for i in UserList['members']}

    #List of all the channels with information
    ChanList = scBot.api_call("channels.list")

    #Mapping between channel name and channel IDs
    ChanNameID_mapping = { i['name']:i['id'] for i in ChanList['channels']}
    IDChanName_mapping = { i['id']:i['name'] for i in ChanList['channels']}

    #Loading censored channels list
    if os.path.isfile('MutedChannels.txt'):
        with open('MutedChannels.txt', 'r') as f:
            MutedChannels = f.read().split(',')[:-1]
    else:
        MutedChannels = []

    #Loading channels topics list
    if os.path.isfile('ChannelsTopics.txt'):
        with open('ChannelsTopics.txt', 'rb') as f:
            ChannelsTopics = pk.loads(f.read())
    else:
        #Taking the current topics as default
        ChannelsTopics = { c['id'] : c['topic']['value'] for c in ChanList['channels']}

        #Storing existing topics in txt file
        with open('ChannelsTopics.txt', 'wb') as f:
            pk.dump(ChannelsTopics, f)

    def postMessage(self, data, msg, chan = '', SC = ''):
        'Will post a message in the current channel'

        if not chan:
            chan = data['channel']

        #Slack client control
        if not SC:
            SC = self.scBot
        
        SC.api_call('chat.postMessage', channel= chan, 
                    text = msg, icon_emoji = self.botAvatar, 
                    username = 'Harpocrates')  

    def delete(self, data):
        '''
        Will delete a msg and post a warning message in the respective channel
        '''

        #Deleting message
        self.scAdmin.api_call("chat.delete", channel = data['channel'],
                               ts=data['ts'], as_user = True)
        return


    def catch_all(self, data):
        'Catching all events (like joined team)'

        if data['type'] == 'team_join':
            self.UserList['members'].append(data['user']['id'])
            self.UserNameID_mapping[data['user']['name']] = data['user']['id']


    def process_message(self, data):
        'Will process all posts on watched channels.'

        #Getting user and channel information
        userinfo = self.scBot.api_call('users.info', user=data['user'])
        username = userinfo['user']['name']
        userID   = self.UserNameID_mapping[username]

        #Allow admins
        if self.isAdmin(userinfo):

            #Check if admins is using $mute commands
            if 'mute' in data['text']:
                self.MuteControl(data)

            #Check if admins is using $inviteAll command
            elif "$inviteAll" in data['text']:
                self.InviteAll(data)

            #Check if admin is changing topic
            elif 'topic' in data:
                self.TopicMonitor(data, isAdmin = True)

            #Ignore everything else the adming is doing
            return

        #Preventing topic change
        if 'topic' in data:
            self.TopicMonitor(data, isAdmin = False)

        #Delete everything else
        if data['channel'] in self.MutedChannels:
            self.delete(data)

    ### --------------------------- MODIFIERS -------------------------- ###

    def isAdmin(self, userinfo):
        'Will return True if user is admin'

        if userinfo['user']['is_admin']:
            return True
        else:
            return False

    def tag2name(self, chan):
        ''' 
            Will verify if the provided user information is the name of 
            the channel or whether it is their ID. Will return the name
            in both cases.
        '''

        if '<#' in chan:

            name = chan[12:-1] #Name of channel, removing '<#CHANID| >'
            return name 

        else:
            return chan

    ### ----------------------- COMMANDS CONTROL ----------------------- ###

    def MuteControl(self, data):
        'Will control which channel is muted or not'

        #Text contained in data
        text = data['text']

        #Splitting text
        splitText = text.split()

        if '$unmute ' in text:

            #Name of specified moderator
            chanName = self.tag2name( splitText[splitText.index('$unmute')+1] )
            chanID   = self.ChanNameID_mapping[chanName]

            #Removing channel from MutedChannels list
            if chanID in self.MutedChannels:        
                del self.MutedChannels[self.MutedChannels.index(chanID)]

                #Message
                msg = 'This channel has been un-silenced. Everyone is welcomed to post!'

                #Channel message
                self.postMessage(data, msg, chan = chanID)

                #Log message
                self.postMessage(data, '*<#{}>* has been unmuted.'.format(chanID))

            else:
                self.postMessage(data, 'Channel *<#{}>* is not muted.'.format(chanID))

        elif '$mute list' in text:

            #Printing list of moderators
            self.postMessage(data, 'Silenced channels list: ' + '*<#' + '>*, *<#'.join(self.MutedChannels) + '>*')

        elif '$mute help' in text :

            self.postMessage(data, 'List of mods commands : `$mute CHANNEL` ~|~ `$unmute CHANNEL` ~|~ `$mute list`')

        elif '$mute ' in text:

            #Name & ID of specified channel
            chanName = self.tag2name( splitText[splitText.index('$mute')+1] )
            chanID   = self.ChanNameID_mapping[chanName]

            #Muting new channel
            if not chanID in self.MutedChannels:

                #Adding to MutedChannels list    
                self.MutedChannels.append(chanID)

                #Message
                msg = 'This channel has been silenced. Only Admins and bots have permission to post here.'

                #Emoji wrapper
                msg = ':no_pedestrians: ' + msg + ' :no_pedestrians:'

                #Channel message
                self.postMessage(data, msg, chan = chanID)

                #Log message
                self.postMessage(data, '*<#{}>* has been muted.'.format(chanID))

            else:

                self.postMessage(data, 'Channel *<#{}>* is already muted.'.format(chanID))


        #Writing self.Moderator list to Moderators.txt
        with open('MutedChannels.txt', 'w') as f:
            for item in self.MutedChannels:
                f.write("%s," % item)

    ### ----------------------- EXTRA FUNCTIONS ----------------------- ###

    def InviteAll(self, data):
        'Will invite all users on a given channel'

        #Text contained in data
        text = data['text']

        #Splitting text
        splitText = text.split()

        #Name of specified channel
        chanName = self.tag2name( splitText[splitText.index('$inviteAll')+1] )
        chanID   = self.ChanNameID_mapping[chanName]

        #Log message
        self.postMessage(data, ['Inviting all users to *<#{}>*. *NOTE : the '.format(chanID)  + 
                                'bot will be unable to do anything else in the meantime.*'][0])

        #Users in channel
        inChannel = self.scAdmin.api_call('channels.info', channel = chanID)['channel']['members']

        #Looping over all users
        for user in self.UserNameID_mapping:

            #ID of current user
            userID = self.UserNameID_mapping[user]

            #Checking if user in channel
            if not userID in inChannel: 

                #Inviting user to channel
                self.scAdmin.api_call('channels.invite', user = userID, channel = chanID)

                #Sleep to prevent triggering 1 sec stupid API
                time.sleep(.8)

        #Log message
        self.postMessage(data, 'Invited all users to *<#{}>*.'.format(chanID))

    def TopicMonitor(self, data, isAdmin = False):
        'Will prevent channel topic changes by non-admin users.'

        #Channel ID
        chanID   = data['channel']
        chanInfo = self.scAdmin.api_call('channels.info', channel = chanID)
        topic    = chanInfo['channel']['topic']['value']
        
        #If admin, update topic
        if isAdmin:
            if not topic == self.ChannelsTopics[chanID]:

                #Editing default topic
                self.ChannelsTopics[chanID] = topic

                #Updating  ChannelsTopics file
                with open('ChannelsTopics.txt', 'wb') as f:
                    pk.dump(self.ChannelsTopics, f)

                return

            else:
                #To delete message after overwrite by bot
                self.delete(data)

        #If not admin, overwrite change
        else:


            #Overwrite topic with default
            self.scAdmin.api_call('channels.setTopic', topic = self.ChannelsTopics[chanID],
                                   channel = chanID)

            #Delete notificaiton of topic change by unauthorized user
            self.delete(data)



    def isAdmin(self, userinfo):
        'Verify if user if admin'

        if userinfo['user']['is_admin']:
            return True
        else:
            return False
