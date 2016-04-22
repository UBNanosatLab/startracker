from flask import Flask, jsonify, render_template, request
import socket
import struct

server = Flask(__name__)

@server.route('/exception', methods = ['POST'])
def post_data():
    args = request.get_json()
    device_code = args['device']
    exception_code = args['exception']
    exception_code = str(exception_code)
    print type(exception_code) is str
    device_port_map = {0:8000, 1:8001, 2:8002, 3:8003, 4:8004, 23:8023, 5:8005, 6:8006,7:8007,8:8008, 9:8009, 10:8010,11:8011, 20:8020, 21:8021}
    fs_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    fs_socket.connect(('192.168.100.100', device_port_map[int(device_code)]))
    fs_socket.send(struct.pack("I",len(exception_code)))
            #chr(len(exception_code)))
    fs_socket.send(exception_code)
    fs_socket.close()
    return jsonify({"message":"SUCCESS"})

@server.route('/', methods = ['GET'])
def post_data2():
    return "Hello"

server.run(host='0.0.0.0', port=9002, debug=True)

#DEFINE FUNCTION TO DISTINGUISH WHICH DEVICE/PORT RECIEVES THE EXCEPTION ERROR

