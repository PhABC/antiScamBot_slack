from __future__ import print_function
from rtmbot.core import Plugin
from slackclient import SlackClient

import time
import re
try:
    from urlparse import urlparse
except:
    from urllib.parse import urlparse

import requests
import glob, os
from PIL import Image

class AntiScam(Plugin):

    flagged_users = {}

    #Adming token 
    adminToken = 'xoxp-141131384855-141120363014-217638948963-4a213fe36db486a8b1a6e3120755b28c'
    scAdmin    = SlackClient(adminToken)
    
    #Whitelist
    user_whitelist = [] # truncated left as example
    id_whitelist   = [] # truncated left as example
    chan_whitelist = [] # truncated left as example
    
    #Blacklist
    user_blacklist = ['jarrad', 'jared', 'carl', 'hope', 'bennetts'] # truncated left as example

    
    time_lapse   = 3600
    last_time    = time.time()
    msg_count    = 0
    msg_interval = 20

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
                                
        return True

    def process_message(self, data):
        print(data)


        #Returning if whitelisted user
        if data['user'] in self.id_whitelist:
            print('Whitelisted user')
            return     

        #Returning if whitelisted channel
        if data['channel'] in self.chan_whitelist:
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
        if 'https://etherscan.io/' in data['text']:
            print('Etherscan address')
            return 

        #ETH address detection
        print(eth_result)
        print(eth_result.group(1))
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
