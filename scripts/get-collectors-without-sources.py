# Get collectors where field contains some specified string
#
# python get-collectors.py <accessId> <accessKey> <field> <string>

import sys
import time
from sumologic import SumoLogic

args = sys.argv
sumo = SumoLogic(args[1], args[2])
#field, string = args[3], args[4]
cs = sumo.collectors()

for c in cs:
	# if field in c and string in c[field]:
	if c['collectorType'] == "Installable" and "ip-172" in c['name']:
		time.sleep(.5)
		collector = sumo.collector(c['id'])
		sumo.update_collector(collector[0],collector[1])