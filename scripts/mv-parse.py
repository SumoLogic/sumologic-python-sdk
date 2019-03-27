# Clobbers (unconditional replace) parse expression everywhere in a given content
#
# python mv-parse.py <accessId> <accessKey> <fully_qualified_folder> <from_expression> <to_expression>

#import logging
import string
import sys

from sumologic import SumoLogic

## These two lines enable debugging at httplib level (requests->urllib3->http.client)
## You will see the REQUEST, including HEADERS and DATA, and RESPONSE with HEADERS but without DATA.
## The only thing missing will be the response.body which is not logged.
#try:
#    import http.client as http_client
#except ImportError:
#    # Python 2
#    import httplib as http_client
#http_client.HTTPConnection.debuglevel = 1
#
## You must initialize logging, otherwise you'll not see debug output.
#logging.basicConfig()
#logging.getLogger().setLevel(logging.DEBUG)
#requests_log = logging.getLogger("requests.packages.urllib3")
#requests_log.setLevel(logging.DEBUG)
#requests_log.propagate = True

args = sys.argv
sumo = SumoLogic(args[1], args[2])
path, from_expr, to_expr = args[3], args[4], args[5]
cs = sumo.contents(path)['children']

for c in cs:
	if c['type'] == 'Search':
		print('before: ' + c['searchQuery'] + '\n')
		c['searchQuery'] = string.replace(c['searchQuery'], from_expr, to_expr, 1)
		print('after: ' + c['searchQuery'] + '\n')
	elif c['type'] == 'Dashboard':
		for col in c['columns']:
			for m in col['monitors']:
				print('before: ' + m['searchQuery'] + '\n')
				m['searchQuery'] = string.replace(m['searchQuery'], from_expr, to_expr, 1)
				print('after: ' + m['searchQuery'] + '\n')
print(sumo.create_contents(string.strip(path, '/').split('/')[0], cs))

