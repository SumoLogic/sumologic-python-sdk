# Submits search job, waits for completion, then prints and emails _messages_
# (as opposed to records).  Pass the query via stdin.
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
# 1408643380441 1408649380441 PST false

import json
import sys
import time

from sumologic import SumoLogic

LIMIT = 42

args = sys.argv
sumo = SumoLogic(args[1], args[2])
fromTime = args[3]
toTime = args[4]
timeZone = args[5]
byReceiptTime = args[6]

delay = 5
q = ' '.join(sys.stdin.readlines())
sj = sumo.search_job(q, fromTime, toTime, timeZone, byReceiptTime)

status = sumo.search_job_status(sj)
while status['state'] != 'DONE GATHERING RESULTS':
	if status['state'] == 'CANCELLED':
		break
	time.sleep(delay)
	status = sumo.search_job_status(sj)

print(status['state'])

if status['state'] == 'DONE GATHERING RESULTS':
    count = status['messageCount']
    limit = count if count < LIMIT and count != 0 else LIMIT # compensate bad limit check
    r = sumo.search_job_messages(sj, limit=limit)
    print(r)
