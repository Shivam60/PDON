try:
	import os,sys,socket,threading,zipfile,subprocess,random,Networking
	from Networking import client
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
	d.remove(code)
	lst=[d[i::nodes] for i in range(nodes)]
	[i.append(code) for i in lst]	
	print("Dividing all data into ' %d ' compress files. "%len(lst))
	for i in range(0,len(lst)):
		compress(lst[i],name="node_"+str(i+1))
		print(subprocess.run(("mv node_"+str(i+1)+" "+path+'/node_files/').split()))	
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

def scannodes(interface='wlps20'):
	nf=True
	try:
		ip=os.popen('ip a | grep "wlp2s0" | grep "inet" ').read().split()[1]
		print("Local IP %s address on %s " %(ip,interface))
		answered,unanswered=srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=ip), timeout=2, verbose=0)
	except Exception as e:
		nf=False
		print(e)
	finally:
		if nf:
			d={}
			for i in range(0,len(answered)):
					d[str(answered[i][1].psrc)]=str(answered[i][1].hwsrc)
			return d
		return -1

class ThreadedServer(object):
	def __init__(self, host, port,nodes,secret,path):
		self.host = host
		self.port = port
		self.path = path
		self.limit = nodes
		self.nodes = {}
		self.port_used=[]
		self.secret = secret
		self.commands = {
			1:"Ready".encode('utf-8'),
			2:"Port".encode('utf-8'),
			3:"IP".encode('utf-8')
		}
		try:
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			self.sock.bind((self.host, self.port))
		except Exception as e:
			print(e)	
		finally:
			print("Master is now running.")	
	def listen(self):
		self.sock.listen(self.limit)
		threading.Thread(target = processfolder,args = ('code.py',self.path,self.limit)).start()
		while len(self.nodes) != self.limit:
			client, address = self.sock.accept()
			threading.Thread(target = self.listenToClient,args = (client,address)).start()
			self.nodes[address[0]]='node_'+str(len(self.nodes)+1)		
	def listenToClient(self, client, address):
		size = 102400
		try:
			data = client.recv(size).decode('utf-8')
			if data==self.secret:
				print("Slave %s Authenitcated "%(str(address[0])))
				client.sendall("Authenitcated".encode('utf-8'))
				i=1
				while not os.path.exists(self.path+'/node_files/'+self.nodes[address[0]]):
					pass
				print("Initating Slave %s Data Transfer" %(str(address[0])))
				client.sendall("READY".encode('utf-8'))
				data = client.recv(size).decode('utf-8')
				if data=='ACK':
					while True:
						port=random.randint(999,9999)					
						while port in self.port_used:
							port=random.randint(999,9999)
						print("Communicating Slave %s with connection details"%address[0])					
						self.port_used.append(port)
						client.sendall((str(address[0])+' '+str(port)).encode('utf-8'))
						data = client.recv(size).decode('utf-8')
						if data=='ACK':
							print("ACK")
							break
					clin=client(host='localhost',port=port,filenm='self.nodes[address[0]]')
					clin.begin(client_directory=self.path)
					clin.handshake(self.secret)
		except:
			client.close()
			return False
if __name__ == "__main__":
	ip='localhost'
	port=9998
	d=2
	secret='shivam'	
	ThreadedServer('',port,d,secret,path='/home/shivam/Work/Projects/test/master').listen()
