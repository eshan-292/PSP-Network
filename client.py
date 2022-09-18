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



    # INITIALISATION FINISHED



    # # REQUESTING REMAINING CHUNKS FROM SERVER

    # for i in range(n):
    #     if (recd_chunks[i] == 0):
    #         TCPClientSocket.send(str(i+1).encode())
    #         #server_message = TCPClientSocket.recv(CHUNK_SIZE)        # Receiving chunk index
    #         #TCPClientSocket.send(str(1).encode())
    #         server_message = TCPClientSocket.recv(CHUNK_SIZE)        # Receiving chunk data
    #         TCPClientSocket.send(str(1).encode())
    #         recd_chunks[i] = 1        # Marking the chunk_no to be received 
    #         chunks_dict[i+1] = server_message.decode()
    #         print('From Server: Received Chunk:',  i+1)
    #         print('From Server: ',  server_message.decode())

    #     else:
    #         print("Chunk:", i) 
    #         print("Chunk Data", chunks_dict[i+1] )


    #TCPClientSocket.send(str(-1).encode())
        
    TCPClientSocket.close()
   



    # for i in range(1,6):

    #     TCPClientSocket.send(str(i).encode())
    #     server_message = TCPClientSocket.recv(1024)
    #     print('From Server: ', server_message.decode())

    # TCPClientSocket.send(str(-1).encode())
    # TCPClientSocket.close()
   


print( "CHUNKS DICT DICT: " , client_chunks_dict_dict)
print("RECD CHUNKS DICT", client_recd_chunks_dict)



threads =[]
startTime = time.time()
noOfThreads = 5

for i in range(noOfThreads):   
    print("Thread ", i+1, " created")
    x = threading.Thread(target=TCPClientSocketCreateInit, args=(i+1, serverPort + (10*i),2048,))        #Created a buffer of 2048 to account for extra bytes
    threads.append(x)
    x.start()
    
for i in range(noOfThreads):
    threads[i].join()
    
endTime = time.time()


#INITIALISATION OF CLIENTS ENDS






# UDP STARTS FOR SENDING REQUESTS FOR MISSING CHUNKS TO SERVER



#UDP SOCKET


serverAddressPort   = ("127.0.0.1", 50000)
bufferSize          = 2048

import socket

localIP     = "127.0.0.1"
localPort   = 35000





def UDPClientSocketCreate(ind, port):
    # Create a UDP socket at client side
    UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    #UDPClientSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    UDPClientSocket.bind(("127.0.0.1",0))   




    # # REQUESTING REMAINING CHUNKS FROM SERVER

    UDPClientSocket.sendto(str.encode(str(ind)), port)
    server_message = UDPClientSocket.recvfrom(bufferSize)
    

    # Terminating condition



def TCPServerSocketFinal(client_no,port):
    TCPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
    #TCPServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
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
        message = connectionSocket.recv(bufferSize).decode()

        if (index == -1):
            break
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
        
        
            



    print("connection closed with ",addr)
    connectionSocket.close()   
    


for client_no in range(1,1+noOfThreads):
    y = threading.Thread(target=TCPServerSocketFinal, args=(client_no,localPort + (10*(client_no-1)),))
    threads.append(y)
    y.start()    

flag = 0

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



for client_no in range(1,1+noOfThreads):
    while(True):
        flag= 0
        for i in range(total_chunks_no):
            if (client_recd_chunks_dict[client_no][i] == 0):
                flag=1
                break
        if flag==0:
            x = threading.Thread(target=UDPClientSocketCreate, args=(-1,(serverAddressPort[0],serverAddressPort[1] + (10*(client_no-1))),))
            threads.append(x)
            x.start()
            break
        
        #if(len(client_recd_chunks_dict[client_no]) == total_chunks_no):

        # x = threading.Thread(target=UDPClientSocketCreate, args=(i+1,(serverAddressPort[0],serverAddressPort[1] + (10*(client_no-1))),))
        # threads.append(x)
        # x.start()

        
        
print("THE END")


# #UDP SOCKET


# serverAddressPort   = ("127.0.0.1", 50000)
# bufferSize          = 2048

# import socket










# def UDPClientSocketCreate(client_no, port):
#     # Create a UDP socket at client side
#     UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
#     #\UDPClientSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#     UDPClientSocket.bind(("127.0.0.1",0))   




#     # # REQUESTING REMAINING CHUNKS FROM SERVER

#     for i in range(total_chunks_no):
#         if (client_recd_chunks_dict[client_no][i] == 0):
#             UDPClientSocket.sendto(str.encode(str(i+1)), port)
#             server_message = UDPClientSocket.recvfrom(bufferSize)
#             #if int(server_message.decode()) ==1:
#             UDPClientSocket.sendto(str(client_no).encode(), port)
#                 #server_message = UDPClientSocket.recvfrom(bufferSize)

#             break 
#             #UDPClientSocket.sendto(str(1).encode(), serverAddressPort)

            
#             #client_recd_chunks_dict[client_no][i] = 1        # Marking the chunk_no to be received 
#             #client_chunks_dict_dict[client_no][i+1] = server_message.decode()
#             #print('From Server: Received Chunk:',  i+1)
#             #print('From Server: ',  server_message.decode())
    


#     # # # REQUESTING REMAINING CHUNKS FROM SERVER

#     # for i in range(1):
#     #     #if (client_recd_chunks_dict[client_no][i] == 0):
#     #     UDPClientSocket.sendto(str.encode(str(i+1)), port)
#     #     server_message = UDPClientSocket.recvfrom(bufferSize)
#     #         #if int(server_message.decode()) ==1:
#     #     UDPClientSocket.sendto(str(client_no).encode(), port)
#     #             #server_message = UDPClientSocket.recvfrom(bufferSize)

        
#     #         #UDPClientSocket.sendto(str(1).encode(), serverAddressPort)

            
#     #         #client_recd_chunks_dict[client_no][i] = 1        # Marking the chunk_no to be received 
#     #         #client_chunks_dict_dict[client_no][i+1] = server_message.decode()
#     #         #print('From Server: Received Chunk:',  i+1)
#     #         #print('From Server: ',  server_message.decode())









# threads =[]
# startTime = time.time()
# noOfThreads = 5


# client_chunk_dict = []
# for i in range(noOfThreads):   
#     x = threading.Thread(target=UDPClientSocketCreate, args=(i+1,(serverAddressPort[0],serverAddressPort[1] + (10*i)),))
#     threads.append(x)
#     x.start()
    
# endTime = time.time()

# for i in range(noOfThreads):
#     threads[i].join()


# # hash = hashlib.md5(open("./A2_small_file.txt", 'r').read().encode()).hexdigest()
# # print("md5 sum:",hash)



# #UDP ENDS




# from socket import socket


# #TCP Server 



# # TCP STARTS FOR DISTRIBUTING REQUESTED CHUNKS TO CLIENTS





# #TCP SOCKET

# localIP     = "127.0.0.1"
# localPort   = 35000

# bufferSize = 2048




# def TCPServerSocketFinal(client_no,port):
#     TCPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
#     TCPServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#     TCPServerSocket.bind((localIP, port))


#     TCPServerSocket.listen(5)   # Parameter is the number of unaccepted connections that the system will allow before refusing new connections
#     print("TCP server up and listening")

#     connectionSocket, addr = TCPServerSocket.accept()

#     # #Sending the requested remaining chunks to client

#     message = connectionSocket.recv(bufferSize).decode()
#     while(message):
#         message = int(message)
#         if message != -1:
#             connectionSocket.send(chunks_dict[message].encode())
#             message = connectionSocket.recv(bufferSize).decode()
#             message = int(message)
#             if message != 1:
#                 print("Packet Lost Connection closed with ",addr)
#                 connectionSocket.close()
#                 break
#             message = connectionSocket.recv(bufferSize).decode()
#         else:
#             break 
    

#     print("connection closed with ",addr)
#     connectionSocket.close()   

# threads =[]
# startTime = time.time()
# noOfThreads = 5

# for i in range(noOfThreads):   
#     x = threading.Thread(target=TCPServerSocketFinal, args=(i+1,localPort + (10*i),))
#     threads.append(x)
#     x.start()
    
# endTime = time.time()

# # hash = hashlib.md5(open("./A2_small_file.txt", 'r').read().encode()).hexdigest()
# # print("md5 sum:",hash)




