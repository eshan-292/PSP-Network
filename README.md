# PSP-Network
The goal is to build a PSP network, that distributes the desired file to all the peers, starting with some distribution of file chunks among them


This PSP network is similar to a P2P file distribution framework. Traditional P2P, or peer-to-peer networks work with minimal to no reliance on a central server. Each connected node in the network, also called a “peer”, is a user device: a laptop, PC, phone etc. These peers communicate by direct message passing instead of needing a shared server. A common P2P file sharing application is BitTorrent. Put in simple terms, peers in the network connect to other peers to request the missing parts of file they want. These peers also act as servicers by being open to sharing the parts of file they already possess.
This project is a simplified communication, which passes through a central server. The server will act as a mediator to facilitate data transfer among peers. Hence the name PSP network.


- Simulated a server and n clients (separate scripts are written for the simulation of server and client, in the client script, multiple clients have been implemented using threads).

- The server divides the file into n disjoint but exhaustive chunks 3 and distributes one chunk to each client. At this point, each client should have one chunk, and no pair of clients should have any overlapping information

- Server deletes the file. Thus now, the server has no data with it

In the process that follows, each client operates independently. From now on, each chunk of data exchanged would be of 1 Kilobytes. The simulation ends when each client has obtained all the chunks required to construct the file. The server ‘S’ has a cache installed, following LRU policy 4. This cache has a fixed size of n Kilobytes. S cannot store any other data outside this cache. Following is the process for each client:
(a) Client ‘p’ identifies what chunk of file it doesn’t have. Call it chunk ‘c’.
(b) p sends a UDP message to S, requesting c
(c) S checks its cache for c. If the query results in a hit, it opens up a TCP connection with p and shares c with p
(d) If the cache query results in a miss, the server sends a broadcast 5 to all clients, requesting c.
(e) When a client receives a broadcast, it sends c to S through a TCP connection if it has it. If the client does not have the requested chunk, it ignores the broadcast.
(f) S receives c from (possibly) multiple clients. It discards the duplicates, adds c to its cache, and sends it back to p via TCP.
(g) p, on receiving c, adds it to its available chunks. It checks if it now has the complete file. If not, it repeats steps 5.a-5.g.


Explicitly handled packet loss in case of UDP commuication owing to its unreliability. 
