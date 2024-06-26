import json
import urllib
import wget
from pathlib import Path
from zipfile import ZipFile
import os
import shutil
import subprocess
import sys
from pathlib import Path
import urllib.request

version = 'dev' # CHANGE TO VERSION NUMBER FOR RELEASE COMMITS!!!!   
                
with urllib.request.urlopen("https://api.github.com/repos/craftnut/GZLauncher/tags") as tags: 
    tags = json.load(tags)
    print(tags)
    
    latest_version = tags[1]
    
    version_num = latest_version['name']
    dl_url = latest_version['zipball_url']
    
    if version == 'dev':
        subprocess.Popen([sys.executable, './gzlauncher.pyw'])
        exit()
    
    elif version_num != version:
        
        update = input(f'New version {version_num} available, would you like to update? (Y, n)')
        
        if update in ['Y', 'y', '']:
            temp_dir = Path("./temp")
            temp_dir.mkdir()
            
            print("Downloading...")
            wget.download(dl_url, out="./temp/temp.zip")
            
            print("Extracting")
            with ZipFile('./temp/temp.zip', 'r') as archive:
                archive.extractall(path='./temp')
                
            temp_dir_list = os.listdir('./temp')
            update = temp_dir_list[0]
                
            os.remove('./main.py')
            os.remove('./gzlauncher.pyw')    
            os.rename(f'./temp/{update}/main.py', './main.py')
            os.rename (f'./temp/{update}/gzlauncher.pyw', './gzlauncher.pyw')  
            shutil.rmtree('./temp')
            
            subprocess.Popen([sys.executable, './main.py'])
            exit()
            
        else:
            print('Launching GZLauncher.')
            subprocess.Popen([sys.executable, './gzlauncher.pyw'])
            exit()
             
    else:
        print('Launching GZLauncher.')
        subprocess.Popen([sys.executable, './gzlauncher.pyw'])
        exit()
    