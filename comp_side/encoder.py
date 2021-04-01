def encode(data):
    encoded = []
    data = data.lower()

    i=0
    vibsym = '_'
    while i<4:
        symbol = data[i]
        if symbol in ["a", "1"]:
            vibsym += ("A")
        elif symbol in ["b", "2"]:
            vibsym += ("AA")
        elif symbol in ["c", "3"]:
            vibsym += ("AAA")
        elif symbol in ["d", "4"]:
            vibsym += ("AAAA")
        elif symbol in ["e", "5"]:
            vibsym += ("B")
        elif symbol in ["f", "6"]:
            vibsym += ("BB")
        elif symbol in ["g", "7"]:
            vibsym += ("BBB")
        elif symbol in ["h", "8"]:
            vibsym += ("BBBB")
        else:
            print("ERROR")
            return

        if i in [1,3]:
            vibsym += '_'
            encoded.append(vibsym)
            vibsym = '_'
        else:
            vibsym += "_"
        i +=1

    return encoded