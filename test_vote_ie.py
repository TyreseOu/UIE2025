import json
import os
from openai import OpenAI
from logger import logger
from utils import get_prompt, field_majority_vote, get_set_content

client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

NUM_SAMPLES = 1
MODEL_NAME = "qwen-max-latest"

if __name__ == '__main__':
    text_content = get_set_content()

    sample_outputs = []

    for i in range(NUM_SAMPLES):
        try:
            completion = client.chat.completions.create(
                model=MODEL_NAME,
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
        except Exception:
            logger.warning(f"[警告] 第{i + 1}次调用失败")

        extracted_json_str = completion.choices[0].message.content.strip()
        extracted_json = json.loads(extracted_json_str)
        sample_outputs.append(extracted_json)

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
