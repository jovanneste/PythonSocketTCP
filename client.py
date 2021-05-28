import socket 
import sys
import hashlib # used to compute checksum of files
from PIL import Image # used to display images


# function returns checksum of a given file
def getChecksum(filename):
	with open(filename, "rb") as f:
		bytes = f.read()
		# creates a hash code using md5 encryption and puts it in hexadecimal
		readableHash = hashlib.md5(bytes).hexdigest()
	return readableHash


# main function to connect to socket and send and recieve files 
def Main(csocket):
	# connect to server socket
	cli_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
	cli_sock.connect((sys.argv[1], csocket)) 
	print("Connected - ")

	# check if there is a third arguement
	try:
		if sys.argv[3] == "put":
			# code for client to upload a file to server 
			# start by sending server "put" so the server knows what the client wants to do
			s = "put"
			cli_sock.sendall(s.encode('utf-8'))

			# send server the calculated checksum of the file the client wants to upload 
			filename = sys.argv[4] 
			checksum = getChecksum(filename)
			cli_sock.sendall(checksum.encode('utf-8'))
			
			# open binary version of file and send data over 
			f = open(filename,"rb")
			bits = f.read(1024)
			while (bits):
				cli_sock.sendall(bits)
				print("Sending data...")      			
				bits = f.read(1024)
			f.close()
			# file finishes uploading

			print("File "+ filename + " sent")
			cli_sock.close()

		elif sys.argv[3]=="get":
			# code for client to downlaod a file to server 
			# client decides name of new file, will not allow client to  
			# overwrite a file which already exists
			done = False
			while(not done):
				userFilename = input("What would you like to call the file?: ")
				try:
					f = open(userFilename)
					f.close()
					print("File already exists, choose another file name.")
				except FileNotFoundError:
					done = True

			# code for client to download file from server
			# start by sending sever "get" so the server knowns that the client wants to do
			s = "get"
			cli_sock.sendall(s.encode('utf-8'))
			cli_sock.recv(1024).decode('utf-8') 

			# send to server name of file the client wants to download
			filename = sys.argv[4]
			cli_sock.sendall(filename.encode('utf-8'))

			# recieve checksum for that file from server
			srvChecksum = cli_sock.recv(1024).decode('utf-8') 

			# open a new file in binary mode to write data
			with open(userFilename, "wb") as f:
				while True:
					print("Receiving data...")
					data = cli_sock.recv(1024)
					if not data:
						break
					f.write(data)
					print("Writing")
			f.close() 
			# all data has now been downloaded and written to file

			# computes checksum of the file it has created
			cliChecksum = getChecksum(userFilename)

			# checks the checksum received earlier from server agaisnt the 
			# checksum of the file that data has been written to 
			if srvChecksum == cliChecksum:
				print("Successfully recieved and written to file")
				try:
					# if the file that was downlaoded from the server was a picture 
					img = Image.open(userFilename)
					imgOpen = input("Do you want to open the image that you have been sent? (y/n): ")
					if imgOpen == "y":
						# open uploaded picture
						img.show()
					elif imgOpen == "n":
						print("Okay, closing connection.")
				except:
					pass
				cli_sock.close()
				
			else:
				# if the checksums don't match
				print("WARNING: some file data lost")
				cli_sock.close()


		elif sys.argv[3] == "list":
			# code for if client wants to see a list of possible files server can send
			fileList = []
			s = "list"
			cli_sock.sendall(s.encode('utf-8'))
			# loop to recieve and add each file name to an array as they come
			while (True):
				file = cli_sock.recv(1024).decode('utf-8')
				if file == "done":
					break
				else:
					fileList.append(file)
				
			# display all file names client received 
			for i in fileList:
				print(i)
				
			cli_sock.close()


	# if there is no third arguement ie client doesn't want to upload or download files
	except:

		# start by sending "notfile" so server knows what client wants to do
		s = "notfile"
		cli_sock.sendall(s.encode('utf-8'))

		# send client's name to server and receive server's name
		name = input("Name: ")
		print("Waiting for connection")
		srv_name = cli_sock.recv(1024).decode('utf-8')
		print(srv_name + " has connected to chat")
		cli_sock.sendall(name.encode('utf-8'))


		# loop to recieve and send messages
		done = True
		while (done == True):
			try:
				request = cli_sock.recv(1024)

				print(srv_name +": " + request.decode('utf-8'))
				message = input("Me: ")
				if message == "QUIT":
					cli_sock.close()
				else:
					cli_sock.sendall(message.encode('utf-8'))

			# if the socket has disconnected 
			except:
				userAnswer = input("The socket has disconnected, would you like to reconnect? (y/n): ")
				if userAnswer == "y":
					# connect to a new socket with the last port number +1
					Main(int(csocket)+1)
				elif userAnswer == "n":
					print("Okay, closing socket")
					cli_sock.close()
					done = False
					
# calls main function to start program
Main(int(sys.argv[2]))

