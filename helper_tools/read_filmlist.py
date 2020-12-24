# sudo apt install libyajl-dev 
# sudo pip3 install jsonslicer

import sys

from jsonslicer import JsonSlicer

# Iterate over collection(s) by using wildcards in the path:
with open(sys.argv[1]) as data:
	for liste in JsonSlicer(data, ('X'), path_mode='map_keys'):
		print(liste[1][2])

