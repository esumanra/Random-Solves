def Solve(SL, PL, S, P):
    # write your code here
    # return your answer
    count = 0
    dic = dict()
    subset = dict()
    for char in S:
        dic[char] = dic.get(char, 0) + 1
    for char in P:
        subset[char] = subset.get(char, 0) + 1

    flag = True
    while flag:
        for key, value in subset.items():
            if not dic[key] >= subset[key]:
                flag = False
            else:
                dic[key] = dic[key] - subset[key]

        if flag:
            count += 1

    return count


SL, PL = 10, 4

S = "abcbbcabcc"

P = "bccb"

out_ = Solve(SL, PL, S, P)

print(out_)
