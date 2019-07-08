from datetime import datetime, timedelta
from enum import Enum
from time import sleep
from abc import ABC, abstractmethod
from typing import *


def _sumoTime(date = None):
    date = date or datetime.now()
    return int(date.timestamp()*1000)

class State(Enum):
    DONE = 'DONE GATHERING RESULTS'
    GATHERING = 'GATHERING RESULTS'

states = { i.value for i in State }


class _ResultGenerator:

    MAX_PER_REQ = 1000
    MIN_PER_REQ = 10
    delay = 1

    def __init__(self, sumo, searchJob: dict):
        """
        :type sumo: sumologic.SumoLogic
        """
        self.client = sumo
        self.yielded = 0
        self.searchJob = searchJob

    @abstractmethod
    def getListOfRecords(self) -> list:
        pass

    @abstractmethod
    def getCountFromStatus(self, status: dict) -> int:
        pass

    def _yield_next_n(self, n: int, yieldUntil: int):
        while self.yielded < yieldUntil:
            records = self.getListOfRecords()
            numMessages = len(records)
            self.yielded += numMessages
            yield from (m['map'] for m in records)

    def _yield_from_status(self, status: dict):
        count = self.getCountFromStatus(status)
        state = State(status['state'])
        n_waiting = count - self.yielded

        if (state == State.DONE or (state == State.GATHERING and n_waiting > self.MIN_PER_REQ)):
            yield from self._yield_next_n(self.MAX_PER_REQ, count)

    def yield_all(self):
        while True:
            status = self.client.search_job_status(self.searchJob)
            from pprint import pprint
            yield from self._yield_from_status(status)

            state = State(status['state'])
            if state == State.DONE:
                assert self.yielded == self.getCountFromStatus(status)
                break

            sleep(self.delay)

class _MessagesGenerator(_ResultGenerator):
    def getListOfRecords(self):
        return self.client.search_job_messages(self.searchJob, limit=self.MAX_PER_REQ, offset=self.yielded)['messages']
    def getCountFromStatus(self, status):
        return status['messageCount']

class _RecordsGenerator(_ResultGenerator):
    def getListOfRecords(self):
        return self.client.search_job_records(self.searchJob, limit=self.MAX_PER_REQ, offset=self.yielded)['records']
    def getCountFromStatus(self, status):
        return status['recordCount']

class SumoLogicSimple:

    def __init__(self, sumo):
        """
        Initialize the Simple SumoLogic API.

        :type sumo: sumologic.SumoLogic
        """
        self.client = sumo

    @staticmethod
    def _getTime(t: Union[datetime, timedelta, None]) -> datetime:
        if isinstance(t, datetime):
            return t
        elif t is None:
            return datetime.now()
        else:
            return datetime.now() + t

    def search(self, query, startTime: Union[datetime, timedelta, None], endTime: Union[datetime, timedelta, None], timeZone='UTC'):
        """
        Search Sumo with a given query, and return a streaming iterable of results.

        :type query: str
        :type startTime: Union[datetime, timedelta]
        :type endTime: Union[datetime, timedelta]

        :return Tuple of (fields, messages, records).
        :rtype: Tuple[dict, Iterable[dict], Iterable[dict]]
        """
        MAX_PER_REQ = 1000
        MIN_PER_REQ = 10

        messages_yielded = 0
        records_yielded = 0

        startTime = self._getTime(startTime)
        endTime = self._getTime(endTime)

        sj = self.client.search_job(query, _sumoTime(startTime), _sumoTime(endTime), timeZone=timeZone, byReceiptTime=False)

        firstResponse = self.client.search_job_messages(sj, limit=1)
        fields = firstResponse['fields']

        messagesGenerator = _MessagesGenerator(self.client, sj)
        recordsGenerator = _RecordsGenerator(self.client, sj)

        return (fields, messagesGenerator.yield_all(), recordsGenerator.yield_all())