import os
from dashscope import Generation
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pydantic import BaseModel, Field
from typing import Optional

from langchain.document_loaders import TextLoader
from langchain_core.output_parsers import JsonOutputParser

from utils import save_to_json

os.environ["DASHSCOPE_API_KEY"] = "sk-30fbb850596b4ca3a08a361b3a0f0df0"

loader_txt = TextLoader(r'E:\test.txt', encoding='utf8')
docs_txt = loader_txt.load()

text_splitter_txt = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200,
                                                   separators=["\n\n", "\n", " ", "", "。", "，"])
documents_txt = text_splitter_txt.split_documents(docs_txt)


class Person(BaseModel):
    """人物基本信息"""
    name: Optional[str] = Field(default=None, description="人物名称")
    gender: Optional[str] = Field(default=None, description="人物性别")
    age: Optional[str] = Field(default=None, description="人物年龄")
    hair_color: Optional[str] = Field(default=None, description="人物发色")
    height_in_meters: Optional[str] = Field(default=None, description="人物身高")


class Relation(BaseModel):
    """两个人物之间的关系"""
    name0: Optional[str] = Field(default=None, description="第一个人物名称")
    name1: Optional[str] = Field(default=None, description="第二个人物名称")
    relationship: Optional[str] = Field(default=None, description="两者的关系")


class Data_guanxi(BaseModel):
    """包含人物及其关系的抽取数据"""
    people: list[Person]
    relations: list[Relation]


def prompt_yun(ct):
    system_prompt = """
    您是一个专家，专门从文本中提取人物信息和人物关系。请从文本中提取所有人物的信息，仅仅从正文中提取人物信息，不要从注释或文章题目等其他地方提取人物信息，确保包括以下内容：
    1. 人物名称
    2. 人物的性别（如果提到）
    3. 人物的年龄（如果提到）
    4. 人物的外貌特征（例如发色、身高等，若有描述）
    5. 人物与其他人的关系，确保每一段关系都明确，关系类型应尽可能精确，具体到父子、朋友、战友、夫妻等关系。

    例如：
    - 例子1：’阿米尔与哈桑是童年朋友，两人关系深厚，阿米尔时常保护哈桑。’
    - 例子2：’阿塞夫与阿米尔之间的关系是敌对的，阿塞夫曾在过去伤害过阿米尔。’

    如果无法从文本中获取某个属性值，请返回 null。输出结果应为字典形式。例子如下：
    {'age': None, 'gender': '女', 'hair_color': None, 'height_in_meters': None, 'name': '我的妈妈'}
    {'name0': '普什图人', 'name1': '哈扎拉人', 'relationship': '压迫者与被压迫者'}。

    """
    prompt = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": ct}
    ]
    return prompt


def get_response_1t(mess):
    try:
        response = Generation.call(
            model='qwen-plus',
            messages=mess,
            tools=[{
                "type": "function",
                "function": {
                    "name": "Data_guanxi",
                    "description": "提取人物信息和人物间关系数据",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "people": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string"},
                                        "gender": {"type": "string"},
                                        "age": {"type": "string"},
                                        "hair_color": {"type": "string"},
                                        "height_in_meters": {"type": "string"}
                                    }
                                }
                            },
                            "relations": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "name0": {"type": "string"},
                                        "name1": {"type": "string"},
                                        "relationship": {"type": "string"}
                                    }
                                }
                            }
                        }
                    }
                }
            }], result_format='json'
        )
        if response is not None:
            return response
        else:
            print("API 响应无效: response 为 None")
            return None
    except Exception as e:
        print(f"API 调用失败: {e}")
        return None


def process_documents(docs):
    all_people = []
    all_relations = []

    for doc in docs:
        p_y = prompt_yun(doc.page_content)
        res = get_response_1t(p_y)

        if res is not None:
            print("提取结果：")
            print(res.output)

            if hasattr(res, 'output') and hasattr(res.output, 'choices'):
                try:
                    if 'tool_calls' in res.output.choices[0].message:
                        res_data = JsonOutputParser().parse(
                            res.output.choices[0].message['tool_calls'][0]['function']['arguments'])
                    else:
                        print("警告：未找到 'tool_calls'，正在直接从消息内容中提取人物和关系。")
                        res_data = {
                            "people": res.output.choices[0].message.get('people', []),
                            "relations": res.output.choices[0].message.get('relations', [])
                        }

                    if res_data:
                        people = res_data.get('people', [])
                        relations = res_data.get('relations', [])
                    else:
                        print("警告：未能提取有效的数据，跳过当前文档。")
                        people = []
                        relations = []

                except Exception as e:
                    print(f"解析错误: {e}")
                    people = []
                    relations = []
            else:
                print("API 响应格式不正确，缺少预期的字段：'output' 或 'choices'")
                people = []
                relations = []
        else:
            print("API 响应为 None，跳过当前文档")
            people = []
            relations = []

        for person in people:
            if person not in all_people:
                all_people.append(person)

        for relation in relations:
            if relation not in all_relations:
                all_relations.append(relation)

    return all_people, all_relations


if __name__ == '__main__':

    people, relations = process_documents(documents_txt)

    print("所有人物信息：")
    for person in people:
        print(person)

    print("所有人物关系：")
    for relation in relations:
        print(relation)

    save_to_json(people, relations)
