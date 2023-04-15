import logging
import telegram
from telegram.error import NetworkError
from time import sleep
import validators
import musicHelper
import json
from datetime import datetime
import _thread
import os
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from telegram import Update
import dbHelper
import eyed3
import config
#the working directory when the script is run as a service is [C:\Users\---\AppData\Local\Programs\Python\Python310]

update_id = None
TOKEN = config.BOT_TOKEN
TIPU_USERNAME = config.TIPU_USERNAME

known_users = config.known_users

#custom keyboard
custom_keyboard = [['=M', '=N']]
reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard, one_time_keyboard=False, resize_keyboard=True)

async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    global update_id

    if update.message:
        # Reply to the message
        user_msg = update.message.text

        user_first_name = update.message.chat.first_name
        chatid = update.message.chat.id
        userid = update.message.from_user.id

        is_group = False
        if (update.message.chat.type in ['group', 'supergroup']):
            is_group = True
            if (user_msg[0] == '/'):
                user_msg = user_msg[1:]
            if(not validators.url(user_msg)):
                if not (TIPU_USERNAME in user_msg):
                    return
            
        if (userid in known_users):
            await process_message(chatid, user_msg, bot, userid, is_group)
        # don't talk to strangers
        #else:
            #generic_response =  "Greetings "+user_first_name

async def process_message(chatid, message, bot, userid, is_group):
    now = datetime.now()
    logging.info("===============================================================")
    logging.info(f"Message from [{known_users[userid]}] - \"{message}\" Group? [{str(is_group)}]")
    if (validators.url(message)):
        downloading_msg_details = await bot.send_message(chat_id = chatid, text = "downloading...")

        mp3file, error_message = musicHelper.download_music(message)
    
        if (mp3file != "ERROR"):
            logging.info(f"Downloaded file [{mp3file}]")
            s_metadata_json = error_message
            metadata = json.loads(s_metadata_json)
            logging.info(f"metadata [{metadata}]")
            _duration = metadata['duration']
            
            thumbnail_file_loc = config.THUMBNAIL_PATH
            # get the album art of the mp3 file about to be sent
            audio_file = eyed3.load(mp3file)
            album_art = audio_file.tag.images[0]
            thumb_file = open(thumbnail_file_loc, "wb")
            thumb_file.write(album_art.image_data)
            thumb_file.close()
            
            logging.info(f"Starting to send MP3 file [{mp3file}]...")            
            await bot.send_audio(chat_id = chatid, audio=open(mp3file, 'rb'), duration=_duration, thumb=open(thumbnail_file_loc,"rb"))
            logging.info(f"MP3 file [{mp3file}] was sent to chat!")
            #save the file to pCloud also
            start_pcloud_upload()
        else:
            if error_message and error_message.strip():
                await bot.send_message(chat_id = chatid, text = error_message)
            else:
                await bot.send_message(chat_id = chatid, text = "something went wrong =")
        await bot.delete_message(chat_id = chatid, message_id=downloading_msg_details.message_id)
    else:
        response = "Hi "+known_users[userid]+"!"
        await bot.send_message(chat_id = chatid, text = response)


async def save_audio_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info(update.message.audio.file_name + " was sent to Tipu to be saved and replicated")
    save_path = config.MUSIC_DIR + update.message.audio.file_name
    
    #save song details to db
    m_info = dbHelper.MusicInfo()
    m_info.source = "direct upload"
    m_info.filename = save_path
    dbHelper.insert_music_base_info(m_info)

    # dowload the file to local storage
    music_file = await update.message.audio.get_file()
    await music_file.download_to_drive(save_path)
    await context.bot.send_message(chat_id = update.message.chat.id, text = update.message.audio.file_name + " was saved to disk. Replication will follow.")
    
    #save the file to pCloud
    start_pcloud_upload()

def start_pcloud_upload():
    logging.info("********\tStarting thread to upload file to pcloud\t********")
    _thread.start_new_thread(os.system, ('python \"' + config.PROJECT_DIR + 'pcloudUpload.py\"',))

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(filename)15s:%(lineno)3s - %(funcName)20s() ::: %(message)s',
    filename=config.LOG_PATH, 
    filemode="a+", 
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')


if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()

    reply_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), reply)

    # for when audio file is sent to Tipu directly
    audio_handler = MessageHandler(filters.AUDIO & (~filters.COMMAND), save_audio_file)
    
    application.add_handler(reply_handler)
    application.add_handler(audio_handler)

    application.run_polling()