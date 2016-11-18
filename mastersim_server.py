#!/usr/bin/python
from threading import Thread
from time import time
import socket

#gps mag1 mag2 gyro1 gyro2
sensor_data = "3.903,64.407,-6.3719e+06 22951,-5592.8,21485 22664,-5067.3,22395 -0.020777,0.04141,0.022879 0.021835,0.065337,0.024995 1,0,0,0,1,0,0,0 0"
#magnetorquer rxn_wheel
actuator_data=["0,0,0","0.0,0.0,0.0"]
sep = " "
logfile=open('/var/log/mastersim_server.log','w+')
def mastersim_com():
    global sensor_data
    global actuator_data
    global sep
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("0.0.0.0", 7000))
    s.listen(1)
    while 1:
        conn, addr = s.accept()
        data = conn.recv(1024)
        if not data: break
        print >> logfile, str(time())+' ' +data
        logfile.flush()
        sensor_data=data
        conn.sendall(sep.join(actuator_data)+"\r\n")
        conn.close()

def gps_out():
    global sensor_data
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("0.0.0.0", 7001))
    s.listen(1)
    while 1:
        conn, addr = s.accept()
        conn.sendall(sensor_data.split()[0]+"\r\n")
        conn.close()

def mag1_out():
    global sensor_data
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("0.0.0.0", 7002))
    s.listen(1)
    while 1:
        conn, addr = s.accept()
        conn.sendall(sensor_data.split()[1]+"\r\n")
        conn.close()

def mag2_out():
    global sensor_data
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("0.0.0.0", 7003))
    s.listen(1)
    while 1:
        conn, addr = s.accept()
        conn.sendall(sensor_data.split()[2]+"\r\n")
        conn.close()

def gyro1_out():
    global sensor_data
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("0.0.0.0", 7004))
    s.listen(1)
    while 1:
        conn, addr = s.accept()
        conn.sendall(sensor_data.split()[3]+"\r\n")
        conn.close()

def gyro2_out():
    global sensor_data
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("0.0.0.0", 7005))
    s.listen(1)
    while 1:
        conn, addr = s.accept()
        conn.sendall(sensor_data.split()[4]+"\r\n")
        conn.close()

def magnetorquer_in():
    global actuator_data
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("0.0.0.0", 7006))
    s.listen(1)
    while 1:
        conn, addr = s.accept()
        data = conn.recv(1024)
        actuator_data[0]=data
        conn.close()

def rxn_wheel_in():
    global actuator_data
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("0.0.0.0", 7007))
    s.listen(1)
    while 1:
        conn, addr = s.accept()
        data = conn.recv(1024)
        print >> logfile, str(time()) + " rxn cmd: "+data
        logfile.flush()
        #actuator_data[1]=data
        conn.close()

def state_out():
    global sensor_data
    global actuator_data
    global sep
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("0.0.0.0", 7008))
    s.listen(1)
    while 1:
        conn, addr = s.accept()
        conn.sendall(sensor_data+sep+sep.join(actuator_data)+"\r\n")
        conn.close()

def rxn_wheel_real_in():
    global actuator_data
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("0.0.0.0", 7010))
    s.listen(1)
    while 1:
        conn, addr = s.accept()
        data = conn.recv(1024)
        print >> logfile, str(time()) +" rxn real: "+data
        logfile.flush()
        actuator_data[1]=data
        conn.close()

mastersim_com = Thread( target=mastersim_com )
gps_out = Thread( target=gps_out)
mag1_out = Thread( target=mag1_out )
mag2_out = Thread( target=mag2_out)
gyro1_out = Thread( target=gyro1_out)
gyro2_out = Thread( target=gyro2_out)
magnetorquer_in = Thread( target=magnetorquer_in)
rxn_wheel_in = Thread( target=rxn_wheel_in)
rxn_wheel_real_in = Thread( target=rxn_wheel_real_in)
state_out = Thread( target=state_out)

mastersim_com.start()
gps_out.start()
mag1_out.start()
mag2_out.start()
gyro1_out.start()
gyro2_out.start()
magnetorquer_in.start()
rxn_wheel_in.start()
rxn_wheel_real_in.start()
state_out.start()

mastersim_com.join()
gps_out.join()
mag1_out.join()
mag2_out.join()
gyro1_out.join()
gyro2_out.join()
magnetorquer_in.join()
rxn_wheel_in.join()
rxn_wheel_real_in.join()
state_out.join()
