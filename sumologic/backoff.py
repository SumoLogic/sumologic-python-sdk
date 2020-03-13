import requests
import logging
import time

logger = logging.getLogger('sumologic.backoff')

MAX_TRIES = 8

def backoff(func):
    def limited(*args, **kwargs):
        delay = 0.1
        tries = 0
        lastException = None
        while tries < MAX_TRIES:
            tries += 1
            try:
                return func(*args, **kwargs)
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429: # rate limited
                    logging.debug("Rate limited, sleeping for {0}s".format(delay))
                    time.sleep(delay)
                    delay *= 2
                    lastException = e
                    continue
                else:
                    raise
        logging.debug("Rate limited function still failed after {0} retries.".format(MAX_TRIES))
        raise lastException

    return limited
