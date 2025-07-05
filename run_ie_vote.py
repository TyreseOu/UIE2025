import os
import json
from openai import OpenAI
from data_prepare import get_sorted_file_list, get_text_file_list
from logger import logger
from utils import get_prompt, field_majority_vote

client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

MODEL_LIST = [
    "qwen-max-latest",
    "qwen-plus",
    "qwen-turbo"
]

if __name__ == '__main__':
    file_path_list_sorted = get_sorted_file_list(base_dir='/data/clz/unziped_files')

    for file_path in file_path_list_sorted:
        text_file_list = get_text_file_list(file_path=file_path)

        extraction_results = []

        for text_file in text_file_list:
            with open(text_file, "r", encoding="utf-8") as f:
                text_content = f.read()

            sample_outputs = []

            for model_name in MODEL_LIST:
                completion = client.chat.completions.create(
                    model=model_name,
                    temperature=0.8,
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
                    logger.warning(f"[警告] 模型 {model_name} 输出无法解析JSON: {text_file}")
                    extracted_data = {"raw_output": extracted_json_str}

                sample_outputs.append({
                    "model": model_name,
                    "data": extracted_data
                })

            all_dict = all(isinstance(item["data"], dict) for item in sample_outputs)

            if all_dict:
                final_data = field_majority_vote([item["data"] for item in sample_outputs])
                logger.info(f"[多模型投票] {os.path.basename(text_file)} 字段投票完成")
            else:
                final_data = {"all_model_outputs": sample_outputs}
                logger.info(f"[多模型投票] {os.path.basename(text_file)} 有非JSON输出，保留所有")

            extraction_results.append({
                "file_name": os.path.basename(text_file),
                "final_extracted_data": final_data
            })

        folder_name = os.path.splitext(os.path.basename(file_path))[0]
        output_json_path = os.path.join("/data/oyt/result_ie", f"{folder_name}_results.json")

        os.makedirs(os.path.dirname(output_json_path), exist_ok=True)

        with open(output_json_path, "w", encoding="utf-8") as out_f:
            json.dump(extraction_results, out_f, ensure_ascii=False, indent=2)

        logger.info(f"[完成] {file_path} 提取结果已保存至 {output_json_path}")
