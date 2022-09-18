from ctypes import sizeof
import sys
import os
import socket
import hashlib
import threading
import time


from socket import *

lock = threading.Lock()


import socket

#TCP SOCKET

localIP     = "127.0.0.1"
localPort   = 20000

#data_dict = {1:"Packet 1 data",2:"Packet 2 data",3:"Packet 3 data",4:"Packet 4 data",5:"Packet 5 data"}
bufferSize = 2048


MD5Sum = "9f9d1c257fe1733f6095a8336372616e" 
file = 'A2_small_file.txt'
file_size = os.path.getsize(file)

chunks_dict = {}




#INITIALISATION

#File Chunks Division among Clients

def break_chunks(file, CHUNK_SIZE):
    #CHUNK_SIZE = 1024 
    chunk_no = 1

    with open(file) as f:
        chunk = f.read(CHUNK_SIZE)
        while chunk:
            #print("chunk no: ", chunk_no)
            #print(chunk)

            chunks_dict[chunk_no] = chunk


            #with open('my_song_part_' + str(file_number)) as chunk_file:
            #    chunk_file.write(chunk)
            chunk_no += 1
            chunk = f.read(CHUNK_SIZE)



def TCPServerSocketCreateInit(port,a,b):
    TCPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
    TCPServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    TCPServerSocket.bind((localIP, port))


    TCPServerSocket.listen(5)   # Parameter is the number of unaccepted connections that the system will allow before refusing new connections
    print("TCP server up and listening")
    
    while(True):
        connectionSocket, addr = TCPServerSocket.accept()
        
        # Sending the total no of chunks to client
        connectionSocket.send(str(total_chunks_no).encode())
        message = connectionSocket.recv(bufferSize).decode()
        message = int(message)
        if message != 1:
            #print("Packet Lost Connection closed with ",addr)
            connectionSocket.close()

        for i in range (a,b+1):
            ind = str(i)
            while(len(ind) !=3):
                ind = "0" + ind
            connectionSocket.send(ind.encode())
            message = connectionSocket.recv(bufferSize).decode()
            message = int(message)
            if message == 1:
                connectionSocket.send(chunks_dict[i].encode())
                message = connectionSocket.recv(bufferSize).decode()
                message = int(message)
                if message != 1:
                    print("Packet Lost Connection closed with ",addr)
                    #connectionSocket.close()
                    break
            else:
                print("Packet Lost Connection closed with ",addr)
                #connectionSocket.close()
                break
            print("Sent chunk no: ", i)
            #print("WITH CHUNK DATA: ", chunks_dict[i])
            print("Size of this chunk's index is: ",  len(ind))
            print("Chunk index is: ",  ind)
            print("Size of this chunk's data is: ",  len(chunks_dict[i].encode()))
        #connectionSocket.send(str(-1).encode())
        break 
    
    connectionSocket.send(str(-1).encode())


    # INITIALISATION ENDED



    # #Sending the requested remaining chunks to client

    # message = connectionSocket.recv(bufferSize).decode()
    # while(message):
    #     message = int(message)
    #     if message != -1:
    #         connectionSocket.send(chunks_dict[message].encode())
    #         message = connectionSocket.recv(bufferSize).decode()
    #         message = int(message)
    #         if message != 1:
    #             print("Packet Lost Connection closed with ",addr)
    #             connectionSocket.close()
    #             break
    #         message = connectionSocket.recv(bufferSize).decode()
    #     else:
    #         break 
    

    # print("connection closed with ",addr)
    connectionSocket.close()   
        






    # while(True):
    #     connectionSocket, addr = TCPServerSocket.accept()
        
    #     while True:
    #         message = connectionSocket.recv(bufferSize).decode()
    #         message = int(message)
            
    #         if message != -1:
    #             connectionSocket.send(data_dict[message].encode())
    #         else: 
    #             print("connection closed with ",addr)
    #             connectionSocket.close()
    #             break






threads =[]
startTime = time.time()
noOfThreads = 5

break_chunks(file, 1024)    # Breaking file into 1kb chunks

print("CHUNKS DICTIONARY: ", chunks_dict)

total_chunks_no = len(chunks_dict)

print ("Number of chunks: ", total_chunks_no)
chunks_per_client = int(total_chunks_no/noOfThreads)
print("Chunks per client: ", chunks_per_client)

for i in range(noOfThreads-1):   
    x = threading.Thread(target=TCPServerSocketCreateInit, args=(localPort + (10*i),(i*chunks_per_client) + 1,((i+1)*chunks_per_client),))
    threads.append(x)
    x.start()
i = noOfThreads-1
x = threading.Thread(target=TCPServerSocketCreateInit, args=(localPort + (10*i),(i*chunks_per_client) + 1,total_chunks_no,))
threads.append(x)
x.start()    

for i in range(noOfThreads):
    threads[i].join()


endTime = time.time()

# hash = hashlib.md5(open("./A2_small_file.txt", 'r').read().encode()).hexdigest()
# print("md5 sum:",hash)



# INITIALISATION ENDED



from socket import socket

#TCP Client 

serverName = "127.0.0.1"

serverPort = 35000

def TCPClientSocketFinal(client_no, index, port,CHUNK_SIZE):
    

    TCPClientSocket = socket(AF_INET, SOCK_STREAM)

    TCPClientSocket.connect((serverName,port))

    print("SENT INDEX OF CHUNK NO: ", index, " TO CLIENT NO: ", client_no)
    
    TCPClientSocket.send(str(index).encode())

    message = TCPClientSocket.recv(bufferSize).decode()

    print("RECEIVED ACK FROM CLIENT NO: ", client_no, " FOR INDEX OF CHUNK NO: ", index)
    #message = int(message)
    # if message != 1:
    #     print("Packet Lost Connection closed ")
    #     TCPClientSocket.close()
    #     return

    print("SENT DATA OF CHUNK NO: ", index, " TO CLIENT NO: ", client_no)
    TCPClientSocket.send(chunks_dict[index].encode())
    
    message = TCPClientSocket.recv(bufferSize).decode()

    print("RECEIVED ACK FROM CLIENT NO: ", client_no, " FOR DATA OF CHUNK NO: ", index)

    #TCPClientSocket.send(str(-1).encode())

    # if index == total_chunks_no:
    #     TCPClientSocket.send(str(-1).encode())
        
    TCPClientSocket.close()
    return



# threads =[]
# startTime = time.time()
# noOfThreads = 5



# for i in range(noOfThreads):   
#     print("Thread ", i+1, " created")
#     x = threading.Thread(target=TCPClientSocketFinal, args=(i+1, serverPort + (10*i),2048,))        #Created a buffer of 2048 to account for extra bytes
#     threads.append(x)
#     x.start()
    
# endTime = time.time()

# # hash = hashlib.md5(open("./A2_small_file.txt", 'r').read().encode()).hexdigest()
# # print("md5 sum:",hash)











print("UDP STARTS")



from socket import socket




# UDP SOCKET



localIP     = "127.0.0.1"
localPort   = 50000
bufferSize  = 2048



client_req_ind_dict = {}

def UDPServerSocketCreate(client_no, port):


    UDPServerSocket = socket(AF_INET,SOCK_DGRAM)
    #UDPServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    UDPServerSocket.bind((localIP, port))

    #data_dict = {1:"Packet 1 data",2:"Packet 2 data",3:"Packet 3 data",4:"Packet 4 data",5:"Packet 5 data"}
    
    print("UDP server up and listening")    
    

    while(True):    
        
    
        
        
        bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)     #receiving index of chunk required by client
        index = int(bytesAddressPair[0])
        address = bytesAddressPair[1]
    
        
        #bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)     #receiving client no 
        #cl_no = int(bytesAddressPair[0])
        #address = bytesAddressPair[1]

        if index == -1:
            break

        print("Index requested: ", index, ", By Client Number: ", client_no)
        #print("Client Number: ", cl_no)

        #global client_req_ind_dict

        #client_req_ind_dict[cl_no] = index


        
        TCPClientSocketFinal(client_no, index, serverPort + 10*(client_no-1),2048)       

        UDPServerSocket.sendto(str(1).encode(), address)        #Sending acknowledgment to client for sending complete data for requested chunk



threads =[]
startTime = time.time()
noOfThreads = 5

for i in range(noOfThreads):   
    x = threading.Thread(target=UDPServerSocketCreate, args=(i+1,localPort + (10*i),))
    threads.append(x)
    x.start()
    
endTime = time.time()


for i in range(noOfThreads):
    threads[i].join()


# hash = hashlib.md5(open("./A2_small_file.txt", 'r').read().encode()).hexdigest()
# print("md5 sum:",hash)






print("UDP ENDS")





