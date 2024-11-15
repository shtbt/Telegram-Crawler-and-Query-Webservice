![alt text](https://github.com/shtbt/Telegram-Crawler-and-Query-Webservice/blob/main/icon_telegram.png?raw=true)


# Telegram Crawler & Web Service

This project is a Python-based hobby project for real-time data crawling from Telegram, including messages and profile pictures, with a RESTful API for querying the gathered data. It utilizes [Telethon](https://github.com/LonamiWebs/Telethon), database management using SQLite, and building a RESTful API with [Flask](https://flask.palletsprojects.com/). 
We start by running an event-based telegram crawler (`main_event.py`) and save them in sqlite DB. This code is running always and catches every event including **new message** and **edit message** and save them in sqlite db. Then we run `query_services.py` to enable querying through gathered data via webservices. 

## Features

- **Telegram Client Connection**: Connect to a Telegram client using the Telethon library.
- **Catching messege events**: Instantly catches any messages and any edits of the corresponding telegram client and save them in sqlite db
- **Downloading Profile Pictures**: Downloading profile pictures of any user who messaged private or in groups. Also Profile pictures of channels and groups.  
- **Web Service**: Set up a Flask-based REST API to query and access the crawled data.

## DB 

- **Channels_**: Contains information about channels, groups and users which has been crawled.
  - cid_: channel or group or user id
  - channel_name: channel or group or user name
  - user_name
- **Messages**: Crawled messages history. In this table, al messages and all versions of a specific maessage is ebeing saved.
  - cid_: corresponding channel id
  - mid_: message unique id in channel
  - message_txt
  - dt: message publish date
  - edit_dt: edit date for message.
- **profile_pics**: All profile pictures will be saved here.
  - cid_
  - pic_id: Profile Picture Unique ID
  - dt
  - p_pic
  - file_name
- **auth_**: contains information about webservice users
## Webservices
  - **/create_user**: Create user for accessing webservices. gets **username** , **password** and **confirm_password**. Admin must set **active_** field in **auth_** table to 1 in order to enable user for accessing webservices.
  - **/get_wordcount_general**: Gets **query_word** parameter as well as **username** and **password** then searches the whole DB for number of  occurences of **query_word** in all dialogs.
  - **/get_wordcount_channel**: Gets **query_word** and **channel** parameter as well as **username** and **password** then searches the DB for number of  occurences of **query_word** in **channel**.

## Getting Started

### Prerequisites

To run this project, you will need the following Python packages:

- `Telethon` - For connecting and interacting with the Telegram client.
- `Flask` - For setting up the web service.

Install dependencies using pip:

```bash
pip install telethon flask telethon
```
 Also, you need to get ***api_id*** and ***api_hash*** for a telegram account. 
 To do so:
 1. Go to [my.telegram.org](https://my.telegram.org/)  
 2. Enter Phone Number of Telegram Account and Hit **Next**
 3. Go to API development tools 
 4. Create an app and get **api_id** & **api_hash**
 5. Place these two in the `creds.json` file to be used in the codes.



### Run The Event Crawler
Run the code `main_event.py` once:
```bash
python3 main_event.py
```
In the first run, you will be asked to enter the phone number and then enter the verification code which is being sent to your telegram account. This code must be up always, so, you can cancel the run and run it again with ***nohup*** in order to prevent process from being killed:
```bash
nohup python3 main_event.py >> ev.log &
```
### Run The Query Service
In order to query the whole data that we have in sqlite (and is being larger every seconds), we use ***Flask*** in order to develope webservices to give information to cunsumers. In order to run the code:
1. Set environment vaniables of flask:
```bash
export FLASK_APP=query_services
export FLASK_ENV=production
```
2. Run the code using ***nohup*** to be up always:
```bash
nohup flask run --host=0.0.0.0 >> flask_log.log &
```
here `--host=0.0.0.0` allows requests to be accepted from any address.
The webservices will be available at `http://127.0.0.1:5000` locally or `http://YOUR_SERVER_IP:5000` remotely.

## Security Note 
To avoid exposing sensitive information like Telegram credentials, please ensure they are kept private or use environment variables to manage them.

## Contributing
Contributions are welcome! If you have ideas to improve this project, feel free to submit a pull request.

## License
This project is open-source and available under the MIT License.