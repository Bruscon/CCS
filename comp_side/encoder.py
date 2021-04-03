def encode(data):
    encoded = []
    data = data.lower()

    i=0
    vibsym = '_'
    while i<4:
        symbol = data[i]
        if symbol in ["a", "1"]:
            vibsym += ("a")
        elif symbol in ["b", "2"]:
            vibsym += ("aa")
        elif symbol in ["c", "3"]:
            vibsym += ("aaa")
        elif symbol in ["d", "4"]:
            vibsym += ("aaaa")
        elif symbol in ["e", "5"]:
            vibsym += ("B")
        elif symbol in ["f", "6"]:
            vibsym += ("Bb")
        elif symbol in ["g", "7"]:
            vibsym += ("Bbb")
        elif symbol in ["h", "8"]:
            vibsym += ("Bbbb")
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