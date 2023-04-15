from pytube import YouTube,Search
import os
from urllib.parse import urlparse
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util
import dbHelper
import json
from moviepy.editor import *
import requests
import eyed3
from eyed3.id3.frames import ImageFrame
from PIL import Image
import config

import logging
log = logging.getLogger(__name__)

MUSIC_DIR = config.MUSIC_DIR
PROJECT_DIR = config.PROJECT_DIR
THUMBNAIL_PATH = config.THUMBNAIL_PATH

errorList = {
    "UNKNOWN_HOST_ERR" : "UNKNOWN_HOST_ERR::umm, i don't know what to do with <HOSTNAME> 😬",
    "SPOTIFY_PLAYLIST_ERR" : "SPOTIFY_PLAYLIST_ERR::Spotify playlists are not handled 😐",
    "YT_NO_RESULTS_ERR" : "YT_NO_RESULTS_ERR::Could not find any results for \"<SEARCHQUERY>\" on Youtube 😣"
}

SPOTIFY_PLAYLIST_URI = config.SPOTIFY_PLAYLIST_URI

SPOTIFY_USER = config.SPOTIFY_USER
SPOTIFY_CLIENT_ID = config.SPOTIFY_CLIENT_ID
SPOTIFY_CLIENT_SECRET = config.SPOTIFY_CLIENT_SECRET
scope = 'playlist-modify-private playlist-modify-public'
    

def download_music(url):
    try:
        logging.info (f"Working directory - [{os.getcwd()}]")
        m_info = dbHelper.MusicInfo()
        logging.info(f"url [{url}]")
        m_info.url = url

        #check if we have already downloaded from this url
        p_file_meta = dbHelper.is_music_present_in_db(url)
        if(p_file_meta is not None):
            logging.info(f"File was already downloaded from [{url}]")
            return (p_file_meta[0], p_file_meta[1])

        if (is_youtube_url(url)):
            yt = YouTube(url)
            m_info.source = "YouTube"
        else:
            yt, source_name = get_yt_object(url)
            m_info.source = source_name

        logging.info("Fetching video details...")
        video = yt.streams.filter(only_audio=True).first()
        destination = MUSIC_DIR 
        logging.info("starting download...")
        out_file = video.download(output_path=destination)
        logging.info("download complete!")
        base, ext = os.path.splitext(out_file)
        new_file = base + '.mp3'
        m_info.filename = new_file
        mp4_to_mp3(out_file, new_file, True)
        
        set_yt_thumbnail(yt, new_file, 'music.youtube' in url)
        duration = yt.length

        artist_name = yt.author
        if artist_name[-7:] == "- Topic":
            artist_name = artist_name[:-7].strip()
        metadata ={"duration": str(duration), "artist": artist_name}
        metadata_json = str(json.dumps(metadata))
        m_info.metadata = metadata_json
        
        dbHelper.insert_music_base_info(m_info)
        return (new_file, metadata_json)
    except FileExistsError:
        logging.error(f"File [{new_file}] already exists")
        return ("ERROR", "")
    except Exception as e:
        return process_error(str(e))

def set_yt_thumbnail(yt_object, audio_file, is_yt_music):
    try:
        #first, download the thumbnail image
        logging.info(f"Youtube thumbnail available at [{yt_object.thumbnail_url}]")
        response = requests.get(yt_object.thumbnail_url)
        if response.status_code:
            fp = open(THUMBNAIL_PATH, 'wb')
            fp.write(response.content)
            fp.close()
            #if the url is from youtube music, crop the thumbnail to get proper album art
            if is_yt_music:
                logging.info("Url is from youtube music. Cropping the album art now.")
                thumbnail_img = Image.open(THUMBNAIL_PATH)
                album_art_img = thumbnail_img.crop((140, 60, 500, 420))
                album_art_img.save(THUMBNAIL_PATH)
        #now, we use eyed3 to set this thumbnail for our audio file
        audiofile = eyed3.load(audio_file)
        if (audiofile.tag == None):
            audiofile.initTag()

        audiofile.tag.album = config.DEFAULT_ALBUM_NAME
        audiofile.tag.images.set(ImageFrame.FRONT_COVER, open(THUMBNAIL_PATH, 'rb').read(), 'image/jpeg')
        artist_name = yt_object.author
        if artist_name[-7:] == "- Topic":
            artist_name = artist_name[:-7].strip()
        audiofile.tag.artist = artist_name
        audiofile.tag.save(version=eyed3.id3.ID3_V2_3)
        audiofile.tag.save()
        logging.info(f"Thumbnail added to file [{audio_file}]")
    except Exception as e:
        logging.error(f"Error while adding thumbnail to file [{audio_file}] | Exception {e}")
        
def mp4_to_mp3(mp4, mp3, delete_source_mp4):
    logging.info("converting to mp3...")
    mp4_without_frames = AudioFileClip(mp4)
    mp4_without_frames.write_audiofile(mp3, verbose=False, logger=None)
    mp4_without_frames.close() 
    if (delete_source_mp4):
        os.remove(mp4)
    logging.info ("conversion complete")

def process_error(error_msg):
    logging.error (f"Error! [{error_msg}]")
    for err in errorList:
        if err in error_msg:
            return ("ERROR", error_msg.replace(err+"::" ,""))
    logging.error("Unexpected error: %s", error_msg)
    return ("ERROR", "")
        

def get_hostname(url):
    parsed_uri = urlparse(url)
    hostname = parsed_uri.netloc
    path = parsed_uri.path
    return (hostname, path)

def is_youtube_url(url):
    hostname = get_hostname(url)[0]
    yt_hostnames = ["youtube", "youtu.be"]
    for yt_hostname in (yt_hostnames):
        if (yt_hostname in hostname):
            return True
    else:
        return False

def get_yt_object(url):
    hostname = get_hostname(url)[0]
    if ("spotify" in hostname):
        logging.info("Song from spotify, find it on yt")
        path = get_hostname(url)[1]
        stype = "PLAYLIST"
        if ("track/" in path):
            stype = "TRACK"
        path = path[1:]
        uri = path[path.index('/')+1:]
        yt_obj = get_yt_object_for_spotify(url, stype, uri)
        return (yt_obj, "Spotify")
    else:
        raise Exception(errorList['UNKNOWN_HOST_ERR'].replace('<HOSTNAME>', hostname))
    
def get_yt_object_for_spotify(s_url, resource_type, uri):
    yt_url = s_url
    if (resource_type == "PLAYLIST"):
        logging.error("Spolity playlist url was given, raising error")
        raise Exception(errorList['SPOTIFY_PLAYLIST_ERR'])

    token = util.prompt_for_user_token(SPOTIFY_USER,scope,SPOTIFY_CLIENT_ID,SPOTIFY_CLIENT_SECRET,"http://localhost:8080/")
    sp = spotipy.Spotify(auth=token)

    track_details = sp.track(uri)
    song_name = track_details["name"]
    artists = ""
    for artist_details in (track_details["artists"]):
        artists += artist_details["name"] + " "
    sq = artists + song_name
    logging.info (f"search query = [{sq}]")
    s = Search(sq)
    if (len(s.results) == 0):
        raise Exception(errorList['YT_NO_RESULTS_ERR'].replace('<SEARCHQUERY>', sq))

    add_song_to_spotify_pl(sp, uri, SPOTIFY_PLAYLIST_URI)

    return (s.results[0])


def add_song_to_spotify_pl(spotify_ob, track_uri, playlist_uri):
    spotify_ob.user_playlist_add_tracks(
        user=SPOTIFY_USER,
        playlist_id=playlist_uri,
        tracks=[track_uri],
        position=None)
    return

#mp3file = dowmload_music("https://youtu.be/lXPYzs2BgWg")
#mp3file = dowmload_music("https://open.spotify.com/track/5JKU2tXiG3yvJtefNwe7ZQ?si=RaJ6sp2cR5Ow-7lZM7R3wA&utm_source=native-share-menu")
#print ("File downloaded ["+mp3file+"]")

