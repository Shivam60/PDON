try:
	import os,sys,scapy
	from scapy.all import*

except Exception as e:
	print(e)
	sys.exit(1)

def scannodes(interface='wlps20'):
	nf=True
	try:
		ip=os.popen('ip a | grep "wlp2s0" | grep "inet" | cut -b 10-25').read().split('\n')[0]
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

