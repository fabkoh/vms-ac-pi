import psutil

for interface, data in psutil.net_if_addrs().items(): 
    addr = data[0]
    print('interface:', interface)
    print('address  :', addr.address)
    print('netmask  :', addr.netmask)
    print('broadcast:', addr.broadcast)
    print('---')