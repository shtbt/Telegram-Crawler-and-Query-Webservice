import asyncio
import sqlite3
import datetime

import telethon
from telethon import TelegramClient, events, utils
from telethon.tl.functions.messages import GetHistoryRequest
import time
import os
import shutil
import json

###################################################
### Telegram Crawler (Event-Based)
###################################################
### By S.H.Tabatabaei
##################################################

# Database Operations: Connect to DB and Create tables if not exists
def connect_to_db():
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


# Download Profile Photo: gets an event and save the correspondent profile photo in DB as well as Folder
async def check_profile_photo_event(event):
    global crs, con,cln
    if event.message is not None and event.message.chat is not None and event.message.chat.photo is not None:
        crs.execute('select count(*) from profile_pics_ where cid_ = ? and pic_id = ?',
                    [event.message.chat.id, event.message.chat.photo.photo_id])
        pp_exists = crs.fetchall()[0][0]
        if not pp_exists:
            pic_path = await cln.download_profile_photo(event.message.chat.id, file='prof_pics/'+str(event.message.chat.id))
            with open(pic_path, 'rb') as f:
                path_, ext_ = os.path.splitext(pic_path)
                blb = f.read()
                crs.execute('insert into profile_pics_ (cid_, pic_id, dt, p_pic,file_name) values (?,?,?,?,?)',
                            [event.message.chat.id, event.message.chat.photo.photo_id, datetime.datetime.now(), blb,
                             str(event.message.chat.photo.photo_id) + ext_])
                con.commit()
                shutil.copy(pic_path, 'prof_pics//' + str(event.message.chat.photo.photo_id) + ext_)
            try:
                os.remove(pic_path)
            except:
                pass

# Download Profile Photo: gets an sender and save the correspondent profile photo in DB as well as Folder
async def check_profile_photo_sender(sender):
    global crs, con
    if sender.photo is not None:
        crs.execute('select count(*) from profile_pics_ where cid_ = ? and pic_id = ?',
                    [sender.id, sender.photo.photo_id])
        pp_exists = crs.fetchall()[0][0]
        if not pp_exists:
            pic_path = await cln.download_profile_photo(sender.id, file='prof_pics/'+str(sender.id))
            with open(pic_path, 'rb') as f:
                path_, ext_ = os.path.splitext(pic_path)
                blb = f.read()
                crs.execute('insert into profile_pics_ (cid_, pic_id, dt, p_pic,file_name) values (?,?,?,?,?)',
                            [sender.id, sender.photo.photo_id, datetime.datetime.now(), blb,
                             str(sender.photo.photo_id) + ext_])
                con.commit()
                shutil.copy(pic_path, 'prof_pics//' + str(sender.photo.photo_id) + ext_)
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


@cln.on(events.NewMessage())
async def main(event):
    if con is None: connect_to_db()
    sender = await event.get_sender()

    _ = await check_profile_photo_event(event)

    _ = await check_profile_photo_sender(sender)

    dlg_id = sender.id
    dlg_name = str(sender.first_name or '') + ' ' + str(sender.last_name or '') if type(
        sender) == telethon.tl.types.User else sender.title
    dlg_username = sender.username if hasattr(sender, 'username') else ''
    crs.execute('insert into channels_ values (?,?,?) on CONFLICT(cid_) DO UPDATE SET channel_name=?,user_name=?',
                [dlg_id, dlg_name, dlg_username, dlg_name, dlg_username])

    cid_ = sender.id
    message_txt = event.message.message
    mid_ = event.message.id
    dt = event.message.date
    edit_dt = event.message.edit_date if event.message.edit_date is not None else event.message.date
    crs.execute(
        'insert into messages_ (cid_, mid_, message_txt, dt, edit_dt) values (?,?,?,?,?) on CONFLICT(cid_, mid_,edit_dt) DO UPDATE SET message_txt=? , dt=?',
        [cid_, mid_, message_txt, dt, edit_dt, message_txt, dt])
    con.commit()

    print('New Message from', dlg_name, ' :', event.message.message)


@cln.on(events.MessageEdited())
async def main(event):
    if con is None: connect_to_db()
    sender = await event.get_sender()

    _ = await check_profile_photo_event(event)

    _ = await check_profile_photo_sender(sender)

    dlg_id = sender.id
    dlg_name = str(sender.first_name or '') + ' ' + str(sender.last_name or '') if type(
        sender) == telethon.tl.types.User else sender.title
    dlg_username = sender.username if hasattr(sender, 'username') else ''
    crs.execute('insert into channels_ values (?,?,?) on CONFLICT(cid_) DO UPDATE SET channel_name=?,user_name=?',
                [dlg_id, dlg_name, dlg_username, dlg_name, dlg_username])

    cid_ = event.chat_id
    message_txt = event.message.message
    mid_ = event.message.id
    dt = event.message.date
    edit_dt = event.message.edit_date if event.message.edit_date is not None else event.message.date
    crs.execute(
        'insert into messages_ (cid_, mid_, message_txt, dt, edit_dt) values (?,?,?,?,?) on CONFLICT(cid_, mid_,edit_dt) DO UPDATE SET message_txt=? , dt=?',
        [cid_, mid_, message_txt, dt, edit_dt, message_txt, dt])
    con.commit()

    print('Edited Message:  from', dlg_name, ' :', event.message.message)


cln.run_until_disconnected()
