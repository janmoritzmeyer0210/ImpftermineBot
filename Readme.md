# ImpftermineBot

This Python Bot crawls the impfterminservice.de page and searches for avaialable Slots in desired locations using Selenium. Notification service is based on the [PUSHOVER](https://pushover.net/) Service.

## Setup Pushover
Go to [Pushover](https://pushover.net/), create an account, an application and download the App to your device. After that set the following enviroment Variables for your User:
- PUSHOVER_TOKEN (The Token for your Pushover Application) 
- PUSHOVER_USER (The Token for your Pushover User)

## Install
After you've set the Enviroment Variables, install docker and docker-compose and docker-compose up -d should do the rest :)

## Install additional selenium Servers
Run the following Command \
`` apt-get update && apt-get upgrade -y && apt-get install docker.io -y && docker run -d -p 4444:4444 selenium/standalone-chrome:4.0.0``

## Todos
- Twitter Integration
- Check which dates are available and include them in the notification
- Reserve appointments