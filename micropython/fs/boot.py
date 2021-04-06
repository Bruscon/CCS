# This file is executed on every boot (including wake-boot from deepsleep)
import esp
esp.osdebug(None)
import gc, time
import webrepl
webrepl.start()

def do_connect():
    import network
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        #sta_if.connect('EAC8F5', 'thedarkknight')
        sta_if.connect('Fios-J2m9Y', 'mod439coot532owl')
        while not sta_if.isconnected():
            pass
    print('network config:', sta_if.ifconfig())
'''
for i in range(10):
    print(i)
    time.sleep(1)
'''
do_connect()
gc.collect() #maybe remove GC to save memory?
'''
print("connected!")
for i in range(10):
    print(i)
    time.sleep(.3)
'''