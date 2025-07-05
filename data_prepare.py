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
            if file.endswith('.txt'):
                file_path = os.path.join(root, file)
                file_path_list.append(file_path)

    file_path_list_sorted = []
    file_path_list_sorted = sorted(file_path_list, key=extract_index)

    logger.info("sorted list example: " + str(file_path_list_sorted[80]))

    return file_path_list_sorted


def get_text_file_list(file_path):
    """
    将单个html加工成文本列表返回
    """
    text_file_list = []
    with open(file_path, "r", encoding='utf-8', errors='ignore') as cf:
        int_error = 0
        for i, line in tqdm(enumerate(cf)):
            if i == 0:
                print(line)
            if i > 1 and i <= 100:
                line2 = eval(line.split('"\t"')[2].replace('""', '"'))
                if 'DocInfoVo' in line2.keys():
                    try:
                        # print(line2.keys())
                        doc_line = line2['DocInfoVo']["qwContent"]
                        doc_line_list = html2text(doc_line).split("\n")
                        doc_line_list = [i for i in doc_line_list if i != "" and i != ' \xa0']
                        assert doc_line_list != []
                        text_file_list.append(doc_line_list)
                        logger.info("processed html: " + str(doc_line_list))
                    except:
                        int_error += 1
            if i > 100:
                break

    return text_file_list
