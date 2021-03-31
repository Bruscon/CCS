import socket, select, time, ches, interpret, encoder

def reconnect():
    soc = socket.socket()
    soc.connect(("192.168.0.118", 80))
    # soc.send(bytes("sup", encoding = 'utf8'))
    print("recieved from ESP: ", soc.recv(1024))
    return soc

game = ches.Ches()
soc = reconnect()
square = ''

print("\n\n")
msg = "FF"
try:
    soc.send(bytes(msg, encoding='utf8'))
except:
    soc = reconnect()

game.brd()

#if you are white, send a blank. else send anything
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
    print("starting as black")

while (1):

    valid = False
    while valid == False:
        print(game.board.fen())
        reply = soc.recv(1024).decode("utf-8").strip('][').replace('\'', '').replace(' ', '').replace(',', '')
        move = interpret.interpret(reply, soc)
        if move == -1: continue
        if len(move) == 2:
            reply = soc.recv(1024).decode("utf-8").strip('][').replace('\'', '').replace(' ', '').replace(',', '')
            move2 = interpret.interpret(reply)
            if move2 == -1: continue
            move = move + move2
        print(move)
        valid = game.sendmove(move.lower())
        game.brd()

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



