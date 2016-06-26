# This is a tree method for finding the points in cities. The states will come with the cities. Also should have a method to just find the states. 

import shapefile
import numpy as np
import os
import Inclusion as incl

class Coornode:

	def __init__(self, level, lat_range, long_range):
		
		if level%2 != 0:		# Odd tree levels splot on the longitude, evens split on the latitudes. 
			
			self.split = "Longitude"
			self.splitpoint = long_range[0] + ((long_range[1] - long_range[0])/2)
		else:
			
			self.split = "Latitude"
			self.splitpoint = lat_range[0] + ((lat_range[1] - lat_range[0])/2)

		self.children = []

		self.lat = lat_range
		self.long = long_range
		self.identity = "Coornode"
		self.parent = None
		self.level = level
		self.states = []
		
	def updatestates(self,states):
		if len(states) == 0:
			self.states = None
		else:
			self.states = states

	def addparent(self, parent):

		self.parent = parent 

	def addchild(self, child):

		self.children.append(child)

	def getchild(self, index):

		return self.children[index] 

class LandmarkNode:		# Node that signals 

	def __init__(self, level, states):

		if len(states) == 0:
			self.states = []
		else:
			self.states = states

		self.identity = "LandmarkNode"
		self.level = level
		self.children = []

	def addchild(self, child):
		
		self.children.append(child)

	def addparent(self, parent):

		self.parent = parent 

class LocationTree:

	def __init__(self, des_city_levels, des_state_levels, state_shapefile = "cb_2014_us_state_500k.shp", city_shapefile = "cb_2014_us_cbsa_500k.shp"):

		self.poly_city, self.city_info = self.extract_cities(city_shapefile)
		self.poly_state = self.extract_states(state_shapefile)
		self.cityroot = Coornode(1, (24.396308, 49.384358), (-124.848974, -66.885444))		# Bounding box of the US
		self.unresolved_nodes = [self.cityroot]
		self.cityroot.updatestates(self.poly_city.keys())
		self.levels = 1
		self.nodes = [self.cityroot]		# Good for trouble shoot and seeing things about your tree. 

		self.stateroot = Coornode(1, (24.396308, 49.384358), (-124.848974, -66.885444))		# Bounding box of the US
		self.unresolved_statenodes = [self.stateroot]
		self.statelevels = 1
		self.statenodes = [self.stateroot]
		self.stateroot.updatestates(self.poly_state.keys())
		
		self.buildcitytree(des_city_levels)	
		print "Done Constructing City Tree"	
		self.buildstatetree(des_state_levels)		# Build the tree when objected is initiated. 
		print "Done Constructing State Tree"
			

	def update_levels(self, levels):
		self.levels = levels

	def updateroot(self, root):
		self.root = root

	def extract_cities(self,city_shapefile):

		city_info = {}
		city_dict = {}
		sf = shapefile.Reader(rel_path(city_shapefile))
		shaperecs = sf.shapeRecords()
		for record in shaperecs:
			
			city_info[record.record[4].split(', ')[0]] = (record.record[4].split(', ')[1], record.record[3])		# [:2] to cut off other states	# Tuple of the state and zip code. 
			city_dict[record.record[4].split(', ')[0]] = np.asarray(record.shape.points)		# the key is the name of the city
			
		return city_dict, city_info
		
		
	def extract_states(self,state_shapefile):

		state_dict = {}
		sf = shapefile.Reader(rel_path(state_shapefile))
		shaperecs = sf.shapeRecords()
		for record in shaperecs:
			
			state_dict[record.record[4]] = np.asarray(record.shape.points)

		return state_dict


	def split_itcity(self,currnode, des_levels):

		latt_split = 0
		long_split = 0
		currlat_range = currnode.lat
		currlong_range = currnode.long
		if currnode.split == "Latitude":		# Split on latitude. 
	
			latt_split = (currlat_range[1] - currlat_range[0])/2		# Space between ranges. 
	
		else:
	
			long_split = (currlong_range[1] - currlong_range[0])/2		# Space between ranges. 

		intersecting = []
		num_inter =0

		# First check for less than the split point and generate the left child node. 
		less_split_lat = (currlat_range[0], currlat_range[1]-latt_split)
		less_split_long = (currlong_range[0], currlong_range[1] - long_split)

		for key in currnode.states:  # No more cities are going to be added with reduction. 
			
			if self.intersect(self.poly_city[key], less_split_lat, less_split_long):
		
				intersecting.append(key)
				num_inter += 1

		if num_inter <= 1 or currnode.level == des_levels - 1:			# Means only one state intersects or we have found a grid space that has no city in it or that we reach the desired depth. 
			#print intersecting
			newleftnode = LandmarkNode(currnode.level + 1, intersecting)
			newleftnode.addparent(currnode)
			currnode.addchild(newleftnode)
			if currnode.level < des_levels - 1:
				self.unresolved_nodes.append(newleftnode)

		else:
			newleftnode = Coornode(currnode.level + 1, (currlat_range[0], currlat_range[1] - latt_split), (currlong_range[0], currlong_range[1] - long_split))
			newleftnode.addparent(currnode)
			#print newleftnode.lat, newleftnode.long
			currnode.addchild(newleftnode)
			newleftnode.updatestates(intersecting)			# Reduces the cities to test for intersection later. 
			self.unresolved_nodes.append(newleftnode)		# Add this to be processed later. (Next since depth first). 
	

		#print prevleft
		#print intersecting
		prevleft = list(intersecting)
		#print prevleft
		intersecting = [] 
		num_inter = 0

		# Now check for the more split point (right child)
		more_split_lat = (currlat_range[0]+latt_split, currlat_range[1])
		more_split_long = (currlong_range[0]+ long_split, currlong_range[1] )

		for key in currnode.states:		
	
			if self.intersect(self.poly_city[key], more_split_lat, more_split_long):
		
				intersecting.append(key)
				num_inter += 1

		if num_inter <= 1 or currnode.level == des_levels - 1:			# Means only one state intersects or we have found a grid space that has no city in it.	
			#print intersecting
			newrightnode = LandmarkNode(currnode.level + 1, intersecting)
			currnode.addchild(newrightnode)
			if currnode.level < des_levels - 1:
				self.unresolved_nodes.append(newrightnode)

		else:
			newrightnode = Coornode(currnode.level + 1, (currlat_range[0] + latt_split, currlat_range[1]), (currlong_range[0] + long_split, currlong_range[1]))
			#print newrightnode.lat, newrightnode.long
			currnode.addchild(newrightnode)
			newrightnode.updatestates(intersecting)
			self.unresolved_nodes.append(newrightnode)
	
		if newrightnode.level > self.levels:
			self.levels = newrightnode.level

		self.nodes.append(newleftnode)
		self.nodes.append(newrightnode)
		

	def buildcitytree(self, des_levels):			# Recursively builds the trees with the lead nodes being single state nodes. 						# Could be done in a while loop. 
						# Optional inputs are to check for unresolvable border conflicts. 	
		
		while self.levels < des_levels or len(self.unresolved_nodes) != 0 and self.levels < des_levels: 
			#print len(self.unresolved_nodes)
			currnode = self.unresolved_nodes.pop(0)		# Get the last item on the list and do another run through.
			if len(currnode.children) > 2:
					print len(node.children)
			#print self.levels

			if currnode.identity == "LandmarkNode":						# This is simpy to make indexing easier when reloading the tree. 
				newleftchild = LandmarkNode(currnode.level + 1, [])
				newrightchild = LandmarkNode(currnode.level + 1, [])
				currnode.addchild(newleftchild)
				currnode.addchild(newrightchild)
				self.unresolved_nodes.append(newleftchild)
				self.unresolved_nodes.append(newrightchild)									
				self.nodes.append(newleftchild)
				self.nodes.append(newrightchild)

			elif currnode.identity != "LandmarkNode":			# None of this analysis should be done for LandmarkNodes
				self.split_itcity(currnode, des_levels)
		else:
			count = 0
			while len(self.unresolved_nodes) != 0:			# Finish off the last level
				node = self.unresolved_nodes.pop(0)
				
				if node.level == des_levels:
					continue
				#print self.levels
				#print len(self.unresolved_nodes)
				if node.identity == "LandmarkNode":						# This is simpy to make indexing easier when reloading the tree. 
					
					newleftchild = LandmarkNode(currnode.level + 1, [])
					newrightchild = LandmarkNode(currnode.level + 1, [])
					node.addchild(newleftchild)
					node.addchild(newrightchild)
					self.nodes.append(newleftchild)
					self.nodes.append(newrightchild)
				
				else:
					
					self.split_itcity(node,des_levels)

		return			# If we get to this point everything has been fully resolved. 



	def split_itstate(self,currnode, des_levels):

		latt_split = 0
		long_split = 0
		currlat_range = currnode.lat
		currlong_range = currnode.long
		if currnode.split == "Latitude":		# Split on latitude. 
	
			latt_split = (currlat_range[1] - currlat_range[0])/2		# Space between ranges. 
	
		else:
	
			long_split = (currlong_range[1] - currlong_range[0])/2		# Space between ranges. 

		intersecting = []
		num_inter =0

		# First check for less than the split point and generate the left child node. 
		less_split_lat = (currlat_range[0], currlat_range[1]-latt_split)
		less_split_long = (currlong_range[0], currlong_range[1] - long_split)

		for key in currnode.states:  # No more cities are going to be added with reduction. 
			
			if self.intersect(self.poly_state[key], less_split_lat, less_split_long):
		
				intersecting.append(key)
				num_inter += 1

		if num_inter <= 1 or currnode.level == des_levels - 1:			# Means only one state intersects or we have found a grid space that has no city in it or that we reach the desired depth. 
			#print intersecting
			newleftnode = LandmarkNode(currnode.level + 1, intersecting)
			newleftnode.addparent(currnode)
			currnode.addchild(newleftnode)
			if currnode.level < des_levels - 1:
				self.unresolved_statenodes.append(newleftnode)

		else:
			newleftnode = Coornode(currnode.level + 1, (currlat_range[0], currlat_range[1] - latt_split), (currlong_range[0], currlong_range[1] - long_split))
			newleftnode.addparent(currnode)
			#print newleftnode.lat, newleftnode.long
			currnode.addchild(newleftnode)
			newleftnode.updatestates(intersecting)			# Reduces the cities to test for intersection later. 
			self.unresolved_statenodes.append(newleftnode)		# Add this to be processed later. (Next since depth first). 
	
		intersecting = [] 
		num_inter = 0

		# Now check for the more split point (right child)
		more_split_lat = (currlat_range[0]+latt_split, currlat_range[1])
		more_split_long = (currlong_range[0]+ long_split, currlong_range[1] )

		for key in currnode.states:		
	
			if self.intersect(self.poly_state[key], more_split_lat, more_split_long):
		
				intersecting.append(key)
				num_inter += 1

		if num_inter <= 1 or currnode.level == des_levels - 1:			# Means only one state intersects or we have found a grid space that has no city in it.	
			#print intersecting
			newrightnode = LandmarkNode(currnode.level + 1, intersecting)
			currnode.addchild(newrightnode)
			if currnode.level < des_levels - 1:
				self.unresolved_statenodes.append(newrightnode)

		else:
			newrightnode = Coornode(currnode.level + 1, (currlat_range[0] + latt_split, currlat_range[1]), (currlong_range[0] + long_split, currlong_range[1]))
			#print newrightnode.lat, newrightnode.long
			currnode.addchild(newrightnode)
			newrightnode.updatestates(intersecting)
			self.unresolved_statenodes.append(newrightnode)
	
		if newrightnode.level > self.statelevels:
			self.statelevels = newrightnode.level

		self.statenodes.append(newleftnode)
		self.statenodes.append(newrightnode)

	def buildstatetree(self, des_levels):
		
		while self.statelevels < des_levels or len(self.unresolved_statenodes) != 0 and self.statelevels < des_levels:
			#print len(self.unresolved_statenodes)
			currnode = self.unresolved_statenodes.pop(0)		# Get the last item on the list and do another run through.
			#print self.statelevels

			if currnode.identity == "LandmarkNode":						# This is simpy to make indexing easier when reloading the tree. 
				newleftchild = LandmarkNode(currnode.level + 1, [])
				newrightchild = LandmarkNode(currnode.level + 1, [])
				currnode.addchild(newleftchild)
				currnode.addchild(newrightchild)
				self.unresolved_statenodes.append(newleftchild)
				self.unresolved_statenodes.append(newrightchild)									
				self.statenodes.append(newleftchild)
				self.statenodes.append(newrightchild)

			if currnode.identity != "LandmarkNode":			# None of this analysis should be done for LandmarkNodes
				self.split_itstate(currnode, des_levels)
		else:
			while len(self.unresolved_statenodes) != 0:			# Finish off the last level
				node = self.unresolved_statenodes.pop(0)
				if node.level == des_levels:
					continue
				#print self.statelevels
				#print len(self.unresolved_statenodes)
				if node.identity == "LandmarkNode":						# This is simpy to make indexing easier when reloading the tree. 
					newleftchild = LandmarkNode(currnode.level + 1, [])
					newrightchild = LandmarkNode(currnode.level + 1, [])
					node.addchild(newleftchild)
					node.addchild(newrightchild)
					self.statenodes.append(newleftchild)
					self.statenodes.append(newrightchild)
				
				else:
					self.split_itstate(node,des_levels)
		
		
			
	def searchcity(self,coorlat, coorlong):		# No need for recursion here, while loop will do fine. !!!!!!!!!!!!!!!!!! Hasn't been test !!!!!!!!!!!!!!!!!!!!!!

		currnode = self.cityroot		# Start at the root. 

		while currnode.identity != "LandmarkNode":
			
			if currnode.split == "Latitude":
				if coorlat <= currnode.splitpoint:
					currnode = currnode.children[0]		# Get the left child
				else:
					currnode = currnode.children[1]		# Get the right child

			else:
				if coorlong <= currnode.splitpoint:
					currnode = currnode.children[0]		# Get the left child
				else:
					currnode = currnode.children[1]		# Get the right child

		else:		# We have run into a landmark node
		
			if len(currnode.states) > 1:
				
				for place in currnode.states:	 # Run inclusion algorithm

					if incl.InsidePolygon(np.asarray(self.poly_city[place]), np.array([coorlong, coorlat])):
						return {'city':place, 'state':self.city_info[place][0], 'zip':self.city_info[place][1]}

				# The box was too big for all of these cities, Find the state
				return self.searchstate(coorlat,coorlong)

			else:
				if len(currnode.states) == 0:		# Test for the state
					return self.searchstate(coorlat,coorlong)
				else:

					if incl.InsidePolygon(np.asarray(self.poly_city[currnode.states[0]]), np.array([coorlong, coorlat])):	# Return the information about the city, state, zip. 
						return {'city':currnode.states[0], 'state':self.city_info[currnode.states[0]][0], 'zip':self.city_info[currnode.states[0]][1]}

					else:	# Our box was too big for this point and the point is not in a city	
						return self.searchstate(coorlat,coorlong)
				
	def searchstate(self, coorlat, coorlong):

		currnode = self.stateroot

		while currnode.identity != "LandmarkNode":
			
			if currnode.split == "Latitude":
				if coorlat <= currnode.splitpoint:
					currnode = currnode.children[0]		# Get the left child
				else:
					currnode = currnode.children[1]		# Get the right child

			else:
				if coorlong <= currnode.splitpoint:
					currnode = currnode.children[0]		# Get the left child
				else:
					currnode = currnode.children[1]		# Get the right child

		else:
			if len(currnode.states) > 1:
				
				for place in currnode.states:	 # Run inclusion algorithm
					
					if incl.InsidePolygon(self.poly_state[place], np.array([coorlong, coorlat])):
						
						return {'city':'n/a', 'state':place, 'zip':'n/a'}			# We dont have this info if just finding state

							# Noise with the data and no state found for this. 
				return {'city':'n/a', 'state':'n/a', 'zip':'n/a'}

			else:
				if len(currnode.states) == 0:

					return {'city':'n/a', 'state':'n/a', 'zip':'n/a'}

				if len(currnode.states) == 1:	# Check to make sure it fits. 
#	incl.InsidePolygon(np.asarray(self.poly_state[currnode.states[0]]), np.array([coorlat, coorlong]))
					
					return {'city':'n/a', 'state':currnode.states[0], 'zip':'n/a'}

				else:	# Something is wrong with the data and it is not in a state

						return {'city':'n/a', 'state':'n/a', 'zip':'n/a'}


	def intersect(self,polygon, lat_range, long_range):			# Finds if a polygon intersects with the lat-long box
		
		# First find that the latitude intersects atleast somepoints. 
		lat_check = False
		long_check = False
		up_side = False
		down_side = False
		for row in polygon:	
			
			if up_side == True and down_side == True:

				lat_check = True
				break

			if lat_range[0] >= row[1]:
				
				up_side = True

			if lat_range[0] <= row[1]:

				down_side = True

			if lat_range[1] >= row[1]:

				up_side = True

			if lat_range[1] <= row[1]:

				down_side = True

		if up_side == True and down_side == True:
			lat_check = True


		right_side = False
		left_side = False
		for row in polygon:		# If false both sides will be on the right side or both lines will be on the left side of the polygon. 
			
			if right_side == True and left_side == True:

				long_check = True
				break

			if long_range[0] >= row[0]:
				
				right_side = True

			if long_range[0] <= row[0]:

				left_side = True

			if long_range[1] >= row[0]:

				right_side = True

			if long_range[1] <= row[0]:

				left_side = True
	
		if right_side == True and left_side == True:
			long_check = True
		
		if lat_check == True and long_check == True:
			return True

		else:
			
			return False		# Our tests have failed and there is no intersection. 

	def writetocsv(self, filepath):	# Based off the idea that when indexing the children of binary trees are at indices, n*2 and n*2 +1
							
		currnode = self.root

		with open(filepath, 'wb') as csv:

			writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
			
			index_end = 3
			curr_index = 0
			while len(currnode.children) != 0 and curr_index == index_end: 

				if currnode.identity == "Coornode":

					writer.writerow(["Coornode", currnode.level, str(currnode.lat[0]), str(currnode.lat[1]), str(currnode.long[0]), str(currnode.long[1])])
					left2do.append(currnode.children[0])
					left2do.append(currnode.children[1])

				elif currnode.identity == "LandmarkNode":

					states = currnode.states.insert(0, "LandmarkNode")
					states.insert(1,currnode.level)
					writer.writerow(states)

				currnode = left2do.pop(0)
				curr_index += 1

				if curr_index == index_end:
					index_end = (index_end*2) + 1


def rel_path(filename):
    #Return the path of this filename relative to the current script. Code is taken from 
    
    return os.path.join(os.getcwd(), os.path.dirname(__file__), filename)

