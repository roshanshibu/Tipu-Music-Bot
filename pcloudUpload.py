import requests
import dbHelper
import config

import logging
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(filename)15s:%(lineno)3s - %(funcName)20s() ::: %(message)s',
    filename=config.LOG_PATH, 
    filemode="a+", 
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')


PCLOUD_FOLDER_ID = config.PCLOUD_FOLDER_ID
PCLOUD_PLAYLIST_ID = config.PCLOUD_PLAYLIST_ID

PCLOUD_USERNAME = config.PCLOUD_USERNAME
PCLOUD_PASSWORD = config.PCLOUD_PASSWORD

def addToPlaylist(fileid_list, playlistid = PCLOUD_PLAYLIST_ID):
	fileid_string = ",".join([str(i) for i in fileid_list])
	session = requests.Session()
	data = {'username': PCLOUD_USERNAME, 'password': PCLOUD_PASSWORD, 'collectionid':str(playlistid), 'fileids': fileid_string}
	post = session.post('https://eapi.pcloud.com/collection_linkfiles', data=data) 
	if (post.json()['result'] == 0):
		#move the newly added song to first in playlist.. this works only for 1 song
		cur_pos = post.json()['collection']['items']
		new_pos = 1
		fileid = post.json()['linkresult'][-1]['fileid']
		data = {'username': PCLOUD_USERNAME, 'password': PCLOUD_PASSWORD, 'collectionid':str(playlistid), 'item':str(cur_pos), 'fileid': str(fileid), 'position': new_pos}
		reorder_post = session.post('https://eapi.pcloud.com/collection_move', data=data)
		if reorder_post.json()['result'] != 0:
			logging.error ('********\tCould not move song to first position in playlist!')
		else:
			logging.info ('********\tMoved to first position in playlist')

	return post.json()['result']


def uploadFiles(file_list, folderid = PCLOUD_FOLDER_ID):
	logging.info ('********\tUploading...')
	session = requests.Session()
	
	files = {}
	i = 0
	for file in file_list:
		i += 1
		placeholder_name = 'placeholder' + str(i)
		files[placeholder_name] = open(file, 'rb')
	
	data = {'username': PCLOUD_USERNAME, 'password': PCLOUD_PASSWORD, 'folderid': str(folderid)}
	
	post = session.post('https://eapi.pcloud.com/uploadfile', files=files, data=data)
	if (post.json()['result'] == 0):
		logging.info ('********\tUpload complete')
		
		if(folderid == PCLOUD_FOLDER_ID):
			logging.info ('********\tAdding to playlist...')
			
			uploaded_fileid_list = post.json()['fileids']
			ret_add = addToPlaylist(uploaded_fileid_list)
			
			if ret_add != 0:
				logging.error ('********\tFailed to add to playlist!')
	else:
		logging.error ('********\tError while uploading [%s]', post.json())

	logging.info ('********\tCompleted pcloud upload!')
	return (post.json()['result'])
	#https://docs.pcloud.com/methods/file/uploadfile.html
	#returns 0 when successful


pending_list = dbHelper.get_files_not_uploaded_to_cloud()
if len(pending_list) > 0:
	ret = uploadFiles (pending_list)
	if ret == 0:
		if not dbHelper.update_SavedToCloud_for_file(pending_list):
			logging.error ('********\tError while updating SavedToCloud flag in db!')
else:
	logging.info ('********\tNo files pending upload')
logging.info ('********\tExiting pcloud thread\t********')
