#!/usr/bin/python
# gen_gateschema.py - Generate Gate Schema XML file for the X3 Remapper utility
import argparse
import xml.etree.cElementTree as ET
import pandas
from xml.dom import minidom

def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="    ")


parser = argparse.ArgumentParser(description="This utility generates the Gate Network Schema file used by the X3 Remapper Utility.")
parser.add_argument("-i", "--inputmap", help="Reference map: input file name", required=True)
parser.add_argument("-s", "--inputschema", help="Remap schema: input file name", required=True)
parser.add_argument("-n", "--sectorsout", help="Generate new sectors schema: output file name", required=False)
parser.add_argument("-g", "--gatesout", help="Generate gates schema: output file name", required=False)
args = parser.parse_args()

if not args.sectorsout and not args.gatesout:
    print "You did not request a New Sectors schema or Gates schema. Nothing to do, exiting now."
    exit()

# Load reference map via Element Tree 
map_tree = ET.parse(args.inputmap)
map_root = map_tree.getroot()

# Export Gate Schema
if args.gatesout:
    # Create a new XML root for exporting
    schema_export = ET.Element('universe')

    # Iterate through sectors
    for sector in map_root.findall('o'):
        sector_out = ET.SubElement(schema_export, 'o', sector.attrib)

        for gate in sector.findall(".//o[@t='18']"):
            gate_out = ET.SubElement(sector_out, 'o', gate.attrib)

    # Output XML to disk
    with open(args.gatesout, 'w') as f:
        f.write(prettify(schema_export))
    f.close()

# Export New Sectors Schema
if args.sectorsout:
    # Create a new XML root for exporting
    schema_export = ET.Element('universe')

    # Load map schema table from CSV into a pandas DataFrame
    map_schema = pandas.read_csv(args.inputschema, index_col='key')
    map_schema.sort_index(inplace=True)

    # Loop through sectors flagged in schema for addition and lookup each sector in reference map
    add_sectors = map_schema[map_schema.action == 1]
    for index, row in add_sectors.iterrows():
        x = row['x2']
        y = row['y2']
        sector = map_root.find(".//o[@x='" + str(x) + "'][@y='" + str(y) + "']")

        # Append sector to New Sectors Schema
        sector_out = ET.SubElement(schema_export, 'o', sector.attrib)
        for child in sector:
            ET.SubElement(sector_out, 'o', child.attrib)

    # Output XML to disk
    with open(args.sectorsout, 'w') as f:
        f.write(prettify(schema_export))
    f.close()