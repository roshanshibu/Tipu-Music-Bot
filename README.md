# Tipu Music Bot
Tipu is a telegram bot that was created to help download, replicate and manage a music collection. It can help you if you like to pretend it's 2005 and hoard MP3 files.  

### When you send Tipu:  
- A YouTube link

### Tipu will:
- Download the audio from the link to a folder in your server,
- Send you the MP3 file,
- Upload the same file to your pCloud folder and playlist,
- Save details about the song to your local database

<br>

### When you send Tipu:  
- A Spotify link

### Tipu will:
- Add the song to your Spotify playlist,
- Find the same song on Youtube (or the best approximate of it), and do the same things done for YouTube links (MP3 file, pCloud upload and save metadata to DB)

<br>

### When you send Tipu:  
- A music file

### Tipu will:
- Upload the file to your pCloud folder and playlist,
- Save details about the song to your local database

<br>

## Running Tipu
You will need
1. A Telegram Bot (make one through [@BotFather](https://t.me/botfather))
2. [API access](https://developer.spotify.com/) to your spotify account
3. A [pCloud account](https://e.pcloud.com/#page=register&invite=9pkRZJURX17)

Create a `config.py` file similar to the `sample-config.py`. Update the access credentials.   
Also update your bot username, your telegram userId, path to the log file and the directory where the music should be saved to. 

Install dependencies and run `bot.py`

> On Windows, consider using [NSSM](https://nssm.cc/) to run the script [as a service](https://www.oreilly.com/library/view/hands-on-software-engineering/9781788622011/66a35121-d465-4318-b566-264dc91b5829.xhtml) 


Happy hoarding :)