import os
import random


class TESTCLASS:
    def __init__(self, f):
        self.f = f
        self.opened_file = open(f)
        self.preload_data_list = []
        self.preload_n = 3
        self.preload_data()

    def preload_data(self):
        print("-" * 50)
        print(f"before preload:{self.preload_data_list}")
        if len(self.preload_data_list) < self.preload_n:
            for example in self.opened_file:
                self.preload_data_list.append(example)
                if len(self.preload_data_list) >= self.preload_n:
                    break

        # 发现读取到文件尾部了，重新打开文件
        if len(self.preload_data_list) < self.preload_n:
            self.opened_file = open(self.f)
            for example in self.opened_file:
                self.preload_data_list.append(example)
                if len(self.preload_data_list) >= self.preload_n:
                    break

        print(f"after preload:{self.preload_data_list}")
        print("-" * 50)

    def get_one_line(self):
        random_i = random.randint(0, len(self.preload_data_list) - 1)
        print("random_i:", random_i)
        example = self.preload_data_list[random_i]
        del self.preload_data_list[random_i]
        self.preload_data()
        return example

    def get_i(self, i):
        example = self.get_one_line()
        print(f"--get ex:{example}")
        print("-" * 100)


if __name__ == '__main__':

    f = "test.txt"
    with open(f, 'w') as fw:
        for i in range(4):
            fw.write(f"{i}\n")

    tc = TESTCLASS(f)

    for i in range(10):
        tc.get_i(0)
