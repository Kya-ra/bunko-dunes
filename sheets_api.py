#!/usr/bin/env python3

import httplib2

from apiclient import discovery
from google.oauth2 import service_account

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
CREDS = "creds_bunko.json"

class SheetsAPI:
    sheet = None

    @classmethod
    def init_sheet(cls):
        creds = service_account.Credentials.from_service_account_file(CREDS, scopes=SCOPES)
        service = discovery.build("sheets", "v4", credentials=creds)
        cls.sheet = service.spreadsheets()

    @classmethod
    def get_sheet_data(cls, sheet_id, sheet_range):
        if cls.sheet == None:
            cls.init_sheet()
            
        result = cls.sheet.values().get(spreadsheetId = sheet_id, range = sheet_range).execute()
        
        return result.get("values", [])

    @classmethod
    def append_to_sheet(cls, sheet_id, sheet_range, value):
        if cls.sheet == None:
            cls.init_sheet()
            
        value_input_option = "USER_ENTERED"
                
        insert_data_option = "INSERT_ROWS"
        
        value_input_body = { 
            "majorDimension" : "ROWS",
            "values" : [[value]]
            }

        request = cls.sheet.values().append(spreadsheetId = sheet_id, range=sheet_range, valueInputOption=value_input_option, insertDataOption=insert_data_option, body=value_input_body)
        response = request.execute()

        return response


def debug_sheet_usage(SPREADSHEET_ID):

    SheetsAPI.init_sheet()

    values = SheetsAPI.get_sheet_data(SPREADSHEET_ID,RANGE)

    for row in values:
        print(row[0])

    test = "test@example.com"

    print("Appending",test,"...")

    SheetsAPI.append_to_sheet(SPREADSHEET_ID,RANGE, test)

    for row in SheetsAPI.get_sheet_data(SPREADSHEET_ID,RANGE):
        print(row[0])


def debug_sheet_error(ID):
    SheetsAPI.append_to_sheet(ID,"sheet!A1:A" ,"test")
