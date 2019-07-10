def isPrime(n):
    if (n <= 1):
        return False
    if (n <= 3):
        return True
    if (n % 2 == 0 or n % 3 == 0):
        return False
    i = 5
    while(i * i <= n):
        if (n % i == 0 or n % (i + 2) == 0):
            return False
        i = i + 6

    return True


def gangs(grid):
    primes = 0
    composites = 0
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if grid[i][j] != 0:
                prime = isPrime(grid[i][j])
                dfs(grid, i, j, prime)
                if prime:
                    primes += 1
                else:
                    composites += 1

    return (primes, composites)


def dfs(grid, i, j, key):
    if(i < 0 or i >= len(grid) or j < 0 or j >= len(grid[i]) or
       grid[i][j] == 0 or isPrime(grid[i][j]) != key):
        return
    grid[i][j] = 0
    dfs(grid, i+1, j, key)
    dfs(grid, i-1, j, key)
    dfs(grid, i, j+1, key)
    dfs(grid, i, j-1, key)


if __name__ == '__main__':
    T = int(input())
    for i in range(T):
        row, col = [int(i) for i in input().split()]
        grid = list()
        for k in range(row):
            items = [int(i) for i in input().split()]
            grid.append(items)
        res = gangs(grid)
        print(res)
