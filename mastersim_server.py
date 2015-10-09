#!/usr/bin/python
from threading import Thread
import socket

#gps mag1 mag2 gyro1 gyro2
sensor_data = "235317.000,4003.9039,N,10512.5793,W,08,1577.9 0.0,0.0,0.0 0.0,0.0,0.0 0.0,0.0,0.0 0.0,0.0,0.0"
#magnetorquer rxn_wheel
actuator_data=["0,0,0","0.0,0.0,0.0"]

def mastersim_com(threadname):
    global sensor_data
    global actuator_data
    sep = " "
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("0.0.0.0", 7000))
    s.listen(1)
    while 1:
        conn, addr = s.accept()
        while 1:
            data = conn.recv(1024)
            if not data: break
            sensor_data=data
            conn.sendall(sep.join(actuator_data))
        conn.close()

def gps_out(threadname):
    global sensor_data
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("0.0.0.0", 7001))
    s.listen(1)
    while 1:
        conn, addr = s.accept()
        while 1:
            data = conn.recv(1024)
            if not data: break
            conn.sendall(sensor_data.split()[0]+"\r\n")
        conn.close()

def mag1_out(threadname):
    global sensor_data
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("0.0.0.0", 7002))
    s.listen(1)
    while 1:
        conn, addr = s.accept()
        while 1:
            data = conn.recv(1024)
            if not data: break
            conn.sendall(sensor_data.split()[1]+"\r\n")
        conn.close()

def mag2_out(threadname):
    global sensor_data
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("0.0.0.0", 7003))
    s.listen(1)
    while 1:
        conn, addr = s.accept()
        while 1:
            data = conn.recv(1024)
            if not data: break
            conn.sendall(sensor_data.split()[2]+"\r\n")
        conn.close()

def gyro1_out(threadname):
    global sensor_data
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("0.0.0.0", 7004))
    s.listen(1)
    while 1:
        conn, addr = s.accept()
        while 1:
            data = conn.recv(1024)
            if not data: break
            conn.sendall(sensor_data.split()[3]+"\r\n")
        conn.close()

def gyro2_out(threadname):
    global sensor_data
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("0.0.0.0", 7005))
    s.listen(1)
    while 1:
        conn, addr = s.accept()
        while 1:
            data = conn.recv(1024)
            if not data: break
            conn.sendall(sensor_data.split()[4]+"\r\n")
        conn.close()

def magnetorquer_in(threadname):
    global actuator_data
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("0.0.0.0", 7006))
    s.listen(1)
    while 1:
        conn, addr = s.accept()
        while 1:
            data = conn.recv(1024)
            actuator_data[0]=data
            if not data: break
            conn.sendall("\r\n")
        conn.close()

def rxn_wheel_in(threadname):
    global actuator_data
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("0.0.0.0", 7007))
    s.listen(1)
    while 1:
        conn, addr = s.accept()
        while 1:
            data = conn.recv(1024)
            actuator_data[1]=data
            if not data: break
            conn.sendall("\r\n")
        conn.close()

mastersim_com = Thread( target=mastersim_com, args=("mastersim_com", ) )
gps_out = Thread( target=gps_out, args=("gps_out", ) )
mag1_out = Thread( target=mag1_out, args=("mag1_out", ) )
mag2_out = Thread( target=mag2_out, args=("mag2_out", ) )
gyro1_out = Thread( target=gyro1_out, args=("gyro1_out", ) )
gyro2_out = Thread( target=gyro2_out, args=("gyro2_out", ) )
magnetorquer_in = Thread( target=magnetorquer_in, args=("magnetorquer_in", ) )
rxn_wheel_in = Thread( target=rxn_wheel_in, args=("rxn_wheel_in", ) )

mastersim_com.start()
gps_out.start()
mag1_out.start()
mag2_out.start()
gyro1_out.start()
gyro2_out.start()
magnetorquer_in.start()
rxn_wheel_in.start()

mastersim_com.join()
gps_out.join()
mag1_out.join()
mag2_out.join()
gyro1_out.join()
gyro2_out.join()
magnetorquer_in.join()
rxn_wheel_in.join()
