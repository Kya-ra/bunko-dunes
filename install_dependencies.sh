#!/usr/bin/bash

sudo apt -y update && sudo apt -y upgrade && sudo apt -y dist-upgrade

# python stuff
pip install --upgrade discord.py zalgolib python-dotenv httplib2 apiclient
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlibpip

# is that all?