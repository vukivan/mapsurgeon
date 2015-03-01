X3 Map Surgeon
==============

This is a Python utility for performing "plastic surgery" on the galaxy map in [Egosoft's X3](http://www.egosoft.com/) videogame series. It was designed specifically to simplify updating a custom map for new versions of the X3 overhaul [Litcube's Universe](https://code.google.com/p/litcubesuniverse/wiki/Index), which is based on **X3: Albion Prelude**. However, this utility will also work for vanilla versions of **X3:AP**, **X3: Terran Conflict**, and possibly **X3: Reunion**.

*Map Surgeon* consists of two commandline utilities, plus a set of input files, referred to as Schemas, which instruct *Map Surgeon* on what changes to make to the galaxy map.

*remap.py* is the program that performs the map surgery.

    usage: python remap.py [-h] -m INPUTMAP -s INPUTSCHEMA -n INPUTNEWSECTORS [-g INPUTGATES] -o OUTPUT 

*remap.py* accepts commandline arguments for 3 Required, plus a 4th optional but Recommended, input files, and the output filename for the new galaxy map.

* INPUTMAP - the original galaxy map to be altered (X3 vanilla name: x3universe.xml)
* INPUTSCHEMA - the Remap Schema CSV file that specifies what sectors are to be removed (if any), new sectors to be added, and the new coordinates for all map sectors (currently: remap_schema.csv)
* INPUTNEWSECTORS - an XML file that holds all new sectors and their contents to be added to the galaxy (currently: newsectors.xml)
* (RECOMMENDED) INPUTGATES - the XML Gate Schema that specifies all gate position and orientation coordinates for all sectors in the new map.
* OUTPUT - the filename for the new galaxy map to be generated

*gen_schema.py* is a helper utility used to auto-generate the INPUTSCHEMA and INPUTGATES schema files from an exemplar galaxy map. Because fine-tuning a new galaxy map (placing sector objects, positioning gates, etc.) typically requires working in the X3 Galaxy Editor, creating the initial version of a new map for the game has to be completed before this utility is fully useful. With a final draft of the galaxy map on hand, you can input it into *gen_schema.py* to generate the New Sectors Schema and the Gates Schema files.

The master Remap Schema which specifies all major changes to the map (sector removals, additions, new coordinates, and gate cardinal positions) is edited via the included Excel spreadsheet "Remap Schema.xlsx".

**TODO (2015-03-01) ndr:** Now thinking about it, I might actually add a third output function to create the master Remap Schema file too, by comparing the vanilla map with the the new master map. But the advatage of using the Excel spreadsheet to generate the Remap Schema is that you can work on the map layout outside of the game.

Once the schema files are generated for your map, future updates of the map will just require re-running *remap.py* with updated versions of the original map, and an updated remap will be created. Specific changes in the original game map still require monitoring in case, one or more of the schemas need to be updated also.

Additional files often have to be edited for a new galaxy map, and the *Map Surgeon* package does not currently alter any of those other files (Jobs.txt, etc.)

##Example Usage
Generate New Sectors Schema:

    python gen_schema.py -i maps/x3_universe_LUV.xml -s schemas/remap_schema.csv -n schemas/new_sectors.xml

Generate Gate Schema:

    python gen_schema.py -i maps/x3_universe_LUV.xml -s schemas/remap_schema.csv -g schemas/gate_schema.xml


Generate Both Schemas:

    python gen_schema.py -i maps/x3_universe_LUV.xml -s schemas/remap_schema.csv -g schemas/gate_schema.xml -n schemas/new_sectors.xml

Generate New Map:

    python remap.py -m maps/x3_universe_LUV.xml -s schemas/remap_schema.csv -n schemas/newsectors.xml -g schemas/gate_schema.xml -o maps/x3_universe_out.xml

