# -*- coding: utf-8 -*-
"""
Created on Wed Jan 27 15:10:49 2021

@author: Nick Brusco
"""
import socket, select, time, random
import ches


def reconnect():
    soc = socket.socket()
    soc.connect(("192.168.0.118", 80))
    #soc.send(bytes("sup", encoding = 'utf8'))
    print("recieved from ESP: ", soc.recv(1024))
    return soc
 
soc = reconnect()
square = ''


while(1):
    try:
        (soc.recv(1024).decode("utf-8").strip('][').replace('\'','').replace(' ','').replace(',',''))
    except:
        soc = reconnect()
        continue
    print("\n\n")
    time.sleep(1.5)
    msg = random.choice("ABCD") + random.choice("ABCD") + random.choice("ABCD") + random.choice("ABCD")
    try:
        soc.send(bytes(msg, encoding = 'utf8'))
    except:
        soc = reconnect()
        continue
    reply = soc.recv(1024).decode("utf-8").strip('][').replace('\'','').replace(' ','').replace(',','')
    print("You said          : ", reply)
    print("Correct answer was: ", msg)
    print("\n\n")
    
    time.sleep(1.0)
    try:
        if reply == msg:
            soc.send(bytes("E",encoding='utf8'))
        else:
            soc.send(bytes("FFF",encoding='utf8'))
    except:
       soc = reconnect()
       continue
    
