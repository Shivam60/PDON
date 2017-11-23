try:
	import os,sys,socket,subprocess,Networking,time,zipfile
except Exception as e:
	print(e)
	sys.exit(1)
finally:
    print("Imports Complete")
#return the uncompressed version of the data
def decompress(filenm,dir):
    t=os.getcwd()
    os.chdir(dir)
    z=zipfile.ZipFile(filenm)
    z.extractall()
    z.close()
    os.chdir(t)
def compress(lst,name):
	file = zipfile.ZipFile(name, "w")
	if type(lst)==list:
		for i in lst:
			file.write(i,os.path.basename(i),zipfile.ZIP_DEFLATED)
	else:
		file.write(lst,os.path.basename(lst),zipfile.ZIP_DEFLATED)
	file.close()    
class client():
    def __init__(self,port,ip,secret,path):
        self.port=port
        self.host=ip
        self.path=path
        self.secret=secret
        try:
            self.sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((ip,port))
        except Exception as e:
            print(e)
            os._exit(0)
        finally:
            print("Slave is now Running")
    def sendmsg(self,msg):
        try:
            self.sock.sendall(msg.encode('utf-8'))
        except Exception as e:
            print(e)
            os._exit(0)
    def recvmsg(self):
        return self.sock.recv(65656).decode('utf-8')
    def start(self):
        self.sendmsg(self.secret)
        if self.recvmsg()=="Authenitcated":
            print("Slave Authenitcated")
            if self.recvmsg()=="READY":
                self.sendmsg("ACK")
                print("Setting Recieving Server. ")
                try:
                    ip,port,filenm=self.recvmsg().split()
                    t=os.getcwd()
                    os.chdir(self.path)
                    serv=Networking.server(host=ip,port=int(port),packetsize=65536,filenm=filenm,sever_directory=self.path)    
                except e as Exception:
                    print(e)
                    nf=True
                    self.sendmsg("ERROR")
                finally:
                    self.sendmsg("ACK")
                    print("Server Set, Waiting For Data")
                    serv.handshake(self.secret)
                self.sendmsg("ACK")
                decompress(filenm=filenm,dir=os.getcwd())
                subprocess.run(("rm "+filenm).split())
                ls=os.listdir()
                ls.remove('code.py')
                print(os.getcwd())
                for i in ls:
                    subprocess.run(("python code.py "+ str(i)).split())
                    subprocess.run(("rm "+str(i)).split())
                subprocess.run(("rm code.py").split())
                ls=os.listdir()
                compress(ls,"output")
                input("enter")
                c=Networking.client(host=self.host,port=int(port)+1,filenm='output',secret=self.secret)
                c.begin(os.getcwd()+'/')
                for i in os.listdir():
                    try:
                        subprocess.call("rm "+str(i))
                    except:
                        try:
                            subprocess.call("rm -r"+str(i))
                        except:
                            pass                
                os.chdir(t)
                if self.recvmsg()=="ACK":
                    print("Output recieved. Slave Shutting Down")
            else:
                self.sendmsg("ERROR")          
if __name__=="__main__":
    port=9927
    ip='10.42.0.180'
    secret='shivam'
    path='/home/shivam/Work/Projects/test/slave/'
    client(port,ip,secret,path).start()
    os.chdir(path)    
    print(os.listdir()) 

