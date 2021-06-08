# ImpftermineBot

This Python Bot crawls the impfterminservice.de page and searches for avaialable Slots in desired locations using Selenium and tor based proxy. Notification service is based on a telegram bot. Full configuration can be done in the docker-compose.yml file

## Telegram Channels
- [Hamburg](https://t.me/corona_impftermine_hh)
- [Stuttgart & Umgebung](https://t.me/corona_impftermine_str)

## Concept
You can run multiple bots on the same machine. For every bot you need:
- 1 selenium container
- 1 Scraper container
- 1 tor proxy

Every bot goes through the locations array, checks for appointments and sends an telegram message if an appointment is available. The Location Array has the following structure:
`` [["Name of Location", "URL of Location Page", "URL of Location REST Url", "Telegram Channel for mRNA", "Telegram Channel for Vektor", (seconds * 10) of maximum waiting time in waiting room before proceeding to next location, "Vermittlungscode"]] ``

## Setup
Copy docker-compose-example.yml to docker-compose.yml
- Set the environment Variable ``TELEGRAM_TOKEN`` or set it in the docker-compose file
- Set the locations Variable
- Set the proxy and selenium variable according to your container names

## Install
After you've set the Enviroment Variables, install docker and docker-compose and docker-compose up -d should do the rest :)


## Todos
- Twitter Integration
- Check which dates are available and include them in the notification
- Reserve appointments