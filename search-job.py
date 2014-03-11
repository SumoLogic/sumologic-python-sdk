# Submits search job, waits for completion and returns results.  Pass the query
# via stdin.
#
# cat query.sumoql | python search-job.py <accessId/email> <accessKey/password> <fromTime> <toTime>

import sys

from sumologic import SumoLogic

args = sys.argv
sumo = SumoLogic(args[1], args[2])
fromTime = args[3]
toTime = args[4]
timeZone = args[5]

q = sys.stdin.readlines()
sj = sumo.search_job(q, fromTime, toTime, timeZone)
print sj
status = sumo.search_job_status(sj)
while status['state'] != 'DONE GATHERING RESULTS':
	if status['state'] == 'CANCELLED':
		break
	status = sumo.search_job_status(sj)
print status
