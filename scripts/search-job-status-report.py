# Submits search job, waits for completion, then prints stats about the searchjob  Pass the query via stdin.
#
# cat query.sumoql | python search-job-messages.py <accessId> <accessKey> \
# <fromDate> <toDate> <timeZone> <byReceiptTime>
#
# Note: fromDate and toDate must be either ISO 8601 date-times or epoch
#       milliseconds
#
# Example:
#
# cat query.sumoql | python search-job-messages.py <accessId> <accessKey> \
# https://api.us2.sumologic.com/api/v1/ 1553630969000 1408649380441 PST false

import json
import sys
import time

from sumologic import SumoLogic

LIMIT = 42




args = sys.argv
sumo = SumoLogic(args[1], args[2], args[3])
fromTime = args[4]
toTime = args[5]
timeZone = args[6]
byReceiptTime = args[7]

delay = 5
duration = 0
q = ' '.join(sys.stdin.readlines())
sj = sumo.search_job(q, fromTime, toTime, timeZone, byReceiptTime)

status = sumo.search_job_status(sj)
while status['state'] != 'DONE GATHERING RESULTS':
    if status['state'] == 'CANCELLED':
        break
    time.sleep(delay)
    status = sumo.search_job_status(sj)
    duration += delay
    print("STILL GATHERING RESULTS ({})".format(duration))

print(status['state'])

if status['state'] == 'DONE GATHERING RESULTS':
    count = status['messageCount']
    limit = count if count < LIMIT and count != 0 else LIMIT # compensate bad limit check
    r = sumo.search_job_messages(sj, limit=limit)
    print(r)