import socket
from feeds import *
from time import time


def feeds_server(self,port,feednames=[]):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind(("0.0.0.0", port))
	s.listen(1)
	while 1:
		try:
			conn, addr = s.accept()
			if len(feednames)>0:
				data = conn.recv(1024)
				x=[[float(j) for j in i.split(",")] for i in data.split(" ")]
				for i in range(0,len(feednames)):
					feeds[feednames[i]].publish(x[i])
			if len(self.subscriptions)>0:
				conn.sendall(' '.join([','.join([str(j) for j in feeds[i][0]]) for i in self.subscriptions])+"\r\n")
		except Exception, e:
			logger.error(e)
		conn.close()


mastersim = subscriber(target=feeds_server, args=[7000,["gps","mag1","mag2","gyro1","gyro2","actual-attitude"]])
gps_out = subscriber(target=feeds_server, args=[7002])
mag1_out = subscriber( target=feeds_server, args=[7003])
mag2_out = subscriber( target=feeds_server, args=[7004])
gyro1_out = subscriber( target=feeds_server, args=[7005])
gyro2_out = subscriber( target=feeds_server, args=[7006])
torquer_in = subscriber(target=feeds_server, args=[7007,["torquer"]])
rxn_in = subscriber(target=feeds_server, args=[7008,["rxn",]])


feed("gps")
feed("mag1")
feed("mag2")
feed("gyro1")
feed("gyro2")
feed("actual-attitude")
feed("rxn")
feed("torquer")

feeds["gps"].add([3.903,64.407,-6.3719e+06])
feeds["mag1"].add([22951,-5592.8,21485])
feeds["mag2"].add([2664,-5067.3,22395])
feeds["gyro1"].add([-0.020777,0.04141,0.022879])
feeds["gyro2"].add([0.021835,0.065337,0.024995])
feeds["actual-attitude"].add([1,0,0,0,1,0,0,0,0])
feeds["rxn"].add([0.0,0.0,0.0])
feeds["torquer"].add([0.0,0.0,0.0])

mastersim.subscribe("rxn")
mastersim.subscribe("torquer")
gps_out.subscribe("gps")
mag1_out.subscribe("mag1")
mag2_out.subscribe("mag2")
gyro1_out.subscribe("gyro1")
gyro2_out.subscribe("gyro2")

mastersim.start()
gps_out.start()
mag1_out.start()
mag2_out.start()
gyro1_out.start()
gyro2_out.start()
torquer_in.start()
rxn_in.start()

#only do this part if we were run as a python script
if __name__ == '__main__':
	mastersim.join()
	gps_out.join()
	mag1_out.join()
	mag2_out.join()
	gyro1_out.join()
	gyro2_out.join()
	torquer_in.join()
	rxn_in.join()
