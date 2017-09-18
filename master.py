try:
	import os,sys,socket,threading,zipfile
except Exception as e:
	print(e)
	sys.exit(1)
finally:
    print("Imports Complete")
#process folder to make pair of data and code to be sent to slave
def processfolder(code='code.py',path=os.getcwd(),nodes=2):
	subprocess.run("mkdir node_file".split())
	d=os.listdir(path)
	t=os.getcwd()
	d.remove(code)
	lst=[d[i::nodes] for i in range(nodes)]
	[i.append(code) for i in lst]	
	print("Dividing into %d compress files. "%len(lst))
	os.chdir(path)
	for i in range(0,len(lst)):
		compress(lst[i],name="node_"+str(i+1))
		subprocess.run(("mv node_"+str(i+1)+" "+t+'/node_files').split())
		print("node_"+str(i+1)+".zip written")
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
	def __init__(self, host, port,nodes,secret):
		self.host = host
		self.port = port
		self.limit=nodes
		self.nodes={}
		self.secret=secret
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
		while len(self.nodes) != self.limit:
			client, address = self.sock.accept()
			threading.Thread(target = self.listenToClient,args = (client,address)).start()
			self.nodes[address[0]]=''
		#processfolder()
	def listenToClient(self, client, address):
		size = 102400
		try:
			data = client.recv(size).decode('utf-8')
			if data==self.secret:
				print("Slave Authenitcated")
				client.sendall("Authenitcated".encode('utf-8'))
				while True:
					data = client.recv(size).decode('utf-8')
					print(data)
					client.sendall(data.upper().encode('utf-8'))
		except:
			client.close()
			return False
if __name__ == "__main__":
	ip='localhost'
	port=9998
	d=1
	secret='shivam'	
	ThreadedServer('',port,d,secret).listen()
