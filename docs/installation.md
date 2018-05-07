# Installation

## Requirements

* **PostgreSQL or MySQL**
* **Redis:** message queue for the backend jobs
* **Memcache:** Caches ESI requests (can used Redis for this too with django-redis and skip Memcache)
* **Python 2.7**
* **Virtualenv**

And of course a WSGI server to serve the content but I'll leave that up to you. If you're unfamiliar with that then [this tutorial](http://uwsgi-docs.readthedocs.io/en/latest/tutorials/Django_and_nginx.html) should give you all the info you're looking for. For testing purposes, just running `./manage.py 0:80` will for now.


## Creating the Environment

First we need to create a virtualenv to run the application.

* Create a folder to install the auth system into
* Go to the folder and run `virtualenv -p python2.7 .`
* `source bin/activate`
* Clone the repo by running `git clone https://github.com/skyride/avrse-auth`
* `cd avrse-auth`
* `pip install -r requirements.txt` If this generates any errors it'll just be because of missing packages on your server you can install with apt/yum/etc. If you get an error with zeroc-ice (the library used to talk to mumble) try `sudo apt-get install libssl-dev`
* If using MySQL: `pip install MySQL-python`
* If using PostgreSQL: `pip install psycopg2`
* `cp avrseauth/local_settings.sample.py avrseauth/local_settings.py`
* `cp eveauth/config.yaml.sample eveauth/config.yaml`
* Run `./manage.py check` and it should identify no issues

## EVE Developer Applications

You'll need to create 2 profiles at [https://developers.eveonline.com/](https://developers.eveonline.com/), one for logging in and one for character information. Log in and click "Create New Application". First create an application for the login system.

* **Name:** Anything you like, this this is the name your user will see on the SSO page.
* **Description:** Anything you like, no one sees this.
* **Connection Type:** Authentication & API Access
* **Permissions:** Find publicData and add it to the Requested Scopes List
* **Callback URL:** This the URL the system redirects back to. It should be `http(s)://<your url>/complete/eveonline/`, for example the TISHU auth uses `https://avrse.men/complete/eveonline/`

When complete you'll get a Client ID and Secret Key, write these down somewhere.

Now create another one for characters with the following info:

* **Name:** Anything you like, this this is the name your user will see on the SSO page.
* **Description:** Anything you like, no one sees this.
* **Connection Type:** Authentication & API Access
* **Permissions:** All of them (yes this means a lot of clicking)
* **Callback URL:** should be `http(s)://<your url>/complete/character_auth/`, for example the TISHU auth uses `https://avrse.men/complete/character_auth/`

Again write down the Client ID and Secret Key.

## Discord Developer Application

You also need to create a Discord application at [https://discordapp.com/developers/applications/me](https://discordapp.com/developers/applications/me) so that users can SSO their Discord accounts and the bot has a way to connect.

* **App Name:** This will be the name users see when they SSO their account and also the name of the bot on discord.
* **Redirect URI(s)**: should be `http(s)://<your url>/complete/discord/`, for example the TISHU auth uses `https://avrse.men/complete/discord/`
* **App Description:** Whatever you want, users will see this when the SSO.
* **App Icon:** Users will see this when the SSO and it'll also be the bot's avatar on Discord.

Click create app. Now scroll down to Bot and click "Create a Bot User". It makes a big fuss about this being irreversible for some reason but don't worry. After doing this you'll now have your bot. click on the "click to reveal token" link and write this token down somewhere. Also write down the Client ID and Client Secret at the top of the page.

Lastly, you need to create a discord server and invite the bot to it. I'm assuming you already know how to create a discord server if you've got this far. To save you some google, paste this link  `https://discordapp.com/oauth2/authorize?client_id=<CLIENT_ID>&scope=bot` and replace <CLIENT_ID> with the client ID you got from the discord app page. You need be owner or have the administrator permission for the discord server to make it show up on the list. Just click authorize and the bot should appear offline in your server.

## Discord Server Configuration

First off I'd highly recommend creating a random discord account to own the server. Even with the highest possible permissions the bot cannot update groups for the server owner plus it means you don't have to be in every channel.

The bot needs the administrator role. The easiest way to do this is to create a bot role, assign it to the bot, and be done with it.

Once it's up and running and a user connects to discord, the bot assigns them roles, and creates those roles if they don't exist. It assigns the following roles:

* Member/Blue/Non-member, generally used to distinguish which channels you see (e.g. pings, allies-pings, lobby, og games, etc)
* Corporation Ticker e.g. HRDKX
* All groups you are a member of on auth with "Send to discord" enabled

I'd recommend creating the Member/Blue/Non-member roles yourself (case-sensitive) so you can assign permissions/grouping/channels to them, then simply letting the bot handle everything else. When you have a lot of groups/members it can seem really messy, but the bot handles every so it's best to just trust it and let it do it's thing. The key point is the bot assigns groups on auth, so group in auth == role in discord. This gives you a lot of flexibility.

## Configuration Files

### avrseauth/local_settings.py

This is the main settings file you'll be editing. Let's go through all the settings you'll change.

* **SECRET_KEY:** This is a cryptographic salt, just face roll the keyboard or use a random string generator.
* **AUTH_NAME:** This is the name that shows up at the top left of the all the pages and in the page title.
* **DATABASES:** Refer to [django documentation](https://docs.djangoproject.com/en/1.11/ref/settings/#databases)
* **CACHES:** Refer to [django documentation](https://docs.djangoproject.com/en/1.11/ref/settings/#caches)
* **CELERY_APP_NAME:** Don't worry about this unless you're running multiple installtions on the same server
* **BROKER_URL:** Don't worry about this unless you're running multiple installtions on the same server
* **SOCIAL_AUTH_EVEONLINE_[KEY/SECRET]:** The login client id/secret we got on the eve developers site
* **SOCIAL_AUTH_CHARACTER_AUTH_[KEY/SECRET]:** The characters client id/secret we got on the eve developers site
* **SOCIAL_AUTH_DISCORD_[KEY/SECRET]:** The client id/secret we got on the discord developers site. **If the KEY is blank all discord functionality is disabled and all options hidden on the auth site**
* **DISCORD_BOT_TOKEN:** The token we got on the discord developers site
* **DISCORD_INVITE_KEY:** The key from the invite link for your discord server e.g. EjnJX
* **DISCORD_ACCESS_LEVEL:** This is the minimum access level you need to join discord, 0/1/2 = Non-member/Blue/Member
* **DISCORD_ALLOWED_BOTS:** This is for putting the user ID of any other bots you might add to your discord server so that the main bot doesn't kick them.
* **ESI_URL:** The URL used for all ESI requests
* **ESI_DATASOURCE:** don't touch this
* **ESI_RETRIES:** don't touch this
* **MUMBLE_HOST:** The host for your mumble server. **If it's blank all mumble-related functionality is disabled, do this if you don't want to use mumble**
* **MUMBLE_PORT:** The standard connect port for mumble
* **MUMBLE_ACCESS_LEVEL:** The access level required to connect to mumble
* **MUMBLE_AUTO_AFK:** Enables the auto-afk drag script. If a user has been deafened for more than MUMBLE_AFK_DELAY in minutes or inactive for 2hrs, they are automatically dragged to the channel ID specified in MUMBLE_AUTO_AFK_CHANNEL.
* **MUMBLE_AUTO_AFK_DELAY:** see above
* **MUMBLE_AUTO_AFK_CHANNEL:** see above
* **FORUM_ADDRESS:** The address of the IPB forum. **If this is blank all forum functionality is disabled. Do this if you don't want to use forum integration.**
* **FORUM_ACCESS_GROUPS:** The group IDs to assign for each access level
* **members/blues:** This is a list of alliance/corp/character ids that are valid for each access level. For example if GOTG were using this auth system, you would add the alliance IDs for Darkness/Slyce/etc to members, then possibly friendly Pure Blind entities as blues. If someone is in both members and blues, members will take priority.

### eveauth/config.yaml

This is just a basic config for the discord bot. All you need to do is put the same discord bot token you put in DISCORD_BOT_TOKEN above in the token field


## Background Processes

I'll leave it to you to decide how to how run these, but in short there's a few things you need to leave running in the background at all times. I'll show you the commands to run these but I would highly recommend running them using something like supervisor.

### Discord Bot
`cd eveauth; ./discord.sh` will run the bot. If the bot crashes it will reconnect after about 15s. If it doesn't you can just restart it. This happens from time to time with certain commands but I'm slowly fixing them.

### Mumble Authentication

`cd eveauth; python mumble.py` will run this. This connects to mumble and mumble will then pass any login attempts to it. If you restart your mumble server you need to restart this also.

### Celery

Celery is the main task runner that handles all the account checking/API scraping. With the exception of the inline update when you first add a character, all API requests are run through this. It's highly resilient and won't crash, but you should pay attention to it's logs to make sure API requests are going through. This where you'll see errors if there's a problem.

`celery worker -A avrseauth -B -c 8`

The -c parameter is how many threads to run. Anything from 4-16 is a good number. 8 is a good place to start.