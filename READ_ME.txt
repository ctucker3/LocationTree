### README FOR LocationTree ####

The location tree package takes a latitude and a longitude, in that order, and returns the city, state, and zip code when available.

The tree works by defining split points, the split points by latitude and longitude alternate by level. 

The USA is split level by level until the resulting box created by the sequential splits contains the point, and is contained solely
by one geographic shape. 

The shapes are shapefile polygons downloaded from the US TIGER database and are in the folder with the LocationTree script. 

At the moment the algorithm is slower than I would like. While the tree increases splitting efficiency, once the tree can no longer
rule out states based on latitude and longitude splits, and inclusion algorithm must be used to select the state that the point is within. 

The reason the inclusion algorithm is so slow is because it is based on the worst inclusion test possible, the degree test. 
With this test you sum the angles between the point you are testing inclusion of and every point in the surrounding polygon. 
The more granularity the surrounding polygon has the most costly this algorithm is. 

The speed could be reduced greatly by improving this algorithm. 

Another option would be to make more levels in the tree. But this becomes a very intensive process because the number of nodes in the
tree is exponential with the number of levels. 

An example of how to use the tree can be seen by running the example.py script. This loads in some sample data I included and calculates
the location. 

The function Location.searchcity(latitude, longitude) returns a dictionary of {'city':value, 'state':value, 'zip_code':value}. 

The code hasn't been cleaned up yet so there is likely a lot of repeat code blocks. 


