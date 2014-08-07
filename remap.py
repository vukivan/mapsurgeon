import xml.etree.ElementTree as ET
# TODO: command line arguments for original x3, new x3 and instructions
tree = ET.parse('x3_universe_LUV.xml')
root = tree.getroot()

def findSector (x,y):
	print 'Searching for sector ' + str(x) + ',' + str(y)
	for child in root:
		if child.get('x') == str(x) and child.get('y') == str(y):
			print 'Found sector ' + child.get('x'), child.get('y')
			return child

def switchSector (x1, y1, x2, y2):

	firstSector = None
	secondSector = None
	
	firstSector = findSector(x1,y1)
	secondSector = findSector(x2,y2)
			
	if (firstSector is not None):
		firstSector.set('x', str(x2))
		firstSector.set('y', str(y2))
		print 'First sector is now at ' + firstSector.get('x'), firstSector.get('y')
	if (secondSector is not None):
		secondSector.set('x', str(x1))
		secondSector.set('y', str(y1))
		print 'Second sector is now at ' + secondSector.get('x'), secondSector.get('y')
	
def moveSector (x1,y1,x2,y2):
	switchSector (x1,y1,x2,y2)
	
def write():	
	tree.write('x3_temp_out.xml')

#may have to check for subtype (determines if NSWE)
#alternative is to change both gid and subtype during rotation
def disconnectGate (x,y,gid,twoway):
	sector = findSector (x,y)
	for obj in sector.iter ('o'):
		if obj.get ('t')  == '18' and obj.get('gid') == str(gid):
			print 'Found a gate with gid=' + obj.get('gid') + ' gx=' + \
			obj.get('gx') + ' gy=' + obj.get('gy') + ' gtid=' + obj.get('gtid') 
			gx = obj.get('gx')
			gy = obj.get('gy')
			gtid = obj.get('gtid')
			obj.set('gx','0')
			obj.set('gy','0')
			obj.set('gtid','0')
			if twoway:
				disconnectGate (gx,gy,gtid,0)					

def disconnectSector (x,y):
	sector = findSector (x,y)
	for obj in sector.iter ('o'):
		if obj.get('t') == '18':
			disconnectGate (x,y,obj.get('gid'),1)
			
def reconnectGate(x,y,gid,gx,gy,gtid,twoway):
	sector = findSector (x,y)
	for obj in sector.iter ('o'):
		if obj.get('t') == '18' and obj.get('gid') == str(gid):
			print 'Found a gate with gid=' + obj.get('gid') + ' gx=' + \
			obj.get('gx') + ' gy=' + obj.get('gy') + ' gtid=' + obj.get('gtid')
			obj.set('gx', str(gx))
			obj.set('gy', str(gy))
			obj.set('gtid', str(gtid))
			if twoway:
				reconnectGate (gx,gy,gtid,x,y,gid,0)

# for t=18 change both gid and subtype during rotation but don't rotate object
# everything else needs to be rotated		
def rotateSector (x,y):
	sector = findSector (x,y)
	for obj in sector.iter ('o'):
		if obj.get('t') == '18' or \
		   obj.get('t') == '17' or \
		   obj.get('t') == '20' or \
		   (obj.get('t') == '6'  and obj.get('x') is not None) or \
		   (obj.get('t') == '5'  and obj.get('x') is not None):
			print 'Object type=' + obj.get('t') + ' X,Y,Z ' + obj.get('x') + ' ' \
			 + obj.get('y') + ' ' + obj.get('z') + ' a,b,g ' + obj.get('a') + ' ' \
			 + obj.get('b') + ' ' + obj.get('g')
		if obj.get('t') == '3' or \
			obj.get('t') == '4' or \
			(obj.get('t') == '7' and obj.get('x') is not None):
			print 'Object type=' + obj.get('t') + ' X,Y,Z ' + obj.get('x') + ' ' \
			 + obj.get('y') + ' ' + obj.get('z')

#test procedures
#TODO: instructions parser
#switchSector (3,1,4,1)
#moveSector (0,0, 50,50)
#disconnectSector (1,2)
#disconnectGate (1,2,0,1)
#reconnectGate (1,2,0,1,1,1,1)
rotateSector(1,3)
write()

