# Queries for new hosts and builds a monitor for each
#
# python mk-monitors-by-host.py <accessId> <accessKey> <monitor.json>
#
# where <monitor.json> describes the monitor
#
# 1/ Run query for new hosts
# 2/ Find appropriate dashboard
# 3/ Modify monitor.json query constraint
# 4/ PUT monitor.json

import sys

from sumologic import SumoLogic

args = sys.argv
sumo = SumoLogic(args[1], args[2])
oldWindow = args[3]
newWindow = args[4]

ds = sumo.dashboards()
