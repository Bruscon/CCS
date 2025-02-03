import socket, select, time, ches, interpret, encoder

def w2b(move):
    '''transforms white justified moves to black'''
    rv = ''
    rv += ( invert_letter(move[0]) )
    rv += str( 9 - int(move[1]) ) 
    rv += ( invert_letter(move[2]) )
    rv += str( 9 - int(move[3]) ) 

    return rv

def invert_letter(letter):
    letter = letter.upper()
    if letter == 'A':
        return 'H'
    if letter == 'B':
        return 'G'
    if letter == 'C':
        return 'F'
    if letter == 'D':
        return 'E'
    if letter == 'E':
        return 'D'
    if letter == 'F':
        return 'C'
    if letter == 'G':
        return 'B'
    if letter == 'H':
        return 'A'
        


def reconnect():
    soc = socket.socket()
    soc.settimeout(2)
    soc.connect(("192.168.0.202", 80))
    # soc.send(bytes("sup", encoding = 'utf8'))
    print("recieved from ESP: ", soc.recv(1024))
    soc.settimeout(None)
    return soc

while 1:
    try:
        soc = reconnect()
        break
    except:
        print("Waiting for ESP...")
        continue

game = ches.Ches()
print("\n\n")
msg = "FF"
try:
    soc.send(bytes(msg, encoding='utf8'))
except:
    soc = reconnect()

game.brd()

#if you are white, send a blank. else send anything
iswhite = True
msg = soc.recv(1024).decode("utf-8").strip('][').replace('\'', '').replace(' ', '').replace(',', '')
print(msg)
if msg == '':
    print("starting as white")
    game.startwhite()
    compmove = game.getmove()
    print(compmove)
    game.brd()
    commands = encoder.encode(compmove)
    print(commands)
    while commands != []:
        soc.send(bytes(commands[0], encoding='utf8'))
        commands.pop(0)
        if commands != []:
            soc.recv(1024)
else:
    iswhite = False
    print("starting as black")

while (1):

    valid = False
    while valid == False:
        print(game.board.fen())
        reply = soc.recv(1024).decode("utf-8").strip('][').replace('\'', '').replace(' ', '').replace(',', '')
        move = interpret.interpret(reply, soc)
        if move == -1: continue

        if not iswhite:
            move = w2b(move)        

        print(move)
        valid = game.sendmove(move.lower())

        if valid == False:
            soc.send(bytes("FF", encoding='utf8'))
        game.brd()

    compmove = game.getmove()
    print(compmove)
    game.brd()

    if not iswhite:
        compmove = w2b(compmove)     

    commands = encoder.encode(compmove)
    print(commands)
    while commands != []:
        soc.send(bytes(commands[0], encoding='utf8'))
        commands.pop(0)
        if commands != []:
            soc.recv(1024)
