from flask import Flask, jsonify, request
import sqlite3
from flask_bcrypt import Bcrypt

app = Flask(__name__)
bcrypt = Bcrypt(app)

def connect_to_db():
    # Database Operations: Connect to DB and Create tables if not exists
    global con, crs
    try:
        con = sqlite3.connect('telegram_crawler.db',check_same_thread=False)
        crs = con.cursor()
        crs.execute('create table if not exists channels_ (cid_ text primary key, channel_name text,user_name text)')
        crs.execute(
            'create table if not exists messages_ (cid_ text ,mid_ text, message_txt text, dt TIMESTAMP, edit_dt TIMESTAMP , constraint messages2_pk primary key (cid_, mid_,edit_dt))')
        crs.execute(
            'create table if not exists profile_pics_ (cid_ text , pic_id text, dt TIMESTAMP, p_pic BLOB,file_name text)')
        crs.execute('create table if not exists auth_ (uid_  INTEGER PRIMARY KEY,uname_ text, pass_ text,active_ integer)')
    except Exception as ex:
        print('Error in DB: ' + str(ex))
        exit()


def create_user_(user_name , passwd,conf_pass):
    crs.execute('select count(*) from auth_ where uname_=?',[user_name])
    if(crs.fetchall()[0][0] > 0):
        return -1,'User exists'
    if(passwd!=conf_pass):
        return -2,'Password and Confirm Password not match'
    pw_hash = bcrypt.generate_password_hash(passwd)
    
    crs.execute('insert into auth_ (uname_ , pass_ ,active_ ) values(?,?,?)',[user_name,pw_hash,0])
    con.commit()
    return 1,'User Created Successfull. Please ask admin to activate!'

def authenticate_user_(user_name , passwd):
    pw_hash = bcrypt.generate_password_hash(passwd)
    crs.execute('select uname_ , pass_ ,active_ from auth_ where uname_=?',[user_name])
    res=crs.fetchall()
    if(len(res)!= 1):
        return -1,'User Not exists:'
    
    if(not bcrypt.check_password_hash(res[0][1], passwd)):
        return -3,'Incorrect Password'
    
    if(res[0][2]!=1):
        return -2,'User Not Active'
    
    return 1,'Success!'

        
con, crs = None, None
connect_to_db()

@app.route('/create_user')
def create_user_req_():
    uname=request.args.get('username')
    pwd=request.args.get('password')
    cpwd=request.args.get('confirm_password')
    _,mes=create_user_(uname,pwd,cpwd)
    resp={'message':mes }
    return jsonify(resp)

@app.route('/get_all_dialogs')
def get_all_dialogs_req_():
    q=request.args.get('query_word')
    uname=request.args.get('username')
    pwd=request.args.get('password')
    n_,mes=authenticate_user_(uname,pwd)
    if n_!=1:
        resp={'query_word':q ,'message':mes }
        return jsonify(resp)
     
    resp={'query_word':q ,'message':mes }
    return jsonify(resp)

@app.route('/get_wordcount_general')
def get_wordcount_general_req_():
    q=request.args.get('query_word')
    uname=request.args.get('username')
    pwd=request.args.get('password')
    n_,mes=authenticate_user_(uname,pwd)
    if n_!=1:
        resp={'query_word':q ,'resp':None,'message':mes }
        return jsonify(resp)
    
    crs.execute(f"select count(*) from messages_ where lower(message_txt) like '%{q.lower()}%' ")
    res=crs.fetchall()[0][0]
    
    resp={'query_word':q,'resp':res ,'message':mes }
    return jsonify(resp)

@app.route('/get_wordcount_channel')
def get_wordcount_channel_req_():
    q=request.args.get('query_word')
    c=request.args.get('channel')
    uname=request.args.get('username')
    pwd=request.args.get('password')
    n_,mes=authenticate_user_(uname,pwd)
    if n_!=1:
        resp={'query_word':q ,'resp':None,'message':mes }
        return jsonify(resp)
    
    crs.execute(f"select count(*) from messages_ m , channels_ c where c.cid_=m.cid_ and c.user_name='{c}' and lower(m.message_txt) like '%{q.lower()}%'   ")
    res=crs.fetchall()[0][0]
    
    resp={'query_word':q,'channel':c,'resp':res ,'message':mes }
    return jsonify(resp)

