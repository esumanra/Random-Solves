d = {1: 'a', 2: 'b', 3: 'c', 4: 'd'}

def find_key_from_val(val):
    for k, v in d.items():
        if v is val:
            break
    print("{}".format(k))

find_key_from_val('d')
