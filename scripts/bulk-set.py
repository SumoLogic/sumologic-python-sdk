# Sets an attribute across all collectors and sources in a given account.
#
# python bulk-set.py <accessId> <accessKey> <attribute> <value>

import pprint
import sys
import time

from sumologic import SumoLogic

args = sys.argv
sumo = SumoLogic(args[1], args[2])
delay = .25
time.sleep(delay)
attr, val = args[3], args[4]
cs = sumo.collectors()
time.sleep(delay)
f = [{u'regexp': u'\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.(\\d{1,3})', u'mask': u'255', u'filterType': u'Mask', u'name': u'last octet mask'}]

for c in cs:
    if 'category' not in c or 'bwe' not in c['category'] and 'bwm' not in c['category']:
        print 'collector: ' + c['name']
        ss = sumo.sources(c['id'])
        time.sleep(delay)
        for s in ss:
            sv, etag = sumo.source(c['id'], s['id'])
            time.sleep(delay)
            svi = sv['source']
            if 'category' not in svi or 'bwe' not in svi['category'] and 'bwm' not in svi['category']:
                print 'source: ' + svi['name']
                svi['filters'] = f
                r = sumo.update_source(c['id'], sv, etag)
                print r
                print r.text
                time.sleep(delay)
            #if svi['forceTimeZone'] == False:
            #    svi['forceTimeZone'] = True
            #    svi[u'timeZone'] = u'UTC'
            #    r = sumo.update_source(c['id'], sv, etag)
            #    print str(r) + ': ' + str(r.text)
            #    time.sleep(delay)
