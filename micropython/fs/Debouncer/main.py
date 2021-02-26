import time,machine

pin0 = machine.Pin(0,machine.Pin.IN, machine.Pin.PULL_UP)
pin2 = machine.Pin(2,machine.Pin.OUT)

global last_time
last_time = 0

def ISR(trigger_pin):
    global last_time
    this_time = time.time()
    if this_time-last_time > 1:
        print('toggle')
        if pin2.value():
            pin2.off()
        else:
            pin2.on()
    else:
        print('debounced')
    last_time = this_time
    
pin0.irq(trigger = machine.Pin.IRQ_FALLING, handler=ISR)
