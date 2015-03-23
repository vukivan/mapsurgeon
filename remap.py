#!/usr/bin/python
# x3remapper.py - Remap X3 universe map to new layout using predefined schema data
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


def export_sorted_map(tree):
    """Sort sectors and gates, and output map to disk
       Sorting is probably not strictly necessary, but it helps with ensuring
       human-readability, and to maintain consistency with the vanilla map
       (as much as is possible.)
    """
    map_export = ET.Element('universe')

    root = tree.getroot()

    # sort sectors by Y,X coordinates
    data = []
    for elem in root:
        y = int(elem.get('y'))
        x = int(elem.get('x'))
        data.append((y, x, elem))

    data.sort()

    # insert the last item from each tuple
    root[:] = [item[-1] for item in data]

    # now iterate through sorted sectors and append to map_export tree
    # we export map elements in the following order to reorder the new gates
    # which were appended to the end of the sector element. This
    # places them back in front of the other sector objects, behind the sector
    # background settings.
    for sector in root:
        sector_out = ET.SubElement(map_export, 'o', sector.attrib)
        for background in sector.findall(".//o[@t='2']"):
            ET.SubElement(sector_out, 'o', background.attrib)
            # Remove elements from original sector so we later we can easily copy remaining children
            sector.remove(background)

        for gate in sector.findall(".//o[@t='18']"):
            ET.SubElement(sector_out, 'o', gate.attrib)
            sector.remove(gate)

        for child in sector:
            ET.SubElement(sector_out, 'o', child.attrib)

    # write map_export to disk
    with open(args.output, 'w') as f:
        f.write(prettify(map_export))
    f.close()


parser = argparse.ArgumentParser(description="This utility generates a new X3 universe map using the sector and gate network schema input files.")
parser.add_argument("-m", "--inputmap", help="Input file name for original map.", required=True)
parser.add_argument("-s", "--inputschema", help="Input file name for remap schema.", required=True)
parser.add_argument("-n", "--inputnewsectors", help="Input file name for new sectors schema.", required=True)
parser.add_argument("-o", "--output", help="Output file name for new map.", required=True)
parser.add_argument("-g", "--inputgates", help="Input file name for new gate schema. (If no gate schema is provided, default gate positions and connectivity rules will be applied.)", required=False)
args = parser.parse_args()

# Load original universe map via Element Tree 
map_tree = ET.parse(args.inputmap)
map_root = map_tree.getroot()

# Load map schema table from CSV into a pandas DataFrame (powerful associative table)
map_schema = pandas.read_csv(args.inputschema, index_col='key')
map_schema.sort_index(inplace=True)

# Load gate network schema file, if provided
if args.inputgates:
    gates_default = False   # flag to indicate whether default gate attributes, instead of the gate schema
    gate_schema_tree = ET.parse(args.inputgates)
    gate_schema_root = gate_schema_tree.getroot()

else:
    gates_default = True

# Loop through sectors flagged in map schema for removal and find each sector in the XML tree
# then remove it and its children
del_sectors = map_schema[map_schema.action == -1]
for index, row in del_sectors.iterrows():
    x = row['x1']
    y = row['y1']
    sector = map_root.find(".//o[@x='" + str(x) + "'][@y='" + str(y) + "']")
    map_root.remove(sector)

# Loop through XML tree again, this time to reassign sector coordinates
for sector in map_root.findall('o'):
    x1 = sector.get('x')    # sector's old x
    y1 = sector.get('y')    # sector's old y

    # lookup current sector in map schema
    sector_schema = map_schema.query('x1 == ' + x1 + ' & y1 == ' + y1)
    sector.set('x', str(sector_schema.iloc[0]['x2']))
    sector.set('y', str(sector_schema.iloc[0]['y2']))

    # Loop through gate positions (N, S, W, E) and update gates according to map schema
    gate_position = {0: 'gate_n', 1: 'gate_s', 2: 'gate_w', 3: 'gate_e'}
    for gid in gate_position:
        gate = sector.find(".//o[@t='18'][@gid='" + str(gid) + "']")
        
        if gate is not None:  # There is a gate here
            # check if map schema specifies a gate to be here
            if sector_schema.iloc[0][gate_position[gid]] == 0:  # No: Remove this gate
                sector.remove(gate)

            else: #YES: Keep this gate and update coordinates, if needed
                if not gates_default:   # we have a gate schema to verify/update this gate (otherwise move on)
                    # Lookup current sector in map schema
                    lookup_sector = gate_schema_root.find(".//o[@x='" + str(sector_schema.iloc[0]['x2']) + "'][@y='" + str(sector_schema.iloc[0]['y2']) + "']")

                    # then find this gate schema
                    lookup_gate = lookup_sector.find(".//o[@t='18'][@gid='" + str(gid) + "']")

                    # assign schema attributes to current gate
                    gate.attrib = lookup_gate.attrib


        else:  # There is no gate here
            if sector_schema.iloc[0][gate_position[gid]] == 1:  # Yes: Add a gate here
                if gates_default:  # we don't have a gate schema, so just apply default attributes
                    if gid == 0:
                        gate_attrib = {"f" : "1", "t": "18", "s": "0", "x": "0", "y": "0", "z": "25000000", "gid": "0", "gx": str(sector_schema.iloc[0]['x2']), "gy": str(sector_schema.iloc[0]['y2'] + 1), "gtid": "1", "a": "0", "b": "0", "g": "0"}
                    elif gid == 1:
                        gate_attrib = {"f" : "1", "t": "18", "s": "1", "x": "0", "y": "0", "z": "-25000000", "gid": "1", "gx": str(sector_schema.iloc[0]['x2']), "gy": str(sector_schema.iloc[0]['y2'] - 1), "gtid": "0", "a": "32768", "b": "0", "g": "0"}
                    elif gid == 2:
                        gate_attrib = {"f" : "1", "t": "18", "s": "2", "x": "-25000000", "y": "0", "z": "0", "gid": "2", "gx": str(sector_schema.iloc[0]['x2'] - 1), "gy": str(sector_schema.iloc[0]['y2']), "gtid": "3", "a": "16384", "b": "0", "g": "0"}
                    else:
                        gate_attrib = {"f" : "1", "t": "18", "s": "3", "x": "25000000", "y": "0", "z": "0", "gid": "3", "gx": str(sector_schema.iloc[0]['x2'] + 1), "gy": str(sector_schema.iloc[0]['y2']), "gtid": "2", "a": "-16384", "b": "0", "g": "0"}

                    # append gate to current sector
                    ET.SubElement(sector, 'o', gate_attrib)  

                else: # use gate schema
                    # find current sector in gate schema
                    lookup_sector = gate_schema_root.find(".//o[@x='" + str(sector_schema.iloc[0]['x2']) + "'][@y='" + str(sector_schema.iloc[0]['y2']) + "']")

                    # then find this gate element
                    lookup_gate = lookup_sector.find(".//o[@t='18'][@gid='" + str(gid) + "']")

                    # and append gate to current sector
                    ET.SubElement(sector, 'o', lookup_gate.attrib)

# Finally, load new sectors data and append to map
newsectors_tree = ET.parse(args.inputnewsectors)
newsectors_root = newsectors_tree.getroot()
for newsector in newsectors_root:
    newsector_out = ET.SubElement(map_root, 'o', newsector.attrib)
    for child in newsector:
        ET.SubElement(newsector_out, 'o', child.attrib)

export_sorted_map(map_tree)


# TODO: display message to user when gate defaults were used. User will need to verify and adjust gates in X3 Galaxy Editor to fix any positioning/collision issues. The exported galaxy map can then be used to generate a gate schema file for future map updates.