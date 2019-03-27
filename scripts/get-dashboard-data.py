# Get all dashboard data
#
# python get-dashboard-data.py <accessId> <accessKey>

import sys

from sumologic import SumoLogic

args = sys.argv
sumo = SumoLogic(args[1], args[2], args[3])
ds = sumo.dashboards(True)
print(ds)

#for d in ds:
#	print(d)
