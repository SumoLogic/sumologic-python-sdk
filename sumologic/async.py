from copy import copy
import json
import logging
import asyncio
import aiohttp
import threading


class SumoLogic(object):
    def __init__(self, accessId, accessKey, endpoint=None, cookieFile='cookies.txt'):
        self.session = aiohttp.ClientSession(
            auth=aiohttp.BasicAuth(accessId, accessKey), headers={
                'content-type': 'application/json',
                'accept': 'application/json'
            })

        self._lock = asyncio.Lock()
        self._endpoint = None

    async def __aenter__(self):
        await self.session.__aenter__()
        return self

    async def __aexit__(self, *args):
        await self.session.__aexit__(*args)

    async def _set_endpoint(self):
        if self._endpoint is None:
            with await self._lock:
                if self._endpoint is None:
                    async with self.session.get('https://api.sumologic.com/api/v1/collectors') as resp:  # Dummy call to get endpoint
                        self._endpoint = str(resp.url).replace('/collectors', '')  # dirty hack to sanitise URI and retain domain

    async def delete(self, method, params=None):
        await self._set_endpoint()
        r = await self.session.delete(self._endpoint + method, params=params)
        r.raise_for_status()
        return r

    async def get(self, method, params=None):
        await self._set_endpoint()
        r = await self.session.get(self._endpoint + method, params=params)
        if 400 <= r.status < 600:
            r.reason = await r.text()
        r.raise_for_status()
        return r

    async def post(self, method, params, headers=None):
        await self._set_endpoint()
        r = await self.session.post(self._endpoint + method, data=json.dumps(params), headers=headers)
        r.raise_for_status()
        return r

    async def put(self, method, params, headers=None):
        await self._set_endpoint()
        r = await self.session.put(self._endpoint + method, data=json.dumps(params), headers=headers)
        r.raise_for_status()
        return r

    async def search(self, query, fromTime=None, toTime=None, timeZone='UTC'):
        params = {'q': query, 'from': fromTime, 'to': toTime, 'tz': timeZone}
        r = await self.get('/logs/search', params)
        async with r:
            return json.loads(await r.text())

    async def search_job(self, query, fromTime=None, toTime=None, timeZone='UTC'):
        params = {'query': query, 'from': fromTime, 'to': toTime, 'timeZone': timeZone}
        r = await self.post('/search/jobs', params)
        async with r:
            return json.loads(await r.text())

    async def search_job_status(self, search_job):
        r = await self.get('/search/jobs/' + str(search_job['id']))
        async with r:
            return json.loads(await r.text())

    async def search_job_messages(self, search_job, limit=None, offset=0):
        params = {'limit': limit, 'offset': offset}
        r = await self.get('/search/jobs/' + str(search_job['id']) + '/messages', params)
        async with r:
            return json.loads(await r.text())

    async def search_job_records(self, search_job, limit=None, offset=0):
        params = {'limit': limit, 'offset': offset}
        r = await self.get('/search/jobs/' + str(search_job['id']) + '/records', params)
        async with r:
            return json.loads(await r.text())

    async def delete_search_job(self, search_job):
        return await self.delete('/search/jobs/' + str(search_job['id']))

    async def collectors(self, limit=None, offset=None):
        params = {'limit': limit, 'offset': offset}
        r = await self.get('/collectors', params)
        async with r:
            return json.loads(await r.text())['collectors']

    async def collector(self, collector_id):
        async with r:
            r = await self.get('/collectors/' + str(collector_id))
            return json.loads(await r.text()), r.headers['etag']

    async def update_collector(self, collector, etag):
        headers = {'If-Match': etag}
        return await self.put('/collectors/' + str(collector['collector']['id']), collector, headers)

    async def delete_collector(self, collector):
        return await self.delete('/collectors/' + str(collector['id']))

    async def sources(self, collector_id, limit=None, offset=None):
        params = {'limit': limit, 'offset': offset}
        async with r:
            r = await self.get('/collectors/' + str(collector_id) + '/sources', params)
            return json.loads(await r.text())['sources']

    async def source(self, collector_id, source_id):
        async with r:
            r = await self.get('/collectors/' + str(collector_id) + '/sources/' + str(source_id))
            return json.loads(await r.text()), r.headers['etag']

    async def create_source(self, collector_id, source):
        return await self.post('/collectors/' + str(collector_id) + '/sources', source)

    async def update_source(self, collector_id, source, etag):
        headers = {'If-Match': etag}
        return await self.put('/collectors/' + str(collector_id) + '/sources/' + str(source['source']['id']), source, headers)

    async def delete_source(self, collector_id, source):
        return await self.delete('/collectors/' + str(collector_id) + '/sources/' + str(source['source']['id']))

    async def create_content(self, path, data):
        r = await self.post('/content/' + path, data)
        async with r:
            return await r.text()

    async def get_content(self, path):
        r = await self.get('/content/' + path)
        async with r:
            return json.loads(await r.text())

    async def delete_content(self):
        r = await self.delete('/content/' + path)
        async with r:
            return json.loads(await r.text())

    async def dashboards(self, monitors=False):
        params = {'monitors': monitors}
        r = await self.get('/dashboards', params)
        async with r:
            return json.loads(await r.text())['dashboards']

    async def dashboard(self, dashboard_id):
        r = await self.get('/dashboard' + str(dashboard_id))
        async with r:
            return json.loads(await r.text())['dashboard']

    async def dashboard_data(self, dashboard_id):
        r = await self.get('/dashboards/' + str(dashboard_id) + '/data')
        async with r:
            return json.loads(await r.text())['dashboardMonitorDatas']

    async def search_metrics(self, query, fromTime=None, toTime=None, requestedDataPoints=600, maxDataPoints=800):
        '''Perform a single Sumo metrics query'''

        def millisectimestamp(ts):
            '''Convert UNIX timestamp to milliseconds'''
            if ts > 10**12:
                ts = ts / (10**(len(str(ts)) - 13))
            else:
                ts = ts * 10**(12 - len(str(ts)))
            return int(ts)

        params = {
            'query': [{
                "query": query,
                "rowId": "A"
            }],
            'startTime': millisectimestamp(fromTime),
            'endTime': millisectimestamp(toTime),
            'requestedDataPoints': requestedDataPoints,
            'maxDataPoints': maxDataPoints
        }
        r = await self.post('/metrics/results', params)
        async with r:
            return json.loads(await r.text())
