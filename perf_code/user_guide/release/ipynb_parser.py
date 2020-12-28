import os


def get_file_path(repo_name, root_path):
    """
    得到repo_name中所有release文件的路径
    :param repo_name: str, 库名
    :param root_path: str, 库的根目录
    :return files_path: list, 该库的所有release文件的路径
    """
    files_path = []  # 存放该库的所有release文件的路径
    repo_path = os.path.join(root_path, repo_name)
    list_dir = os.listdir(repo_path)
    for f in list_dir:
        files_path.append(os.path.join(repo_path, f))
    return files_path