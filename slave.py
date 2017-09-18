try:
	import os,sys,socket,subprocess,zipfile
except Exception as e:
	print(e)
	sys.exit(1)
finally:
    print("Imports Complete")

class client():
    def __init__(self,port,ip,secret):
        self.port=port
        self.host=ip
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
        pass
def decompress(zippedfile):
    subprocess.call("mkdir input".split())
    zap=zipfile.ZipFile(zippedfile)
    for files in zap.namelist():
        zap.extract(files,os.getcwd()+"/input")
if __name__=="__main__":
    port=9998
    ip='localhost'
    secret='shivam'
    c=client(port,ip,secret)
    c.sendmsg(c.secret)
    if c.recvmsg()=='Authenitcated':
        print("Master has authenticated the slave")
        while True:
            p=input("Enter Message to send: ")
            if p!='close':
                c.sendmsg(p)
                print("Reply From server: "+c.recvmsg())
            else:
                c.sendmsg('close')
            