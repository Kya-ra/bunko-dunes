#!/usr/bin/env python3

import requests
import os
import re
from dotenv import load_dotenv
from sheets_api import SheetsAPI
from googleapiclient.errors import HttpError

load_dotenv()
SHEET_ID = os.getenv("SIGNUPS_SHEET_ID")    


def valid_email(email):
    return re.fullmatch(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', email)

def check_membership(email):
    #data = request....

    returncode = {"status":False, "details":""}

    print("Checking email "+email+"...")

    r = SheetsAPI.get_sheet_data(SHEET_ID,"signups!A2:A")

    try:
        for entry in r:
            if r[0] == email:
                # gottem
                
                print("Membership confirmed")

                returncode["status"] = True
                
                # User is valid, make an entry on the discord_accounts sheet and send it through

                if email in [e[0] for e in SheetsAPI.get_sheet_data(SHEET_ID,"discord_accounts!A2:A")]:
                    returncode["details"]="already_validated"
                    
                else:
                    print("Recording email")

                    try:
                        r = SheetsAPI.append_to_sheet(SHEET_ID, "discord_accounts!A2:A", email)
                        print("New entry added successfully.")
                        returncode["details"]="email_added"
                    except HttpError as e:
                        print("Error adding new entry:",r)
                        print("Reason:",str(e))
                        returncode["details"]=str(e)                        
                break
                
    except Exception as e:
        returncode["details"] = str(e)
        
    return returncode
