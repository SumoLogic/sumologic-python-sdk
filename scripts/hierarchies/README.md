# create_hierarchy.py

Creates hierarchy in sumologic org.

# Prerequisites

1> Install the sumologic-python-sdk using below command.
   `pip install sumologic-sdk`
   
2> Download the [create_hierarchy.py](create_hierarchy.py) script from the github.

3> Download the json hierarchy configuration file for the hierarchy ([Real User Monitoring](RealUserMonitoring.json)). Note, that this api is not yet supported for custom hierarchies so only use the ones provided in the hierarchies folder.

4> Sumo Logic user whose role has "Manage Entity Type Configs" permissions is required which you will use to login and generate access_id/access_keys using the instructions in [doc](https://help.sumologic.com/Manage/Security/Access-Keys#manage-your-access-keys-on-preferences-page).

Note: The below command first deletes any existing hierarchy with same name and then deploys the new hierarchy.

Tested on:
Python 3.8.0
Python 3.7.0


# Usage

usage: create_hierarchy.py [-h] -d DEPLOYMENT -c ACCESS_ID -k ACCESS_KEY -f FILE

optional arguments:
```
   -h, --help            show this help message and exit

  -d DEPLOYMENT, --deployment DEPLOYMENT
                        Provide sumologic deployment ex us1,ca,au,de,eu,jp,us2,fed,in
  -c ACCESS_ID, --access_id ACCESS_ID
                        Provide sumologic access_id
  -k ACCESS_KEY, --access_key ACCESS_KEY
                        Provide sumologic access_key
  -f FILE, --hierarchy_filepath FILE
                        Provide path to json file containing hierarchy
```

Example:

`python create_hierarchy.py -d us1 -c abcdefgh -k abc123 -f RealUserMonitoring.json`

Here's the output

![image](https://user-images.githubusercontent.com/3620468/128547303-7830878f-e630-4426-8739-b3b16e06144d.png)



