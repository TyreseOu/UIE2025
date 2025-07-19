from tqdm import tqdm
from logger import logger
from utils import html2text, extract_index
import json
import os


def get_sorted_file_list(base_dir):
    """
    获取文件夹下排序好的文件列表
    """
    # '/data/clz/unziped_files'
    base_dir = base_dir
    file_path_list = []
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                file_path_list.append(file_path)

    file_path_list_sorted = []
    file_path_list_sorted = sorted(file_path_list, key=extract_index)

    logger.info("sorted list example: " + str(file_path_list_sorted[1]))

    return file_path_list_sorted


def get_text_file(file_path):
    """
    读取文件
    """
    with open(file_path, "r", encoding='utf-8', errors='ignore') as cf:
        data = json.load(cf)

    return data
