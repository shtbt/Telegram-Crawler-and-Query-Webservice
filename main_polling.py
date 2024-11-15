import asyncio
import os
import shutil
import sqlite3
from telethon import TelegramClient, sync
from telethon.tl.functions.messages import GetHistoryRequest
import time
import datetime
import json

###################################################
### Telegram Crawler
###################################################
### By S.H.Tabatabaei
##################################################

delta_days = 1  # Number of Max Days of Message Crawling
sleep_sec = 1200  # Number of Seconds between iterations.
just_once=False



def connect_to_db():
    # Database Operations: Connect to DB and Create tables if not exists
    global con, crs
    try:
        con = sqlite3.connect('telegram_crawler.db')
        crs = con.cursor()
        crs.execute('create table if not exists channels_ (cid_ text primary key, channel_name text,user_name text)')
        crs.execute(
            'create table if not exists messages_ (cid_ text ,mid_ text, message_txt text, dt TIMESTAMP, edit_dt TIMESTAMP , constraint messages2_pk primary key (cid_, mid_,edit_dt))')
        crs.execute(
            'create table if not exists profile_pics_ (cid_ text , pic_id text, dt TIMESTAMP, p_pic BLOB,file_name text)')
    except Exception as ex:
        print('Error in DB: ' + str(ex))
        exit()


def check_profile_photo(dlg):
    global crs, con,cln
    #####################################################
    ##########################Check Profile Photo########
    #####################################################
    if dlg.message is not None and dlg.message.chat is not None and dlg.message.chat.photo is not None:
        crs.execute('select count(*) from profile_pics_ where cid_ = ? and pic_id = ?',
                    [dlg.id, dlg.message.chat.photo.photo_id])
        pp_exists = crs.fetchall()[0][0]
        if not pp_exists:
            pic_path = cln.download_profile_photo(dlg.id, file='prof_pics/'+str(dlg.id))
            with open(pic_path, 'rb') as f:
                path_, ext_ = os.path.splitext(pic_path)
                blb = f.read()
                crs.execute('insert into profile_pics_ (cid_, pic_id, dt, p_pic,file_name) values (?,?,?,?,?)',
                            [dlg.id, dlg.message.chat.photo.photo_id, datetime.datetime.now(), blb,
                             str(dlg.message.chat.photo.photo_id) + ext_])
                con.commit()
                shutil.copy(pic_path, 'prof_pics//' + str(dlg.message.chat.photo.photo_id) + ext_)
            try:
                os.remove(pic_path)
            except:
                pass


con, crs = None, None
connect_to_db()

try:
    os.mkdir('prof_pics')
except:
    pass


# Telegram Client Operations
# Enter https://my.telegram.org  --> API development tools --> create an app and get api_id & api_hash --> place them into creds.json
# In the first run, you will be asked to enter the phone number and write the verification code
json_file_path = r"creds.json"
try:
    with open(json_file_path, "r") as f:
        credentials = json.load(f)
except:
    print('Error Reading Credential Files!')
    exit()

session_name=credentials['session_name']
api_id=credentials['api_id']
api_hash=credentials['api_hash']

cln = TelegramClient(session_name,api_id , api_hash)
cln.start()


# Main Loop
while True:
    dlgs = cln.get_dialogs()  # Getting All Telegram Account Dialogs(Channels, Groups, Users)

    for dlg in dlgs:
        #########################################
        check_profile_photo(dlg)
        dlg_id = dlg.id
        dlg_name = dlg.name
        dlg_username = dlg.entity.username if hasattr(dlg.entity, 'username') else ''
        crs.execute('insert into channels_ values (?,?,?) on CONFLICT(cid_) DO UPDATE SET channel_name=?,user_name=?',
                    [dlg_id, dlg_name, dlg_username, dlg_name, dlg_username])
        con.commit()


        peer = dlg.dialog.peer  # Getting Peer for crawling the dialog

        if peer is None:
            continue

        # If the las message belongs to more than delta_days ago, do not crawl this dialog
        if dlg.message is not None and dlg.message.date.date() < (
                datetime.datetime.now() - datetime.timedelta(days=delta_days)).date():
            continue

        print(f'Crawling {dlg_id}({dlg_name})')
        flag = True
        offset = 0
        # Crawling this dialog in a loop. You can get maximum 100 messgaes per request.
        # Continue this requests until you get a message for more than delta_days ago.
        while flag:
            history = cln(
                GetHistoryRequest(peer=peer, offset_id=offset, offset_date=None, add_offset=0, limit=100, max_id=0,
                                  min_id=0, hash=0))
            # If the dialog is empty, go to the next dialog
            if len(history.messages) == 0:
                break

            offset = history.messages[-1].id
            for h in history.messages:
                if h.date.date() < (datetime.datetime.now() - datetime.timedelta(days=delta_days)).date():
                    flag = False
                    break

                cid_ = dlg_id#h.chat_id
                message_txt = h.message
                mid_ = h.id
                dt = h.date
                edit_dt = h.edit_date if h.edit_date is not None else h.date
                crs.execute(
                    'insert into messages_ (cid_, mid_, message_txt, dt, edit_dt) values (?,?,?,?,?) on CONFLICT(cid_, mid_,edit_dt) DO UPDATE SET message_txt=? , dt=?',
                    [cid_, mid_, message_txt, dt, edit_dt, message_txt, dt])
                con.commit()
    if just_once:
        exit()
    print(f'Falling sleep for {sleep_sec} seconds.')
    time.sleep(sleep_sec)
