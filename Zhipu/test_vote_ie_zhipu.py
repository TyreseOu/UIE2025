import asyncio
import json

from zhipuai import ZhipuAI

from logger import logger
from utils import get_prompt, field_majority_vote, get_set_content

client = ZhipuAI(api_key="你的API_KEY")
NUM_SAMPLES = 3


def call_zhipu_sync(text_file, i):
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


async def call_zhipu_async(text_file, i):
    return await asyncio.to_thread(call_zhipu_sync, text_file, i)


async def main():
    text_content = get_set_content()

    tasks = [call_zhipu_async(text_content, i) for i in range(NUM_SAMPLES)]
    results = await asyncio.gather(*tasks)

    sample_outputs = [r for r in results if r is not None]

    all_dict = all(isinstance(sample, dict) for sample in sample_outputs)

    if all_dict:
        final_data = field_majority_vote(sample_outputs)
        logger.info(f"[自一致]字段投票完成")
    else:
        final_data = {"all_samples": sample_outputs}
        logger.info(f"[自一致]部分样本非JSON，保留所有")

    logger.info("最终结果: {}".format(final_data))
    output_file = "final_result.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(final_data, f, ensure_ascii=False, indent=4)

    logger.info(f"[文件输出] 已将结果保存到 {output_file}")


if __name__ == '__main__':
    asyncio.run(main())
