# -*- coding: utf-8 -*-
import json
from bs4 import BeautifulSoup
import csv


def get_token_num(text: str) -> int:
    """
    简单的token估算方法（适用于中英文混合文本）
    近似规则：1个汉字 ≈ 2个token，1个英文单词 ≈ 1.3个token
    """
    import re
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    non_chinese = re.sub(r'[\u4e00-\u9fff]', '', text)
    words = len(re.findall(r'\w+', non_chinese))

    return int(chinese_chars * 2 + words * 1.3)


def save_to_json(people, relations, file_name="output.json"):
    """
    保存结果到JSON文件
    """
    result = {
        "people": people,
        "relations": relations
    }
    with open(file_name, 'w', encoding='utf-8') as json_file:
        json.dump(result, json_file, ensure_ascii=False, indent=4)


def html2text(html):
    """
    将HTML转换为纯文本
    """
    csv.field_size_limit(500 * 1024 * 1024)
    soup = BeautifulSoup(html, 'html.parser')
    for br in soup.find_all('br'):
        br.replace_with('\n')
    text = soup.get_text(separator='\n')
    return text


def try_dict_key(dict_x, key_y):
    try:
        return dict_x[key_y]
    except:
        return "NONE"


def get_month(date):
    try:
        return date.split("-")[0]
    except:
        return "NONE"


def extract_index(file_path):
    filename = file_path.split("/")[-1]  # 获取文件名
    idx_str = filename.split(".")[0]  # 获取不包含扩展名的文件名部分
    # 尝试将字符串转换为整数，如果失败则返回None
    try:
        idx = int(idx_str)
    except ValueError:
        idx = None
    return idx
