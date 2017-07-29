# antiScamBot_slack
antiScam-bot is a slack bot allowing admins to better control what is going in their slack channels and reduce potential scams, bad behaviours. The bot comes with a range of functions that admins can use to interact with the bot. The free slack API does not allow things like banning users and such, so more soft methods have been implemented for now. This bot is a work in progress and it is my hope that feedback and contributions will improve its reach. 

***Note:** Slack is not the best platform when it comes to security and I would advise using a platform like [Rocket Chat](https://rocket.chat/) (an opensource clone of slack), which has to be hosted locally, but allows you to fully define how the app behaves. It is my hope that we could build a rocket chat version that would be very secure against potential scams and other forms of attacks.*

## Installation

The bot was written in **python 3.6** and has been written for **Ubuntu 16**. Contributions to make it platform independent are welcomed. 

**Python dependencies** ;
+ Python 3.6+
+ rtmbot
+ slack_client

### 1. Setting up an independent machine (Optional)
 I would recommend setting up a machine using [Google cloud](https://cloud.google.com/), [Digital Ocean](https://m.do.co/c/4555fc0a5367), or another cloud computing platform. Both Google Cloud and Digital Ocean offer about 300$ when newly registered (which would last for a bit more than a year). By using a cloud computing platform, the bot would always be up and running without you having to worry about your computer shutting off (and it would allow you to have an Ubuntu 16 machine if you currently do not process one). For the price (free at first and then between 5$ to 20$ a month), this is really a must in my opinion. Here, I will give instructions on how to install this on Digital Ocean (simplest platform I found). 


**1.1 Creating a Droplet**

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


**1.2 Connecting to Droplet**
You will need to install a few things on your remote machine before being able to run the bot. First, you need to connect to it, either via SSH or by clicking on **More** and selecting **Access console**. If you use your own terminal, just type `ssh root@your.node.IP` To login, type **root** as your login username and typing the password sent by email when you created the Droplet (Can’t copy paste with the Digital Ocean terminal!!!). You will then be asked to repeat the password (sorry for those who don’t use SSH) and choose a new password. **Please**, choose a secure password. The last thing you want is someone hacking your bot, although this is unlikely. 

**1.3 Installing dependencies**

First, let’s install Anaconda, an awesome Python library manager. Go on [Anaconda download page](https://www.continuum.io/downloads#linux), right click on the Python 3.X version and select **copy link address**. It should look like `https://repo.continuum.io/archive/Anaconda3-4.4.0-Linux-x86_64.sh`. In your terminal, run the following commands:
``` bash
wget PYTHON_DOWNLOAD_LINK_ADDRESS 
bash NAME_OF_FILE_DOWNLOADED #(can be seen if you type ls)
#press ENTER, type yes, press ENTER
```
Now that anaconda is installed, we can install our python dependencies. Run the following commands:
``` bash
pip install rtmbot
pip install slack_client
```

  


