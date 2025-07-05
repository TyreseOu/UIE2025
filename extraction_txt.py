import os
import traceback
import logging
import json
from bs4 import BeautifulSoup
import csv
from tqdm import tqdm

logging.basicConfig(
    filename='error_log.txt',
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

base_dir = 'E:\\unziped_data'
output_dir = 'E:\\unziped_data'
os.makedirs(output_dir, exist_ok=True)

file_path_list = []

for root, dirs, files in os.walk(base_dir):
    for file in files:
        if file.endswith('.txt'):
            file_path_list.append(os.path.join(root, file))


def extract_index(file_path):
    filename = os.path.basename(file_path)
    idx_str = filename.split(".")[0]
    try:
        return int(idx_str)
    except ValueError:
        return float('inf')


file_path_list_sorted = sorted(file_path_list, key=extract_index)

csv.field_size_limit(500 * 1024 * 1024)


def html2text(html):
    soup = BeautifulSoup(html, 'html.parser')
    for br in soup.find_all('br'):
        br.replace_with('\n')
    return soup.get_text(separator='\n')


for file_path in file_path_list_sorted:
    results = []
    int_error = 0
    print(f"Processing: {file_path}")

    try:
        with open(file_path, "r", encoding='utf-8', errors='ignore') as cf:
            for i, line in tqdm(enumerate(cf), desc=f"Parsing {os.path.basename(file_path)}"):
                if i <= 1:
                    continue
                try:
                    parts = line.strip().split('\t')
                    if len(parts) < 3 or not parts[2].strip():
                        continue

                    raw_json_str = parts[2].replace('""', '"').strip()
                    if raw_json_str.startswith('"') and raw_json_str.endswith('"'):
                        raw_json_str = raw_json_str[1:-1]

                    line2 = json.loads(raw_json_str)

                    if 'qwContent' in line2 and line2['qwContent']:
                        raw_content = line2['qwContent']
                        text_content = html2text(raw_content)
                        cleaned_content = [line.strip().replace('\u3000', ' ') for line in text_content.split('\n') if
                                           line.strip()]
                        line2['qwContent'] = cleaned_content

                        extra_fields = {}
                        if len(parts) > 0:
                            extra_fields["id"] = parts[0].strip()
                        if len(parts) > 1:
                            extra_fields["docId"] = parts[1].strip()
                        if len(parts) > 3:
                            extra_fields["insertTime"] = parts[3].strip()
                        if len(parts) > 4:
                            extra_fields["flag"] = parts[4].strip()
                        if len(parts) > 5:
                            extra_fields["docId_md5"] = parts[5].strip()

                        merged_result = {**extra_fields, **line2}

                        results.append(merged_result)

                except Exception as e:
                    error_msg = f"Error in file {file_path}, line {i}: {str(e)}"
                    print(error_msg)
                    logging.error(error_msg)
                    logging.error(traceback.format_exc())
                    int_error += 1

        base_name = file_path.replace('.txt', '.json')
        output_path = os.path.join(output_dir, base_name)
        with open(output_path, "w", encoding="utf-8") as out_file:
            json.dump(results, out_file, indent=2, ensure_ascii=False)

        print(f"保存成功: {output_path}，结果数量： {len(results)} ，错误数量 {int_error} ")

    except Exception as e:
        logging.error(f"读取文件失败: {file_path}")
        logging.error(traceback.format_exc())
