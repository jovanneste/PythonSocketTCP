import socket
import sys
import hashlib # used to compute checksum of files
from PIL import Image # used to display images
import os # used to get files in the same directory 
import time # used to stop the program momentarily


# function returns checksum of a given file
def getChecksum(filename):
	with open(filename, "rb") as f:
		bytes = f.read()
		# creates a hash code using md5 encryption and puts it in hexadecimal
		readableHash = hashlib.md5(bytes).hexdigest()
	return readableHash



# main function to create socket and send and recieve files 
def Main(ssocket): 
	# attempt to create socket
	try:
		srv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
		srv_sock.bind(("", (ssocket)))
	except:
		# is there's an error get a new port number an try create a new subject
		newSocket = input("Socket is already in use, enter a new port number: ")
		Main(int(newSocket))

	# wait for client to connect 
	print("Server up and running, port number: "+ str(ssocket) +"\nWaiting for client to connect...")
	srv_sock.listen(5)
	cli_sock, cli_addr = srv_sock.accept()
	print("Connected - ")

	# recieves a word from client to know what the client wants to do
	firstRequest = cli_sock.recv(1024).decode('utf-8')


	if (firstRequest == "put"):
		# if client want to upload to server 
		# server recives client's computed checksum of file it is about to send
		cliChecksum = cli_sock.recv(1024).decode('utf-8')
		
		# open a new file in binary to write data to
		with open("ClientToServer.txt", "wb") as f:
		    while True:
		        print('Receiving data...')
		        data = cli_sock.recv(1024)
		        if not data:
		            break
		        # write data to a file
		        f.write(data)
		        print("Writing")
		f.close()
		# all data has been written to file

		# compute checksum of the new file
		srvChecksum = getChecksum("ClientToServer.txt")

		# check the computed checksum of new file against recieved checksum of client
		if cliChecksum == srvChecksum:
			print("Successfully recieved and written to file")
			cli_sock.close()
			try:
				# if the file that was uploaded to server was a picture 
				img = Image.open("ClientToServer.txt")
				imgOpen = input("Do you want to open the image that you have been sent? (y/n): ")
				if imgOpen == "y":
					# open uploaded picture
					img.show()
				elif imgOpen == "n":
					print("Okay, closing connection.")
			except:
				pass
			srv_sock.close()
		else:
			# if the checksums don't match
			print("WARNING: some file data lost")
			srv_sock.close()

	elif (firstRequest == "get"):
		# if client wants to download a file
		cli_sock.sendall("yes".encode('utf-8'))

		# receive filname from client 
		filename = cli_sock.recv(1024).decode('utf-8')

		# send checksum of file the client wants to download
		checksum = getChecksum(filename)
		cli_sock.sendall(checksum.encode('utf-8'))
		
		# open file in binary mode and send data to client
		f = open(filename,"rb")
		bits = f.read(1024)
		while (bits):
			cli_sock.sendall(bits)    
			print("Sending data...")  			
			bits = f.read(1024)
		f.close()
		print("File "+ filename + " sent")
		srv_sock.close()
		# all file data send to client


	elif (firstRequest == "list"):
		# if client wants to see list of files in server directory
		# server gets a list of files and recusively sends them to client
		fileList = os.listdir()
		for i in fileList:
			# condition to not send any python files that are in the same directory
			if i.endswith(".py"):
				pass
			else:
				cli_sock.sendall(i.encode('utf-8'))
				# pauses for 0.01 seconds to allow client to receive previous file name
				time.sleep(0.01)
		cli_sock.sendall("done".encode('utf-8'))
		print("All files send")
		
		srv_sock.close()
		# all file names are sent and the connection is closed

	else:
		# if client doesn't want to upload or download files
		# send server's name to client and receive client's name
		name = input("Name: ")
		cli_sock.sendall(name.encode('utf-8'))
		cli_name = cli_sock.recv(1024).decode('utf-8')
		print(cli_name + " has connected to chat")



		# loop to recieve and send messages
		done = True
		while (done == True):
			try:
				message = input("Me: ")
				if message == "QUIT":
					print("Exiting chat")
					srv_sock.close()
					done = False
				else:
					cli_sock.sendall(message.encode('utf-8'))
					request = cli_sock.recv(1024)
					print(cli_name + ": " + request.decode('utf-8'))
			# if the socket has disconnected 
			except:
				userAnswer = input("The socket has disconnected, would you like to re-open it? (y/n): ")
				if userAnswer == "y":
					# create a new socker with the last port number +1
					Main(int(ssocket)+1)
				else:
					print("Okay, closing socket")
					srv_sock.close()
					done = False
					
# calls main function to start program
Main(int(sys.argv[1]))
print("DONE")