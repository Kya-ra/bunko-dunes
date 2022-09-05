#!/usr/bin/env python3

import requests
import os
import re
from dotenv import load_dotenv


load_dotenv()
API_URL = os.getenv("SIGNUPS_API_URL")    


def valid_email(email):
    return re.fullmatch(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', email)

def check_membership(email):
    #data = request....

    returncode = {"status":False, "details":""}

    print("Checking email "+email+"...")
    
    r = requests.get(API_URL+"/search?sheet=signups&email="+email)

    if isinstance(r.json(), list) and len(r.json()) > 0 and r.json()[0]["email"] == email:
        print("Membership confirmed")

        returncode["status"] = True
        
        # User is valid, make an entry on the discord_accounts sheet and send it through

        r = requests.get(API_URL+"/search?sheet=discord_accounts&email="+email)
        if len(r.json()) > 0 and r.json()[0]["email"] == email:
            returncode["details"]="already_validated"
        else:
            print("Recording email")
            json = { "data" : [{"email": email}]}
            r = requests.post(API_URL+"?sheet=discord_accounts", json=json)
            try:
                if r.json()["created"] >= 1:
                    print("New entry added successfully.")
                    returncode["details"]="email_added"
                else:
                    raise Exception("Couldn't seem to add entry:",r.json())
            except:
                print("Error adding new entry:",r.json())
                returncode["details"]="error_adding_email"
                      
    return returncode
