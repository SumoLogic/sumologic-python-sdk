# create_hierarchy.py

Creates hierarchy in sumologic org.

# Prerequisites

1> Install the sumologic-python-sdk using below command.
   `pip install sumologic-sdk`
   
2> Download the [create_hierarchy.py](create_hierarchy.py) script from the github.

3> Download the json hierarchy configuration file for one of the hierarchies ([Application Serview View](ApplicationServiceView.json), [Service Application View](ServiceApplicationView.json) or [Real User Monitoring](RealUserMonitoring.json)). You can also create your using the samples provided.


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
