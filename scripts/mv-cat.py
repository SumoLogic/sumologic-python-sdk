# Renames a category across all collectors and sources in a given account.
#
# python mv-cat.py <accessId> <accessKey> <fromName> <toName>
#
# TODO update query category constraints
# TODO regex

import sys

from sumologic import SumoLogic

args = sys.argv
sumo = SumoLogic(args[1], args[2])
fromCat, toCat = args[3], args[4]
cs = sumo.collectors()

for c in cs:
	if 'category' in c and c['category'] == fromCat:
		cv, etag = sumo.collector(c['id'])
		cv['collector']['category'] = toCat
		print sumo.update_collector(cv, etag).text
	ss = sumo.sources(c['id'])
	for s in ss:
		if s['category'] == fromCat:
			sv, etag = sumo.source(c['id'], s['id'])
			sv['source']['category'] = toCat
			print sumo.update_source(c['id'], sv, etag).text
