# -*- coding: utf-8 -*-


import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from file_to_text import file_to_text
import requests


# Login data locations.
CREDENTIALS_PATH = '../login/credentials.json'
TOKEN_PATH = '../login/token.pickle'
YOUTUBE_KEY = file_to_text('../login/youtube_key.txt')

# Usage rights. If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of a spreadsheet.
SPREADSHEET_ID = '19zkQ7QJvqH4PDiYZQ3ddRPN0sscht17wP4DjM6zjaLA'
RANGE_NAME = 'A1:E10'


def get_youtube_subscribers(channel_id, key):
    return requests.get('https://www.googleapis.com/youtube/v3/channels?part=statistics&id=' + channel_id + '&key=' + key).json()['items'][0]['statistics']['subscriberCount']


def get_vk_subscribers(group_id, key):
    pass


def get_telegram_subscribers(channel_id, key):
    pass


def main():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """


    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(TOKEN_PATH, 'wb') as token:
            pickle.dump(creds, token)
    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                range=RANGE_NAME).execute()
    values = result.get('values', [])


    if not values:
        print('ERROR: No data found.')
    else:
        for row in values:
            print('%s, %s' % (row[0], row[1]))

if __name__ == '__main__':
    main()
