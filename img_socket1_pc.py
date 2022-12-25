import socket  

HOST = '192.168.143.152'
PORT = 8080 
sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)  
sock.connect((HOST,PORT))   
sock.send(('Hello Raspberry').encode("utf-8"))  
    
receivedstr=sock.recv(1024)
print(receivedstr.decode()) 