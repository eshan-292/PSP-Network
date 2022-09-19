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


    connectionSocket.close()   








#Creating threads for the initialisation 


threads =[]
startTime = time.time()     #START TIME
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




# hash = hashlib.md5(open("./A2_small_file.txt", 'r').read().encode()).hexdigest()
# print("md5 sum:",hash)





# INITIALISATION ENDED



# DELETING THE FILE FROM SERVER AND CREATING A CACHE

chunks_dict = {}
cache_queue = []

cache_size = noOfThreads
from socket import socket

#TCP Client 

serverName = "127.0.0.1"

serverPort = 35000


ctr = 0         # Global counter for checking when all clients have received the file and program needs to be terminated

base_port = 10000

def broadcast(index):
    
    if index==-1:               #Sending the termination message to all clients
        for client_no in range(1, noOfThreads+1):
            port = base_port + (10*(client_no-1))
            #broadcast_single(index, port)

            
            clientSocket = socket(AF_INET, SOCK_STREAM)
            clientSocket.connect((serverName, port))

            #SENDING THE INDEX OF THE CHUNK NEEDED
            clientSocket.send(str(index).encode())      


            clientSocket.close()
    else:

        for client_no in range(1, noOfThreads+1):
            port = base_port + (10*(client_no-1))
            #broadcast_single(index, port)

            
            clientSocket = socket(AF_INET, SOCK_STREAM)
            clientSocket.connect((serverName, port))

            #SENDING THE INDEX OF THE CHUNK NEEDED
            clientSocket.send(str(index).encode())
            
            # Receives 1 if the index has been found, -1 otherwise
            message = clientSocket.recv(bufferSize).decode()
            message = int(message)
            if message == 1:
                clientSocket.send(str(1).encode())
                message = clientSocket.recv(bufferSize).decode()        #Receiving the corresponding chunk data
                clientSocket.close()
                return message
            
            clientSocket.close()




def TCPClientSocketFinal(client_no, index, port,CHUNK_SIZE):
    

    TCPClientSocket = socket(AF_INET, SOCK_STREAM)

    TCPClientSocket.connect((serverName,port))

    print("SENT INDEX OF CHUNK NO: ", index, " TO CLIENT NO: ", client_no)
    
    TCPClientSocket.send(str(index).encode())

    message = TCPClientSocket.recv(bufferSize).decode()



    print("RECEIVED ACK FROM CLIENT NO: ", client_no, " FOR INDEX OF CHUNK NO: ", index)

    # if index == -1:
    #     TCPClientSocket.close()
    #     return
    

    lock.acquire()
    #CHECKING IF DATA IS PRESENT IN CACHE
    if index in chunks_dict:
        print("DATA PRESENT IN CACHE")
        print("SENT DATA OF CHUNK NO: ", index, " TO CLIENT NO: ", client_no)
        TCPClientSocket.send(chunks_dict[index].encode())    
    #ELSE DO A BROADCAST TO ALL CLIENTS
    else:
        #Call broadcast handling function
        print("DATA NOT PRESENT IN CACHE")
        
        if index == -1:
            global ctr
            ctr=ctr+1
            if ctr == noOfThreads:
                chunk_data = broadcast(index)
                TCPClientSocket.close()
                return
        else:
            #lock.acquire()
            chunk_data = broadcast(index)       # Receive the requested chunk data through broadcast
            
            #Updating the cache

            #If cache is full, remove the least recently used chunk (the first element of the queue)
            
            if len(cache_queue) == cache_size:
                del chunks_dict[cache_queue[0]]     # Remove the chunk data from the dictionary
                cache_queue.pop(0)                  # Remove the chunk index from the cache
            cache_queue.append(index)       # Add the current index to the cache
            chunks_dict[index] = chunk_data     # Add the current chunk data to the cache
            #lock.release()
            TCPClientSocket.send(chunk_data.encode())    
    
    lock.release()  
    message = TCPClientSocket.recv(bufferSize).decode()

    print("RECEIVED ACK FROM CLIENT NO: ", client_no, " FOR DATA OF CHUNK NO: ", index)

    #TCPClientSocket.send(str(-1).encode())

    # if index == total_chunks_no:
    #     TCPClientSocket.send(str(-1).encode())
        
    TCPClientSocket.close()



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
        UDPServerSocket.sendto(str(1).encode(), address)        #Sending acknowledgment to client for sending complete data for requested chunk

        print("Index requested: ", index, ", By Client Number: ", client_no)
        #print("Client Number: ", cl_no)

        #global client_req_ind_dict

        #client_req_ind_dict[cl_no] = index


        
        TCPClientSocketFinal(client_no, index, serverPort + 10*(client_no-1),2048)       

        

        

        if index == -1:
            break



threads =[]
#startTime = time.time()
noOfThreads = 5

for i in range(noOfThreads):   
    x = threading.Thread(target=UDPServerSocketCreate, args=(i+1,localPort + (10*i),))
    threads.append(x)
    x.start()
    
#endTime = time.time()





for i in range(noOfThreads):
    threads[i].join()

# hash = hashlib.md5(open("./A2_small_file.txt", 'r').read().encode()).hexdigest()
# print("md5 sum:",hash)






#UDP ENDS





endTime = time.time()

print("Total time taken: ", endTime-startTime)