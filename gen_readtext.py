#!/usr/bin/python
# gen_readtext.py - Generate updated ReadText file for sector names and descriptions based on the Remap Schema
import argparse
import xml.etree.cElementTree as ET
from xml.dom import minidom
import pandas as pd
import os

INPUT_PATH = "input/"
OUTPUT_ROOT = "output_package/addons/"
TEXT_PATH = "t/"
FILE_PRETEXT = "readtext_names_prepend.csv"
OUTPUT_FILENAME = "9337-L044.xml"


def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="    ", encoding="utf-8")


parser = argparse.ArgumentParser(description="This utility generates the updated ReadText file needed for the new map.")
parser.add_argument("--version", action='version', version='%(prog)s 1.0')
parser.add_argument("--inputnames", default="readtext_names.csv", help="Source Names File: input file name.")
parser.add_argument("--inputdescr", default="readtext_descriptions.csv", help="Source Descriptions File: input file name.")
parser.add_argument("--inputschema", default="remap_schema.csv", help="Input file name for remap schema.")
args = parser.parse_args()

print "ReadText Update Utility: Loading updated readtext values"

# Load values for sector names and descriptions from CSV
readtext_pre = pd.read_csv(INPUT_PATH + FILE_PRETEXT, header=1)
readtext_names = pd.read_csv(INPUT_PATH + args.inputnames, header=1)
readtext_descr = pd.read_csv(INPUT_PATH + args.inputdescr, header=1)

print "Loading the Remap Schema"
# Load map schema table from CSV into a pandas DataFrame
map_schema = pd.read_csv(INPUT_PATH + args.inputschema, index_col='key')
map_schema.sort_index(inplace=True)

names_root = ET.Element('language')
names_root.set('id', '44')

page = ET.SubElement(names_root, 'page')
page.set('id', '350007')
page.set('title', 'Boardcomp. Sectornames')
page.set('descr', 'Names of all sectors (spoken by Boardcomputer)')
page.set('voice', 'yes')

for index, row in readtext_pre.iterrows():
    if row[0] > 0:
        element = ET.SubElement(page, 't', {"id": str(row[0])})
        element.text = row[1]

# append sector names
for index, row in readtext_names.iterrows():
    if row[0] > 0:
        element = ET.SubElement(page, 't', {"id": str(row[0])})
        element.text = row[1]


page = ET.SubElement(names_root, 'page')
page.set('id', '350019')
page.set('title', 'Sector Descriptions WIP')
page.set('descr', 'Sector descriptions for galaxy map')
page.set('voice', 'no')

# append sector descriptions
for index, row in readtext_descr.iterrows():
    if row[0] > 0:
        element = ET.SubElement(page, 't', {"id": str(row[0])})
        element.text = row[1]


with open(OUTPUT_ROOT + TEXT_PATH + OUTPUT_FILENAME, 'w') as f:
    f.write(prettify(names_root))
f.close()

print "Updated readtext file saved to: " + OUTPUT_ROOT + TEXT_PATH + OUTPUT_FILENAME

