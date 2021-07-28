# create_hierarchy.py

Creates hierarchy in sumologic org.

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
