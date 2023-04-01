import random

a = [1, 2, 3]

history_len = random.randint(0, len(a) - 1)
print(history_len)
print(a[:history_len])
