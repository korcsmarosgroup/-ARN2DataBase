"""
 Opens pdb files, runs DSSP and ELMpred script on them, then deletes them
"""

# Imports
import subprocess
import logging
import os, gzip, shutil
from DATA.workflow.PTM.databases.ELMpred import pred_new

# Defining constants
dir_path = os.path.dirname(os.path.realpath(__file__))
print(dir_path)
LOCATION = os.path.join(dir_path, '..', '..', '..', '..', '..', '..', 'DSSP', 'pdb', 'pdb')
logging.basicConfig(level=logging.DEBUG)
loc = subprocess.run('cd ' + LOCATION, shell=True)
for directory in os.listdir(LOCATION):
    unzip_this = os.path.join(dir_path, LOCATION, directory)
    unzip_tohere = os.path.join(dir_path, LOCATION, directory, 'unzipped')
    if not os.path.exists(unzip_tohere):
        os.makedirs(unzip_tohere)
    for zipped in os.listdir(unzip_this):
        pred_new.file_list = []
        print(os.path.join(unzip_this, zipped))
        try:
            with open(os.path.join(unzip_tohere, zipped), 'wb') as outfile:
                with gzip.open(os.path.join(unzip_this, zipped), 'rb') as f:
                    shutil.copyfileobj(f, outfile)
        except OSError:
            continue
        #logging.debug(os.listdir(unzip_tohere))
        logging.debug(os.path.join(unzip_tohere, zipped))
        dssp_name = os.path.join(unzip_tohere, zipped + '.dssp')
        dssp_command = ['/home/signalink/DSSP/dssp-2.0.4-linux-amd64', '-i', os.path.join(unzip_tohere, zipped), '-o', dssp_name]
        #print(dssp_command)
        subprocess.call(dssp_command)
        pred_new.file_list.append(os.path.join(unzip_tohere, zipped))
        #logging.debug(pred_new.file_list)
        """
        run_command = ['python3.5', 'pred_new.py']
        subprocess.Popen(run_command, shell=True)
        remove_command = ['rm -rf', os.path.join(unzip_tohere, '*')]
        subprocess.call(remove_command, shell=True)
        """
