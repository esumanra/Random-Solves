def substrCount(n, s):
    s = s + '0'
    l = []
    sum_ = 0
    count = 1
    for i in range(len(s)-1):
        if s[i] == s[i+1]:
            count += 1
        else:
            l.append((s[i], count))
            count = 1
    print(l)
    for tup in l:
        sum_ += (tup[1] * (tup[1] + 1)) // 2
    #     t = tup[1]
    #     temp = (t * (t+1)) / 2
    #     if temp > 1 and temp%2 != 0:
    #         temp -= 1
    #     sum_ += temp
    #     print(temp)
    # print(sum_)

    for i in range(1, len(l)-1):
        if l[i][1] == 1 and (l[i-1][0] == l[i+1][0]):
            sum_ += l[i-1][1]
    print(sum_)

if __name__ == '__main__':
    # s = 'aaaa'
    s = 'mnonopoooo'
    n = len(s)
    result = substrCount(n, s)
