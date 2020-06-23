import requests
import json
import sys
import subprocess
import time

with open('config.json') as f:
    config = json.load(f)

api_url = config['api_url']
api_key = config['api_key']

headers = {'Authorization': 'Bearer ' + api_key}

r = requests.get(api_url + '/api/v1/server/config', headers=headers)
server_config  = r.json()
# write private key to file
f = open('.privatekey', 'w')
f.write(server_config['private_key'])
f.close()


# start infinite loop of getting client configs and setting them on the server
while True:
    # get current wg config
    cmd = ['wg', 'show', server_config['name']]
    o = subprocess.run(cmd, encoding='utf-8', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if o.returncode != 0:
        print('Failed to get wg status: ' + o.stderr)
        sys.exit(1)
    wg_show = o.stdout

    # get all client devices
    r = requests.get(api_url + '/api/v1/server/devices', headers=headers)
    for client in r.json():
        if client['public_key'] not in wg_show:
            cmd = ['wg', 'set', server_config['name'], 'peer', client['public_key'], 'allowed-ips', client['ip'] + '/32']
            print(' '.join(cmd))
            o = subprocess.run(cmd, encoding='utf-8', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if o.returncode != 0:
                print('Failed to add client: ' + o.stderr)

    # wait a bit
    time.sleep(15)
