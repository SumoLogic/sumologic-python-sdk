import json
import requests
import urllib
import time
import os
import sys
import warnings
from logzero import logger
import logzero
try:
    import cookielib
except ImportError:
    import http.cookiejar as cookielib


# API RATE Limit constants
MAX_TRIES = 10
NUMBER_OF_CALLS = 4
# per
PERIOD = 1  # in seconds


def backoff(func):
    def limited(*args, **kwargs):
        delay = PERIOD / NUMBER_OF_CALLS
        tries = 0
        lastException = None
        while tries < MAX_TRIES:
            tries += 1
            try:
                return func(*args, **kwargs)
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429: # rate limited
                    logger.debug("Rate limited, sleeping for {0}s".format(delay))
                    time.sleep(delay)
                    delay = delay * 2
                    lastException = e
                    continue
                else:
                    raise
        logger.debug("Rate limited function still failed after {0} retries.".format(MAX_TRIES))
        raise lastException

    return limited


class SumoLogic(object):
    def __init__(self, accessId, accessKey, endpoint=None, log_level='info', log_file=None, caBundle=None, cookieFile='cookies.txt'):
        self.session = requests.Session()
        self.log_level = log_level
        self.set_log_level(self.log_level)
        if log_file:
            logzero.logfile(str(log_file))
        self.session.auth = (accessId, accessKey)
        self.session.headers = {'content-type': 'application/json', 'accept': 'application/json'}
        if caBundle is not None:
            self.session.verify = caBundle
        cj = cookielib.FileCookieJar(cookieFile)
        self.session.cookies = cj
        if endpoint is None:
            self.endpoint = self._get_endpoint()
        else:
            self.endpoint = endpoint
        if self.endpoint[-4:] == "/v1":
            self.endpoint = self.endpoint[:-4]
            warnings.warn('Endpoint should no longer end in "/v1/", it has been removed from your endpoint string.',
                          DeprecationWarning)
        if endpoint[-1:] == "/":
            self.endpoint = self.endpoint[:-1]
            warnings.warn(
                "Endpoint should not end with a slash character, it has been removed from your endpoint string.")

    def set_log_level(self, log_level):
        if log_level == 'info':
            self.log_level = log_level
            logzero.loglevel(level=20)
            return True
        elif log_level == 'debug':
            self.log_level = log_level
            logzero.loglevel(level=10)
            logger.debug("[Sumologic SDK] Setting logging level to 'debug'")
            return True
        else:
            raise Exception("Bad Logging Level")
            logger.info("[Sumologic SDK] Attempt to set undefined logging level.")
            return False

    def get_log_level(self):
        return self.log_level

    def _get_endpoint(self):
        """
        SumoLogic REST API endpoint changes based on the geo location of the client.
        For example, If the client geolocation is Australia then the REST end point is
        https://api.au.sumologic.com/api/v1

        When the default REST endpoint (https://api.sumologic.com/api/v1) is used the server
        responds with a 401 and causes the SumoLogic class instantiation to fail and this very
        unhelpful message is shown 'Full authentication is required to access this resource'

        This method makes a request to the default REST endpoint and resolves the 401 to learn
        the right endpoint
        """

        self.endpoint = 'https://api.sumologic.com/api'
        self.response = self.session.get('https://api.sumologic.com/api/v1/collectors')  # Dummy call to get endpoint
        endpoint = self.response.url.replace('/v1/collectors', '')  # dirty hack to sanitise URI and retain domain
        logger.info("SDK Endpoint {}".format(str(endpoint)))
        return endpoint

    def get_versioned_endpoint(self, version):
        return self.endpoint+'/%s' % version

    @backoff
    def delete(self, method, params=None, headers=None, data=None):
        logger.debug("DELETE: " + self.endpoint + method)
        logger.debug("Headers:")
        logger.debug(headers)
        logger.debug("Params:")
        logger.debug(params)
        logger.debug("Body:")
        logger.debug(data)
        r = self.session.delete(self.endpoint + method, params=params, headers=headers, data=data)
        logger.debug("Response:")
        logger.debug(r)
        logger.debug("Response Body:")
        logger.debug(r.text)
        if r.status_code != 200:
            r.reason = r.text
        r.raise_for_status()
        return r

    @backoff
    def get(self, method, params=None, headers=None):
        logger.debug("GET: " + self.endpoint + method)
        logger.debug("Headers:")
        logger.debug(headers)
        logger.debug("Params:")
        logger.debug(params)
        r = self.session.get(self.endpoint + method, params=params, headers=headers)
        logger.debug("Response:")
        logger.debug(r)
        logger.debug("Response Body:")
        logger.debug(r.text)
        if r.status_code != 200:
            r.reason = r.text
        r.raise_for_status()
        return r

    @backoff
    def post(self, method, data, headers=None, params=None):
        logger.debug("POST: " + self.endpoint + method)
        logger.debug("Headers:")
        logger.debug(headers)
        logger.debug("Params:")
        logger.debug(params)
        logger.debug("Body:")
        logger.debug(data)
        r = self.session.post(self.endpoint + method, data=json.dumps(data), headers=headers, params=params)
        logger.debug("Response:")
        logger.debug(r)
        logger.debug("Response Body:")
        logger.debug(r.text)
        if r.status_code != 200:
            r.reason = r.text
        r.raise_for_status()
        return r

    @backoff
    def put(self, method, data, headers=None, params=None):
        logger.debug("PUT: " + self.endpoint + method)
        logger.debug("Headers:")
        logger.debug(headers)
        logger.debug("Params:")
        logger.debug(params)
        logger.debug("Body:")
        logger.debug(data)
        r = self.session.put(self.endpoint + method, data=json.dumps(data), headers=headers, params=params)
        logger.debug("Response:")
        logger.debug(r)
        logger.debug("Response Body:")
        logger.debug(r.text)
        if r.status_code != 200:
            r.reason = r.text
        r.raise_for_status()
        return r

    def post_file(self, method, params, headers=None):
        """
        Handle file uploads via a separate post request to avoid having to clear
        the content-type header in the session.  

        Requests (or urllib3) does not set a boundary in the header if the content-type
        is already set to multipart/form-data.  Urllib will create a boundary but it 
        won't be specified in the content-type header, producing invalid POST request.

        Multi-threaded applications using self.session may experience issues if we 
        try to clear the content-type from the session.  Thus we don't re-use the 
        session for the upload, rather we create a new one off session.
        """

        post_params = {'merge': params['merge']}
        file_data = open(params['full_file_path'], 'rb').read()  
        files = {'file': (params['file_name'], file_data)} 
        r = requests.post(self.endpoint + method, files=files, params=post_params,
                auth=(self.session.auth[0], self.session.auth[1]), headers=headers)
        if 400 <= r.status_code < 600:
            r.reason = r.text
        r.raise_for_status()
        return r

    # Search API

    def search_job(self, query, fromTime=None, toTime=None, timeZone='UTC', byReceiptTime=False):
        data = {'query': str(query), 'from': str(fromTime), 'to': str(toTime), 'timeZone': str(timeZone), 'byReceiptTime': str(byReceiptTime)}
        r = self.post('/v1/search/jobs', data)
        return r.json()

    def search_job_status(self, search_job):
        r = self.get('/v1/search/jobs/' + str(search_job['id']))
        return r.json()

    def search_job_records_sync(self, query, fromTime=None, toTime=None, timeZone=None, byReceiptTime=None):
        searchjob = self.search_job(query, fromTime=fromTime, toTime=toTime, timeZone=timeZone, byReceiptTime=byReceiptTime)
        status = self.search_job_status(searchjob)
        numrecords = status['recordCount']
        while status['state'] != 'DONE GATHERING RESULTS':
            if status['state'] == 'CANCELLED':
                break
            status = self.search_job_status(searchjob)
            numrecords = status['recordCount']
        if status['state'] == 'DONE GATHERING RESULTS':
            jobrecords=[]
            iterations = numrecords // 10000 + 1

            for iteration in range(1, iterations + 1):
                records = self.search_job_records(searchjob, limit=10000,
                                                  offset=((iteration - 1) * 10000))
                for record in records['records']:
                    jobrecords.append(record)
            return jobrecords   #returns a list
        else:
            return status

    def search_job_messages_sync(self, query, fromTime=None, toTime=None, timeZone=None, byReceiptTime=None):
        searchjob = self.search_job(query, fromTime=fromTime, toTime=toTime, timeZone=timeZone, byReceiptTime=byReceiptTime)
        status = self.search_job_status(searchjob)
        nummessages = status['messageCount']
        while status['state'] != 'DONE GATHERING RESULTS':
            if status['state'] == 'CANCELLED':
                break
            status = self.search_job_status(searchjob)
            nummessages = status['messageCount']
        if status['state'] == 'DONE GATHERING RESULTS':
            jobmessages=[]
            iterations = nummessages // 10000 + 1

            for iteration in range(1, iterations + 1):
                messages = self.search_job_messages(searchjob, limit=10000,
                                                  offset=((iteration - 1) * 10000))
                for message in messages['messages']:
                    jobmessages.append(message)
            return jobmessages   #returns a list
        else:
            return status

    def search_job_messages(self, search_job, limit=None, offset=0):
        params = {'limit': limit, 'offset': offset}
        r = self.get('/v1/search/jobs/' + str(search_job['id']) + '/messages', params)
        return r.json()

    def search_job_records(self, search_job, limit=None, offset=0):
        params = {'limit': limit, 'offset': offset}
        r = self.get('/v1/search/jobs/' + str(search_job['id']) + '/records', params)
        return r.json()

    def delete_search_job(self, search_job):
        r = self.delete('/v1/search/jobs/' + str(search_job['id']))
        return r.json()

    # Collectors API

    # included for backwards compatibility with older community SDK
    def collectors(self, limit=None, offset=None, filter_type=None):
        return self.get_collectors(limit=limit, offset=offset)

    def get_collectors(self, limit=1000, offset=None, filter_type=None):
        params = {'limit': limit, 'offset': offset}
        if filter_type:
            params['filter'] = filter_type
        r = self.get('/v1/collectors', params)
        return r.json()['collectors']

    def get_collectors_sync(self, limit=1000, filter_type=None):
        offset = 0
        results = []
        r = self.get_collectors(limit=limit, offset=offset, filter_type=filter_type)
        offset = offset + limit
        results = results + r
        while not (len(r) < limit):
            r = self.get_collectors(limit=limit, offset=offset, filter_type=filter_type)
            offset = offset + limit
            results = results + r
        return results

    def get_collector_by_id(self, collector_id):
        r = self.get('/v1/collectors/' + str(collector_id))
        return r.json()['collector'], r.headers['etag']

    # The following calls the Sumo "get collector by name" method which does not support special characters like ; / % \
    def get_collector_by_name(self, name):
        encoded_name = urllib.parse.quote(str(name))
        r = self.get('/v1/collectors/name/' + encoded_name)
        return r.json()['collector'], r.headers['etag']

    # this version makes multiple calls but should work with special characters in the collector name
    def get_collector_by_name_alternate(self, name):
        sumocollectors = self.get_collectors_sync()
        for sumocollector in sumocollectors:
            if sumocollector['name'] == str(name):
                collector, _ = self.get_collector_by_id(sumocollector['id'])
                return collector

    # for backward compatibility with old community API
    def collector(self, collector_id):
        r = self.get('/collectors/' + str(collector_id))
        return r.json(), r.headers['etag']

    def create_collector(self, collector, headers=None):
        r = self.post('/v1/collectors', collector, headers)
        return r.json()

    def update_collector(self, collector, etag):
        headers = {'If-Match': etag}
        r = self.put('/v1/collectors/' + str(collector['collector']['id']), collector, headers)
        return r.json()

    def delete_collector(self, collector_id):
        r = self.delete('/v1/collectors/' + str(collector_id))
        return r.json()

    def get_sources(self, collector_id, limit=None, offset=None):
        params = {'limit': limit, 'offset': offset}
        r = self.get('/v1/collectors/' + str(collector_id) + '/sources', params)
        return json.loads(r.text)['sources']

    def get_sources_sync(self, collector_id, limit=1000):
        offset = 0
        results = []
        r = self.get_sources(collector_id, limit=limit, offset=offset)
        offset = offset + limit
        results = results + r
        while not (len(r) < limit):
            r = self.get_sources(collector_id, limit=limit, offset=offset)
            offset = offset + limit
            results = results + r
        return results

    # for backward compatibility with old community API
    def sources(self, collector_id, limit=None, offset=None):
        return self.get_sources(collector_id, limit=limit, offset=offset)

    def get_source(self, collector_id, source_id):
        r = self.get('/v1/collectors/' + str(collector_id) + '/sources/' + str(source_id))
        return r.json()

    def get_source_with_etag(self, collector_id, source_id):
        r = self.get('/v1/collectors/' + str(collector_id) + '/sources/' + str(source_id))
        return r.headers.get('etag'), r.json()

    # for backward compatibility with old community API
    def source(self, collector_id, source_id):
        return self.get_source(collector_id, source_id)

    def create_source(self, collector_id, source):
        r = self.post('/v1/collectors/' + str(collector_id) + '/sources', source)
        return r.json()

    def update_source(self, collector_id, source, etag):
        headers = {'If-Match': etag}
        r = self.put('/v1/collectors/' + str(collector_id) + '/sources/' + str(source['source']['id']), source, headers)
        return r.json()

    def delete_source(self, collector_id, source_id):
        r = self.delete('/v1/collectors/' + str(collector_id) + '/sources/' + str(source_id))
        return r

    ############################################

    ###############################################


    # Unverified API calls. These are disabled as they are not documented by Sumo Logic or have been replaced
    # def dashboards(self, monitors=False):
    #     params = {'monitors': monitors}
    #     r = self.get('/v1/dashboards', params)
    #     return json.loads(r.text)['dashboards']
    #
    # def dashboard(self, dashboard_id):
    #     r = self.get('/v1/dashboards/' + str(dashboard_id))
    #     return json.loads(r.text)['dashboard']
    #
    # def dashboard_data(self, dashboard_id):
    #     r = self.get('/v1/dashboards/' + str(dashboard_id) + '/data')
    #     return json.loads(r.text)['dashboardMonitorDatas']

    # def search_metrics(self, query, fromTime=None, toTime=None, requestedDataPoints=600, maxDataPoints=800):
    #     '''Perform a single Sumo metrics query'''
    #     def millisectimestamp(ts):
    #         '''Convert UNIX timestamp to milliseconds'''
    #         if ts > 10**12:
    #             ts = ts/(10**(len(str(ts))-13))
    #         else:
    #             ts = ts*10**(12-len(str(ts)))
    #         return int(ts)
    #
    #     params = {'query': [{"query": query, "rowId": "A"}],
    #               'startTime': millisectimestamp(fromTime),
    #               'endTime': millisectimestamp(toTime),
    #               'requestedDataPoints': requestedDataPoints,
    #               'maxDataPoints': maxDataPoints}
    #     r = self.post('/v1/metrics/results', params)
    #     return r.json()

    # def create_content(self, path, data):
    #     r = self.post('/content/' + path, data)
    #     return r.text

    def get_available_builds(self):
        r = self.get('/v1/collectors/upgrades/targets')
        return r.json()['targets']

    # def sync_folder(self, folder_id, content):
    #     return self.post('/content/folders/%s/synchronize' % folder_id, params=content, version='v2')
    #
    # def check_sync_folder(self, folder_id, job_id):
    #     return self.get('/content/folders/%s/synchronize/%s/status' % (folder_id, job_id), version='v2')

    # Permissions API

    def get_permissions(self, id, explicit_only=False, adminmode=False):
        headers = {'isAdminMode': str(adminmode).lower()}
        params = {'explicitOnly': bool(explicit_only)}
        r = self.get('/v2/content/' + str(id) + '/permissions', headers=headers, params=params)
        return r.json()

    def add_permissions(self, id, body, adminmode=False):
        headers = {'isAdminMode': str(adminmode).lower()}
        r = self.put('/v2/content/' + str(id) + '/permissions/add', body, headers=headers)
        return r.json()

    def remove_permissions(self, id, body, adminmode=False):
        headers = {'isAdminMode': str(adminmode).lower()}
        r = self.put('/v2/content/' + str(id) + '/permissions/remove', body, headers=headers)
        return r.json()

        # Folder API

    def create_folder(self, folder_name, parent_id, adminmode=False):
        headers = {'isAdminMode': str(adminmode).lower()}
        data = {'name': str(folder_name), 'parentId': str(parent_id)}
        r = self.post('/v2/content/folders', data, headers=headers)
        return r.json()

    def get_folder(self, folder_id, adminmode=False):
        headers = {'isAdminMode': str(adminmode).lower()}
        r = self.get('/v2/content/folders/' + str(folder_id), headers=headers)
        return r.json()

    def update_folder(self, id, name, description='', adminmode=False):
        headers = {'isAdminMode': str(adminmode).lower()}
        data = {'name': str(name), 'description': str(description)}
        r = self.put('/v2/content/folders/' + str(id), data, headers=headers)
        return r.json()

    def get_personal_folder(self):
        r = self.get('/v2/content/folders/personal')
        return r.json()

    def get_global_folder_job_status(self, job_id):
        r = self.get('/v2/content/folders/global/' + str(job_id) + '/status')
        return r.json()

    def get_global_folder(self, adminmode=False):
        headers = {'isAdminMode': str(adminmode).lower()}
        r = self.get('/v2/content/folders/global', headers=headers)
        return r.json()

    def get_global_folder_job_result(self, job_id):
        r = self.get('/v2/content/folders/global/' + str(job_id) + '/result')
        return r.json()

    def get_global_folder_sync(self, adminmode=False):
        r = self.get_global_folder(adminmode=adminmode)
        job_id = str(r['id'])
        status = self.get_global_folder_job_status(job_id)
        while status['status'] == 'InProgress':
            status = self.get_global_folder_job_status(job_id)
        if status['status'] == 'Success':
            r = self.get_global_folder_job_result(job_id)
            return r
        else:
            return status

    def get_admin_folder_job_status(self, job_id):

        r = self.get('/v2/content/folders/adminRecommended/' + str(job_id) + '/status')
        return r.json()

    def get_admin_folder(self, adminmode=False):
        headers = {'isAdminMode': str(adminmode).lower()}
        r = self.get('/v2/content/folders/adminRecommended', headers=headers)
        return r.json()

    def get_admin_folder_job_result(self, job_id):
        r = self.get('/v2/content/folders/adminRecommended/' + str(job_id) + '/result')
        return r.json()

    def get_admin_folder_sync(self, adminmode=False):
        r = self.get_admin_folder(adminmode=adminmode)
        job_id = str(r['id'])
        status = self.get_admin_folder_job_status(job_id)
        while status['status'] == 'InProgress':
            status = self.get_admin_folder_job_status(job_id)
        if status['status'] == 'Success':
            r = self.get_admin_folder_job_result(job_id)
            return r
        else:
            return status

    # Application API

    def install_app(self, app_id, content):
        return self.post('/apps/%s/install' % (app_id), params=content)

    def check_app_install_status(self, job_id):
        return self.get('/apps/install/%s/status' % job_id)

        # Content API

        # for backward compatibility with old community API

    def get_content(self, path):
        return self.get_content_by_path(path)

    def get_content_by_path(self, item_path):
        # item_path should start with /Library and use the user's email address if referencing a user home dir
        # firstname + :space: + lastname will not work here, even though that's how it's displayed in the UI
        # YES: "/Library/Users/user@demo.com/someItemOrFolder" could be a valid path
        # NO: "/Library/Users/Demo User/someItemOrFolder" is not a valid path because user first/last names are not
        # unique identifiers
        params = {'path': str(item_path)}
        r = self.get('/v2/content/path', params=params)
        return r.json()

    def get_item_path(self, item_id):
        r = self.get('/v2/content/' + str(item_id) + '/path')
        return r.json()

    def delete_content_job(self, item_id, adminmode=False):
        headers = {'isAdminMode': str(adminmode).lower()}
        r = self.delete('/v2/content/' + str(item_id) + '/delete', headers=headers)
        return r.json()

        # for backward compatibility with old community API

    def check_delete_status(self, item_id, job_id, adminmode=False):
        return self.get_delete_content_job_status(item_id, job_id, adminmode=adminmode)

    def get_delete_content_job_status(self, item_id, job_id, adminmode=False):
        headers = {'isAdminMode': str(adminmode).lower()}
        r = self.get('/v2/content/' + str(item_id) + '/delete/' + str(job_id) + '/status', headers=headers)
        return r.json()

    def delete_content_job_sync(self, item_id, adminmode=False):
        r = self.delete_content_job(str(item_id), adminmode=adminmode)
        job_id = str(r['id'])
        status = self.get_delete_content_job_status(str(item_id), str(job_id), adminmode=adminmode)
        while status['status'] == 'InProgress':
            status = self.get_delete_content_job_status(str(item_id), str(job_id), adminmode=adminmode)
        return status

        # for backward compatibility with old community API

    def export_content(self, item_id, adminmode=False):
        return self.export_content_job(item_id, adminmode=adminmode)

    def export_content_job(self, item_id, adminmode=False):
        headers = {'isAdminMode': str(adminmode).lower()}
        data = {}
        r = self.post('/v2/content/' + str(item_id) + '/export', data, headers=headers)
        return r.json()

        # for backward compatibility with old community API

    def check_export_status(self, item_id, job_id, adminmode=False):
        return self.get_export_content_job_status(item_id, job_id, adminmode=adminmode)

    def get_export_content_job_status(self, item_id, job_id, adminmode=False):
        headers = {'isAdminMode': str(adminmode).lower()}
        r = self.get('/v2/content/' + str(item_id) + '/export/' + str(job_id) + '/status', headers=headers)
        return r.json()

        # for backward compatibility with old community API

    def get_export_content_result(self, item_id, job_id, adminmode=False):
        return self.get_export_content_job_result(item_id, job_id, adminmode=adminmode)

    def get_export_content_job_result(self, item_id, job_id, adminmode=False):
        headers = {'isAdminMode': str(adminmode).lower()}
        r = self.get('/v2/content/' + str(item_id) + '/export/' + str(job_id) + '/result', headers=headers)
        return r.json()

    def export_content_job_sync(self, item_id, adminmode=False):
        r = self.export_content_job(str(item_id), adminmode=adminmode)
        job_id = str(r['id'])
        status = self.get_export_content_job_status(item_id, job_id, adminmode=adminmode)
        while status['status'] == 'InProgress':
            status = self.get_export_content_job_status(item_id, job_id, adminmode=adminmode)
        if status['status'] == 'Success':
            r = self.get_export_content_job_result(item_id, job_id, adminmode=adminmode)
            return r
        else:
            return status

    def import_content_job(self, folder_id, content, adminmode=False, overwrite=False):
        headers = {'isAdminMode': str(adminmode).lower()}
        params = {'overwrite': str(overwrite).lower()}
        r = self.post('/v2/content/folders/' + str(folder_id) + '/import', content, headers=headers, params=params)
        return r.json()

    def get_import_content_job_status(self, folder_id, job_id, adminmode=False):
        headers = {'isAdminMode': str(adminmode).lower()}
        r = self.get('/v2/content/folders/' + str(folder_id) + '/import/' + str(job_id) + '/status', headers=headers)
        return r.json()

    def import_content_job_sync(self, folder_id, content, adminmode=False, overwrite=False):
        r = self.import_content_job(str(folder_id), content, adminmode=adminmode, overwrite=overwrite)
        job_id = str(r['id'])
        status = self.get_import_content_job_status(str(folder_id), str(job_id), adminmode=adminmode)
        while status['status'] == 'InProgress':
            time.sleep(1)
            status = self.get_import_content_job_status(str(folder_id), str(job_id), adminmode=adminmode)
        return status

    # Role API

    def get_roles(self, limit=1000, token='', sort_by='name', name=''):
        if name != '':
            params = {'limit': int(limit), 'token': str(token), 'sortBy': str(sort_by), 'name': str(name)}
        else:
            params = {'limit': int(limit), 'token': str(token), 'sortBy': str(sort_by)}
        r = self.get('/v1/roles', params=params)
        return r.json()

    def get_roles_sync(self, limit=1000, sort_by='name', name=''):
        token = ''
        results = []
        while True:
            r = self.get_roles(limit=limit, token=token, sort_by=sort_by, name=name)
            token = r['next']
            results = results + r['data']
            if token is None:
                break
        return results

    def create_role(self, body):
        r = self.post('/v1/roles', body)
        return r.json()

    def get_role(self, id):
        r = self.get('/v1/roles/' + str(id))
        return r.json()

    def update_role(self, id, body):
        r = self.put('/v1/roles/' + str(id), body)
        return r.json()

    def delete_role(self, id):
        r = self.delete('/v1/roles/' + str(id))
        return r

    def assign_role_to_user(self, role_id, user_id):
        r = self.put('/v1/roles/' + str(role_id) + '/users/' + str(user_id))
        return r.json()

    def remove_role_from_user(self, role_id, user_id):
        r = self.delete('/v1/roles/' + str(role_id) + '/users/' + str(user_id))
        return r.json()

    # User API

    def get_users(self, limit=1000, token=None, sort_by='lastName', email=''):
        if email != '':
            params = {'limit': int(limit), 'token': str(token), 'sortBy': str(sort_by), 'email': str(email)}
        else:
            params = {'limit': int(limit), 'token': str(token), 'sortBy': str(sort_by)}
        r = self.get('/v1/users', params=params)
        return r.json()

    def get_users_sync(self, limit=1000, sort_by='lastName', email=''):
        token = ''
        results = []
        while True:
            r = self.get_users(limit=limit, token=token, sort_by=sort_by, email=email)
            token = r['next']
            results = results + r['data']
            if token is None:
                break
        return results

    def get_user(self, user_id):
        r = self.get('/v1/users/' + str(user_id))
        return r.json() # ['data']

    # This call gets the user and then all roles the user belongs to. This is useful for exporting or copying a user
    # to a new org.
    def get_user_and_roles(self, user_id):
        user = self.get_user(str(user_id))
        user['roles'] = []
        for role_id in user['roleIds']:
            role = self.get_role(str(role_id))
            user['roles'].append(role)
        return user

    def create_user(self, first_name, last_name, email, roleIDs):
        data = {'firstName': str(first_name), 'lastName': str(last_name), 'email': str(email), 'roleIds': roleIDs}
        r = self.post('/v1/users', data)
        return r.json()

    def update_user(self, id, first_name, last_name, email, roleIDs):
        data = {'firstName': str(first_name), 'lastName': str(last_name), 'email': str(email), 'roleIds': roleIDs}
        r = self.put('/v1/users' + str(id), data)
        return r.json()

    def delete_user(self, id, transferTo=None):
        if transferTo:
            params = {'transferTo': str(transferTo)}
        else:
            params = None
        r = self.delete('/v1/users/' + str(id), params=params)
        return r

    def change_user_email(self, id, email):
        data = {'email': str(email)}
        r = self.post('/v1/users' + str(id) + '/email/requestChange', data)
        return r.json()

    def reset_user_password(self, id):
        r = self.post('/v1/users' + str(id) + '/password/reset')
        return r.json()

    def unlock_user(self, id):
        r = self.post('/v1/users' + str(id) + '/unlock')
        return r.json()

    def disable_user_MFA(self, id, email, password):
        data = {'email': str(email), 'password': str(password)}
        r = self.put('/v1/users/' + str(id) + 'mfa/disable', data)
        return r.json()

    # Connections API

    def get_connections(self, limit=1000, token=''):
        params = {'limit': limit, 'token': token}
        r = self.get('/v1/connections', params=params)
        return r.json()

    def get_connections_sync(self, limit=1000):
        token = None
        results = []
        while True:
            r = self.get_connections(limit=limit, token=token)
            token = r['next']
            results = results + r['data']
            if token is None:
                break
        return results

    def create_connection(self, connection):
        r = self.post('/v1/connections', connection)
        return r.json()

    def test_connection(self, connection):
        r = self.post('/v1/connections/test', connection)
        return r.json()

    def get_connection(self, item_id, type):
        params = {'type': str(type)}
        r = self.get('/v1/connections/' + str(item_id), params=params)
        return r.json()

    def update_connection(self, item_id, connection):
        r = self.put('/v1/connections/' + str(item_id), connection)
        return r.json()

    def delete_connection(self, item_id, item_type):
        params = {'type': str(item_type)}
        r = self.delete('/v1/connections/' + str(item_id), params=params)
        return r

    # Field Extraction Rules API

    def get_fers(self, limit=1000, token=''):
        params = {'limit': limit, 'token': token}
        r = self.get('/v1/extractionRules', params=params)
        return r.json()

    def get_fers_sync(self, limit=1000):
        token = None
        results = []
        while True:
            r = self.get_fers(limit=limit, token=token)
            token = r['next']
            results = results + r['data']
            if token is None:
                break
        return results

    def create_fer(self, name, scope, parse_expression, enabled=False):
        data = {'name': name, 'scope': scope, 'parseExpression': parse_expression, 'enabled': str(enabled).lower()}
        r = self.post('/v1/extractionRules', data)
        return r.json()

    def get_fer(self, item_id):
        r = self.get('/v1/extractionRules/' + str(item_id))
        return r.json()

    def update_fer(self, item_id, name, scope, parse_expression, enabled=False):
        data = {'name': name, 'scope': scope, 'parseExpression': parse_expression, 'enabled': str(enabled).lower()}
        r = self.put('/v1/extractionRules/' + str(item_id), data)
        return r.json()

    def delete_fer(self, item_id):
        r = self.delete('/v1/extractionRules/' + str(item_id))
        return r


    # Scheduled View API

    def get_scheduled_views(self, limit=1000, token=''):
        params = {'limit': limit, 'token': token}
        r = self.get('/v1/scheduledViews', params=params)
        return r.json()

    def get_scheduled_views_sync(self, limit=1000):
        token = None
        results = []
        while True:
            r = self.get_scheduled_views(limit=limit, token=token)
            token = r['next']
            results = results + r['data']
            if token is None:
                break
        return results

    #start time must be in RFC3339 format
    # https://tools.ietf.org/html/rfc3339
    # https://medium.com/easyread/understanding-about-rfc-3339-for-datetime-formatting-in-software-engineering-940aa5d5f68a
    def create_scheduled_view(self, index_name, query, start_time, retention_period=-1, data_forwarding_id=None):
        data = {'indexName': str(index_name), 'query': str(query), 'startTime': str(start_time), 'retentionPeriod': int(retention_period), "dataForwardingId": str(data_forwarding_id) }
        r = self.post('/v1/scheduledViews', data)
        return r.json()

    def get_scheduled_view(self, item_id):
        r = self.get('/v1/scheduledViews/' + str(item_id))
        return r.json()

    def update_scheduled_view(self, item_id, data_forwarding_id=None, retention_period=-1, reduce_retention_period_immediately=False):
        data = {'retentionPeriod': retention_period, "dataForwardingId": data_forwarding_id, "reduceRetentionPeriodImmediately" : str(reduce_retention_period_immediately).lower()}
        r = self.put('/v1/scheduledViews/' + str(item_id),data)
        return r.json()

    def disable_scheduled_view(self, item_id):
        r = self.delete('/v1/scheduledViews/' + str(item_id) + '/disable')
        return r


    # Partitions API

    def get_partitions(self, limit=1000, token=''):
        params = {'limit': limit, 'token': token}
        r = self.get('/v1/partitions', params=params)
        return r.json()

    def get_partitions_sync(self, limit=1000):
        token = None
        results = []
        while True:
            r = self.get_partitions(limit=limit, token=token)
            token = r['next']
            results = results + r['data']
            if token is None:
                break
        return results

    def create_partition(self, name, routing_expression, analytics_tier="enhanced", retention_period=-1, data_forwarding_id=None, is_compliant=False):
        data = {'name': str(name),
                'routingExpression': str(routing_expression),
                'analyticsTier': str(analytics_tier),
                'retentionPeriod': int(retention_period),
                'dataForwardingId': str(data_forwarding_id),
                'isCompliant': str(is_compliant).lower()}

        r = self.post('/v1/partitions', data)
        return r.json()

    def get_partition(self, item_id):
        r = self.get('/v1/partitions/' + str(item_id))
        return r.json()

    def update_partition(self, item_id,  data_forwarding_id=None, retention_period=-1, reduce_retention_period_immediately=False, is_compliant=False):
        data = {'retentionPeriod': retention_period,
                "dataForwardingId": data_forwarding_id,
                "reduceRetentionPeriodImmediately" : str(reduce_retention_period_immediately).lower(),
                "isCompliant": str(is_compliant).lower()}
        r = self.put('/v1/partitions/' + str(item_id),data)
        return r.json()

    def decommission_partition(self, item_id):
        data ={}
        r = self.post('/v1/partitions/' + str(item_id) + '/decommission', data)
        return r

    # Monitors API

    def get_usage_info(self):
        r = self.get('/v1/monitors/usageInfo')
        return r.json()

    def bulk_get_monitors(self, item_ids):
        item_ids_string = ''
        for item_id in item_ids:
            item_ids_string = item_ids_string + str(item_id) + ','
        item_ids_string = item_ids_string[:-1]
        params = {'ids': item_ids_string}
        r = self.get('/v1/monitors', params=params)
        return r.json()

    def create_monitor(self, parent_id, monitor):
        params = { 'parentId': str(parent_id)}
        r = self.post('/v1/monitors', monitor, params=params)
        return r.json()

    def create_monitor_folder(self, parent_id, name, description=''):
        data = {'name': str(name),
                'description': str(description),
                'type': 'MonitorsLibraryFolder'}
        r = self.create_monitor(parent_id, data)
        return r

    def bulk_delete_monitors(self, item_ids):
        item_ids_string = ''
        for item_id in item_ids:
            item_ids_string = item_ids_string + str(item_id) + ','
        item_ids_string = item_ids_string[:-1]
        params = {'ids': item_ids_string}
        r = self.delete('/v1/monitors', params=params)
        return r

    def get_monitor_folder_root(self):
        r = self.get('/v1/monitors/root')
        return r.json()

    def get_monitor_by_path(self, path):
        params = {'path': str(path)}
        r = self.get('/v1/monitors/path', params=params)
        return r.json()

    def search_monitors(self, query, limit=100, offset=0):
        params = {'query': str(query),
                  'limit': int(limit),
                  'offset': int(offset)}
        r = self.get('/v1/monitors/search', params=params)
        return r.json()

    def search_monitors_sync(self, query, limit=100):
        offset = 0
        results = []
        r = self.search_monitors(query, limit=limit, offset=offset)
        offset = offset + limit
        results = results + r
        while not (len(r) < limit):
            r = self.search_monitors(query, limit=limit, offset=offset)
            offset = offset + limit
            results = results + r
        return results

    def get_monitor(self, item_id):
        r = self.get('/v1/monitors/' + str(item_id))
        return r.json()

    def update_monitor(self, item_id, name, version, type, description=''):
        data = {'name': str(name),
                'description': str(description),
                'version': int(version),
                'type': str(type)}
        r = self.put('/v1/monitors/' + str(item_id), data)
        return r.json()

    def delete_monitor(self, item_id):
        r = self.delete('/v1/monitors/' + str(item_id))
        return r

    def get_monitor_path(self, item_id):
        r = self.get('/v1/monitors/' + str(item_id) + '/path')
        return r.json()

    def move_monitor(self, item_id, parent_id):
        params = { 'parentId': str(parent_id)}
        r = self.post('/v1/monitors/' + str(item_id) + '/move', params=params)
        return r.json()

    def copy_monitor(self, item_id, parent_id, name=None, description=''):
        data = {'parentId': str(parent_id),
                'description': str(description)}
        if name:
            data['name'] = str(name)
        r = self.post('/v1/monitors/' + str(item_id) + '/copy')
        return r.json()

    def export_monitor(self, item_id):
        r = self.get('/v1/monitors/' + str(item_id) + '/export')
        return r.json()

    def import_monitor(self, parent_id, monitor):
        r = self.post('/v1/monitors/' + str(parent_id) + '/import', monitor)
        return r.json()

    # SAML Config API

    def get_saml_configs(self):
        r = self.get('/v1/saml/identityProviders')
        return r.json()

    def get_saml_config_by_name(self, name):
        configs = self.get_saml_configs()
        for config in configs:
            if config['name'] == str(name):
                return config
        return False

    def get_saml_config_by_id(self, item_id):
        configs = self.get_saml_configs()
        for config in configs:
            if config['id'] == str(item_id):
                return config
        return False

    def create_saml_config(self, saml_config):
        r = self.post('/v1/saml/identityProviders', saml_config)
        return r.json()

    def update_saml_config(self, item_id, saml_config):
        r = self.put('/v1/saml/identityProviders/' + str(item_id), saml_config)
        return r.json()

    def delete_saml_config(self, item_id):
        r = self.delete('/v1/saml/identityProviders/' + str(item_id))
        return r

    def get_whitelisted_users(self):
        r = self.get('/v1/saml/whitelistedUsers')
        return r.json()

    def set_whitelisted_user(self, user_id):
        r = self.post('/v1/saml/whitelistedUsers' + str(user_id))
        return r.json()

    def remove_whitelisted_user(self, user_id):
        r = self.delete('/v1/saml/whitelistedUsers/' + str(user_id))
        return r.json()

    def enable_saml_lockdown(self):
        r = self.post('/v1/saml/lockdown/enable')
        return r.json()

    def disable_saml_lockdown(self):
        r = self.post('/v1/saml/lockdown/disable')
        return r.json()


    # Lookup table API
    def create_lookup_table(self, content):
        return self.post('/v1/lookupTables', params=content)
    
    def get_lookup_table(self, id):
        return self.get('/v1/lookupTables/%s' % id)
    
    def edit_lookup_table(self, id, content):
        return self.put('/v1/lookupTables/%s' % id, params=content)

    def delete_lookup_table(self, id):
        return self.delete('/v1/lookupTables/%s' % id)

    def upload_csv_lookup_table(self, id, file_path, file_name, merge='false'):
        params={'file_name': file_name,
                'full_file_path': os.path.join(file_path, file_name),
                'merge': merge
                }
        return self.post_file('/v1/lookupTables/%s/upload' % id, params)
    
    def check_lookup_status(self, id):
        return self.get('/v1/lookupTables/jobs/%s/status' % id)

    def empty_lookup_table(self, id):
        return self.post('/v1/lookupTables/%s/truncate'% id, params=None)
    
    def update_lookup_table(self, id, content):
        return self.put('/v1/lookupTables/%s/row' % id, params=content)
