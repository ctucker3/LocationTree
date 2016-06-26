import Location_Tree
import sys
import time
import pandas as pd

# The ./States/cb_2014_us_state_500k.shp and ./Cities/cb_2014_us_cbsa_500k.shp are paths to shape files

US = Location_Tree.LocationTree(8, 8, "./States/cb_2014_us_state_500k.shp", "./Cities/cb_2014_us_cbsa_500k.shp")

df = pd.read_csv('example_data.csv', sep = ',')

df =  df.merge(pd.DataFrame.from_dict(df.apply(lambda row: US.searchcity(row.latitude, row.longitude), axis = 1).values.tolist()), left_index = True, right_index = True)


print df.head()


