import os

# Credentuials -------------------------------------------------------------
# Telegram Bot Token
BOT_TOKEN = '000000:ABCDEFGHIJKLMOP'

# Spotify Developer API Credentials 
# https://developer.spotify.com/
SPOTIFY_USER = "1234567890"
SPOTIFY_CLIENT_ID = "1234567890abcd1234567890"
SPOTIFY_CLIENT_SECRET = "1234567890abcd1234567890"

# the id for a spotify playlist containing all songs *from spotify* that Tipu will download
SPOTIFY_PLAYLIST_URI = "12345678901234567890"

# pCloud Credentials
# https://docs.pcloud.com/
PCLOUD_USERNAME = 'user@mail.com'
PCLOUD_PASSWORD = 'password here'
# the pCloud folder and playlist to which *all* songs will be uploaded to
PCLOUD_FOLDER_ID = 1234567890
PCLOUD_PLAYLIST_ID = 1234567890
#---------------------------------------------------------------------------


TIPU_USERNAME = '@Your bot username'
# The bot will respond only to users whose telegram userIds are in this dict
# Currently, the bot is meant to handle only one user
known_users = {123456789:"User nickname"}

DEFAULT_ALBUM_NAME = 'TipuMusic'

LOG_PATH = 'C:\\Logs\\TipuLogs.log'
MUSIC_DIR = 'C:\\Music\\Tipu Music\\'


PROJECT_DIR = os.path.dirname(__file__)
THUMBNAIL_FILE = 'thumbnail.jpg'
THUMBNAIL_PATH = PROJECT_DIR + '\\' + THUMBNAIL_FILE

DB_NAME = 'TipuMusicInfo.db'
DB_PATH = PROJECT_DIR + '\\' + DB_NAME