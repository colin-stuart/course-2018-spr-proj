import urllib.request
import dml
import prov.model
import datetime
import json
import uuid

class fetchFloodData(dml.Algorithm):
    contributor = 'jlove'
    reads = []
    writes = ['jlove.flood']
    
    @staticmethod
    def execute(trial = False):
        startTime = datetime.datetime.now()
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('jlove', 'jlove')
        
        repo.dropCollection("flood")
        repo.createCollection("flood")
                
        data = None
        url = 'http://bostonopendata-boston.opendata.arcgis.com/datasets/74692fe1b9b24f3c9419cd61b87e4e3b_5.geojson'
        response = urllib.request.urlopen(url)
        if response.status == 200:
            data = response.read().decode('utf-8')
        if data != None:
            entries = json.loads(data)
            repo['jlove.flood'].insert_one(entries)
            repo['jlove.flood'].metadata({'complete':True})
            print(repo['jlove.flood'].metadata())
        repo.logout()
        
        endTime = datetime.datetime.now()
        return {"start":startTime, "end":endTime}
        
        
    @staticmethod
    def provenance(doc = prov.model.ProvDocument(), startTime = None, endTime = None):
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('jlove', 'jlove')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/') # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/') # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#') # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/') # The event log.
        doc.add_namespace('bdp', 'https://data.cityofboston.gov/dataset/')
        
        this_script = doc.agent('alg:jlove#fetchFloodData', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        resource = doc.entity('bdp:36inch-sea-level-rise-high-tide1', {'prov:label':'311, Service Requests', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'geojson'})
        fetch_flood = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(fetch_flood, this_script)
        doc.usage(fetch_flood, resource, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval',
                  'ont:Query':''
                  }
                  )

        flood = doc.entity('dat:jlove#flood', {prov.model.PROV_LABEL:'Boston 36inch Sea Level High Tide', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(flood, this_script)
        doc.wasGeneratedBy(flood, fetch_flood, endTime)
        doc.wasDerivedFrom(flood, resource, fetch_flood, fetch_flood, fetch_flood)


        repo.logout()
                  
        return doc
