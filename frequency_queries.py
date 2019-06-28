def freqQuery(queries):
    dic = {}
    res = []
    found = False
    for q, item in queries:
        if q == 1:
            dic[item] = dic.get(item, 0) + 1
        elif q == 2:
            if item in dic:
                dic[item] -= 1
        else:
            for k in dic.values():
                if k == item:
                    found = True
                    break
            if found:
                res.append(1)
            else:
                res.append(0)
            found = False
    return res

inp = [[1, 5], [1, 6], [3, 2], [1, 10], [1, 10], [1, 6], [2, 5], [3, 2]]
ans = freqQuery(inp)
print('\n'.join(map(str, ans)))