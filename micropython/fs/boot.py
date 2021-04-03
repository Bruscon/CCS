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
        sta_if.connect('EAC8F5', 'thedarkknight')
        while not sta_if.isconnected():
            pass
    print('network config:', sta_if.ifconfig())

do_connect()
gc.collect()


for i in range(10):
    print(i)
    time.sleep(.3)
