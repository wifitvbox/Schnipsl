import xbmc
import xbmcaddon
import xbmcgui
import sys

import json

import socket
from urlparse import urlparse
import re
import time
import base64

class XBMCPlayer( xbmc.Player ):

	def __init__( self, *args, **kwargs ):
		super(XBMCPlayer,self).__init__(*args, **kwargs )
		self.run_flag=True

	def onAVStarted( self ):
		# Will be called when xbmc starts playing a file
		xbmc.log( "Schnipsl: AV Started" ,level=xbmc.LOGNOTICE)

	def onPlayBackStarted( self ):
		# Will be called when xbmc starts playing a file
		xbmc.log( "Schnipsl: Playback Started" ,level=xbmc.LOGNOTICE)
		url=self.getPlayingFile()
		if url:
			url_elements=urlparse(url)
			xbmc.log( "Schnipsl: file url scheme:"+url_elements.scheme ,level=xbmc.LOGNOTICE)
		

	def onPlayBackEnded( self ):
		# Will be called when xbmc stops playing a file
		xbmc.log( "Schnipsl: Playback Stopped" ,level=xbmc.LOGNOTICE)
		self.run_flag = False

	def onPlayBackStopped( self ):
		# Will be called when user stops xbmc playing a file
		xbmc.log( "Schnipsl: Playback Stopped" ,level=xbmc.LOGNOTICE)
		self.run_flag = False

	def onPlayBackError( self ):
		# Will be called when a errors tops xbmc playing a file
		xbmc.log( "Schnipsl: Playback Error" ,level=xbmc.LOGNOTICE)
		self.run_flag = False


MSGLEN=4096

class SatIPSocket:
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
		self.recv=''.join(chunks)
		recs=self.recv.split('\r\n')
		if not recs:
			return False
		status_elements=recs[0].split()
		if len(status_elements)<2 or not status_elements[1]=='200':
			#print('Wrong request answer code',recs[0])
			return False
		return True




	def send_with_params(self, message, param_list):
		for id, value in param_list.items():
			message=message.replace(id,str(value))
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
				return ss[1]


def getPorts(searchst,st):
  """ Searching port numbers from rtsp strings using regular expressions
  """
  pat=re.compile(searchst+"=\d*-\d*")
  pat2=re.compile('\d+')
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
    xbmc.log( rec,level=xbmc.LOGNOTICE)

class SessionData: # object to store the session data
	def __init__(self):
		self.player

def start_sat_server(satip_url,player):
	xbmc.log( "Schnipsl start:" +satip_url,level=xbmc.LOGNOTICE)
	# Launch a dialog box in kodi showing the string variable 'satip_url' as the contents
	#xbmcgui.Dialog().ok(addonname, satip_url)
	cseq=0
	satip_url_object=urlparse(satip_url)

	sat_ip_socket=SatIPSocket()
	sat_ip_socket.connect(satip_url_object.hostname,satip_url_object.port)
	clientports=[60784,60785] # the client ports we are going to use for receiving video

	if not sat_ip_socket.send_with_params(
		"SETUP SATIP_URL RTSP/1.0\r\nCSeq: SEQUENCE\r\nUser-Agent: schnipsl\r\nTransport: RTP/AVP;unicast;client_port=LOWPORT-HIGHPORT\r\n\r\n",
		#"SETUP SATIP_URL RTSP/1.0\r\nCSeq: SEQUENCE\r\nUser-Agent: schnipsl\r\nTransport: RTP/AVP;multicast;client_port=LOWPORT-HIGHPORT\r\n\r\n",
		{
			'SATIP_URL': satip_url,
			'SEQUENCE':cseq,
			'DEST_IP':'192.168.1.127',
			'LOWPORT':clientports[0],
			'HIGHPORT':clientports[1]
		}
	):
		xbmc.log( "Schnipsl cant send SETUP commmand:" ,level=xbmc.LOGERROR)
		sys.exit(0)

	printrec(sat_ip_socket.recv)

	clientports=getPorts("port",sat_ip_socket.recv)
	session_elements=sat_ip_socket.getParam('Session').split(';')
	sesid=session_elements[0]
	timeout=int(session_elements[1].split('=')[1])
	stream_id=sat_ip_socket.getParam('com.ses.streamID')
	transport=sat_ip_socket.getParam('Transport')
	transport_elements=transport.split(';')
	multicast_ip=''
	for transport_element in transport_elements:
		key_values=transport_element.split('=',2)
		if "destination"==key_values[0].lower():
			multicast_ip=key_values[1]

	cseq+=1
	if not sat_ip_socket.send_with_params(
		"PLAY rtsp://SATIP_NETLOC/stream=STREAM_ID RTSP/1.0\r\nCSeq: SEQUENCE\r\nUser-Agent: schnipsl\r\nSession: SESID\r\n\r\n",
		{
			'SATIP_NETLOC': satip_url_object.netloc,
			'STREAM_ID':stream_id,
			'SEQUENCE':cseq,
			'SESID':sesid
		}
	):
		xbmc.log( "Schnipsl cant send PLAY commmand:" ,level=xbmc.LOGERROR)
		sys.exit(0)

	printrec(sat_ip_socket.recv)
	if False:

		client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server_address = ('127.0.0.1', 8080)
		xbmc.log( "Schnipsl try to connect to Kodi" ,level=xbmc.LOGNOTICE)
		client_socket.connect(server_address)
		xbmc.log( "Schnipsl connected  to Kodi" ,level=xbmc.LOGNOTICE)
		jsonstr='{"jsonrpc": "2.0", "id": 1, "method": "Player.Open", "params": {"item": {"file": "rtp://@192.168.1.127:'+str(clientports[0])+'"}}}'
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
		xbmc.log( "Schnipsl sent play to Kodi" ,level=xbmc.LOGNOTICE)
		response = ''
		while True:
				recv = client_socket.recv(1024)
				if not recv:
					break
				response += recv
		client_socket.close()

	if True:
		player.play("rtp://@0.0.0.0:"+str(clientports[0]))
	xbmc.log( "Schnipsl play command sent to Kodi" ,level=xbmc.LOGNOTICE)
	return sat_ip_socket, timeout

def main():



	player = XBMCPlayer()

	addon       = xbmcaddon.Addon()
	addonname   = addon.getAddonInfo('name')
	timeout = 60
	sat_ip_socket = None
	if len(sys.argv)>0 and base64.urlsafe_b64decode(sys.argv[1])!="a" :
		# Das ERSTE HD
		#satip_url='rtsp://192.168.1.99:554/?src=1&freq=11494&pol=h&ro=0.35&msys=dvbs2&mtype=8psk&plts=on&sr=22000&fec=23&pids=0,17,18,5100,5101,5102,5104'
		# 3SAT HD
		#satip_url='rtsp://192.168.1.99:554/?src=1&freq=11347&pol=v&ro=0.35&msys=dvbs2&mtype=8psk&plts=on&sr=22000&fec=23&pids=0,17,18,6500,6510,6520,6530'
		# get URL from command line
		sat_ip_socket, timeout = start_sat_server(base64.urlsafe_b64decode(sys.argv[1]),player)
	else:
		xbmc.log( "Schnipsl missing URL argument!",level=xbmc.LOGERROR)

	timeout/=2 # divide timeout by 2 to be on the save side
	ticks=timeout

	while(not xbmc.abortRequested and player.run_flag):
		#time.sleep(1)
		xbmc.sleep(1000)
		ticks-=1
		if not ticks >0:
			ticks=timeout
			if sat_ip_socket:
				xbmc.log( "Schnipsl sent OPTIONS keepalive:" ,level=xbmc.LOGNOTICE)
				sat_ip_socket.send_with_params(
					"OPTIONS rtsp://SATIP_NETLOC/ RTSP/1.0\r\nCSeq: SEQUENCE\r\nUser-Agent: schnipsl\r\nSession: SESID\r\n\r\n",
					{
						'SATIP_NETLOC': satip_url_object.netloc,
						'SEQUENCE':cseq,
						'SESID':sesid
					}
				)
	'''
	'''
	#say goodby
	if sat_ip_socket:
		xbmc.log( "Schnipsl sent TEARDOWN goodbye" ,level=xbmc.LOGNOTICE)
		sat_ip_socket.send_with_params(
			"TEARDOWN rtsp://SATIP_NETLOC/stream=STREAM_ID RTSP/1.0\r\nCSeq: SEQUENCE\r\nUser-Agent: schnipsl\r\nSession: SESID\r\n\r\n",
			{
				'SATIP_NETLOC': satip_url_object.netloc,
				'STREAM_ID':stream_id,
				'SEQUENCE':cseq,
				'SESID':sesid
			}
		)
		sat_ip_socket.close()
	xbmc.log( "Schnipsl finished" ,level=xbmc.LOGNOTICE)

if __name__ == "__main__":
	main()




