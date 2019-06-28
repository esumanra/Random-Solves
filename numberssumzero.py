def solution(N):
    result = []
    if N%2 != 0:
        result.append(0)
        k = N - 1
    else:
        k = N
    for i in range(1, int(k/2) + 1):
        result.extend([-i, i])
    return result


for i in range(1, 100):
    res = solution(i)
    print(len(res), len(set(res)), res, sum(res))
