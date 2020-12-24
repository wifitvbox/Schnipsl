import json
import sys
from pprint import pprint

with open(sys.argv[1]) as json_file:
    data = json.load(json_file)
    print(repr(data))