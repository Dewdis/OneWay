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
VK_KEY = file_to_text('../login/vk_key.txt')

# Usage rights. If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a spreadsheet.
SPREADSHEET_ID = '1Bs-YiO05A6Rb7L-5HPPxJPC6cYwAvTozxGRMEF9v6Q0'
SOURCE_RANGE_NAME = "'Технические данные'!A2:H100"
OUTPUT_LIST_NAME = 'One Way'


def get_youtube_subscribers(channel_id):
    return requests.get('https://www.googleapis.com/youtube/v3/channels?part=statistics&id=' + channel_id + '&key=' + YOUTUBE_KEY).json()['items'][0]['statistics']['subscriberCount']


def get_vk_subscribers(group_id):
    return requests.get("https://api.vk.com/method/groups.getMembers?group_id=" + group_id + "&v=5.52&&access_token=" + VK_KEY).json()['response']['count']


def get_telegram_subscribers(channel_id):
    pass


def get_sheet():
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
    return sheet


def update_cell(data, cell, sheet):
    values = [[data]]
    body = { 'values': values }
    result = sheet.values().update(
    spreadsheetId=SPREADSHEET_ID, range=cell,
    valueInputOption='RAW', body=body).execute()


def update(sheet):
    # Get data using Technic List in Sheet.
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                range=SOURCE_RANGE_NAME).execute()
    values = result.get('values', [])

    data = {}

    if not values:
        print('ERROR: No data found.')
    else:
        for row in values:
            while len(row) < 4: row.append('')
            print('%s, %s' % (row[0], row[1]))
            title = str(row[0].encode('utf-8'))
            data[title] = {'YT':0, 'VK':0, 'TG':0}
            if row[1] != '': data[title]['YT'] = get_youtube_subscribers(row[1])
            if row[2] != '': data[title]['VK'] = get_vk_subscribers(row[2])
            if row[3] != '': data[title]['TG'] = get_telegram_subscribers(row[3])


    # Write data to Public List in Sheet.
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                range="'" + OUTPUT_LIST_NAME + "'!A2:H100").execute()
    values = result.get('values', [])

    if not values:
        print('ERROR: No data found.')
    else:
        for i in range(len(values)):
            row = values[i]
            print(row[0])
            title = str(row[0].encode('utf-8'))
            if title in data:
                data[title]['YT'] = int(str(data[title]['YT']))
                print(data[title]['YT'])
                data[title]['VK'] = int(str(data[title]['VK']))
                print(data[title]['VK'])
                update_cell(data[title]['YT'], "'" + OUTPUT_LIST_NAME + "'!C"+str(2+i)+":C"+str(2+i), sheet)
                update_cell(data[title]['VK'], "'" + OUTPUT_LIST_NAME + "'!E"+str(2+i)+":E"+str(2+i), sheet)
            else:
                update_cell(0, "'" + OUTPUT_LIST_NAME + "'!C"+str(2+i)+":C"+str(2+i), sheet)
                update_cell(0, "'" + OUTPUT_LIST_NAME + "'!E"+str(2+i)+":E"+str(2+i), sheet)


if __name__ == '__main__':
    update(get_sheet())
