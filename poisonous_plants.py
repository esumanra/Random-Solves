def poisonousPlants(p):
    days = 0
    flag = True
    while flag:
        tlis = []
        prev = 10**11
        for cur in p:
            if cur < prev:
                tlis.append(cur)
            prev = cur
        p = list(tlis)
        if(tlis == sorted(tlis, reverse=True)):
            flag = False
        days += 1
    print(days)


l = [6, 5, 8, 4, 7, 10, 9]
poisonousPlants(l)
