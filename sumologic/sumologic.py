from copy import copy
import json
import logging

import requests

class SumoLogic:
    session = requests.Session()

    def __init__(self, accessId, accessKey, endpoint='https://api.sumologic.com/api/v1'):
        self.endpoint = endpoint
        self.session.auth = (accessId, accessKey)
        self.session.headers = {'content-type': 'application/json', 'accept': 'application/json'}

    def delete(self, method, params=None):
        r = self.session.delete(self.endpoint + method, params=params)
        if r.status_code != 200:
            logging.debug("Response text: %s" % r.text)
        return r

    def get(self, method, params=None):
        r = self.session.get(self.endpoint + method, params=params)
        if r.status_code != 200:
            logging.debug("Response text: %s" % r.text)
        return r

    def post(self, method, params, headers=None):
        r = self.session.post(self.endpoint + method, data=json.dumps(params), headers=headers)
        if r.status_code != 200:
            logging.debug("Response text: %s" % r.text)
        return r

    def put(self, method, params, headers=None):
        r = self.session.put(self.endpoint + method, data=json.dumps(params), headers=headers)
        if r.status_code != 200:
            logging.debug("Response text: %s" % r.text)
        return r

    def search(self, query, fromTime=None, toTime=None, timeZone='UTC'):
        params = {'q': query, 'from': fromTime, 'to': toTime, 'tz': timeZone}
        r = self.get('/logs/search', params)
        try:
            return json.loads(r.text)
        except ValueError:
            raise ValueError(r.text)

    def search_job(self, query, fromTime=None, toTime=None, timeZone='UTC'):
        params = {'query': query, 'from': fromTime, 'to': toTime, 'timeZone': timeZone}
        r = self.post('/search/jobs', params)
        try:
            return json.loads(r.text)
        except ValueError:
            raise ValueError(r.text)

    def search_job_status(self, search_job):
        r = self.get('/search/jobs/' + str(search_job['id']))
        try:
            return json.loads(r.text)
        except ValueError:
            raise ValueError(r.text)

    def search_job_messages(self, search_job, limit=None, offset=0):
        params = {'limit': limit, 'offset': offset}
        r = self.get('/search/jobs/' + str(search_job['id']) + '/messages', params)
        try:
            return json.loads(r.text)
        except ValueError:
            raise ValueError(r.text)

    def search_job_records(self, search_job, limit=None, offset=0):
        params = {'limit': limit, 'offset': offset}
        r = self.get('/search/jobs/' + str(search_job['id']) + '/records', params)
        try:
            return json.loads(r.text)
        except ValueError:
            raise ValueError(r.text)

    def collectors(self, limit=None, offset=None):
        params = {'limit': limit, 'offset': offset}
        r = self.get('/collectors', params)
        try:
            return json.loads(r.text)['collectors']
        except ValueError:
            raise ValueError(r.text)

    def collector(self, collector_id):
        r = self.get('/collectors/' + str(collector_id))
        try:
            return json.loads(r.text), r.headers['etag']
        except ValueError:
            raise ValueError(r.text)

    def update_collector(self, collector, etag):
        headers = {'If-Match': etag}
        return self.put('/collectors/' + str(collector['collector']['id']), collector, headers)

    def delete_collector(self, collector):
        return self.delete('/collectors/' + str(collector['collector']['id']))

    def sources(self, collector_id, limit=None, offset=None):
        params = {'limit': limit, 'offset': offset}
        r = self.get('/collectors/' + str(collector_id) + '/sources', params)
        try:
            return json.loads(r.text)['sources']
        except ValueError:
            raise ValueError(r.text)

    def source(self, collector_id, source_id):
        r = self.get('/collectors/' + str(collector_id) + '/sources/' + str(source_id))
        try:
            return json.loads(r.text), r.headers['etag']
        except ValueError:
            raise ValueError(r.text)

    def update_source(self, collector_id, source, etag):
        headers = {'If-Match': etag}
        r = self.put('/collectors/' + str(collector_id) + '/sources/' + str(source['source']['id']), source, headers)
        return r

    def delete_source(self, collector_id, source):
        return self.delete('/collectors/' + str(collector_id) + '/sources/' + str(source['source']['id']))

    def create_content(self, path, data):
        r = self.post('/content/' + path, data)
        return r.text

    def get_content(self, path):
        r = self.get('/content/' + path)
        try:
            return json.loads(r.text)
        except ValueError:
            raise ValueError(r.text)

    def delete_content(self):
        r = self.delete('/content/' + path)
        try:
            return json.loads(r.text)
        except ValueError:
            raise ValueError(r.text)

    def dashboards(self, monitors=False):
        params = {'monitors': monitors}
        r = self.get('/dashboards', params)
        try:
            return json.loads(r.text)['dashboards']
        except ValueError:
            raise ValueError(r.text)

    def dashboard(self, dashboard_id):
        r = self.get('/dashboards/' + str(dashboard_id))
        try:
            return json.loads(r.text)['dashboard']
        except ValueError:
            raise ValueError(r.text)

    def dashboard_data(self, dashboard_id):
        r = self.get('/dashboards/' + str(dashboard_id) + '/data')
        try:
            return json.loads(r.text)['dashboardMonitorDatas']
        except ValueError:
            raise ValueError(r.text)
