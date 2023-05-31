import socket
from socket import *

s = socket(AF_INET,SOCK_STREAM)

host = '127.0.0.1'
port = 4444

s.connect((host,port))

while True:
    s.send(input("Client: ").encode('utf-8'))
    y = s.recv(2048)
    print('Server: ', y.decode('utf-8'))
s.close()    
