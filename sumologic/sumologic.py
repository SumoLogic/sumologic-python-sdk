from copy import copy
import json
import logging

import requests

class SumoLogic(object):

    def __init__(self, accessId, accessKey, endpoint='https://api.sumologic.com/api/v1'):
        self.endpoint = endpoint
        self.session = requests.Session()
        self.session.auth = (accessId, accessKey)
        self.session.headers = {'content-type': 'application/json', 'accept': 'application/json'}

    def delete(self, method, params=None):
        r = self.session.delete(self.endpoint + method, params=params)
        r.raise_for_status()
        return r

    def get(self, method, params=None):
        r = self.session.get(self.endpoint + method, params=params)
        r.raise_for_status()
        return r

    def post(self, method, params, headers=None):
        r = self.session.post(self.endpoint + method, data=json.dumps(params), headers=headers)
        r.raise_for_status()
        return r

    def put(self, method, params, headers=None):
        r = self.session.put(self.endpoint + method, data=json.dumps(params), headers=headers)
        r.raise_for_status()
        return r

    def search(self, query, fromTime=None, toTime=None, timeZone='UTC'):
        params = {'q': query, 'from': fromTime, 'to': toTime, 'tz': timeZone}
        r = self.get('/logs/search', params)
        return json.loads(r.text)

    def search_job(self, query, fromTime=None, toTime=None, timeZone='UTC'):
        params = {'query': query, 'from': fromTime, 'to': toTime, 'timeZone': timeZone}
        r = self.post('/search/jobs', params)
        return json.loads(r.text)

    def search_job_status(self, search_job):
        r = self.get('/search/jobs/' + str(search_job['id']))
        return json.loads(r.text)

    def search_job_messages(self, search_job, limit=None, offset=0):
        params = {'limit': limit, 'offset': offset}
        r = self.get('/search/jobs/' + str(search_job['id']) + '/messages', params)
        return json.loads(r.text)

    def search_job_records(self, search_job, limit=None, offset=0):
        params = {'limit': limit, 'offset': offset}
        r = self.get('/search/jobs/' + str(search_job['id']) + '/records', params)
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

    def delete_collector(self, collector):
        return self.delete('/collectors/' + str(collector['collector']['id']))

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

    def delete_source(self, collector_id, source):
        return self.delete('/collectors/' + str(collector_id) + '/sources/' + str(source['source']['id']))

    def create_content(self, path, data):
        r = self.post('/content/' + path, data)
        return r.text

    def get_content(self, path):
        r = self.get('/content/' + path)
        return json.loads(r.text)

    def delete_content(self):
        r = self.delete('/content/' + path)
        return json.loads(r.text)

    def dashboards(self, monitors=False):
        params = {'monitors': monitors}
        r = self.get('/dashboards', params)
        return json.loads(r.text)['dashboards']

    def dashboard(self, dashboard_id):
        r = self.get('/dashboards/' + str(dashboard_id))
        return json.loads(r.text)['dashboard']

    def dashboard_data(self, dashboard_id):
        r = self.get('/dashboards/' + str(dashboard_id) + '/data')
        return json.loads(r.text)['dashboardMonitorDatas']
