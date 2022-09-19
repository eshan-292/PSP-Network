import sys
import os
import socket
import hashlib
import threading
import time


from socket import *

import random



lock = threading.Lock()




# INITIALISATION OF CLIENTS RECEIVING CHUNKS

#TCP SOCKET


serverName = "127.0.0.1"

serverPort = 20000

MD5Sum = "9f9d1c257fe1733f6095a8336372616e" 
file = 'A2_small_file.txt'
file_size = os.path.getsize(file)

client_chunks_dict_dict = {}            # Dictionary mapping client no to the dictionary of chunks received by the client (which itself map chunk no to chunk data)

client_recd_chunks_dict = {}            # Dictionary mapping client no to the received chunks list of the client

total_chunks_no = 0
n = 0

def TCPClientSocketCreateInit(client_no, port,CHUNK_SIZE):
    

    TCPClientSocket = socket(AF_INET, SOCK_STREAM)

    #TCPClientSocket.bind((serverName,0))

    TCPClientSocket.connect((serverName,port))

    # Receiving the total no of chunks
    server_message = TCPClientSocket.recv(CHUNK_SIZE)        # Receiving chunk index
    TCPClientSocket.send(str(1).encode())
    
    #lock.acquire()
    global n
    n = int(server_message)
    recd_chunks = [0]* n        # list of chunks received by client, initially it has all zeros 
    global total_chunks_no

    total_chunks_no = n
    #lock.release()
    chunks_dict = {}
    
    server_message1 = TCPClientSocket.recv(CHUNK_SIZE)        # Receiving chunk index
    TCPClientSocket.send(str(1).encode())

    recd_chunks[int(server_message1.decode())-1] = 1        # Marking the chunk_no to be received 

    server_message2 = TCPClientSocket.recv(CHUNK_SIZE)        # Receiving chunk data
    chunks_dict[int(server_message1.decode())] = server_message2.decode()        # Storing the chunk data in a dictionary
    TCPClientSocket.send(str(1).encode())
    
    #print('From Server: ',  server_message1.decode())
    #print('From Server: ',  server_message2.decode())

    while(server_message1):
        server_message1 = TCPClientSocket.recv(CHUNK_SIZE)        # Receiving chunk index
        
        #Terminatihg initialisation condition
        if (int(server_message1.decode())==-1):
            
            break 
        TCPClientSocket.send(str(1).encode())
        
        recd_chunks[int(server_message1.decode())-1] = 1        # Marking the chunk_no to be received 

        server_message2 = TCPClientSocket.recv(CHUNK_SIZE)        # Receiving chunk data
        chunks_dict[int(server_message1.decode())] = server_message2.decode()       # Storing the chunk data in a dictionary

        TCPClientSocket.send(str(1).encode())
        #print('From Server: ',  server_message1.decode())
        #print('From Server: ',  server_message2.decode())
        
    print("RECD CHUNKS: ", recd_chunks)
    print("CHUNKS DICT: ", chunks_dict)
    


    #lock.acquire()
    global client_chunks_dict_dict

    global client_recd_chunks_dict


    client_recd_chunks_dict[client_no] = recd_chunks
        
    client_chunks_dict_dict[client_no] = chunks_dict

    #lock.release() 



        
    TCPClientSocket.close()
   



print( "CHUNKS DICT DICT: " , client_chunks_dict_dict)
print("RECD CHUNKS DICT", client_recd_chunks_dict)



threads =[]
startTime = time.time()     #START TIME
noOfThreads = 5

for i in range(noOfThreads):   
    print("Thread ", i+1, " created")
    x = threading.Thread(target=TCPClientSocketCreateInit, args=(i+1, serverPort + (10*i),2048,))        #Created a buffer of 2048 to account for extra bytes
    threads.append(x)
    x.start()
    
for i in range(noOfThreads):
    threads[i].join()
    






#INITIALISATION OF CLIENTS ENDS










serverAddressPort   = ("127.0.0.1", 50000)
bufferSize          = 2048

import socket

localIP     = "127.0.0.1"
localPort   = 35000






# LISTENING TO BROADCASTS

# BROADCASTING CLIENTS - each client listens for broadcast messages from server\


base_port = 10000

import socket

def TCPBroadcast(client_no, port):
    TCPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
    #TCPServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    TCPServerSocket.bind((localIP, port))


    TCPServerSocket.listen(5)   # Parameter is the number of unaccepted connections that the system will allow before refusing new connections
    print("TCP server up and listening")

    
    connectionSocket, addr = TCPServerSocket.accept()

    message = connectionSocket.recv(bufferSize).decode()    # Message would be the index required by the server

    while(True):

        # connectionSocket, addr = TCPServerSocket.accept()

        # message = connectionSocket.recv(bufferSize).decode()    # Message would be the index required by the server

        index = int(message)
        print("REQUESTED INDEX: ", index)
        if index==-1:
            break

        if index in client_chunks_dict_dict[client_no].keys():
            print("Chunk found in client ", client_no)
            connectionSocket.send(str(1).encode())      # Sending 1 to indicate that the chunk is found
            message = connectionSocket.recv(bufferSize).decode()  #Acknowledgenment from server that it has received the 1 
            connectionSocket.send(client_chunks_dict_dict[client_no][index].encode())     # Sending the chunk data
        else:
            connectionSocket.send(str(-1).encode())      #Sending -1 to indicate that the chunk is not found
        

        connectionSocket, addr = TCPServerSocket.accept()

        message = connectionSocket.recv(bufferSize).decode()    # Message would be the index required by the server
    
    
    print("Broadcast connection closed with ",addr)
    connectionSocket.close()   


#BROADCAST TCP THREADS
for client_no in range(1,1+noOfThreads):
    y = threading.Thread(target=TCPBroadcast, args=(client_no,base_port + (10*(client_no-1)),))
    threads.append(y)
    y.start()    



#UDP SOCKET FOR SENDING REQUESTS FOR REMAINING CHUNKS

def UDPClientSocketCreate(ind, port):
    # Create a UDP socket at client side
    UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    #UDPClientSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    UDPClientSocket.bind(("127.0.0.1",0))   




    # # REQUESTING REMAINING CHUNKS FROM SERVER

    UDPClientSocket.sendto(str.encode(str(ind)), port)
    
    # RECEIVING ACKNOWLEDGEMENT FROM SERVER
    bytesAddressPair = UDPClientSocket.recvfrom(bufferSize)
    server_message = int(bytesAddressPair[0])
    
    # HANDLING THE CASE OF PACKET LOSS
    while(server_message != 1):
        UDPClientSocket.sendto(str.encode(str(ind)), port)
        bytesAddressPair = UDPClientSocket.recvfrom(bufferSize)
        server_message = int(bytesAddressPair[0])


    



def TCPServerSocketFinal(client_no,port):
    TCPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
    TCPServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    TCPServerSocket.bind((localIP, port))


    TCPServerSocket.listen(5)   # Parameter is the number of unaccepted connections that the system will allow before refusing new connections
    print("TCP server up and listening")

    connectionSocket, addr = TCPServerSocket.accept()

    message1 = connectionSocket.recv(bufferSize).decode()
    
    # message1 = "dummy"
    

    while(message1):
        
        #connectionSocket, addr = TCPServerSocket.accept()

        # message1 = connectionSocket.recv(bufferSize).decode()

        index = int(message1)
        connectionSocket.send(str(1).encode())
        if (index == -1):
            break
        
        message = connectionSocket.recv(bufferSize).decode()

        
        #lock.acquire()
        print("HERE")
        global client_chunks_dict_dict
        global client_recd_chunks_dict
        client_recd_chunks_dict[client_no][index-1] = 1
        client_chunks_dict_dict[client_no][index] = message
        #lock.release()
        print("Chunk:", index, " Recd")
        #print("Chunk Data", message)
        connectionSocket.send(str(1).encode())      #Sending Confirmation of recd chunk data to server

        connectionSocket, addr = TCPServerSocket.accept()
        message1 = connectionSocket.recv(bufferSize).decode()
        print("message1: ", message1)
        
        
            



    print("TCP connection closed with ",addr)
    connectionSocket.close()   
    

#TCP FINAL THREADS
for client_no in range(1,1+noOfThreads):
    y = threading.Thread(target=TCPServerSocketFinal, args=(client_no,localPort + (10*(client_no-1)),))
    threads.append(y)
    y.start()    

flag = 0



# THREADS FOR SENDING UDP REQUESTS FOR MISSING CHUNKS TO SERVER
for client_no in range(1,1+noOfThreads):
    last_chunk_index = 0
    for i in range(total_chunks_no):
        flag = 0
        
        if (client_recd_chunks_dict[client_no][i] == 0):

            # y = threading.Thread(target=TCPServerSocketFinal, args=(client_no, i+1,localPort + (10*(client_no-1)),))
            # threads.append(y)
            # y.start()

            last_chunk_index = i 
            #print("Client Number : ", client_no, " is about to request chunk no ", i+1 ) 
            x = threading.Thread(target=UDPClientSocketCreate, args=(i+1,(serverAddressPort[0],serverAddressPort[1] + (10*(client_no-1))),))
            threads.append(x)
            x.start()

            flag = 1

            #break 
        




# Terminating condition - when all the chunks are received by all clients

while(True):
    flag = 0
    for client_no in range(1,1+noOfThreads):
        for i in range(total_chunks_no):
            if (client_recd_chunks_dict[client_no][i] == 0):
                flag=1
                break
    if flag==0:
        #Sending termination message for each client to the server
        for client_no in range(1,1+noOfThreads):
            x = threading.Thread(target=UDPClientSocketCreate, args=(-1,(serverAddressPort[0],serverAddressPort[1] + (10*(client_no-1))),))
            threads.append(x)
            x.start()
        break
        
print("THE END")



endTime = time.time()

for client_no in range(1,1+noOfThreads):
    print("No of chunks recd by client ", client_no, "is : ", sum(client_recd_chunks_dict[client_no]))

print("Total time taken: ", endTime-startTime)

