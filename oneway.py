# -*- coding: utf-8 -*-


import sys

import pickle

# Working with files modules.
import os.path
from file_to_text import file_to_text

import requests

# Google API modules.
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


# Login data locations.
CREDENTIALS_PATH = '../login/credentials.json'
TOKEN_PATH = '../login/token.pickle'
YOUTUBE_KEY = file_to_text('../login/youtube_key.txt')
VK_KEY = file_to_text('../login/vk_key.txt')

# Usage rights. If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a spreadsheet.
SPREADSHEET_ID = '1Bs-YiO05A6Rb7L-5HPPxJPC6cYwAvTozxGRMEF9v6Q0'
MAX_RANGE = 'A2:H200'
SOURCE_RANGE_NAME = "'Технические данные'!" + MAX_RANGE


"""Get YouTube channel subscribers count.
Args:
    channel_id: ID of YouTube channel.
Returns:
    Channel subscribers count.
"""
def get_youtube_subscribers(channel_id):
    return requests.get('https://www.googleapis.com/youtube/v3/channels?part=statistics&id=' + channel_id + '&key=' + YOUTUBE_KEY).json()['items'][0]['statistics']['subscriberCount']


"""Get VK group subscribers/members count.
Args:
    group_id: ID of VK group.
Returns:
    Group subscribers/members count.
"""
def get_vk_subscribers(group_id):
    result = 0
    try:
        result = requests.get("https://api.vk.com/method/groups.getMembers?group_id=" + group_id + "&v=5.52&&access_token=" + VK_KEY).json()['response']['count']
    except Exception as e:
        user_id = group_id
        result = requests.get("https://api.vk.com/method/users.getFollowers?user_id=" + user_id + "&v=5.52&&access_token=" + VK_KEY).json()['response']['count']

    return result


# TODO
def get_telegram_subscribers(channel_id):
    pass


def get_sheet():
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


def get_range(list, begin, end):
    return "'" + list + "'!" + begin + ":" + end


def update_cell(data, cell, sheet):
    values = [[data]]
    body = { 'values': values }
    result = sheet.values().update(
    spreadsheetId=SPREADSHEET_ID, range=cell,
    valueInputOption='RAW', body=body).execute()


def fill_list(list, yt_column, vk_column, tg_column, data, sheet):
    # Write data to given list in sheet.
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                range="'" + list + "'!" + MAX_RANGE).execute()
    values = result.get('values', [])

    if not values:
        print('ERROR: No data found.')
    else:
        for i in range(len(values)):
            row = values[i]
            if len(row) == 0: continue
            print(row[0])
            title = str(row[0].encode('utf-8'))
            if title in data:
                data[title]['YT'] = int(str(data[title]['YT']))
                print(data[title]['YT'])
                data[title]['VK'] = int(str(data[title]['VK']))
                print(data[title]['VK'])
                if yt_column != None:
                    update_cell(data[title]['YT'], get_range(list, yt_column+str(2+i), yt_column+str(2+i)), sheet)
                if vk_column != None:
                    update_cell(data[title]['VK'], get_range(list, vk_column+str(2+i), vk_column+str(2+i)), sheet)
            #else:
            #    if yt_column != None:
            #        update_cell(0, get_range(list, yt_column+str(2+i), yt_column+str(2+i)), sheet)
            #    if vk_column != None:
            #        update_cell(0, get_range(list, vk_column+str(2+i), vk_column+str(2+i)), sheet)


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


    if sys.argv[1] == 'main':
        fill_list('One Way', 'C', 'E', None, data, sheet)
    elif sys.argv[1] == 'youtube':
        fill_list('Список каналов в YouTube', 'C', None, None, data, sheet)
    elif sys.argv[1] == 'vk':
        fill_list('Список сообществ в VK', None, 'C', None, data, sheet)
    #fill_list('Список каналов в Telegram', None, None, 'C', data, sheet)


if __name__ == '__main__':
    assert(len(sys.argv) == 2)
    assert(sys.argv[1] in ['main', 'youtube', 'vk'])
    update(get_sheet())
