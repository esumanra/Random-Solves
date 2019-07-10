def findNth(n, inp):
    # vector to store results
    ans = []

    # push first 6 numbers in the answer
    for i in inp:
        ans.append(i)

    # calculate further results
    for i in range(n+1):
        for j in inp:
            v = ans[i] * 10 + j
            print(v)
            ans.append(v)

    return ans[n - 1]


if __name__ == '__main__':
    n = 13
    inp = [1, 2, 3]
    print(findNth(n, inp))
