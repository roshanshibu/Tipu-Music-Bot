# Tipu Music Bot
Tipu is a telegram bot that was created to help download, replicate and manage a music collection.  
It can help you if you like to pretend it's 2005 and hoard MP3 files.  

<br>

## When you send Tipu: `a YouTube link`
### Tipu will:
- Download the audio from the link to a folder in your server,
- Send you the MP3 file,
- Upload the same file to your pCloud folder and playlist,
- Save details about the song to your local sqlite database

<br>

## When you send Tipu: `a Spotify link`
### Tipu will:
- Add the song to your Spotify playlist,
- Find the same song on Youtube (or the best approximate of it), and do the same things done for YouTube links (MP3 file, pCloud upload and save metadata to DB)

<br>

## When you send Tipu: `an Audio file`
### Tipu will:
- Save the file in your server
- Upload the file to your pCloud folder and playlist,
- Save details about the song to your local sqlite database

<br>

## Running Tipu
You will need
1. A Telegram Bot (make one through [@BotFather](https://t.me/botfather))
2. [API access](https://developer.spotify.com/) to your spotify account
3. A [pCloud account](https://e.pcloud.com/#page=register&invite=9pkRZJURX17)

Create a `config.py` file and copy the contents of `sample-config.py`. Update the access credentials.   
Also update your bot username, your telegram userId, path to the log file and the directory where the music should be saved to. 

Install dependencies and run `bot.py`

> On Windows, consider using [NSSM](https://nssm.cc/) to run the script [as a service](https://stackoverflow.com/a/46450007/5604622) 


Happy hoarding :)
