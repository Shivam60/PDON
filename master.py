try:
	import os,sys,socket,threading,zipfile,subprocess,random,Networking
except Exception as e:
	print(e)
	sys.exit(1)
finally:
    print("Imports Complete")
#process folder to make pair of data and code to be sent to slave
def processfolder(code='code.py',path=os.getcwd(),nodes=2):
	t=os.getcwd()
	d=os.listdir(path)	
	os.chdir(path)
	subprocess.run("mkdir node_files".split())
	os.chdir("node_files")
	subprocess.run(("mkdir recieve").split())
	subprocess.run(("mkdir to_send").split())
	subprocess.run(("mkdir sent").split())
	os.chdir(path)
	d.remove(code)
	lst=[d[i::nodes] for i in range(nodes)]
	[i.append(code) for i in lst]	
	print("Dividing all data into ' %d ' compress files. "%len(lst))
	for i in range(0,len(lst)):
		compress(lst[i],name="node_"+str(i+1))
		subprocess.run(("mv node_"+str(i+1)+" "+path+'/node_files/to_send').split())
		print("Compressed Data for node_"+str(i+1)+" written")	
	os.chdir(t)
#compress a particular file or a list of files
def compress(lst,name):
	file = zipfile.ZipFile(name, "w")
	if type(lst)==list:
		for i in lst:
			file.write(i,os.path.basename(i),zipfile.ZIP_DEFLATED)
	else:
		file.write(lst,os.path.basename(lst),zipfile.ZIP_DEFLATED)
	file.close()
def uploader(filenm,dir):
	print("Preparing To upload")
	os.chdir(dir+r'/node_files')
	subprocess.run(("mkdir " + filenm+"_dir").split())
	subprocess.run(("mv " +filenm+" "+os.getcwd()+r'/'+filenm+"_dir").split())
	return filenm,str(os.getcwd()+r'/'+filenm+'_dir/')

class ThreadedServer(object):
	def __init__(self, host, port,nodes,secret,path):
		self.host = host
		self.port = port
		self.path = path
		self.limit = nodes
		self.nodes = {}
		self.node_limit=0
		self.port_used=[]
		self.secret = secret
		self.busy=False
		try:
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			self.sock.bind((self.host, self.port))
			self.port_used.append(port)		
		except Exception as e:
			print(e)	
		finally:
			print("Master is now running.")	
	def listen(self):
		self.sock.listen(self.limit)
		print("Processing the folder")
		processfolder('code.py',self.path,self.limit)
		print("Processing of the folder completed")
		while self.node_limit != self.limit:
			client, address = self.sock.accept()
			threading.Thread(target = self.listenToClient,args = (client,address)).start()
			self.nodes[address[0]]='node_'+str(len(self.nodes)+1)		
			self.node_limit+=1
	def listenToClient(self, client, address):
		size = 102400
		try:
			data = client.recv(size).decode('utf-8')
			if data==self.secret:
				print("Slave %s Authenitcated "%(str(address[0])))
				client.sendall("Authenitcated".encode('utf-8'))
				i=1
				while not os.path.exists(self.path+'/node_files/to_send/'+self.nodes[address[0]]):
					pass
				while self.busy==True:
					pass
				self.busy=True
				print("Initating Slave %s Data Transfer" %(str(address[0])))				
				subprocess.run(("mv "+self.path+'/node_files/to_send/'+self.nodes[address[0]]+" "+self.path+'/node_files/').split())
				client.sendall("READY".encode('utf-8'))
				data = client.recv(size).decode('utf-8')
				if data=='ACK':
					nf=True
					while nf:
						port=random.randint(999,9999)					
						while port in self.port_used:
							port=random.randint(999,9999)
						print("Communicating Slave %s with connection details"%address[0])					
						client.sendall((str(address[0])+' '+str(port)+' '+self.nodes[address[0]]).encode('utf-8'))
						data = client.recv(size).decode('utf-8')
						if data=='ACK':
							print("Slave is ready to recieve data")
							self.port_used.append(port)
							nf=False
					filenm,dir=uploader(filenm=self.nodes[address[0]],dir=self.path)
					c=Networking.client(host=address[0],port=port,filenm=filenm,secret=self.secret)
					c.begin(dir)
					self.busy=False
					subprocess.run(("mv "+self.path+'/node_files/'+self.nodes[address[0]]+"_dir/"+self.nodes[address[0]]+" "+self.path+'/node_files/sent/').split())
					subprocess.run(("rm -r "+self.path+'/node_files/'+self.nodes[address[0]]+"_dir/").split())
					data = client.recv(size).decode('utf-8')
					if data=='ACK':
						print("Slave node %s has recived data sucessfully. "%address[0])
						print("Waiting for slave %s to send output back"%address[0])
						try:
						  print("mkdir "+self.path+'node_files/recieve/'+filenm)
						  subprocess.run(("mkdir "+self.path+'node_files/recieve/'+filenm).split())
						except:
						  input("error")
						serv=Networking.server(host=ip,port=int(port)+1,packetsize=65536,filenm=filenm,sever_directory=self.path+'node_files/recieve/'+filenm+'/')    
						serv.handshake(self.secret)
						print('Output Recieved.')
						client.sendall("ACK".encode('utf-8'))					
				else:
					print("Error: "+data)
				print("Finishing the output. ")
				for i in os.listdir(self.path+'node_files/recieve/'+filenm+'/'):
					subprocess.run(('rename "s/'+str(i)+'/'+str(i)+'.mp3/g" *').split())
		except:
			client.close()
			return False
if __name__ == "__main__":
	ip='192.168.43.72'
	port=9928
	d=1
	secret='shivam'	
	ThreadedServer('',port,d,secret,path='/home/dharmendra/Desktop/master/').listen()
