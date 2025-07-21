import asyncio
import json
import os
from zhipuai import ZhipuAI
from data_prepare import get_sorted_file_list, get_text_file
from logger import logger
from utils import get_prompt, field_majority_vote

client = ZhipuAI(api_key="你的API_KEY")
NUM_SAMPLES = 3


def call_openai_sync(text_file, i):
    try:
        response = client.chat.completions.create(
            model="GLM-4-Flash",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {
                    "role": "user",
                    "content": get_prompt(text_content=text_file)
                },
            ],
            temperature=0.8,
            top_p=0.7,
            max_tokens=4096
        )
        extracted_json_str = response.choices[0].message.content.strip()
        extracted_json = json.loads(extracted_json_str)
        return extracted_json
    except Exception as e:
        logger.warning(f"[警告] 第{i + 1}次调用失败", exc_info=e)
        return None


async def call_openai_async(text_file, i):
    return await asyncio.to_thread(call_openai_sync, text_file, i)


async def process_text_file(text_file):
    tasks = [call_openai_async(text_file, i) for i in range(NUM_SAMPLES)]
    results = await asyncio.gather(*tasks)

    sample_outputs = [r for r in results if r is not None]
    all_dict = all(isinstance(sample, dict) for sample in sample_outputs)

    if all_dict:
        final_data = field_majority_vote(sample_outputs)
        logger.info(f"[自一致]字段投票完成")
    else:
        final_data = {}
        logger.error(f"[自一致]部分样本非JSON")

    logger.info("最终结果: {}".format(final_data))
    return final_data


async def process_file_group(file_path):
    text_files = get_text_file(file_path=file_path)

    results = []
    for text_file in text_files:
        result = await process_text_file(text_file)
        results.append(result)

    # 保存输出
    parts = file_path.split("/")
    part = parts[-1].split(".")[0]
    output_file = f"/data/oyt/result_ie/{part}"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
    logger.info(f"[文件输出] 已将结果保存到 {output_file}")


async def main():
    file_path_list_sorted = get_sorted_file_list(base_dir='/data/wxr/qwContent_data')

    # 串行处理每个文件夹，文件夹内异步并发
    for file_path in file_path_list_sorted:
        await process_file_group(file_path)


if __name__ == '__main__':
    asyncio.run(main())
