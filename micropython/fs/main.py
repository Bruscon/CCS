import time, machine, struct, math, socket

soc_enabled = False

#hard-coded registers:
MPU6050_RA_PWR_MGMT_1 = const(0x6B)
MPU6050_RA_CONFIG = const(0x1A)
ACCEL_XOUT_H = const(0x3B)
GYRO_XOUT_H = const(0x43)
MPU = const(0x69)   #I pulled AD0 high so 69 not 68

MS_TO_S     = const(10**3)
RAD_TO_DEG  = 180 / math.pi

alpha = 0.95 #used for ypr accel/gyro balance
inv_alpha = 1-alpha

#initialize variables
fusion_ypr  =    [0.0, 0.0, 0.0]
target_period = .01 #seconds
command = []
state = '1st'
paused = True

class Soc :
    def __init__(self):
        self.last = 'A'
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.soc.bind(('', 80))
        self.soc.listen(5)
        self.conn, self.addr = self.soc.accept()
        self.conn.settimeout(0)
        self.conn.sendall("rdy")

    def send_command(self):
        self.conn.sendall(str(command))
        self.st = time.ticks_ms()

    def rx(self,vib):
        try:
            message = self.conn.recv(1024)
            print(message)
            message = list(str(message))[2:-1]
        except:
            return

        vib.send(message)
        self.last = message


    def repeat_last(self,vib):
        vib.send(self.last)


class Vibrator :
    def __init__(self):
        self.vib_enabled = False
        self.vibq = []
        self.vibstep = 0
        self.vibdeadline = time.ticks_add(time.ticks_ms(), 2000000000)  #200 hours?? maybe
        self.SHORT_INT = .19
        self.LONG_INT = .3
        self.PAUSE_INT = .13

        self.vib1 = machine.Pin(12, machine.Pin.OUT)
        self.vib2 = machine.Pin(13, machine.Pin.OUT)
        self.vib1.off()
        self.vib2.off()
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
        #isnt great. time.ticks wraps after ~10 minutes, then the vibs stop working.
        # workaround is to hit a "CAL IMU" when it happens.
        if self.vib_enabled and len(self.vibq) > 0 and (time.ticks_diff( time.ticks_ms(), self.vibdeadline )>0):
            if self.vibstep == 0: #start new command
                if self.vibq[0] in ['A', 'C', 'E', 'F','a']:
                    self.vib1.on()
                    if self.vibq[0] in ['A','E']:
                        self.vibdeadline = time.ticks_add(time.ticks_ms(), round(self.LONG_INT *MS_TO_S))
                    else:
                        self.vibdeadline = time.ticks_add(time.ticks_ms(), round(self.SHORT_INT *MS_TO_S))
                if self.vibq[0] in ['B','D','E','F','b']:
                    self.vib2.on()
                    if self.vibq[0] in ['B','E']:
                        self.vibdeadline = time.ticks_add(time.ticks_ms(), round(self.LONG_INT *MS_TO_S))
                    else:
                        self.vibdeadline = time.ticks_add(time.ticks_ms(), round(self.SHORT_INT *MS_TO_S))
                if self.vibq[0] in ["_"]: #pause
                    self.vib1.off()
                    self.vib2.off()
                    self.vibdeadline = time.ticks_add(time.ticks_ms(), round(self.SHORT_INT * MS_TO_S))
                self.vibstep = 1

            else:

                if self.vibq[0] in ['A', 'B','E','a','b']:
                    self.vib1.off()
                    self.vib2.off()
                    self.vibq.pop(0)
                    self.vibstep = 0
                elif self.vibstep == 1:
                    self.vib1.off()
                    self.vib2.off()
                    self.vibstep = 2
                    self.vibdeadline = time.ticks_add(time.ticks_ms(), round(self.PAUSE_INT *MS_TO_S))
                elif self.vibstep == 2:
                    if self.vibq[0] in ['C','F']:
                        self.vib1.on()
                    if self.vibq[0] in ['D','F']:
                        self.vib2.on()
                    self.vibstep = 3
                    self.vibdeadline = time.ticks_add(time.ticks_ms(), round(self.PAUSE_INT *MS_TO_S))

                elif self.vibstep == 3:
                    self.vib1.off()
                    self.vib2.off()
                    self.vibq.pop(0)
                    self.vibstep = 0
                if self.vibq == []: #last command
                    self.vibdeadline = time.ticks_add(time.ticks_ms(), 2000000000)
                elif self.vibstep == 0: #more commands to do
                    self.vibdeadline = time.ticks_add(time.ticks_ms(), round(self.PAUSE_INT *MS_TO_S))


def calib_IMU(samples):
    print('Cal IMU')
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

    resting_ypr[1] = math.atan( xac / math.sqrt(yac**2 + zac**2)) * RAD_TO_DEG
    resting_ypr[2] = math.atan(-1 * yac / math.sqrt(xac**2 + zac**2)) * RAD_TO_DEG

    G_cal = math.sqrt(xac**2 + yac**2 + zac**2)
    print(resting_ypr)
    return xoffset, yoffset, zoffset, G_cal, resting_ypr

#inits
vib = Vibrator()


#start I2C with MPU6050
i2c = machine.I2C(scl=machine.Pin(0), sda=machine.Pin(2), freq = 100000) #actually measures 150Khz when set to 400??

i2c.writeto_mem(MPU, MPU6050_RA_PWR_MGMT_1, b'\x80' )   #reset device   
time.sleep(.1)
i2c.writeto_mem(MPU, MPU6050_RA_PWR_MGMT_1, b'\x01' )   #wake-up, set Xgyro as clk
time.sleep(.3)
i2c.writeto_mem(MPU, MPU6050_RA_CONFIG, b'\x05')  #set DLPF to 5
    
if (soc_enabled):        
    soc = Soc()

xoffset, yoffset, zoffset, G_cal, resting_ypr = calib_IMU(100)
fusion_ypr = resting_ypr.copy()

old_time = time.ticks_ms()
while(1):
    #reads all accel, temp, gyro registers
    data = i2c.readfrom_mem(MPU, ACCEL_XOUT_H, 14 )

    #interval = ((target_period * MS_TO_S) - time.ticks_diff(time.ticks_ms(), old_time)) / MS_TO_S

    #calculates time delta between data frames
    new_time = time.ticks_ms()
    delta = time.ticks_diff(new_time, old_time) / MS_TO_S #convert to seconds

    if delta>0 and delta < target_period:
        time.sleep(target_period - delta)

    elif delta > target_period: #too slow
        print(">")

    elif delta < 0:
        print("BUG!!")

    new_time = time.ticks_ms()  #do this again to account for sleep
    delta = time.ticks_diff(new_time, old_time) / MS_TO_S #convert to seconds
    old_time = new_time

    #converts binary dump into gyro/accel/temp data
    xac  = struct.unpack('>h', data[0:2])[0] / G_cal
    yac  = struct.unpack('>h', data[2:4])[0] / G_cal
    zac  = struct.unpack('>h', data[4:6])[0] / G_cal
    temp = struct.unpack('>h', data[6:8])[0]
    xgy  = (struct.unpack('>h', data[8:10])[0]   - xoffset)
    ygy  = (struct.unpack('>h', data[10:12])[0]  - yoffset)
    zgy  = struct.unpack('>h', data[12:14])[0]  - zoffset

    #print(xac, "\n", yac, "\n", zac, "\n", temp, "\n", xgy, "\n", ygy, "\n", zgy,"\n\n\n")

    #calculate euler angles
    mag_G = math.sqrt(xac**2 + yac**2 + zac**2) #16384 = 1G
    if (mag_G < 1.2 and mag_G > .8):
        accel_p = math.atan( xac / math.sqrt(yac**2 + zac**2)) * RAD_TO_DEG
        accel_r = math.atan(-1 * yac / math.sqrt(xac**2 + zac**2)) * RAD_TO_DEG

        fusion_ypr[0] = (fusion_ypr[0] + ( delta )  *  ( zgy / 131 )) *.99 #to reduce drift
        fusion_ypr[1] = (fusion_ypr[1] + ( delta )  *  ( ygy / 131 ))*alpha + accel_p*inv_alpha
        fusion_ypr[2] = (fusion_ypr[2] + ( delta )  *  ( xgy / 131 ))*alpha + accel_r*inv_alpha
    else:
        fusion_ypr[0] = (fusion_ypr[0] + ( delta )  *  ( zgy / 131 ))
        fusion_ypr[1] = (fusion_ypr[1] + ( delta )  *  ( ygy / 131 ))
        fusion_ypr[2] = (fusion_ypr[2] + ( delta )  *  ( xgy / 131 ))


    #print('G: ',  mag_G)
    #print( 'y:', round(fusion_ypr[0]- resting_ypr[0]), ",p:", round(fusion_ypr[1]- resting_ypr[1]), ",r:", round(fusion_ypr[2]- resting_ypr[2]) )
    #print('a_p: ',round(accel_p), 'a_r: ', round(accel_r))

    #state machine
    if paused:
        if fusion_ypr[2] - resting_ypr[2] < -62:
            vib.send('F')
            command = []
            print('Unpsd')
            paused = False
            state = 'flt'
    else:
        if state == '1st':
            #Heel up: D
            if fusion_ypr[1] - resting_ypr[1] < -14.0 and (fusion_ypr[2] - resting_ypr[2]) < 6.5:
                command.append('D')
                vib.send("A")
                state = '2nd'
            #Toe Up: E
            elif fusion_ypr[1] - resting_ypr[1] > 9.5 and abs(fusion_ypr[2] - resting_ypr[2]) < 8:
                command.append("E")
                vib.send('B')
                state = '2nd'
            #roll 
            elif fusion_ypr[2] - resting_ypr[2] > 10:
                command.append("C")
                vib.send('A')
                state = '2nd'
            elif fusion_ypr[2] - resting_ypr[2] < -22:
                command.append("F")
                vib.send('B')
                state = '2nd'

            elif zgy < -15000:
                print('CLR')
                command = []
                vib.send(['F','F'])
                state = 'flt'
            elif zgy > 15000:
                print('DEL')
                if len(command) > 0:
                    command.pop(-1)
                vib.send(["E","E"])
                state = 'flt'

        if state == 'flt':
            if ( abs(fusion_ypr[1] - resting_ypr[1]) < 4 ) and \
               ( abs(fusion_ypr[2] - resting_ypr[2]) < 5 ) and \
               ( zgy > -4000 ) and ( zgy < 4000 ) :
                if len(command) >= 4:
                    state = 'snd cmd'
                else:
                    state = '1st'

        if state == '2nd':
            if ( abs(fusion_ypr[1] - resting_ypr[1]) < 4 ) and \
            ( abs(fusion_ypr[2] - resting_ypr[2]) < 5 ) and \
            ( zgy > -4000 ) and ( zgy < 4000 ) :
                print( "in: ", command[-1] )
                if command[-1] == 'C':
                    vib.send('A')
                if command[-1] == 'D':
                    vib.send('A')
                if command[-1] == 'E':
                    vib.send('B')
                if command[-1] == 'F':
                    vib.send('B')
                
                if len(command) >= 4:
                    state = 'snd cmd'
                else:
                    state = '1st'

            elif command[-1] == "C":
                if fusion_ypr[1] - resting_ypr[1] < -15.0:
                    print("in: A")
                    command.pop(-1)
                    command.append('A')
                    vib.send(['a'])
                    state = 'flt'
                elif fusion_ypr[1] - resting_ypr[1] > 4.0:
                    print("in: B")
                    command.pop(-1)
                    command.append('B')
                    vib.send(['a'])
                    state = 'flt'

            elif command[-1] == "F":
                if fusion_ypr[1] - resting_ypr[1] < -14.0:
                    print('in: G')
                    command.pop(-1)
                    command.append('G')
                    vib.send(['B'])
                    state = 'flt'
                elif fusion_ypr[1] - resting_ypr[1] > 5.0:
                    print('in: H')
                    command.pop(-1)
                    command.append('H')
                    vib.send(['B'])
                    state = 'flt'

            elif command[-1] == 'D':
                if zgy < -18000:
                    print("Snd cmd")
                    state = 'snd cmd'
                    command.pop(-1)
                elif zgy > 15000:
                    print("Repeat last")
                    if (soc_enabled):
                        soc.repeat_last(vib)
                    command.pop(-1)
                    state = 'flt'
                elif fusion_ypr[2] - resting_ypr[2] < -45:
                    print("clr cmd")
                    command = []
                    vib.send("F")
                    state = 'flt'

            elif command[-1] == 'E':
                if zgy < -7000:
                    vib.send(["F","F"])
                    command = []
                    print("psd")
                    paused = True
                    state = 'flt'
                elif zgy > 7000:  #dont know why, but this breaks the vibrator.
                    command.pop(-1)
                    time.sleep(1.8)
                    calib_IMU(100)
                    vib.send(["E","E"])
                    state = 'flt'
                    vib.vibdeadline = time.ticks_ms() #might fix?
                    vib.vibstep = 0

        if state == 'snd cmd':
            print("cmd: ", command)
            if(soc_enabled):
                soc.send_command()
            command = []
            state = 'flt'
    if (soc_enabled):        
        soc.rx(vib)
    vib.step()

