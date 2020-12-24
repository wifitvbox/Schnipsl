import sys
import json
from datetime import datetime

lastEnd=0
with open(sys.argv[1]) as json_file:
	data = json.load(json_file)
	times=sorted(list(data['details']))
	for time in times:
		p=data['details'][time]
		print('{0} {1} {2}-{3}'.format( 
			datetime.utcfromtimestamp(p['unixTimeBegin']).strftime('%Y-%m-%d %H:%M'),
			datetime.utcfromtimestamp(p['unixTimeEnd']-p['unixTimeBegin']).strftime('%H:%M'),
			p['name'],
			p['title']
		)
		)
		if lastEnd != p['unixTimeBegin']:
			print('--------------------')
		lastEnd=p['unixTimeEnd']

