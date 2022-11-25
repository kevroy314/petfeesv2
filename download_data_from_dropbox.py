import dropbox
import os

TOKEN = "<INSERT_ACCESS_TOKEN>"
def connect_to_dropbox():
    try:
        dbx = dropbox.Dropbox(TOKEN)
        print('Connected to Dropbox successfully')
    except Exception as e:
        print(str(e))
    return dbx
dbx = connect_to_dropbox()

local_directory = './data'
for root, dirs, files in os.walk(local_directory):
    for filename in files:
        local_path = os.path.join(root, filename)
        relative_path = '/'+os.path.relpath(local_path, local_directory)
        with open(local_path, 'rb') as f:
            print("Uploading {} to {}".format(local_path, relative_path))
            dbx.files_upload(f.read(), relative_path)