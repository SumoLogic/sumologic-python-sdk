def uploadFileInLookupTable(self, lookupContentID, fileName):
        filePath = os.path.join(os.path.dirname(__file__),{path_to_fileDirectory}, fileName)
 
        fileData = open(filePath, 'r').read()
 # Here configuration.host is the Sumologic Host URL, eg. https://api.us2.sumologic.com/api  
        url = self.configuration.host + '/v1/lookupTables/' + lookupContentID + '/upload'
        querystring = {"merge": "false"}
        files = {'file': (fileName, fileData)}
        response = requests.post(url, files=files, params=querystring, auth=(self.configuration.username, self.configuration.password))
        print ("response: " + str(response))
        return response
