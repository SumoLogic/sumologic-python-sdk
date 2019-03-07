# Submits search job, waits for completion, then prints and emails results.
# Pass the query via stdin.
#
# cat query.sumoql | python search-job.py <accessId> <accessKey> \
# <endpoint> <fromDate> <toDate> <timeZone> <byReceiptTime>
#
# Note: fromDate and toDate must be either ISO 8601 date-times or epoch
#       milliseconds
#
# Example:
#
# cat query.sumoql | python search-job.py <accessId> <accessKey> \
# https://api.us2.sumologic.com/api/v1/ 1408643380441 1408649380441 PST false

import json
import sys
import time
import logging

logging.basicConfig(level=logging.DEBUG)

from sumologic import SumoLogic

LIMIT = 42

args = sys.argv
sumo = SumoLogic(args[1], args[2], args[3])
fromTime = int(args[4])
toTime = int(args[5])
# timeZone = args[6]
# byReceiptTime = args[7]

delay = 5
q = ' '.join(sys.stdin.readlines())
# sj = sumo.search_job(q, fromTime, toTime, timeZone, byReceiptTime)
sj = sumo.search_metrics(q, fromTime, toTime)
print(sj)
# status = sumo.search_job_status(sj)
# while status['state'] != 'DONE GATHERING RESULTS':
#     if status['state'] == 'CANCELLED':
#         break
#     time.sleep(delay)
#     status = sumo.search_job_status(sj)
#
# print(status['state'])
#
# if status['state'] == 'DONE GATHERING RESULTS':
#     count = status['recordCount']
#     limit = count if count < LIMIT and count != 0 else LIMIT # compensate bad limit check
#     r = sumo.search_job_records(sj, limit=limit)
#     print(r)
