# Get collectors where field contains some specified string
#
# python get-collectors.py <accessId/email> <accessKey/password> <field> <string>

import sys

from sumologic import SumoLogic

args = sys.argv
sumo = SumoLogic(args[1], args[2])
field, string = args[3], args[4]
cs = sumo.collectors()

for c in cs:
	if field in c and string in c[field]:
		print c
