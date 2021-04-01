import time, machine, struct, math, socket, gc

#hard-coded registers:
MPU6050_RA_PWR_MGMT_1 = 0x6B
MPU6050_RA_CONFIG = 0x1A
ACCEL_XOUT_H = 0x3B
GYRO_XOUT_H = 0x43
MPU = 0x68

US_TO_S     = 10**6
RAD_TO_DEG  = 180 / math.pi

#initialize variables
fusion_ypr  =    [0.0, 0.0, 0.0]
target_period = .01 #seconds
command = []
state = 'get 1st in'
paused = False
not_GH_yet = False


class Soc :
    def __init__(self):
        self.last = 'A'
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.soc.bind(('', 80))
        self.soc.listen(5)
        self.conn, self.addr = self.soc.accept()
        self.conn.settimeout(0)
        #time.sleep(.4)
        #print("Msg from desktop: ", self.conn.recv(1024))
        self.conn.sendall("ready")
        
    def send_command(self):
        gc.collect()
        self.conn.sendall(str(command))
        self.st = time.ticks_us()
        
    def rx(self,vib):
        try:
            message = self.conn.recv(1024)
            print(message)
        except:
            return
        
        if len(message) == 1:#single chars
            message = message.decode("utf-8").strip('][').replace('\'','')
        else:#lists
            message = list(message.decode("utf-8").strip('][').replace('\'','').replace(' ','').replace(',',''))
            
        vib.send(message)
        self.last = message
            

    def repeat_last(self,vib):
        vib.send(self.last)
            
        
    
class Vibrator :
    def __init__(self):
        self.vib_enabled = False 
        self.vibq = []
        self.vibstep = 0
        self.vibdeadline = 100**10 #infinite
        self.SHORT_INT = .13
        self.LONG_INT = .3
        
        self.disable_serial()
        
    def disable_serial(self):
        self.vib1 = machine.Pin(1, machine.Pin.OUT)
        self.vib2 = machine.Pin(3, machine.Pin.OUT)
        self.vib_enabled = True
        
    def send(self, out):
        if not self.vib_enabled: return
        if type(out) == str:
            self.vibq.append(out)
        else:
            self.vibq.extend(out)
        if self.vibstep == 0:
            self.vibdeadline = 0
        
    def step(self):
        tme = time.ticks_us()
        if self.vib_enabled and (tme >= self.vibdeadline):
            if len(self.vibq) > 0 and self.vibstep == 0: #start new command
                if self.vibq[0] in ['A', 'C', 'E', 'F']:
                    self.vib1.on()
                    if self.vibq[0] in ['A','E']:
                        self.vibdeadline = tme + (self.LONG_INT *US_TO_S)
                    else:
                        self.vibdeadline = tme + (self.SHORT_INT *US_TO_S)
                if self.vibq[0] in ['B','D','E','F']:
                    self.vib2.on()
                    if self.vibq[0] in ['B','E']:
                        self.vibdeadline = tme + (self.LONG_INT *US_TO_S)
                    else:
                        self.vibdeadline = tme + (self.SHORT_INT *US_TO_S)
                if self.vibq[0] in ["_"]: #pause
                    self.vib1.off()
                    self.vib2.off()
                    self.vibdeadline = tme + (self.SHORT_INT * US_TO_S)
                self.vibstep = 1
            
            else:
            
                if self.vibq[0] in ['A', 'B','E']:
                    self.vib1.off()
                    self.vib2.off()
                    self.vibq.pop(0)
                    self.vibstep = 0
                elif self.vibstep == 1:
                    self.vib1.off()
                    self.vib2.off()
                    self.vibstep = 2
                    self.vibdeadline = tme + (self.SHORT_INT *US_TO_S)
                elif self.vibstep == 2:
                    if self.vibq[0] in ['C','F']:
                        self.vib1.on()
                    if self.vibq[0] in ['D','F']:
                        self.vib2.on()
                    self.vibstep = 3
                    self.vibdeadline = tme + (self.SHORT_INT *US_TO_S)
                elif self.vibstep == 3:
                    self.vib1.off()
                    self.vib2.off()
                    self.vibq.pop(0)
                    self.vibstep = 0
                if self.vibq == []: #last command
                    self.vibdeadline = 100**10
                elif self.vibstep == 0: #more commands to do 
                    self.vibdeadline = tme + (self.LONG_INT *US_TO_S)
            
        
        
def calib_IMU(samples):
    print('Calib IMU...')
    xoffset, yoffset, zoffset, G_cal = 0, 0, 0, 0
    xac, yac, zac = 0,0,0
    resting_ypr = [0,0,0]
    
    for i in range(samples):
        data = i2c.readfrom_mem(MPU, ACCEL_XOUT_H, 14 )
        xac += struct.unpack('>h', data[0:2])[0]
        yac += struct.unpack('>h', data[2:4])[0]
        zac += struct.unpack('>h', data[4:6])[0]
        
        xoffset += struct.unpack('>h', data[8:10])[0]
        yoffset += struct.unpack('>h', data[10:12])[0]
        zoffset += struct.unpack('>h', data[12:14])[0]
        time.sleep(.01)
        
    xoffset /= samples
    yoffset /= samples
    zoffset /= samples
    
    xac /= samples
    yac /= samples
    zac /= samples
    
    resting_ypr[1] = math.atan( yac / math.sqrt(xac**2 + zac**2)) * RAD_TO_DEG
    resting_ypr[2] = math.atan(-1 * xac / math.sqrt(yac**2 + zac**2)) * RAD_TO_DEG
    
    G_cal = math.sqrt(xac**2 + yac**2 + zac**2)
    
    return xoffset, yoffset, zoffset, G_cal, resting_ypr

#start I2C with MPU6050
i2c = machine.I2C(scl=machine.Pin(0), sda=machine.Pin(2), freq = 400000)

i2c.writeto_mem(MPU, MPU6050_RA_PWR_MGMT_1, bytearray(0x80) )   #reset device
time.sleep(.1)
i2c.writeto_mem(MPU, MPU6050_RA_PWR_MGMT_1, bytearray(0x01) )   #wake-up, set Xgyro as clk
time.sleep(.5)
i2c.writeto_mem(MPU, MPU6050_RA_CONFIG, bytearray(0b00000001))  #set DLPF to 1
time.sleep(.1)


soc = Soc()
vib = Vibrator()
xoffset, yoffset, zoffset, G_cal, resting_ypr = calib_IMU(100)
fusion_ypr = resting_ypr.copy()
print('Ready')

old_time = time.ticks_us()
while(1):
    #calculates time delta between data frames
    new_time = time.ticks_us()
    delta = new_time - old_time
    old_time = new_time
    
    #reads all accel, temp, gyro registers
    data = i2c.readfrom_mem(MPU, ACCEL_XOUT_H, 14 )    
    
    #converts binary dump into gyro/accel/temp data
    xac  = struct.unpack('>h', data[0:2])[0] / G_cal
    yac  = struct.unpack('>h', data[2:4])[0] / G_cal
    zac  = struct.unpack('>h', data[4:6])[0] / G_cal
    temp = struct.unpack('>h', data[6:8])[0]
    xgy  = struct.unpack('>h', data[8:10])[0]   - xoffset 
    ygy  = struct.unpack('>h', data[10:12])[0]  - yoffset
    zgy  = struct.unpack('>h', data[12:14])[0]  - zoffset
    
    #print(xac, "\n", yac, "\n", zac, "\n", temp, "\n", xgy, "\n", ygy, "\n", zgy,"\n\n\n")
    
    #calculate euler angles
    mag_G = math.sqrt(xac**2 + yac**2 + zac**2) #16384 = 1G
    if (mag_G < 1.2 and mag_G > .8):
        accel_p = math.atan( yac / math.sqrt(xac**2 + zac**2)) * RAD_TO_DEG
        accel_r = math.atan(-1 * xac / math.sqrt(yac**2 + zac**2)) * RAD_TO_DEG
    
        fusion_ypr[0] = (fusion_ypr[0] + ( delta / US_TO_S )  *  ( zgy / 131 ))
        fusion_ypr[1] = (fusion_ypr[1] + ( delta / US_TO_S )  *  ( xgy / 131 ))*.95 + accel_p*.05
        fusion_ypr[2] = (fusion_ypr[2] + ( delta / US_TO_S )  *  ( ygy / 131 ))*.95 + accel_r*.05
    else:
        fusion_ypr[0] = (fusion_ypr[0] + ( delta / US_TO_S )  *  ( zgy / 131 ))
        fusion_ypr[1] = (fusion_ypr[1] + ( delta / US_TO_S )  *  ( xgy / 131 ))
        fusion_ypr[2] = (fusion_ypr[2] + ( delta / US_TO_S )  *  ( ygy / 131 ))
    
    #print('mag G: ',  mag_G, "\tpitch: ", fusion_ypr[1], "\tresting pitch: ")
    
    #print( round(fusion_ypr[1]- resting_ypr[1]), " ", round(fusion_ypr[2]- resting_ypr[2]), " ", round(zgy/1000) )
    
    #state machine
    if paused:
        print(fusion_ypr[2] - resting_ypr[2])
        if fusion_ypr[2] - resting_ypr[2] < -50:
            vib.send('F')
            command = []
            print('Unpaused')
            paused = False
            state = 'to flat'
    else:
        if state == 'get 1st in':
            if fusion_ypr[1] - resting_ypr[1] < -14.0 and (fusion_ypr[2] - resting_ypr[2]) < 7:
                command.append('A')
                vib.send(command[-1])
                state = 'get 2nd in'
            elif fusion_ypr[1] - resting_ypr[1] > 9.5 and abs(fusion_ypr[2] - resting_ypr[2]) < 9:
                command.append('B')
                vib.send(command[-1])
                state = 'get 2nd in'
            elif zgy < -15000:
                print('input:  C')
                command.append('C')
                vib.send(command[-1])
                state = 'to flat'
            elif zgy > 15000:
                print('input:  D')
                command.append('D')
                vib.send(command[-1])
                state = 'to flat'
            elif fusion_ypr[2] - resting_ypr[2] > 18:
                command.append("E")
                vib.send('E')
                state = 'get 2nd in'
                print("starting E")
            elif fusion_ypr[2] - resting_ypr[2] < -30:
                command.append("F")
                vib.send('F')
                state = 'get 2nd in'


        if state == 'to flat':
            if ( abs(fusion_ypr[1] - resting_ypr[1]) < 9 ) and \
               ( abs(fusion_ypr[2] - resting_ypr[2]) < 9 ) and \
               ( zgy > -4000 ) and ( zgy < 4000 ) :
                state = 'get 1st in'

        if state == 'get 2nd in':
            if ( abs(fusion_ypr[1] - resting_ypr[1]) < 9 ) and \
            ( abs(fusion_ypr[2] - resting_ypr[2]) < 9 ) and \
            ( zgy > -4000 ) and ( zgy < 4000 ) :
                print( "input: ", command[-1] )
                state = 'get 1st in'

            elif command[-1] == "E":
                if fusion_ypr[1] - resting_ypr[1] < -30.0:
                    print('input:  DELETE')
                    command.pop(-1)
                    if len(command) > 0:
                        command.pop(-1)
                    vib.send("A")
                    state = 'to flat'
                elif fusion_ypr[1] - resting_ypr[1] > 2.0:
                    print('input: CLEAR')
                    command = []
                    vib.send("B")
                    state = 'to flat'

            elif command[-1] == "F":
                if fusion_ypr[1] - resting_ypr[1] < -17.0:
                    print('input:   G')
                    command.pop(-1)
                    command.append('G')
                    vib.send("A")
                    state = 'to flat'
                elif fusion_ypr[1] - resting_ypr[1] > 10.0:
                    print('input:  H')
                    command.pop(-1)
                    command.append('H')
                    vib.send("B")
                    state = 'to flat'

                if fusion_ypr[2] - resting_ypr[2] < -70:
                    vib.send('F')
                    command = []
                    print("Paused")
                    paused = True
                    state = 'to flat'

            elif command[-1] == 'A':
                if zgy < -18000:
                    print("Sending command")
                    state = 'send command'
                    command.pop(-1)
                elif zgy > 15000:
                    print("Repeating last")
                    soc.repeat_last(vib)
                    command.pop(-1)
                    state = 'to flat'
                elif fusion_ypr[2] - resting_ypr[2] < -45:
                    print("clearing command")
                    command = []
                    vib.send("F")
                    state = 'to flat'

            elif command[-1] == 'B':
                if zgy < -7000:
                    print("input:  I")
                    vib.send(["F","F"])
                    command = []
                    print("Paused")
                    paused = True
                    state = 'to flat'

                elif zgy > 7000:
                    print("input:  J")
                    command.pop(-1)
                    time.sleep(2)
                    calib_IMU(100)
                    vib.send(["E","E"])
                    state = 'to flat'



        if state == 'send command':
            print("command: ", command)
            soc.send_command()
            command = []
            state = 'to flat'
        
        
 
    soc.rx(vib)
    vib.step()
    
    interval = ((target_period * US_TO_S) - (time.ticks_us() - old_time)) / US_TO_S 
    if interval>0 and interval < target_period:
        time.sleep(interval)
    elif interval < 0:
        print('too slow! ', interval)
    elif interval > target_period:
        print("BUG DETECTED")
        print("interval: ", interval, "old time: ", old_time, "time: ", time.ticks_us())
        

