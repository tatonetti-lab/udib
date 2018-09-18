"""
Use the Columbia Open Health Data resource to pull grant funding from using the Federal RePORTER API.

COHD API:
http://cohd.nsides.io


"""

import os
import sys
import csv
import json
import tqdm
import urllib2

from fedreporter import *

cohd_allcond_prev_uri = 'http://cohd.io/api/frequencies/mostFrequentConcepts?dataset_id=3&q=100000&domain=Condition'

response = urllib2.urlopen(cohd_allcond_prev_uri)
json_data = response.read()
data = json.loads(json_data)

print >> sys.stderr, "Pulled prevalence data for %d diseases in COHD" % len(data['results'])

for cond in data['results']:
    file_name = cond['concept_id']
    if cond['concept_frequency'] > 0.7:
        continue
    
    ofn = 'data/funding/%s.csv' % file_name
    if os.path.exists(ofn):
        continue
    
    print >> sys.stderr, 'Concept ID:    ', cond['concept_id']
    print >> sys.stderr, 'Concept Name:  ', cond['concept_name']
    print >> sys.stderr, 'Concept Count: ', cond['concept_count']
    print >> sys.stderr, 'Concept Freq:  ', cond['concept_frequency']
    
    search_term = cond['concept_name'].replace('(', ' ').replace(')', ' ')
    
    totals = query_funds_for_term(search_term)
    save_totals(totals, search_term, file_name)
    
    #break
