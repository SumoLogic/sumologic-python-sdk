# Emails you a per-collector per-source usage report
#
# python usage-report.py <accessId> <accessKey> <orgId> <fromTime> <toTime> <timezone> <timeslice> <email>
#
# TODO per-source
# TODO log hook
# TODO delete jobs?

from email.mime.text import MIMEText
import json
from smtplib import SMTP
import sys

from sumologic import SumoLogic

args = sys.argv

sumo = SumoLogic(args[1], args[2], "https://long-api.sumologic.net/api/v1")
orgId = args[3]
fromTime = args[4]
toTime = args[5]
timezone = args[6]
timeslice = args[7]
fromEmail = 'worker@sumologic.com'
toEmail = args[8]

lookup = "lookup/collector_name"

q = r"""
_sourceCategory=config "Collector by name and ID" !GURR "%s"
| parse "[logger=*]" as logger
| where logger = "scala.config.LoggingVisitor"
| parse "Collector by name and ID, id: '*', decimal: '*', name: '*', organization ID: '*', decimal: '*', organization name: '*', organization type: '*'"
  as collector_id, collector_id_decimal, collector_name, org_id, org_id_decimal, org_name, account_type
| where org_id = "%s"
| count by collector_id, collector_name
| fields collector_id, collector_name | save %s
"""
q = q % (orgId, orgId, lookup)
q = q.replace('\n', ' ')

r = sumo.search_and_wait(q, fromTime, toTime, timezone)

print(r)

q = r"""
(_sourceCategory=receiver or _sourceCategory=cloudcollector)
"Message stats, combined" "by collector" "%s"
| parse "customer: '*'" as customer_id
| where customer_id = "%s"
| parse "{\"collector\":*" as collector_json
| parse regex field=collector_json "\"(?<collector_id>\S+?)\":\{\"sizeInBytes\":(?<size_in_bytes>\d+?),\"count\":(?<message_count>\d+?)" multi
| fields - collector_json
| lookup collector_name as collector_name from %s on collector_id = collector_id
| sum(size_in_bytes) as size_in_bytes, sum(message_count) as message_count by collector_id, collector_name
| sort size_in_bytes
"""

q = q % (orgId, orgId, lookup)
q = q.replace('\n', ' ')

r = sumo.search_and_wait(q, fromTime, toTime, timezone)

print(r)

msg = MIMEText(json.dumps(r))
msg['From'] = fromEmail
msg['To'] = toEmail
msg['Subject'] = 'Collector Usage Report'
smtp = SMTP('localhost')
smtp.sendmail(fromEmail, [toEmail], msg.as_string())
smtp.quit()
