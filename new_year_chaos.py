# Complete the minimumBribes function below.
def minimumBribes(q):
    cnt = 0
    for i in range(len(q)-1, 0, -1):
        j = i+1
        if q[i] != j:
            if q[i-1] == j:
                cnt += 1
                q[i-1], q[i] = q[i], q[i-1]
            elif q[i-2] == j:
                cnt += 2
                q[i-2], q[i-1] = q[i-1], q[i-2]
                q[i-1], q[i] = q[i], q[i-1]
            else:
                print("Too chaotic")
                return
    print(cnt)

if __name__ == '__main__':
    s = "2 5 1 3 4"
    q = [int(i) for i in s.split()]
    minimumBribes(q)
