import socket 
import numpy
import cv2 

def getimage():
    HOST = '192.168.143.152'
    PORT = 8080 
    sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)  
    sock.connect((HOST,PORT))   
    sock.send(('Hello Raspberry').encode("utf-8"))
    buf = b''
    recvlen = 100
    while recvlen > 0:
        receivedstr =   sock.recv(1024)
        recvlen = len(receivedstr)
        buf += receivedstr

    sock.close
    narray = numpy.fromstring(buf, dtype='uint8')
    return cv2.imdecode(narray,1)

while True:
    img = getimage()
    cv2.imshow('Capture', img)
    if cv2.waitKey(100) & 0xFF == ord('q'):
        break
    