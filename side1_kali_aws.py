import threading
import logging
import socket
import sys
import time
import requests
import base64
import urllib.parse
import traceback

LISTEN_HOST = 'localhost'
LISTEN_PORT = 10000
HTTP_SERVER = "http://18.191.80.4"

inbuffer = ""

socket_lock = threading.Lock()
do_exit = False

def tcp_server_function(sock):
	global inbuffer
	global do_exit
	logging.info("Thread tcp_server_function: starting")
	
	# Receive the data in small chunks and retransmit it
	try:
		while True:
			#with socket_lock:
			data = sock.recv(2048)
			
			if data:
				logging.info("Thread tcp_server_function: received %d bytes" % len(data))
				inbuffer += data.decode( "utf-8")
			
			time.sleep(0.5)
	except Exception as e:
		logging.info("Thread tcp_server_function: exception hit")
		do_exit = True
		print(e)
	
	logging.info("Thread tcp_server_function: finishing")
	
def http_client_function(sock):
	global inbuffer
	global do_exit
	logging.info("Thread http_client_function: starting")
	
	try:
		while True:
			try:
				if do_exit:
					break
				if len(inbuffer) > 0:
					dataparam = urllib.parse.quote(inbuffer)
					inbuffer = ""
				else:
					dataparam = ""
				logging.info("Thread http_client_function: requesting %s/data=%s" % (HTTP_SERVER, dataparam))
				r = requests.get( "%s/data=%s" % (HTTP_SERVER, dataparam), timeout=1.0)
				if r.status_code == 200:
					t = r.text
					if len(t) > 0:
						logging.info("Thread http_client_function: relaying %d bytes (%s)" % (len(t),t))
						#with socket_lock:
						sock.sendall( bytes( r.text, "utf-8"))
				else:
					logging.info("Thread http_client_function: received error response from HTTP server")

					
				time.sleep(3)
			except requests.ConnectionError:
				logging.info("Thread http_client_function: received requests.ConnectionError")
				#with socket_lock:
				sock.sendall( bytes("hello", "utf-8"))
			
	except Exception as e:
		logging.info("Thread http_client_function: exception hit")
		print(e)
		traceback.print_exc(file=sys.stdout)
	
	logging.info("Thread http_client_function: finishing")

if __name__ == "__main__":
	format = "%(asctime)s: %(message)s"
	logging.basicConfig(format=format, level=logging.INFO,datefmt="%H:%M:%S")
	
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_address = (LISTEN_HOST, LISTEN_PORT)
	logging.info("Main: listening on %s:%s" % (LISTEN_HOST, LISTEN_PORT))
	sock.bind(server_address)
	
	
	sock.listen(1)

		# Wait for a connection
	logging.info("Waiting for a connection")
	connection, client_address = sock.accept()
	
	#sock.setblocking(0)
	#sock.settimeout(1)

	tcp_server_thread = threading.Thread( target=tcp_server_function, args=(connection,))
	tcp_server_thread.start()
	
	http_client_thread = threading.Thread( target=http_client_function, args=(connection,))
	http_client_thread.start()
	
	