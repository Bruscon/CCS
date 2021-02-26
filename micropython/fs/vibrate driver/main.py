#demonstrates using gpio0 as an input and an output, depending on gpio2's state

import time,machine

pin0 = machine.Pin(0,machine.Pin.OUT)
pin2 = machine.Pin(2,machine.Pin.IN)

button_state = 'unpressed'
last_press = 0

while(1):
    if pin2.value():
        pin0 = machine.Pin(0,machine.Pin.OUT)
    
        if time.ticks_ms() - last_press > 500:
            
            last_press = time.ticks_ms()
            
            if pin0.value():
                pin0.off()
            else:
                pin0.on()
        
    else:
        pin0 = machine.Pin(0,machine.Pin.IN)
        
        if not pin0.value() and button_state == 'unpressed' and time.ticks_ms()-last_press > 50:
            last_press = time.ticks_ms()
            button_state = 'pressed'
            print('pressed')
        
        if pin0.value() and button_state == 'pressed' and time.ticks_ms()-last_press > 50:
            last_press = time.ticks_ms()
            button_state = 'unpressed'
            print('unpressed')
            

pin0.off()