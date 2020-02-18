import os
import shutil

def pool2data(POOL_RAW_DATA):
    try:
        # copy raw data from pools server into data folder
        shutil.copy(POOL_RAW_DATA, './data/raw_data')
    except:
        # mount the drive
        os.system('sh ../../../zhaw_cifs.sh')
        # copy raw data from pools server into data folder
        shutil.copy(POOL_RAW_DATA, './data/raw_data')
