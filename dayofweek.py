def day_of_week(S, k):
    days = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
    pos = days.index(S)
    print(f'{pos}')
    print(f'{pos + k}')
    res = (pos + k) % 7
    print(days[res])


day_of_week('sat', 7)
