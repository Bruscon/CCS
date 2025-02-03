# This file is executed on every boot (including wake-boot from deepsleep)
import esp
esp.osdebug(None)
import network
import gc, time
import webrepl
import webrepl_setup
webrepl.start()

try:
  import usocket as socket
except:
  import socket



def do_connect():
    ap_if = network.WLAN(network.AP_IF)
'''

    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        #PUT YOUR WIFI CREDENTIALS HERE:
        sta_if.connect('NAME', 'PASSWORD')
        while not sta_if.isconnected():
            pass
    print('network config:', sta_if.ifconfig())

'''
do_connect()
gc.collect() #maybe remove GC to save memory?

print("connected!")
for i in range(10):
    print(i)
    time.sleep(.2)
