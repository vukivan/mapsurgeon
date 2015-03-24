#!/usr/bin/python
# gen_jobs.py - Generate updated Jobs file based on the Remap Schema
import argparse
import pandas as pd
import os

parser = argparse.ArgumentParser(description="This utility generates the Gate Network Schema file used by the X3 Remapper Utility.")
parser.add_argument("-i", "--inputjobs", help="Reference Jobs File: input file name", required=True)
parser.add_argument("-s", "--inputschema", help="Remap schema: input file name", required=True)
parser.add_argument("-o", "--outputjobs", help="Updated Jobs File: output file name", required=True)
args = parser.parse_args()

print "Jobs Update Utility: Loading original Jobs file"

# Load Jobs from CSV into a pandas DataFrame (powerful associative table)
jobs = pd.read_csv(args.inputjobs, header=None, delimiter=';', skiprows=1)

print "Loading the Remap Schema"
# Load map schema table from CSV into a pandas DataFrame
map_schema = pd.read_csv(args.inputschema, index_col='key')
map_schema.sort_index(inplace=True)

# Reassign job sectors to remapped coordinates (using Remap Schema for reference)
# X = jobs[72], Y = jobs[73]

# search jobs with assigned home sectors
remap_jobs = jobs[jobs[72] > -1]

print "Reassign jobs to new sector coordinates"

for index, row in remap_jobs.iterrows():
    x = row[72]
    y = row[73]

    #print 'job: ' + str(row[0])
    #print 'original: (' + str(x) +',' + str(y) +')'

    # find matching sector in remap schema
    sector_schema = map_schema.query('x1 == ' + str(x) + ' & y1 == ' + str(y))

    #print 'new: (' + str(sector_schema.iloc[0]['x2']) + ',' + str(sector_schema.iloc[0]['y2']) + ')'

    row[72] = sector_schema.iloc[0]['x2']
    row[73] = sector_schema.iloc[0]['y2']

    x = row[72]
    y = row[73]

    #print 'update: (' + str(x) +',' + str(y) +')\n'

# save updated jobs file to a temp file
jobs.to_csv('types/jobs_temp.txt', ';', index=False, header=False)

# and prep the final file, including the special header required by X3
with open('types/jobs_temp.txt', 'r') as temp_jobs: 
    data = temp_jobs.read()
with open(args.outputjobs, 'w') as f:
    f.write("16; // Jobs Updated and Exported by the X3 Map Surgeon utility --*-- 64\n" + data)
f.close()
temp_jobs.close()
os.remove('types/jobs_temp.txt')

print "\nUpdated Jobs saved to disk. \n\nYou may still need to make other adjustments to the Jobs, \nsuch as altering Max Count for specific jobs that need different spawn rates. \nLitcube's Jobs Editor is highly recommended for this task \n(See included documentation for details.)"




