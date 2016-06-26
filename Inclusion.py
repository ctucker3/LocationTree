# This is the polygon inclusion algorithm 
# Adapted from C found on the website http://paulbourke.net/geometry/polygonmesh/

# Order does matter

import numpy as np

'''test1 = [ [0,0], [4,0], [4,-4], [0,-4] ] 
test1 = np.asarray(test1)
test2 = [ [0,0], [3,0], [3,-2], [4,-2], [4,-4], [3,-4], [0,-4] ]
test2 = np.asarray(test2)
test3 = [ [0,0], [4,-4], [0,0] ] 
test3 = np.asarray(test3)'''

# This function takes the points of polygon and tests if the point 
# in that polygon. All points should be x,y. Both should be numpy
# data structures. 

def InsidePolygon(polygon, point):
	
	n = len(polygon)
	angle = 0.0

	for i in range(0, n):
		#print polygon[i]
		#print polygon[((i+1) % n)]
		#print point
		p1 = polygon[i] - point
		p2 = polygon[((i+1) % n)] - point
		angle += Angle(p1,p2)
	if np.absolute(angle) < np.pi:
		return False
	else:
		return True

def Angle(d1,d2):
	#print d1
	#print d2
	theta1 = np.arctan2(d1[0],d1[1])
	#print theta1
	theta2 = np.arctan2(d2[0],d2[1])
	#print theta2
	dtheta = theta2 - theta1
	#print dtheta

	while dtheta > np.pi:
		dtheta -= 2*np.pi
	while dtheta < -np.pi:
		dtheta += 2*np.pi

	return dtheta




			
