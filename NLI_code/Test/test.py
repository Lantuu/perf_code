import inspect
import os

import pandas


num_path = 0


def uniquePaths(m: int, n: int) -> int:
    helper(1, 1, m, n)
    return num_path


def helper(r, c, m, n):
    global num_path
    if r == m and c == n:
        num_path = num_path + 1
        return


    if r > m or c > n:
        return

    helper(r + 1, c, m, n)
    helper(r, c + 1, m, n)


def file_name(file_dir):
    L = []
    for root, dirs, files in os.walk(file_dir):
        for file in files:
            # if os.path.splitext(file)[1] == '.jpeg':  # 想要保存的文件格式
            L.append(os.path.join(root, file))
    return L


if __name__ == "__main__":

    # print(uniquePaths(3,7))
    # print(inspect.getdoc(pandas.DataFrame))
    path = "D:\workspace\performance\clone2\gensim"
    # l = os.listdir("D:\workspace\performance\clone2\gensim")
    # print(len(l))
    # print(l)
    l = file_name(path)
    print(len(l))
    print(l)