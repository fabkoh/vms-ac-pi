# Python program to npm run start

import os

def run_fe():
    npmcmd = 'cd /home/etlas/vms-ac-ui-next && npm run start'
    os.system(npmcmd)

while True:
    try:
        run_fe()
        break
    except:
        pass