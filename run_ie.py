import os
import json
from openai import OpenAI
from data_prepare import get_sorted_file_list, get_text_file_list
from logger import logger
from utils import get_prompt

client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

if __name__ == '__main__':
    file_path_list_sorted = get_sorted_file_list(base_dir='/data/clz/unziped_files')

    for file_path in file_path_list_sorted:
        text_file_list = get_text_file_list(file_path=file_path)

        extraction_results = []

        for text_file in text_file_list:

            with open(text_file, "r", encoding="utf-8") as f:
                text_content = f.read()

            completion = client.chat.completions.create(
                model="qwen-max-latest",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {
                        "role": "user",
                        "content": get_prompt(text_content=text_content)
                    },
                ],
                extra_body={
                    "enable_thinking": False
                },
            )

            extracted_json_str = completion.choices[0].message.content.strip()

            try:
                extracted_data = json.loads(extracted_json_str)
            except json.JSONDecodeError:
                print(f"[警告] 无法解析为JSON: {text_file}")
                extracted_data = {"raw_output": extracted_json_str}

            extraction_results.append({
                "file_name": os.path.basename(text_file),
                "extracted_data": extracted_data
            })

        output_json_path = '/data/oyt/result_ie'
        with open(output_json_path, "w", encoding="utf-8") as out_f:
            json.dump(extraction_results, out_f, ensure_ascii=False, indent=2)

        logger.info(f"[完成] {file_path} 提取结果已保存至 {output_json_path}")
