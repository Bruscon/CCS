# -*- coding: utf-8 -*-
"""
Created on Wed Jan 27 15:10:49 2021

@author: Nick Brusco
"""
import socket, select, time, random

def interpret(data):
    '''takes foot movements and converts to chess moves'''
    row = ''
    column = ''
    
    if data[0] == 'A':
        if data[1] == 'A':
            column = 'A'
        elif data[1] == 'B': 
            column = 'B'
        else:
            print("INVALID INPUT")
    if data[0] == 'B':
        if data[1] == 'A':
            column = 'C'
        elif data[1] == 'B':
            column = 'D'
        else:
            print("INVALID INPUT")
    if data[0] == 'C':
        if data[1] == 'A':
            column = 'E'
        elif data[1] == 'B':
            column = 'F'
        else:
            print("INVALID INPUT")
    if data[0] == 'D':
        if data[1] == 'A':
            column = 'G'
        elif data[1] == 'B':
            column = 'H'
        else:
            print("INVALID INPUT")
    if data[2] == 'A':
        if data[3] == 'A':
            row = '1'
        elif data[3] == 'B':
            row = '2'
        else:
            print("INVALID INPUT")
    if data[2] == 'B': 
        if data[3] == 'A':
            row = '3'
        elif data[3] == 'B':
            row = '4'
        else:
            print("INVALID INPUT")
    if data[2] == 'C':
        if data[3] == 'A':
            row = '5'
        elif data[3] == 'B':
            row = '6'  
        else:
            print("INVALID INPUT")
    if data[2] == 'D':
        if data[3] == 'A':
            row = '7'
        elif data[3] == 'B':
            row = '8'
        else:
            print("INVALID INPUT")
            
    return column + row

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
    
 

while(1):
    ready = select.select([soc], [], [], 5000)
    if ready[0]:
        data = soc.recv(1024).decode("utf-8").strip('][').replace('\'','').split(', ')
        soc.send(bytes('ack', encoding = 'utf8'))
        if data[0] == '':
            time.sleep(3)
            soc = reconnect()
        elif data[0] == 'h':
            pass
            #print("heartbeat recieved")
        else:
            square = interpret(data)
            print(data, square)
    
    else:
        print("timeout occurred, attempting to reconnect...")
        soc = reconnect()