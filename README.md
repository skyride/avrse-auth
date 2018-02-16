# AVRSE Auth

![](screenshot.png)

AVRSE auth is an EVE Online auth system originally created for TISHU/Adversity that I'm developing in public. As it's created for a single alliance the basic features and functionality are heavily tailored towards how we run our group, but if it's a good fit for you too then you're welcome to use it.

~~While I will likely add features as needed, it currently . It's not designed to be a big brother-style entity, just a basic but super reliable tool for locking down your mumble and discord server. The \#1 goal of this project is to provide automated information security and all other considerations are secondary.~~

Users can now connect their characters to the auth using ESI. The user can then see basic information on their characters such as wallet balance, fatigue, current ship/location, and a full listing of all ships and their fits. The convention is that the auth pages are designed for FCs/admins to see detailed information for auditing, whereas the Discord bot is designed to get quick answers for FCs in the heat of the moment. E.g. "Where are my supers staged", "How many people are in range of this system", "Whos alt is this", etc.

## Features
* SSO Login
* Groups with granular permissions
* Multiple membership levels (Member, Blues, Non-member) defined in config file by Corp and Alliance
* Timerboard
* Updates all members/characters hourly
* Light/Dark mode

## Character Information
While the pages/bot commands (and in some cases the API scraping itself) is a continuous work-in-progress, the information available is fixed and unlikely to change. Here's a breakdown of what it accesses.

### Hourly
* Corp/Alliance membership
* Corp Roles
* Wallet Balance
* Jump Fatigue
* Skills
* Personal Assets (with a focus on ships)
* Implants
* Jump Clones

### Every 5 minutes
* Location
* Current Ship

### Every 12 hours
* Killboard history (from Zkill)


## Integrations
### Discord
* Authenticates all users against the auth service
* Connects auth accounts to Discord using Discord's SSO
* Shares membership level, corp and auth groups as groups on the Discord server
* Instantly kicks users when they drop below the required membership level
* Suite of useful bot commands such as !whoinrange, !alts, !whoin, !wallet

### Mumble
* Authenticates all users against the auth service
* Only allows users with the defined membership level to connect
* Fixed name schema (eg. "#HRDKX - Capri Sun KraftFoods")
* Logs last connection time against a user
* Auto afk script, moves users to afk channel after 20 minutes of being deafened or 2 hours no activity
* [Basic Admin Panel](https://i.imgur.com/X50dOPJ.png)
* Temporary link functionality (tags and kicks all users when the templink is deleted/expires)

### IPBoard
* Authenticates all users against the auth service
* Sets membership level as primary group
* Doesn't handle secondary groups at the moment (no corp/alliance/auth groups)
