# Submits metrics search job, waits for completion, then prints results.
# Pass the query via stdin.
#
# cat query.sumoql | python search-job.py <accessId> <accessKey> \
# <endpoint> <fromDate> <toDate>
#
# Note: fromDate and toDate must be either ISO 8601 date-times or epoch
#       milliseconds
#
# Example:
#
# cat query.sumoql | python search-job.py <accessId> <accessKey> \
# https://api.us2.sumologic.com/api/v1/ 1408643380441 1408649380441


## api response layout:
# results = [{}, {}, {}]
# {} -> metric{'dimensions':[{key: _, value: _}, {}]}, datapoints{'timestamp': [], 'value':[]}
#
#
#
#
import json
import os
import sys
import time
import logging
import pandas as pd

logging.basicConfig(level=logging.DEBUG)

from sumologic import SumoLogic


def get_queries():
    # return ['_sourceHost=stag-kafka-metrics-1 CPU_IOWait | quantize to 15m | avg']
    # return ['_sourceCategory=kafka-forge-* ProduceTotalTime 99th* ']
    # queries = {
    #     'ProduceTotalTime': '_sourceCategory=kafka-forge-* ProduceTotalTime 99th*',
    #     'ProduceRequests': '_sourceCategory=kafka-forge-* ProduceRequests One*'}

    # source_category_str = 'kafka-forge-*'
    source_category_str = 'kafka-metrics'
    queries = {'FetchConsumerRequests': ('_sourceCategory=%s FetchConsumerRequests One*' % source_category_str),
               'ProduceRequests': ('_sourceCategory=%s ProduceRequests One*' % source_category_str),
               'TopicsBytesIn': ('_sourceCategory=%s TopicsBytesIn One*' % source_category_str),
               'TopicsBytesOut': ('_sourceCategory=%s TopicsBytesOut One*' % source_category_str),
               'UnderReplicatedPartitions': ('_sourceCategory=%s UnderReplicatedPartitions' % source_category_str),
               'ResponseQueueSize': ('_sourceCategory=%s ResponseQueueSize' % source_category_str),
               'RequestQueueSize': ('_sourceCategory=%s RequestQueueSize' % source_category_str),
               'HeapMemoryUsage': ('_sourceCategory=%s HeapMemoryUsage_used' % source_category_str),
               'CPU_IOWait': ('_sourceCategory=%s CPU_IOWait' % source_category_str),
               'ProduceTotalTime': ('_sourceCategory=%s ProduceTotalTime 99th*' % source_category_str),
               'FetchConsumerTotalTime': ('_sourceCategory=%s FetchConsumerTotalTime 99th*' % source_category_str)
               }

    # queries = {
    # 'hackathon' : '_view=customer_service_report_queries'
    # 'hackathon' : '_view=customer_logins_daily'
    # 'hackathon': '_view=customer_api_queries'
    # }
    return queries


def get_metrics_from_args(query):
    args = sys.argv
    sumo = SumoLogic(args[1], args[2], args[3])
    fromTime = int(args[4])
    toTime = int(args[5])
    sj = sumo.search_metrics(query, fromTime, toTime)
    return sj


def get_metrics_predefined(query, dep='nite', from_time=1551294053000, to_time=1551725652000):
    # args = sys.argv

    # nite
    if dep == 'nite':
        access_id = 'suuKm6NluPTBKb'
        access_key = 'xFV9gSmLEq7NKrn5UFstJ7tUZQkXAzcEJSUNC4nr6Nfp2gIwEBQOSFKBSsif8kJ3'
        endpoint = 'https://nite-api.sumologic.net/api/v1'

    # stag
    if dep == 'stag':
        access_id = 'suNh9kI81gpRF7'
        access_key = 'hag1mGxoTxp2ibq1WuboPQcqpmDFSwXh1wS7V77pLyVyDltt5gi20wEkbVHeMNeH'
        endpoint = 'https://stag-api.sumologic.net/api/v1'

    # prod
    if dep == 'prod':
        access_id = 'sul9VmzfTIBBHP'
        access_key = 'G8KGXzoLByEheJhpTJR7OTG9ImReABZJ3CWSdiOSvHJcUVpJZ8qjhWKq4WVmw3XO'
        endpoint = 'https://long-api.sumologic.net/api/v1'

    # syd
    if dep == 'syd':
        access_id = 'su2tdwsQY4YQzA'
        access_key = 'T7gUFjRnTS6TslndfLCJPpBWkWyvUOPiNDH4RZieTIX6yd1zXR1hpJr26HUC1v71'
        endpoint = 'https://long-api.sumologic.net/api/v1'

    # fra
    if dep == 'fra':
        access_id = 'suWduiVd5aoFaK'
        access_key = 'h74mObUSB8C07B1bkGJx4vxny8yO8Ai2QHlFmUSx4egslLp0lb37VclH7roKx73c'
        endpoint = 'https://long-api.sumologic.net/api/v1'

    # dub
    if dep == 'dub':
        access_id = 'subdcqD455elTq'
        access_key = 'Zt92S7fAUPMgaLXWvok6eLiMHeTO9tKorPVybCetgvjBsFTXD989eUI8So4tCrw6'
        endpoint = 'https://long-api.sumologic.net/api/v1'

    # us2
    if dep == 'us2':
        access_id = 'su7wF3CHsalSad'
        access_key = '6zMudQ08RDJ7S2ajVfqAKL1cHqFzfvipDakbpk0uKYMbrLuYxAyfFWFlL93Ztnmn'
        endpoint = 'https://long-api.sumologic.net/api/v1'
    # from_time = 1551294053000  # has to be int
    # to_time = 1551725652000  # has to be int

    # # customer usage on us2
    # access_id = 'suvEOHJ37D9Gg6'
    # access_key = 'yjRieNaA71BXKm62gStDkvMvVRsqI6W9eg2g6z6FTA9Z89WpwJhCPIas9ILO7LLg'
    # endpoint = 'https://api.us2.sumologic.com/api/v1/'
    # # 15 mins
    # from_time = 1550621442000
    # to_time = 1550622284000
    # # 48 h
    # from_time = 1550363663000
    # to_time = 1550621442000
    # # 14 days
    # from_time = 1549579832000
    # to_time = 1550789432000
    #
    # # 15 jan to 1 feb
    # # to_time = 1549033596000
    #
    # # 15 Jan
    # # from_time = 1547564796000
    #
    # # 22 Jan
    # # from_time = 1548169596000
    #
    # # 7 Jan to 15
    # # to_time = 1547564796000
    # # from_time = 1546887738000
    # # 21 days
    # # from_time = 1549061432000
    # # to_time = 1550789432000

    print("Making a query {} to: {}, with the time range: {} to {}".format(query, dep, from_time, to_time))
    sumo = SumoLogic(access_id, access_key, endpoint)

    sj = sumo.search_metrics(query, from_time, to_time)
    return sj


def create_dataframe_dict(queries_dict, dep='nite', from_time=1551294053000, to_time=1551725652000):
    dataframe = None
    dataframe_dict = {}
    for query_label, query in queries_dict.items():
        # get parameter from args
        # response = get_metrics_from_args(query)

        # get pre-defined parameters
        # print("Before call: ", from_time, to_time)
        print("Query Label: ", query_label)
        response = get_metrics_predefined(query, dep=dep, to_time=to_time, from_time=from_time)

        results = response['response'][0]['results']
        for result in results:
            column_values = {}
            metric_dict = result['metric']
            for dim in metric_dict['dimensions']:
                if dim['key'] == '_collector':
                    collector_name = dim['value']
            timestamp = result['datapoints']['timestamp']
            value = result['datapoints']['value']
            column_values[collector_name] = value
            column_values['timestamp'] = timestamp
            # inserting into a dataframe
            if dataframe is None:
                # dataframe = pd.DataFrame(data=value, index=timestamp, columns=[collector_name])
                # dataframe = pd.DataFrame(data=value, columns=[collector_name])
                dataframe = pd.DataFrame(data=column_values)
            else:
                # convert to series to prevent the value error: Length of Values does not match length of index
                series = pd.Series(value)
                dataframe[collector_name] = series

        dataframe_dict[query_label] = dataframe
        dataframe = None
    return dataframe_dict


def align_dataframe_dict(dataframe_dict):
    col_list = list(dataframe_dict.keys())
    print(col_list)
    aligned_dataframe_dict = {}

    for col_label, dataframe in dataframe_dict.items():
        print(col_label)
        dataframe = dataframe.set_index('timestamp')
        # print(dataframe.head().to_string())
        for column in dataframe:
            print(column)
            # print(dataframe[column].head())
            # print("--")
            if column not in aligned_dataframe_dict:
                temp_df = pd.DataFrame(index=dataframe.index, data=dataframe[column], columns=[col_label])
                temp_df[col_label] = dataframe[column]
                aligned_dataframe_dict[column] = temp_df
            else:
                temp_df = aligned_dataframe_dict[column]
                try:
                    temp_df[col_label] = dataframe[column]
                except:
                    print("Weird Index issue")
                    # print(temp_df.shape, dataframe[column].shape)
                    # print(temp_df, dataframe[column])
                    # raise ValueError("BLAH")

                aligned_dataframe_dict[column] = temp_df
        # print(temp_df.head().to_string())
        # print("****")

    # print(aligned_dataframe_dict)
    for key, val in aligned_dataframe_dict.items():
        print(key, len(val), val.isnull().sum().sum())
        print("Non zero values: ", len(val) * len(val.columns) - val.isnull().sum().sum())
        # print(val.head().to_string())
        print("---------")

    return aligned_dataframe_dict


def save_aligned_dataframes(aligned_dataframe_dict, from_time, to_time):
    for title, df in aligned_dataframe_dict.items():
        # title_str = title + "_" + str(from_time) + "_" + str(to_time)
        title_str = str(from_time) + "_" + str(to_time)
        # print(title_str)
        # new_dir = "../forge_data/" + title
        new_dir = "../metrics_data/" + title
        if not os.path.exists(new_dir):
            os.mkdir(new_dir)
        # df.to_csv('../forge_data/' + title_str + ".csv", encoding='utf-8')
        df.to_csv(new_dir + "/" + title_str + ".csv", encoding='utf-8')


def create_dataframe(queries_dict):
    dataframe = None
    dataframe_dict = {}
    for query_label, query in queries_dict.items():
        # get parameter from args
        # response = get_metrics_from_args(query)

        # get pre-defined parameters
        response = get_metrics_predefined(query)

        # print(response)
        # print(response['response'][0]['results'][0])
        # print(response['response'][0]['results'][1])
        # print(response['response'])
        print(type(response))
        print(len(response))
        if (len(response) > 0):
            return pd.DataFrame(response)


if __name__ == '__main__':
    queries_dict = get_queries()
    # dataframe = create_dataframe(queries_dict)
    # to_time = int(time.time() * 1000)
    # for dep in ['us2', 'prod', 'syd', 'dub', 'fra', 'long', 'stag','nite']:
    # for dep in ['us2']:
    # for dep in ['prod']:
    # for dep in ['syd']:
    # for dep in ['dub']:
    for dep in ['fra']:
        to_time = 1551725652000
    #     to_time = 1549911252000
        for i in range(8):
            from_time = to_time - (24 * 7 * 60 * 60 * 1000)
            print(to_time, from_time)
            dataframe_dict = create_dataframe_dict(queries_dict, dep=dep, to_time=to_time, from_time=from_time)
            aligned_dataframe_dict = align_dataframe_dict(dataframe_dict)
            save_aligned_dataframes(aligned_dataframe_dict, from_time=from_time, to_time=to_time)
            to_time = from_time

