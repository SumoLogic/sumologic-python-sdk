from copy import copy
import json
import requests

class SumoLogic:

	endpoint = 'https://api.sumologic.com/api/v1'
	session = requests.Session()

	def __init__(self, accessId, accessKey):
		self.session.auth = (accessId, accessKey)
		self.session.headers = {'content-type': 'application/json', 'accept': 'application/json'}

	def get(self, method, params=None):
		return self.session.get(self.endpoint + method, params=params)

	def post(self, method, params, headers=None):
		return self.session.post(self.endpoint + method, data=json.dumps(params), headers=headers)

	def put(self, method, params, headers=None):
		return self.session.put(self.endpoint + method, data=json.dumps(params), headers=headers)

	def search(self):
		endpoint = self.endpoint + '/logs/search'

	def search_job(self, query, fromTime, toTime, timeZone=None):
		params = {'query': query, 'from': fromTime, 'to': toTime, 'timeZone': timeZone}
		print params
		r = self.post('/search/jobs', params)
		return json.loads(r.text)

	def search_job_status(self, search_job):
		r = self.get('/search/jobs/' + str(search_job['id']))
		return json.loads(r.text)

	def collectors(self, limit=None, offset=None):
		params = {'limit': limit, 'offset': offset}
		r = self.get('/collectors', params)
		return json.loads(r.text)['collectors']

	def collector(self, collector_id):
		r = self.get('/collectors/' + str(collector_id))
		return json.loads(r.text), r.headers['etag']

	def update_collector(self, collector, etag):
		headers = {'If-Match': etag}
		return self.put('/collectors/' + str(collector['collector']['id']), collector, headers)

	def sources(self, collector_id, limit=None, offset=None):
		params = {'limit': limit, 'offset': offset}
		r = self.get('/collectors/' + str(collector_id) + '/sources', params)
		return json.loads(r.text)['sources']

	def source(self, collector_id, source_id):
		r = self.get('/collectors/' + str(collector_id) + '/sources/' + str(source_id))
		return json.loads(r.text), r.headers['etag']

	def update_source(self, collector_id, source, etag):
		headers = {'If-Match': etag}
		return self.put('/collectors/' + str(collector_id) + '/sources/' + str(source['source']['id']), source, headers)

	def dashboards(self, monitors=False):
		params = {'monitors': monitors}
		r = self.get('/dashboards', params)
