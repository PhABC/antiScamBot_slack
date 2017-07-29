#antiScamBot_slack
antiScam-bot is a slack bot allowing admins to better control what is going in their slack channels and reduce potential scams, bad behaviours. The bot comes with a range of functions that admins can use to interact with the bot. The free slack API does not allow things like banning users and such, so more soft methods have been implemented for now. This bot is a work in progress and it is my hope that feedback and contributions will improve its reach. 

***Note:** Slack is not the best platform when it comes to security and I would advise using a platform like [Rocket Chat](https://rocket.chat/) (an opensource clone of slack), which has to be hosted locally, but allows you to fully define how the app behaves. It is my hope that we could build a rocket chat version that would be very secure against potential scams and other forms of attacks.*

# Setup

The bot was written in **python 3.6** and has been written for **Ubuntu 16**. Contributions to make it platform independent are welcomed. 

**Python dependencies** ;
+ Python 3.6+
+ rtmbot
+ slack_client

## 1. Setting up an independent machine (Optional)
 I would recommend setting up a machine using [Google cloud](https://cloud.google.com/), [Digital Ocean](https://m.do.co/c/4555fc0a5367), or another cloud computing platform. Both Google Cloud and Digital Ocean offer about 300$ when newly registered (which would last for a bit more than a year). By using a cloud computing platform, the bot would always be up and running without you having to worry about your computer shutting off (and it would allow you to have an Ubuntu 16 machine if you currently do not process one). For the price (free at first and then between 5$ to 20$ a month), this is really a must in my opinion. Here, I will give instructions on how to install this on Digital Ocean (simplest platform I found). 


### 1.1 Creating a Droplet

After creating an account and logging in, click on the **Create** button in green and select Droplets, with the following options :

+ **Distribution** : Ubuntu 16.04 x64
+ **Size**: > 20$/mo (this might be an overkill and you might want to try with the 5$ or 10$ option at first, especially for small chat teams)
+ No need for block storage
+ **Datacenter region** Toronto or in the US might be better, since Slack HQ is based in Vancouver, CA.
+ No need for additional options
+ **SSH keys**: Can be added for security increase, but not required (strong password might be enough, later on this).
+ **Number of Droplets** : 1
+ **Hostname**: Something like antiscam_bot_PROJECTNAME

Then click **Create**.

###1.2 Connecting to Droplet
You will need to install a few things on your remote machine before being able to run the bot. First, you need to connect to it, either via SSH or by clicking on **More** and selecting **Access console**. If you use your own terminal, just type `ssh root@your.node.IP` To login, type **root** as your login username and typing the password sent by email when you created the Droplet (Can’t copy paste with the Digital Ocean terminal!!!). You will then be asked to repeat the password (sorry for those who don’t use SSH) and choose a new password. **Please**, choose a secure password. The last thing you want is someone hacking your bot, although this is unlikely. 

###1.3 Installing dependencies

First, let’s clone this repository. To do so, run the following command in the console :
``` git clone https://github.com/PhABC/antiScamBot_slack.git``` 

This will download the repository on your remote machine. 

Second, let’s install Anaconda, an awesome Python library manager. Go on [Anaconda download page](https://www.continuum.io/downloads#linux), right click on the Python 3.X version and select **copy link address**. It should look like `https://repo.continuum.io/archive/Anaconda3-4.4.0-Linux-x86_64.sh`. In your terminal, run the following commands:
``` bash
wget PYTHON_DOWNLOAD_LINK_ADDRESS #like https://repo.continuum.io/archive/Anaconda3...
bash NAME_OF_FILE_DOWNLOADED #(can be seen if you type ls) Looks like Anaconda3-4....
#press ENTER, type yes, press ENTER, press yes
source .bashrc
```
Third, now that anaconda is installed, we can install our python dependencies. Run the following commands:
``` bash
pip install rtmbot
pip install slack_client
```
And now you are all set on this machine to be able to launch the bot! Before that, however, we need to add the bot to your slack team.

## 2. Creating the bot/application
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

## 3.Launching the Bot
Now that everything is in order, we can finally launch our bot. To do so, run the following command in the terminal : 
``` bash
cd antiScamBot_slack/
python run.py
```
This will initiate the bot, but we need to add some information: 

1. Paste the **Oauth Access Token**, which will give admin’s right to the bot.
2. Paste the **Bot User Oauth Access Token**
3. Choose your emoji avatar for the bot (e.g. :0x:)
4. Run the following commands:
 ``` bash
source ~/.bashrc
python run.py
```
Et voilà! The bot is now up and running. You can see that he is online on your slack team under **Apps**. You should invite the bot in the channels you want him to monitor.






 





  
