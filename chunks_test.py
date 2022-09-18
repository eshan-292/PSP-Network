CHUNK_SIZE = 1024 
chunk_no = 1

with open('A2_small_file.txt') as f:
    chunk = f.read(CHUNK_SIZE)
    while chunk:
        print("chunk no: ", chunk_no)
        print(chunk)
        #with open('my_song_part_' + str(file_number)) as chunk_file:
        #    chunk_file.write(chunk)
        chunk_no += 1
        chunk = f.read(CHUNK_SIZE)