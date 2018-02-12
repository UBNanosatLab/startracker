import cv2
import socket
import os
import sys
 
if len(sys.argv)==1:
 #see https://codeplasma.com/2012/12/03/getting-webcam-images-with-python-and-opencv-2-for-real-this-time/
 camera = cv2.VideoCapture(0)
 # Captures a single image from the camera and returns it in PIL format
 def get_image():
  # read is the easiest way to get a full image out of a VideoCapture object.
  for i in range(0,6):
   retval, im = camera.read()
  cv2.imwrite("webcam.png", im)
else:
 def get_image():
  os.system("import -window root -crop 720x720+1560+304 -quality 100 webcam.png")
  #os.system("import -window root -crop 720x720+0+304 -quality 100 webcam.png")

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(("0.0.0.0", 8080))
s.listen(1)
while 1:
    conn, addr = s.accept()
    data = conn.recv(1024)
    #you have to do this 6 times or you end up with an old image
    #no idea why.
    get_image()
    webfile = open("webcam.png", "rb")
    webfiledata=webfile.read()
    response="HTTP/1.0 200 OK\r\n"
    response+="Content-Length: "+str(len(webfiledata))+"\r\n"
    response+="Content-Type: image/png\r\n\r\n"
    response+=webfiledata
    conn.sendall(response)
    webfile.close()
    conn.close()

