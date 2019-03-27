# Remove collectors where field contains some specified string
#
# python rm-collectors.py <accessId> <accessKey> <field> <string>

import sys

from sumologic import SumoLogic

args = sys.argv
sumo = SumoLogic(args[1], args[2])
field, string = args[3], args[4]
cs = sumo.collectors()

for c in cs:
	if field in c and string in c[field]:
		cv, _ = sumo.collector(c['id'])
		print(sumo.delete_collector(cv).text)
