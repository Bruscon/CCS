def interpret(data, soc):
    '''takes foot movements and converts to chess moves'''
    row = ''
    column = ''

    if len(data) != 2 and len(data) != 4:
        print("ERROR: command len is " + str(len(data)))
        soc.send(bytes("FF", encoding='utf8'))
        return -1

    column = data[0]
    row = str(ord(data[1]) - 64)

    if len(data) == 2:
        return column + row

    column2 = data[2]
    row2 = str(ord(data[3]) - 64)

    return column + row + column2 + row2