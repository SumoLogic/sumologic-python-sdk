# Exports all content (Library), that is; scheduled searches, dashboards, views...
#   First it gets an index of users, and then it goes one by one.
#
# python export-all-content.py <accessId> <accessKey>

#! /usr/bin/python

# Exports all content (Library), that is; scheduled searches, dashboards, views...
#   First it gets an index of users, and then it goes one by one.

# Please, before running this, set `.env` file in this folder, see example


FOLDER = 'global_content'           # output folder
INDEX  = f'{FOLDER}/_index.json'    # output index of users

STEP = 1        # seconds to wait each step, for the job to be ready
TIMEOUT = 10    # how many steps


import time
import json
import sys

from sumologic import SumoLogic

args = sys.argv
sumo = SumoLogic(args[1], args[2])

def global_content_index():

    # Global index, Schedule job
    s = sumo.global_export_content()
    r = json.loads(s.text)
    job_id = r['id']
    print(job_id)

    # Global index, Wait for job
    timeout = 0
    ready = False
    while not ready:
        time.sleep(STEP)
        s = sumo.global_check_export_status(job_id)
        r = json.loads(s.text)
        print(r)
        if r['status'] == 'Success':
            ready = True
        timeout += 1
        if timeout >= TIMEOUT:
            break
    if not ready:
        print(f'ERROR: timeout while waiting for job: {job_id}')
        return

    # Global index, Get result
    s = sumo.global_get_export_content_result(job_id)
    with open(INDEX, 'w') as f:
        f.write(s.text)


def global_content_user(username, userid):
    print(f'"{username}.{userid}.json"')

    # User, Schedule job
    s = sumo.export_content(userid, isAdminMode=True)
    r = json.loads(s.text)
    job_id = r['id']
    print(job_id)

    # User, Wait for job
    timeout = 0
    ready = False
    while not ready:
        time.sleep(STEP)
        s = sumo.check_export_status(userid, job_id, isAdminMode=True)
        r = json.loads(s.text)
        print(r)
        if r['status'] == 'Success':
            ready = True
        timeout += 1
        if timeout >= TIMEOUT :
            break
    if not ready:
        print(f'ERROR: timeout while waiting for job: {job_id}')
        return

    # Global index, Get result
    s = sumo.get_export_content_result(userid, job_id, isAdminMode=True)
    with open(f'{FOLDER}/{username}.{userid}.json', 'w') as f:
        f.write(s.text)

def global_content_allusers():

    users = {}
    with open(INDEX, 'r') as f:
        j = json.loads(f.read())
        for i in j['data']:
            #users[i['id']] = i['name']
            users[i['name']] = i['id']

    for username in sorted(users.keys()):
        global_content_user(username, users[username])


global_content_index()
global_content_allusers()


