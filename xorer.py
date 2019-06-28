'''
A = [1, 2, 3, 4]
N = size of A - 4
X = xor with - 4
K = no. of elements - 2
'''
from itertools import combinations


def solve(A, N, X, K):
    res = 0
    for i in combinations(range(N), K):
        combination = i
        # print(combination, end='->')
        sum_ = 0
        for j in range(N):
            if j in combination:
                k = A[j] ^ X
            else:
                k = A[j]
            # print(k, end=',')
            sum_ += k
        # print(sum_)
        res = max(sum_, res)
    return res


# A = [1, 2, 3, 4, 5]
# N = 5
# X = 4
# K = 2
A = [10, 15, 20, 13, 2, 1, 44]
N = 7
X = 12
K = 4
out_ = solve(A, N, X, K)
print(out_)
