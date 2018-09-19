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

def mdtablerow(li):
    return '| ' + ' | '.join(map(str,li)) + ' |'

#cohd_allcond_prev_uri = 'http://cohd.io/api/frequencies/mostFrequentConcepts?dataset_id=3&q=100000&domain=Condition'
cohd_hltcond_prev_uri = "http://cohd.io/api/frequencies/mostFrequentConcepts?dataset_id=3&domain=Condition&vocabulary_id=MedDRA&concept_class_id=HLT"

fy = 2017
response = urllib2.urlopen(cohd_hltcond_prev_uri)
json_data = response.read()
data = json.loads(json_data)

print >> sys.stderr, "Loaded %d conditions from URI." % len(data['results'])

headers = ['udibScore', 'ID', 'Disease/Disease Category', 'Number of Patients', 'EHR Disease Frequency', 'Number of Grants', 'Funding Total', 'Funding pScore*']

print >> sys.stdout, mdtablerow(headers)
print >> sys.stdout, mdtablerow(['---']*len(headers))

tabledatadict = dict()
total_cost = 0

for cond in data['results']:
    
    file_name = cond['concept_id']
    
    ofn = 'data/funding/%s.csv' % file_name
    if not os.path.exists(ofn):
        continue
    
    reader = csv.reader(open(ofn))
    nihdata = [row for row in reader if row[0] == str(fy)]
    if not len(nihdata) == 1:
        continue
    
    count = nihdata[0][1]
    cost = nihdata[0][2]
    
    total_cost += int(cost)
    
    row = list()
    row.append(cond['concept_id'])
    row.append(cond['concept_name'])
    row.append(cond['concept_frequency'])
    row.append(count)
    row.append(cost)
    
    tabledatadict[cond['concept_id']] = row

tabledata = list()

for cond, row in tabledatadict.items():
    
    if int(row[-1]) == 0:
        continue
    
    try:
        pCost = float(row[-1])/float(total_cost)
        udipScore = float(row[2])/pCost
    except ZeroDivisionError:
        print >> sys.stderr, "Div by zero error for %s, %s" % (row, total_cost)
        sys.exit(100)
    
    if pCost > 1:
        print >> sys.stderr, row, total_cost
        sys.exit(101)
    
    tabledata.append( [udipScore] + row + [pCost])

tabledata = sorted(tabledata)
tabledata.reverse()

for row in tabledata:
    print >> sys.stdout, mdtablerow(row)
    
    
    
    
