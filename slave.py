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
                for i in ls:
                    subprocess.call("python code.py"+ str(i))
                os.chdir(t)
             
            else:
                self.sendmsg("ERROR")          
if __name__=="__main__":
    port=9998
    ip='localhost'
    secret='shivam'
    path='/home/shivam/Work/Projects/test/slave/'
    client(port,ip,secret,path).start()
    