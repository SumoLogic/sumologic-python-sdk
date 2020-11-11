#!c:\python27\python.exe
"""
sumologic-export
~~~~~~~~~~~~~~~~

Export your Sumologic logs easily and quickly.

Usage:
    sumologic-export configure
    sumologic-export
    sumologic-export <start> <stop>
    sumologic-export
        (<start> | -s <start> | --start <start>)
        [(<stop> | -t <stop> | --stop <stop>)]
        [<increment> | -i <increment> | --increment <increment>]
    sumologic-export (-h | --help)
    sumologic-export (-v | --version)

Written by Randall Degges (http://www.rdegges.com)
Updated by Baine Werny (bainewerny@gmail.com)
     ported to windows python 2.7
     added support for:
		- larger message export files (flush to disk based on pages and sections)
		- command line to adjust export job time increments in hours
		- specified hour of the day start time
		- requests.session with updated SSL/TLS
		- Windows 7zip
"""
from __future__ import print_function

from datetime import datetime, timedelta
from json import dumps, loads
from os import chmod, mkdir
from os.path import exists, expanduser
from subprocess import call
from time import sleep
from gc import collect

from docopt import docopt
import requests


##### GLOBALS
VERSION = '0.1.1'
CONFIG_FILE = expanduser('~/.sumo')


# Pretty print datetime objects.
prettify = lambda x: x.strftime('%Y-%m-%d-%H')


class Exporter(object):
    """Abstraction for exporting Sumologic logs."""

    # Default time increment to move forward by.
    INCREMENT = timedelta(hours=24)

    # Default timerange to use if no dates are specified.
    DEFAULT_TIMERANGE = timedelta(days=7)

    # Sumologic API constants.
    SUMOLOGIC_ENDPOINT = 'https://api.sumologic.com/api/v1/search/jobs'
    SUMOLOGIC_HEADERS = {
        'content-type': 'application/json',
        'accept': 'application/json',
    }

    # Amount of time to wait for API response.
    TIMEOUT = 10

    # Sumologic timezone to specify.
    TIMEZONE = 'PST'

    # Amount of time to pause before requesting Sumologic logs.  60 seconds
    # seems to be a good amount of time.
    SLEEP_SECONDS = 60

    # The number of log messages in a "page". Logs are downloaded from Sumologic and batched in pages.  The higher this
    # is, the more memory is used, but the faster the exports are. This number impacts the disk flushing section size. 
	# Also see PAGES_PER_SECTION.
    MESSAGES_PER_PAGE = 10000

    # The amount of log pages per section. Logs are flushed to disk in sections.  The higher this
    # is, the more memory is used, and the faster the exports are, however python does not seem to support
    # more than about 5.5 million messages per section. Make sure that PAGES_PER_SECTION * MESSAGES_PER_PAGE < 5.5 million.
	# The default of PAGES_PER_SECTION =100 and MESSAGES_PER_PAGE=10000 may require up to 8GB RAM.
    PAGES_PER_SECTION = 100
	
    def __init__(self):
        """
        Initialize this exporter.

        This includes:

        - Loading credentials.
        - Prepping the environment.
        - Setting up class variables.
        """
        if not exists(CONFIG_FILE):
            print ('No credentials found! Run sumologic-export configure')
            raise SystemExit()

        if not exists('exports'):
            mkdir('exports')

        with open(CONFIG_FILE, 'rb') as cfg:
            creds = loads(cfg.read())
            self.credentials = (creds['accessId'], creds['accessKey'])
			
        #Create requests session
        self.cookies = None
        self.session = requests.Session()
        self.session.auth = self.credentials
        self.session.headers = {'content-type': 'application/json', 'accept': 'application/json'}

    def init_dates(self, start, stop):
        """
        Validate and initialize the date inputs we get from the user.

        We'll:

        - Ensure the dates are valid.
        - Perform cleanup.
        - If no dates are specified, we'll set defaults.
        """
        if start:
            try:
                self.start = datetime.strptime(start, '%Y-%m-%d-%H').replace(minute=0, second=0, microsecond=0)
            except:
                print ('Invalid START date format. Format must be YYYY-MM-DD-HH.')
                raise SystemExit(1)

            if self.start > datetime.now():
                print ('Start date must be in the past!')
                raise SystemExit(1)
        else:
            self.start = (datetime.now() - self.DEFAULT_TIMERANGE).replace(hour=0, minute=0, second=0, microsecond=0)

        if stop:
            try:
                self.stop = datetime.strptime(stop, '%Y-%m-%d').replace(hour=0, minute=0, second=0, microsecond=0)
            except:
                print ('Invalid STOP date format. Format must be YYYY-MM-DD.')
                raise SystemExit(1)

            if self.stop > datetime.now():
                print ('Stop date must be in the past!')
                raise SystemExit(1)
        else:
            self.stop = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    def init_increment(self,increment):
        """
		if increment argument included, validate and override default
		"""
        if increment:
           try:
                self.INCREMENT = timedelta(hours=int(increment))
           except Exception as e:
                print ('%s Invalid increment %s. Must be integer 1 - 24.' % (e,increment))
                raise SystemExit(1)

           if int(increment) > 24 or int(increment) < 1:
                print ('Invalid increment %s. Must be integer 1 - 24.' % (increment))
                raise SystemExit(1)
				
        print ('Increment = %s hours' % (self.INCREMENT))
        #raise SystemExit(1)
      					
    def export(self, start, stop, increment):
        """
        Export all Sumologic logs from start to stop.

        All logs will be downloaded one day at a time, and put into a local
        folder named 'exports'.

        :param str start: The datetime at which to start downloading logs.
        :param str stop: The datetime at which to stop downloading logs.
        """
        # Validate / cleanup the date and increment inputs.
        self.init_dates(start, stop)
        self.init_increment(increment)
        
        print ('Exporting all logs from: %s to %s... Could take a while.\n' % (
            prettify(self.start),
            prettify(self.stop),
        ))

        print ('Exporting Logs %s' % datetime.now())
        print ('--------------')

        date = self.start
        while date < self.stop:

            # Schedule the Sumologic job.
            job_url = self.create_job(date, date + self.INCREMENT)
            print ('- getting logs for:\n %s to %s at %s ' % (prettify(date), prettify(date + self.INCREMENT), datetime.now()))

            # Pause to allow Sumologic to process this job.
            sleep(self.SLEEP_SECONDS)

            # Figure out how many logs there are for the given date.
            total_logs = self.get_msg_count(job_url)

            # If there are logs to be downloaded, let's do it.
            if total_logs:
                print (' - Downloading %d logs.' % total_logs)

                for section in xrange(0, (total_logs / self.MESSAGES_PER_PAGE / self.PAGES_PER_SECTION) + 1):
                   logs = []
                   for log in self.get_logs_by_section(job_url, section, total_logs):
                       logs.append(log)

                   print (' - Writing/appending log file section %s to: exports/%s.json' % (section, prettify(date)))
                   with open('exports/%s.json' % prettify(date), 'ab') as exports:
                       exports.write(dumps(logs, indent=2, sort_keys=False))

                collect() #force garbage collection
                print (' - Compressing log file: exports/%s.json' % prettify(date))
                cmd=("C:/Program Files/7-Zip/7z.exe")  #7z version 16.04
                params=('a',' -sdel ','exports\%s.json.zip exports\%s.json' % (prettify(date), prettify(date)))
                call([cmd,params])
                
            else:
                print (' - No logs found.')

            # Move forward.
            date += self.INCREMENT

        print ('\nFinished downloading logs!')

    def create_job(self, start, stop):
        """
        Request all Sumologic logs for the specified date range.

        :param datetime start: The date to start.
        :param datetime stop: The date to stop.

        :rtype: string
        :returns: The URL of the job.
        """
        while True:
            try:
                resp = self.session.post(
                    self.SUMOLOGIC_ENDPOINT,
                    #auth = self.credentials,
                    #headers = self.SUMOLOGIC_HEADERS,
                    timeout = self.TIMEOUT,
                    data = dumps({
                        'query': '*',
                        'from': start.isoformat(),
                        'to': stop.isoformat(),
                        'timeZone': self.TIMEZONE,
                    }),
                    cookies = self.cookies,
                    #session = self.session,
                )
                if resp.cookies:
                    self.cookies = resp.cookies

                #print (resp.status_code)
                if resp.status_code == 202:
                    return '%s/%s' % (self.SUMOLOGIC_ENDPOINT, resp.json()['id'])

                #print resp.auth
                raise Exception(resp)
            except Exception as e:
                print(e)
                sleep(5)

    def get_msg_count(self, job_url):
        """
        Given a Sumologic job URL, figure out how many logs exist.

        :param str job_url: The job URL.

        :rtype: int
        :returns: The amount of logs found in the specified job results.
        """
        while True:
            try:
                resp = self.session.get(
                    job_url,
                    #auth = self.credentials,
                    #headers = self.SUMOLOGIC_HEADERS,
                    timeout = self.TIMEOUT,
                    cookies = self.cookies,
                )
                if resp.cookies:
                    self.cookies = resp.cookies

                if resp.status_code == 200:
                    json = resp.json()
                    print ('%s %s' % (json['state'],json['messageCount']), end='\r')
                    if json['state'] == 'DONE GATHERING RESULTS':
                        print ('')
                        return json['messageCount']

                if resp.status_code <> 200:
                    print ('%s %s' % (json['state'],json['messageCount']))
                    
                raise Exception(resp)
            except Exception as e:
                #print(e)
                sleep(10)

    def get_logs_by_section(self, job_url, section, count):
        """
        Iterate through all Sumologic logs for the given job.

        :param str job_url: The job URL.
        :param int section: section number offset to download.
        :param int count: The total number of logs to retrieve.

        :rtype: generator
        :returns: A generator which returns a single JSON log for each section or until all logs have
            been retrieved.
        """
     
        for page in xrange((section * self.PAGES_PER_SECTION), ((section + 1) * self.PAGES_PER_SECTION)):
            if page > (count / (self.MESSAGES_PER_PAGE)):
               break
                  
            while True:
                try:
                    resp = self.session.get(
                        job_url + '/messages',
                        #auth = self.credentials,
                        #headers = self.SUMOLOGIC_HEADERS,
                        timeout = self.TIMEOUT,
                        params = {
                            'limit': self.MESSAGES_PER_PAGE,
                            'offset': self.MESSAGES_PER_PAGE * page,
                        },
                        cookies = self.cookies,
                    )
                    if resp.cookies:
                        self.cookies = resp.cookies

                    if resp.status_code == 200:
                        json = resp.json()
                        for log in json['messages']:
                            yield log['map']

                        break

                    raise Exception(resp)
                except Exception as e:
                  print(e)
                  sleep(1)

def configure():
    """
    Read in and store the user's Sumologic credentials.

    Credentials will be stored in ~/.sumo
    """
    print ('Initializing `sumologic-export`...\n')
    print ("To get started, we'll need to get your Sumologic credentials.")

    while True:
        accessID = raw_input('Enter your accessID: ').strip()
        accessKey = raw_input('Enter your accessKey: ').strip()
        if not (accessID or accessKey):
            print ('\nYour Sumologic credentials are needed to continue!\n')
            continue

        print ('Your API credentials are stored in the file:', CONFIG_FILE, '\n')
        print ('Run sumologic-export for usage information.')

        with open(CONFIG_FILE, 'wb') as cfg:
            cfg.write(dumps({
                'accessID': accessID,
                'accessKey': accessKey
            }, indent=2, sort_keys=True))

        # Make the configuration file only accessible to the current user --
        # this makes the credentials a bit more safe.
        chmod(CONFIG_FILE, 0600)

        break


def main(args):
    """
    Handle command line options.

    :param args: Command line arguments.
    """
    if args['-v']:
        print (VERSION)
        raise SystemExit()

    elif args['configure']:
        configure()
        raise SystemExit()
        
    exporter = Exporter()
    exporter.export(args['<start>'], args['<stop>'],args['<increment>'])


if __name__ == '__main__':
    main(docopt(__doc__, version=VERSION))
