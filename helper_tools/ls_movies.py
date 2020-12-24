from os import listdir
from os.path import isfile, join
import sys
import base64


from datetime import datetime

def base64_decode(string):
	"""
	Adds back in the required padding before decoding.
	"""
	padding = 4 - (len(string) % 4)
	string = string + ("=" * padding)
	return base64.urlsafe_b64decode(string).decode()


onlyfiles = [f for f in listdir(sys.argv[1]) if isfile(join(sys.argv[1], f))]
for fn in onlyfiles:
	try:
				
		uri = base64_decode(fn.split('.')[0])
		uri_elements= uri.split(':')
		time_stamp=int(uri_elements[2])
		date = datetime.fromtimestamp(time_stamp)
		date_time = date.strftime("%d.%m.%Y %H:%M")
		print('\t'.join(uri_elements)+'\t'+date_time)	

	except:
		pass 
	base64_decode(fn.split('.')[0])

