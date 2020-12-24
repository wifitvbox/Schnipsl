#import requests
import json
import sys
import socket
from urlparse import urlparse
import re
import time

MSGLEN=4096

class SimpleSocket:
	"""demonstration class only
	- coded for clarity, not efficiency
	"""

	def __init__(self, sock=None):
		if sock is None:
			self.sock = socket.socket(
							socket.AF_INET, socket.SOCK_STREAM)
		else:
			self.sock = sock
		self.recv=''

	def connect(self, host, port):
		self.sock.connect((host, port))

	def close(self):
		self.sock.close()

	def mysend(self, msg):
		msg=msg.encode()
		total_len=len(msg)
		totalsent = 0
		while totalsent < total_len:
			sent = self.sock.send(msg[totalsent:])
			if sent == 0:
				raise RuntimeError("socket connection broken")
			totalsent = totalsent + sent

	def myreceive(self):
		self.recv=''
		chunks = []
		socket_recv= True
		while socket_recv:
			chunk = self.sock.recv( MSGLEN)
			if chunk == b'': #broken socket
				socket_recv=False
			else:
				chunks.append(chunk.decode())
				if len(chunk)<MSGLEN:
					socket_recv=False # all read
		#return b''.join(chunks)
		self.recv=''.join(chunks)
		recs=self.recv.split('\r\n')
		if not recs:
			return False
		status_elements=recs[0].split()
		if len(status_elements)<2 or not status_elements[1]=='200':
			print('Wrong request answer code',recs[0])
			return False
		return True




	def send_with_params(self, message, param_list):
		for id, value in param_list.items():
			message=message.replace(id,str(value))
		print('request:\n',message)
		self.mysend(message)
		return self.myreceive()

	def getParam(self,key):
		""" Search session id from rtsp strings
		"""
		key=key.lower()
		recs=self.recv.split('\r\n')
		for rec in recs:
			ss=rec.split(' ',2)
			# print ">",ss
			if (ss[0].strip().lower()==key+':'):
				#return int(ss[1].split(";")[0].strip(),16)
				return ss[1]




def getPorts(searchst,st):
  """ Searching port numbers from rtsp strings using regular expressions
  """
  pat=re.compile(searchst+"=\d*-\d*")
  pat2=re.compile('\d+')
  print('findports',searchst,st)
  mstring=pat.findall(st)[0] # matched string .. "client_port=1000-1001"
  nums=pat2.findall(mstring)
  numas=[]
  for num in nums:
    numas.append(int(num))
  return numas


def getLength(st):
  """ Searching "content-length" from rtsp strings using regular expressions
  """
  pat=re.compile("Content-Length: \d*")
  pat2=re.compile('\d+')
  mstring=pat.findall(st)[0] # matched string.. "Content-Length: 614"
  num=int(pat2.findall(mstring)[0])
  return num


def printrec(recst):
  """ Pretty-printing rtsp strings
  """
  recs=recst.split('\r\n')
  for rec in recs:
    print (rec)


def sessionid(recst):
  """ Search session id from rtsp strings
  """
  recs=recst.split('\r\n')
  for rec in recs:
    ss=rec.split()
    # print ">",ss
    if (ss[0].strip()=="Session:"):
      #return int(ss[1].split(";")[0].strip(),16)
      return ss[1].split(";")[0].strip()


def setsesid(recst,idn):
  """ Sets session id in an rtsp string
  """
  return recst.replace("SESID",str(idn))



def main():

	if not len(sys.argv)==1:
		print('''
Usage: kodi_play_satip satip-Url
example: kodi_play_satip 'rtsp://192.168.1.99:554/?src=1&freq=12188&pol=h&ro=0.35&msys=dvbs&mtype=qpsk&plts=off&sr=27500&fec=34&pids=0,17,18,167,136,47,71'
		''')
		sys.exit()

	#satip_url=sys.argv[1]
	cseq=0
	# Das ERSTE HD
	satip_url='rtsp://192.168.1.99:554/?src=1&freq=11494&pol=h&ro=0.35&msys=dvbs2&mtype=8psk&plts=on&sr=22000&fec=23&pids=0,17,18,5100,5101,5102,5104'
	# 3SAT HD
	#satip_url='rtsp://192.168.1.99:554/?src=1&freq=11347&pol=v&ro=0.35&msys=dvbs2&mtype=8psk&plts=on&sr=22000&fec=23&pids=0,17,18,6500,6510,6520,6530'
	satip_url_object=urlparse(satip_url)

	sat_ip_socket=SimpleSocket()
	sat_ip_socket.connect(satip_url_object.hostname,satip_url_object.port)
	clientports=[60784,60785] # the client ports we are going to use for receiving video
	#setu="SETUP "+adr+" RTSP/1.0\r\nCSeq: 0\r\nUser-Agent: python\r\nTransport: RTP/AVP;unicast;client_port="+str(clientports[0])+"-"+str(clientports[1])+"\r\n\r\n"

	if not sat_ip_socket.send_with_params(
		"SETUP SATIP_URL RTSP/1.0\r\nCSeq: SEQUENCE\r\nUser-Agent: python\r\nTransport: RTP/AVP;unicast;client_port=LOWPORT-HIGHPORT\r\n\r\n",
		#"SETUP SATIP_URL RTSP/1.0\r\nCSeq: SEQUENCE\r\nUser-Agent: python\r\nTransport: RTP/AVP;multicast;destination=DEST_IP;client_port=LOWPORT-HIGHPORT\r\n\r\n",
		#"SETUP SATIP_URL RTSP/1.0\r\nCSeq: SEQUENCE\r\nUser-Agent: python\r\nTransport: RTP/AVP;multicast;client_port=LOWPORT-HIGHPORT\r\n\r\n",
		{
			'SATIP_URL': satip_url,
			'SEQUENCE':cseq,
			'DEST_IP':'192.168.1.127',
			'LOWPORT':clientports[0],
			'HIGHPORT':clientports[1]
		}
	):
		print('cant send SETUP commmand')
		sys.exit(0)

	printrec(sat_ip_socket.recv)
	#for unicast, use 
	# clientports=getPorts("client_port",sat_ip_socket.recv)
	# for multicast, use
	clientports=getPorts("port",sat_ip_socket.recv)
	sesid=sat_ip_socket.getParam('Session').split(';')[0]
	stream_id=sat_ip_socket.getParam('com.ses.streamID')
	transport=sat_ip_socket.getParam('Transport')
	transport_elements=transport.split(';')
	multicast_ip=''
	for transport_element in transport_elements:
		key_values=transport_element.split('=',2)
		if "destination"==key_values[0].lower():
			multicast_ip=key_values[1]
	#play="PLAY rtsp://"+ip+":554/stream=1 RTSP/1.0\r\nCSeq: 1\r\nUser-Agent: python\r\nSession: SESID\r\n\r\n"

	cseq+=1
	if not sat_ip_socket.send_with_params(
		"PLAY rtsp://SATIP_NETLOC/stream=STREAM_ID RTSP/1.0\r\nCSeq: SEQUENCE\r\nUser-Agent: python\r\nSession: SESID\r\n\r\n",
		{
			'SATIP_NETLOC': satip_url_object.netloc,
			'STREAM_ID':stream_id,
			'SEQUENCE':cseq,
			'SESID':sesid
		}
	):
		print('cant send play commmand')
		sys.exit(0)

	printrec(sat_ip_socket.recv)

	kodi_url = "http://192.168.1.127:8080/jsonrpc"
	#url = "http://kodiwohnzimmer.fritz.box:8080/jsonrpc"
	#url = "http://kodi-wohnzimmer.fritz.box:8080/jsonrpc"
	#url = "http://192.168.2.30:8080/jsonrpc"
	#url = "http://192.168.1.94:8080/jsonrpc"

	# Example echo method
	kodi_udp_url='udp://'+satip_url_object.hostname+':'+str(clientports[0])
	kodi_udp_url='udp://@0.0.0.0:'+str(clientports[0])
	kodi_udp_url='rtp://@'+multicast_ip+':'+str(clientports[0])

	print('kodi_udp_url',kodi_udp_url)
	if False:
		payload ={"jsonrpc":"2.0", "id":1, "method": "Player.Open", "params":{"item":{"file":kodi_udp_url}}}
		response = requests.post(kodi_url, json=payload).json()
		print(response)
	else:
		client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server_address = ('127.0.0.1', 8080)
		client_socket.connect(server_address)
		jsonstr='{"jsonrpc": "2.0", "id": 1, "method": "Player.Open", "params": {"item": {"file": "rtp://@192.168.1.127:60784"}}}'
		request_header='''\
POST /jsonrpc HTTP/1.1\r
Host: 127.0.0.1:8080\r
User-Agent: schnipsl\r
Accept-Encoding: gzip, deflate\r
Accept: */*\r
Connection: close\r
Content-Length: '''+str(len(jsonstr))+'''\r
Content-Type: application/json\r
\r
'''+jsonstr
		client_socket.send(request_header)
		print request_header
		response = ''
		while True:
	    		recv = client_socket.recv(1024)
			print recv
	    		if not recv:
	        		break
	    		response += recv

		print response
		client_socket.close()

	ticks = 10
	while ticks:
		ticks -=1
		time.sleep(45)
		sat_ip_socket.send_with_params(
			"OPTIONS rtsp://SATIP_NETLOC/ RTSP/1.0\r\nCSeq: SEQUENCE\r\nUser-Agent: python\r\nSession: SESID\r\n\r\n",
			{
				'SATIP_NETLOC': satip_url_object.netloc,
				'SEQUENCE':cseq,
				'SESID':sesid
			}
		)

	sat_ip_socket.close()

if __name__ == "__main__":
	main()

