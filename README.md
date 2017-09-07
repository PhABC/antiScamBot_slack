**Projects Using antiScamBot_slack**: 
       [0x Protocol](https://0xproject.com/), [Numerai](https://numer.ai/), [Aragon](https://aragon.one/), [Status](https://status.im/), [Privatix](https://privatix.io/), [Mysterium](mysterium.network), [Monetha](https://www.monetha.io/),  [Soma](http://soma.co/), [Request Network](https://request.network/). 

# antiScamBot_slack
antiScam-bot is a slack bot allowing admins to better control what is going in their slack channels and reduce potential scams. The bot comes with a range of functions that admins can use such as restricting channels to admins only, inviting all team members to a channel, reporting and flagging scammers and nominating moderators to help protecting the channels. The free slack API does not allow things like banning users and such, so more soft methods have been implemented for now. This bot is a work in progress and it is my hope that feedback and contributions will improve its reach.  

Please read carefully the [What Can The Bot Do & How To Use It](#what-can-the-bot-do---how-to-use-it), but you probably won't. If you had to only read one section of it, please, **pretty please**, read the [Moderators](#moderators) section.

***Note:** Slack is most likely not the best platform when it comes to security and I would advise using a platform like [Rocket Chat](https://rocket.chat/) (an opensource clone of slack), which has to be hosted locally, but allows you to fully define how the app behaves. It is my hope that we could build a rocket chat (or similar platform) version with strong security layers, protecting users against potential scams, frauds, hacks and other forms of attacks.*

# Table of Content
- [How To Setup The Bot](#how-to-setup-the-bot)
  * [1. Setting Up an Independent Machine (Optional)](#1-setting-up-an-independent-machine--optional-)
    + [1.1 Creating a Droplet](#11-creating-a-droplet)
    + [1.2 Connecting to The Droplet](#12-connecting-to-the-droplet)
    + [1.3 Installing Dependencies](#13-installing-dependencies)
  * [2. Creating The Bot/Application](#2-creating-the-bot-application)
  * [3. Launching The Bot](#3-launching-the-bot)
- [What Can The Bot Do & How To Use It](#what-can-the-bot-do--how-to-use-it)
  * [Preventing ETH and BTC Addresses](#preventing-eth-and-btc-addresses)
  * [Preventing non-whitelisted URL domains](#preventing-non-whitelisted-url-domains)
  * [Preventing Channels' Topic Changes](#preventing-channels-topic-changes)
  * [Muting Channels](#muting-channels)
  * [Inviting All Members](#inviting-all-members)
  * [Flagging Scammers/Spammers](#flagging-scammers-spammers)
  * [Moderators](#moderators)
  * [Additional Notes](#additional-notes)


# How To Setup The Bot

The bot was written in **python 3.6** and has been written for **Ubuntu 16**. Contributions to make it platform independent are welcomed. 

**Python dependencies** ;
+ Python 3.6+
+ rtmbot
+ slack_client

## 1. Setting Up an Independent Machine (Optional)
 I would recommend setting up a machine using [Google cloud](https://cloud.google.com/), [Digital Ocean](https://m.do.co/c/4555fc0a5367), or another cloud computing platform. Both Google Cloud and Digital Ocean offer about 300$ when newly registered (which would last for a bit more than a year). By using a cloud computing platform, the bot would always be up and running without you having to worry about your computer shutting off (and it would allow you to have an Ubuntu 16 machine if you currently do not process one). For the price (free at first and then between 5$ to 20$ a month), this is really a must in my opinion. Here, I will give instructions on how to install this on Digital Ocean (simplest platform I found). 


### 1.1 Creating a Droplet

After creating an account and logging in, click on the **Create** button in green and select Droplets, with the following options :

+ **Distribution** : Ubuntu 16.04 x64
+ **Size**: > 10-20$/month (this might be an overkill and you might want to try with the 5$ option at first, especially for small chat teams). From my experience, the bot doesn't use much ressources, but you never know.
+ No need for block storage
+ **Datacenter region** Toronto or in the US might be better, since Slack HQ is based in Vancouver, CA.
+ No need for additional options
+ **SSH keys**: Can be added for security increase, but not required (strong password might be enough, later on this).
+ **Number of Droplets** : 1
+ **Hostname**: Something like antiscam_bot_PROJECTNAME

Then click **Create**.

### 1.2 Connecting to The Droplet 
You will need to install a few things on your remote machine before being able to run the bot. First, you need to connect to it, either via SSH or by clicking on **More** and selecting **Access console**. If you use your own terminal, just type `ssh root@your.node.IP` To login, type **root** as your login username and typing the password sent by email when you created the Droplet (Can’t copy paste with the Digital Ocean terminal!!!). You will then be asked to repeat the password (sorry for those who don’t use SSH) and choose a new password. **Please**, choose a secure password. The last thing you want is someone hacking your bot, although this is unlikely. 

### 1.3 Installing Dependencies

First, let’s clone this repository. To do so, run the following command in the console :
``` git clone https://github.com/PhABC/antiScamBot_slack.git``` 

This will download the repository on your remote machine. 

Second, let’s install Anaconda, an awesome Python library manager. Go on [Anaconda download page](https://www.continuum.io/downloads#linux), right click on the Python 3.X version and select **copy link address**. It should look like `https://repo.continuum.io/archive/Anaconda3-4.4.0-Linux-x86_64.sh`. In your terminal, run the following commands:
``` bash
wget ANACONDA_DOWNLOAD_LINK_ADDRESS # Looks like ;  https://repo.continuum.io/archive/Anaconda3...
bash NAME_OF_FILE_DOWNLOADED #Looks like ; Anaconda3-4.... (Can be seen if you type ls) 
#press ENTER, type yes, press ENTER, press yes
source ~/.bashrc
```
Third, now that anaconda is installed, we can install our python dependencies. Run the following commands:
``` bash
pip install rtmbot
pip install slack_client
```
A last thing to install is *Tmux* which allows your console to stay open when you leave your ssh session. Otherwise the bot will stop the moment you disconnect. It's usually installed by default, but depending on what you use you might need to install it.

``` bash
sudo apt-get update
sudo apt-get install tmux
```
And now you are all set on this machine to be able to launch the bot! Before that, however, we need to add the bot to your slack team.

## 2. Creating The Bot/Application
Before launching the bot, you need to let Slack know of its existence, so that it can create it on their app (might need to be Admin, and Admins should be the only one to create app, so please check your settings if that’s not the case). 

1. Go [here](https://api.slack.com/apps?new_app=1) and select **Create New App**. You can name it as **antiscam** and make sure you select the right team.
2. Go on the **Basic Information** page in the left menu
3. Click on **Add features and functionality** and click on **Bots**
4. Click **Add a Bot User** and turn on the **Always Show My Bot as Online**. The later step makes sure that scammers don’t wait for the bot to be offline to post stuff.
5. Go back on **Basic Information**
6. Click on **Add features and functionality** and click on **Permissions**
7. Go to Permission Scopes and add the following permissions :
```
admin, bot, channels:history,  channels:read,  channels:write, chat:write:bot, chat:write:user, im:history, im:read, im:write
```
8. Save changes
9. Same page at the top, click on **Install App to Team** under **Oauth Tokens & Redirect URLs**.
10. Authorize

Good job! The bot is now added to your slack. You should now see the **Oauth Access Token** and **Bot User Oauth Access Token** under the **Oauth & Permissions** menu. These are absolutely critical, so please **DO NOT SHARE THEM** as they give access to the control of your bot. They will also be required soon, so keep this webpage open.

*Note: You can also customize your bot in the **Basic Information** menu, in the **Display Information** section.*

## 3. Launching The Bot
Now that everything is in order, we can finally launch our bot. To do so, run the following command in the terminal : 
``` bash
cd antiScamBot_slack/
tmux
python run.py
```
This will initiate the bot, but we need to add some information: 

1. Paste the **Oauth Access Token**, which will give admin’s right to the bot.
2. Paste the **Bot User Oauth Access Token**
3. Choose your emoji avatar for the bot (e.g. :0x:)
4. Choose how many moderators are required for a concensus (2-3 should be the minimum, more if you have many not super trustworthy moderators).
5. Choose if you want the URL filtering to be on or off.
6. Run the following command:
 ``` bash
python run.py
```
Et voilà! The bot is now up and running. You can see that he is online on your slack team under *Apps*.

## 4. Getting Your Slack Ready
The bot is only going to monitor channels in which it is invited. Inviting it in all public channels is reccommended. In addition, you will need to create some channels for certain functionallities. 

+ Create a **public channel** called **#-scam-alert** (bot will report flagged user in this channel). Make sure you invite all users in this channel with the `$inviteAll #-scam-alert` command (will take sometime because of Slack API limit).
+ Create a **private channel** called **#scambot-internal** (bot will post deleted messages and other warnings in this channels so admins can see what's going on). Note that you should not invite all moderators there, only the very most trusted ones (i.e. only admins). If a scammer is invited in this channel, they will know who the moderators are and will purposely not send messages to them. 

# What Can The Bot Do & How To Use It
The bot is primarily for Admins, but as we will see, you can add moderators that have access to certain commands as well. 

## Welcoming Message
The bot will send a message to all new members. There is a default message talking about security on slack, but you can customize it by modifying the Welcome.txt message.

## Preventing ETH and BTC Addresses
This part does not involve any commands. The bot will simply delete any message containing an ETH or BTC address and will post a warning message (except if user is an admin or moderator). It will also delete private keys and notify the user posting the key explaining why they shouldn't do this.

## Preventing non-whitelisted URL domains
Will delete any URL coming from non-whitelisted dimains (except for moderators and admins). Moderators and admin can control which domain is whitelisted using the `$url` commands.

These url commands are (*Admins and Moderators only*) : 
```
 $url add DOMAIN     : Will whitelist DOMAIN
 $url remove DOMAIN  : Will remove DOMAIN from whitelist
 $url help           : Will list the possible $url commands
```

The `$url list` command is available to all and will show which url domains are whitelisted.

## Preventing Channels' Topic Changes
Slack doesn't not have settings to prevent channel topic changes, which which can be dangerous if a malicious change of topic is not reverted. The present bot automatically overwrites changes of a topic made by non-Admin users, making topic changes `admin-only`. 

## Muting Channels
Unfortunately, Slack only allows a single channel to be *Admin and Owners Only*, which is not very convenient. Fortunately for us, this bot can do something close to restricting a channel by deleting every message posted by a non-admin & non-bot users.

The muting commands are (*Admins only*) : 
```
$mute (#)CHANNEL   : Will prevent non-admin, non-bot from posting in CHANNEL 
$unmute (#)CHANNEL : Will unmute a muted channel
$mute list         : Will show which channels are muted
$mute help         : Will show the list of mute commands
```

Where you can ether refer to channel with or without **#**.

## Inviting All Members
The bot also allows you to invite all your slack members to a given channel, by running the following command (*Admins only*) ; 
```
$inviteAll CHANNEL 
```

## Flagging Scammers/Spammers
Because slack free API doesn’t allow banning members with a bot, we need to resort to something a bit softer. Admins and Moderators (described below) can flag users if they behave like scammers / spammers. The consequences of flagging are mild, but should be sufficient to limit the damage, that is, the scammer/spammer messages will automatically be deleted and the bot will post a warning message in **#-scam-alert-** (make sure this channel exist, spelled exactly as written here).

For the flagging warning system to be useful, **you need** to have a channel called **scam-alert**, invite all members to **-scam-alert-** (with `$inviteAll -scam-alert-` and by making it a default channel in your settings for new members) and prevent random members from posting in **-scam-alert-** (with `$mute -scam-alert-`). 

The flagging commands are (*Admins and Moderators only*) :
```
$flag USERNAME   : Will flag USERNAME for scamming
$unflag USERNAME : Will remove the flag on a user
$flag list       : Will show the current list of flagged users
$flag help       : Will list flag commands
```
Where you can ether refer to users with or without **@**.

For now, you need to ban manually the members mentioned in **#-scam-alert-** as soon as possible, so please put slack on your phone with notifications. For some weird reasons, I never found how to ban members via a cellphone.

## Moderators
Admins can add moderators to their slack channel. The only thing moderators can do for now is use the flag commands. However, whereas the bot automatically post in **-scam-alert-** when a member is flagged by an Admin, a consensus of moderators is required for the bot to report the scammer. This is to avoid moderators from being malicious, which might happen if a member gain the trust of admins and they make them a moderator. 

**IT IS CRITICAL** that moderators are not publicly announced. Scammers send private messages to members and exclude admins from their spam attack. If the scammers know who the moderators are, then they could easily exclude them from their script so that they are not contacted during their phising attack. You should therefore **ALWAYS** use the bot commands in a private channel or by directly messaging the **antiscam** bot. Moderators should also never use the flag commands in public channels, as scammers could automatically detect this and blacklist the moderators.

The moderator commands are (*Admins only*):
```
$mods add USERNAME    : Will add USERNAME to the list of moderators
$mods remove USERNAME : Will remove USERNAME from the list of moderators
$mods list            : Will show the current list of moderators
$mods msg MESSAGE     : Will send a message to all moderators
$mods help            : Will list the possible $mods commands
```

Where you can ether refer to users with or without **@**.

Note that adding a moderator will send them a private message explaining briefly their responsibilities and the commands they can use. I recommend adding admins as moderators as well so they can receive this information. 

## Dynamic Reminder Messages
The bot will dynamically post messages to remind users to be careful. The dynamic is with respect to time, where a message will be posted every X message within a given channel. Hence, the bot will post a message more frequently (time based) in a very busy #trading channel (every 30mins-1hour) than in a dead #SEClover channel. 

## Additional Notes
All the flagged members, moderators and mute channels are stored in txt files. Please do not delete these as you would need to readd/reflag/remute everything. Make sure you save these files externally if you ever intend to migrate to another machine.

You should always run antiscam_bot commands in a private channel (where the bot is) or by directly messaging the **antiscam** bot. The goal is to prevent scammers from blacklisting moderators and it would be easy for them to do it automatically if a mod posted in a public channel.

Have fun and please don't forget to leave feedback and suggestions in the github **Issues** page. 

---




  
