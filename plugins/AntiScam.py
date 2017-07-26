#Imports
import re

from rtmbot.core import Plugin
from slackclient import SlackClient

class AntiScam(Plugin):

    #Adming token ( OAuth Access Token )
    adminToken = 'OAuth Access Token'
    scAdmin    = SlackClient(adminToken)
    
    #Whitelist
    whitelist_ID   = [] # List of user IDs to be whitelisted
    whitelist_chan = [] # List of channels to be whitelisted

    #Regular Expressions for ETH and BTC addresses
    eth_prog = re.compile(r'((0x)?[0-9a-fA-F]{40})')
    btc_prog = re.compile(r'([13][a-km-zA-HJ-NP-Z1-9]{25,34})')


    def delete(self, data, msg, warning = False):
        '''
        Will delete a msg and post a warning message in the respective channel
        '''

        #Deleting message
        print('WILL DELETE MSG ' + str(data['ts'] + ' : '))
        print(self.scAdmin.api_call("chat.delete", channel = data['channel'],
                                    ts=data['ts'], as_user = True))

        #Adding warning wrapper if true
        if warning:
            warningWrap = ':exclamation::warning::exclamation:'
            msg = warningWrap + msg + warningWrap

        #Posting warning
        Z = self.scAdmin.api_call('chat.postMessage', channel= data['channel'], 
                                   text = msg, icon_emoji=":exclamation:")            
        return

    def process_message(self, data):
        'Will process all posts on watched channels.'

        #Printing message to console
        print(data)

        #Returning if whitelisted user
        if data['user'] in self.whitelist_ID:
            print('Whitelisted user')
            return     

        #Returning if whitelisted channel
        if data['channel'] in self.whitelist_chan:
            print('Whitelisted channel')
            return

        #Name of the user
        info     = self.slack_client.api_call('users.info', user=data['user'])
        username = info['user']['name']

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
        info     = self.slack_client.api_call('users.info', user=data['user'])
        username = info['user']['name']

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
