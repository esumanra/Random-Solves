# Complete the isValid function below.
from collections import Counter

def isValid(s):
    d = {}
    count = 0
    for ch in s:
        if ch in d:
            d[ch] += 1
        else:
            d[ch] = 1
    g = Counter(d.values())
    if len(g) > 2:
        return 'NO'
    maxx = g.most_common(1)[0][0]
    print(d)
    for _, v  in d.items():
        if v != maxx:
            count += 1
            if v not in [maxx-1, maxx+1, 1]:
                return 'NO'
            if count > 1: return 'NO'
    return 'YES'

if __name__ == '__main__':
    with open('temp.txt', 'r') as f:
        s = f.read()

    result = isValid(s)
    print(result)