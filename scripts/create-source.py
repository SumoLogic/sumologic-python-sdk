# Create source in the collector, where field contains some specified string
#
# python create-source.py <accessId/email> <accessKey/password> <field> <string> <source definition json>

import sys
import json

from sumologic import SumoLogic

args = sys.argv
sumo = SumoLogic(args[1], args[2])
field, string = args[3], args[4]
source = json.loads(args[5])
cs = sumo.collectors()

for c in cs:
        print c
        print field, string
	if field in c and string in c[field]:
		print sumo.create_source(c['id'],source)
