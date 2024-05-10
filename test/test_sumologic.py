import os
import sys
import unittest
import json
from sumologic.sumologic import SumoLogic


class TestSDK(unittest.TestCase):

    '''
        These tests checks all the 4 api calls including the get api endpoint function
        These are numbered so that the create, update and delete are in order
    '''

    SUMOLOGIC_ACCESS_ID = None
    SUMOLOGIC_ACCESS_KEY = None

    @classmethod
    def setUpClass(cls):
        cls.SUMOLOGIC_ACCESS_ID = os.getenv("SUMOLOGIC_ACCESS_ID")
        cls.SUMOLOGIC_ACCESS_KEY = os.getenv("SUMOLOGIC_ACCESS_KEY")
        if not cls.SUMOLOGIC_ACCESS_ID and cls.SUMOLOGIC_ACCESS_KEY:
            print("Please set SUMOLOGIC_ACCESS_ID and SUMOLOGIC_ACCESS_KEY environment variables before running the test.")
            sys.exit(1)
        cls.sumologic_cli = SumoLogic(cls.SUMOLOGIC_ACCESS_ID, cls.SUMOLOGIC_ACCESS_KEY)

    @classmethod
    def tearDownClass(cls):
        cls.sumologic_cli.session.close()

    def assertNoRaise(self, callableObj, msg=None, *args, **kwargs):
        try:
            return callableObj(*args, **kwargs)
        except Exception as err:
            if not msg:
                msg = f"Test failed with error: {err}"
            else:
                msg = msg + f" error: {err}"
            self.fail(msg)

    def test_01_get_api_call(self):
        resp = self.assertNoRaise(self.sumologic_cli.collectors, limit=10, filter_type="Hosted", offset=0, msg="Get API call failed")
        self.assertTrue(isinstance(resp, list), "Get API call returned incorrect result")
        print(f"Fetched collector {resp}")

    def test_02_post_api_call(self):
        collector = {
            'collector': {
                'collectorType': "Hosted",
                'name': "dummy_collector_sumologic_python_sdk_testing",
                'description': '',
                'category': 'test_category'
            }
        }
        resp = self.assertNoRaise(self.sumologic_cli.create_collector, collector=collector, msg="Post API call failed")
        self.assertTrue(resp.ok, f"Post API Call returned incorrect response: {resp}")
        print(f"Created collector {resp.text}")
        TestSDK.collector_id = json.loads(resp.text)['collector']['id']

    def test_03_update_api_call(self):
        existing_collector, etag = self.assertNoRaise(self.sumologic_cli.collector, collector_id=TestSDK.collector_id, msg="Get API call failed")
        existing_collector['collector']['category'] = "new_test_category"
        resp = self.assertNoRaise(self.sumologic_cli.update_collector, collector=existing_collector, etag=etag, msg="Update API call failed")
        self.assertTrue(resp.ok, f"Update API Call returned incorrect response: {resp}")
        print(f"Updated collector {resp.text}")

    def test_04_delete_api_call(self):
        resp = self.assertNoRaise(self.sumologic_cli.delete_collector, collector={"collector": {"id": TestSDK.collector_id}}, msg="Delete API call failed")
        self.assertTrue(resp.ok, f"Delete API Call returned incorrect response: {resp}")
        print(f"Deleted collector {resp.text}")

