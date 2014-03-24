# Deletes all sources (not collectors) in a given category.
#
# python rm-src-by-cat.py <accessId/email> <accessKey/password> <category>

import sys

from sumologic import SumoLogic

args = sys.argv
sumo = SumoLogic(args[1], args[2])
cat = args[3]
cs = sumo.collectors()

for c in cs:
	ss = sumo.sources(c['id'])
	for s in ss:
		if s['category'] == cat:
			sv, _ = sumo.source(c['id'], s['id'])
			print sumo.delete_source(c['id'], sv).text
