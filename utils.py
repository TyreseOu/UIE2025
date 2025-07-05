# -*- coding: utf-8 -*-
import json
from bs4 import BeautifulSoup
import csv
from collections import Counter
import json


def field_majority_vote(sample_outputs):
    """
    针对每个key进行投票，支持任意深度嵌套结构
    """
    if not sample_outputs:
        return {}

    if not all(isinstance(s, dict) for s in sample_outputs):
        raise ValueError("All samples must be dicts.")

    def recursive_vote(values_list):
        """
        values_list: list of values under the same key from all samples
        """
        # 所有值都是dict：递归处理
        if all(isinstance(v, dict) for v in values_list):
            merged = {}
            keys = set().union(*[v.keys() for v in values_list])
            for k in keys:
                merged[k] = recursive_vote([v.get(k, "") for v in values_list])
            return merged

        # 所有值都是list：特殊处理
        if all(isinstance(v, list) for v in values_list):
            # 如果列表为空，直接返回空
            if all(len(v) == 0 for v in values_list):
                return []

            # 如果列表里的元素是dict，用json.dumps投票
            if all(all(isinstance(i, dict) for i in v) for v in values_list):
                # 把每个list转成list of json strings
                vtuples = [tuple(json.dumps(i, sort_keys=True) for i in v) for v in values_list]
                count = Counter(vtuples)
                most_common_tuple = count.most_common(1)[0][0]
                # 再转回list of dict
                return [json.loads(s) for s in most_common_tuple]

            # 如果是list of primitive (str/int)，直接投票整个列表
            vtuples = [tuple(v) for v in values_list]
            count = Counter(vtuples)
            most_common_tuple = count.most_common(1)[0][0]
            return list(most_common_tuple)

        # 其它情况（str/int/float/bool）
        normalized = []
        for v in values_list:
            if isinstance(v, (bool, int, float)):
                normalized.append(v)
            elif isinstance(v, str):
                normalized.append(v.strip())
            else:
                normalized.append(json.dumps(v, sort_keys=True))
        count = Counter(normalized)
        most_common_value = count.most_common(1)[0][0]
        # 尝试转回原始类型
        if isinstance(most_common_value, str):
            try:
                return json.loads(most_common_value)
            except Exception:
                return most_common_value
        else:
            return most_common_value

    return recursive_vote(sample_outputs)


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
    filename = file_path.split("/")[-1]
    idx_str = filename.split(".")[0]
    try:
        idx = int(idx_str)
    except ValueError:
        idx = None
    return idx


def get_set_content():
    """
    返回构造好的内容
    """
    return """
    {
    "id": "\"46941656\"",
    "docId": "\"b6d5e11e-8f16-413e-a329-acd90121b84b\"",
    "insertTime": "\"29/3/2021 06:47:28\"",
    "flag": "\"2\"",
    "s1": "刘合秋与台前县五星蔬菜制品有限公司、刘红军建设工程施工合同纠纷一审民事判决书",
    "s2": "河南省台前县人民法院",
    "s3": "G96",
    "s5": "b6d5e11e8f16413ea329acd90121b84b",
    "s6": "01",
    "s7": "（2021）豫0927民初89号",
    "s8": "民事案件",
    "s9": "民事一审",
    "s31": "2021-01-21",
    "s41": "2021-02-24",
    "s22": "河南省台前县人民法院\n民事判决书\n（2021）豫0927民初89号",
    "s23": "原告刘合秋与被告台前县五星蔬菜制品有限公司、被告刘红军建设工程施工合同纠纷一案，本院于2021年1月12日立案后，依法适用简易程序，公开开庭进行了审理。原告刘合秋的委托诉讼代理人王化俭到庭参加诉讼，被告台前县五星蔬菜制品有限公司、被告刘红军经本院合法传唤无正当理由拒不到庭。本案现已审理终结",
    "s25": "原告刘合秋诉称，2018年4月7日，其与被告刘红军签订《建设工程合同》，约定由原告承建被告位于台前县侯庙镇孙洼村南的厂房，合同就建设工程地址、价位、建设标准、工程款、建设工期、付款方式等均作了明确约定。合同签订后，原告按照合同约定将厂房建设完毕并交付被告使用。2019年1月20日，被告刘红军签订《协议书》一份，认可刘红军欠原告工程款23万元。《协议书》签订后，被告刘红军仅偿还了2万元，剩余21万元工程款经多次催要未果。原告刘合秋诉至法院，请求判令：1.二被告共同偿还原告工程款210000元及逾期利息（按照全国银行间同业拆借中心公布的一年期贷款报价利率计算，自2019年1月20日起计算至实际还清之日止）；2.二被告承担本案诉讼费用。\n被告台前县五星蔬菜制品有限公司未作答辩。\n被告刘红军未作答辩。\n经审理查明，2018年4月7日，原告刘合秋（乙方）与被告台前县五星蔬菜制品有限公司（甲方）签订《建设施工合同》，约定由原告刘合秋为被告台前县五星蔬菜制品有限公司建设厂房及生活区配房、道路地面硬化、绿化等；双方约定工程款按照市场价位结算，分期支付，且剩余工程款不存在利息。2019年1月20日，被告刘红军向原告刘合秋出具《协议书》，写明其欠原告刘合秋23万元工程款，自愿用设备和厂房来顶欠款。后经催要，被告刘红军共支付33000元，剩余197000元未付。\n以上事实，有原告方提交的《建设施工合同》《协议书》，及其在庭审中的陈述记录在卷予以证实",
    "s26": "本院认为，原告刘合秋提交的证据，能够证实其为被告台前县五星蔬菜制品有限公司建设工程后，被告台前县五星蔬菜制品有限公司尚欠工程款197000元未付的事实，以及被告刘红军对案涉197000元欠款亦予认可的事实，应予认定。原告刘合秋虽无建筑施工资质，但被告刘红军所出具的《协议书》写明欠工程款230000元，其应承担还款责任。关于原告方所主张的利息，因原、被告在《建设施工合同》中约定“剩余工程款不存在利息”，本院不予支持。被告刘红军、被告台前县五星蔬菜制品有限公司经本院合法传唤无正当理由拒不到庭，视为自动放弃质证及答辩权利。依照《中华人民共和国民法典》第七百九十三条第一款、第八百零七条，《最高人民法院关于审理建设工程施工合同纠纷案件适用法律问题的解释（一）》第二十五条，《中华人民共和国民事诉讼法》第一百四十四条规定，判决如下",
    "s27": "（2021）被告台前县五星蔬菜制品有限公司支付原告刘合秋工程款197000元，于本判决生效之日起十日内履行完毕。\n（2021）被告刘红军对上述欠款承担连带偿还责任。\n（2021）驳回原告刘合秋的其它诉讼请求。\n案件受理费2225元，由被告台前县五星蔬菜制品有限公司、被告刘红军负担2120元，原告刘合秋负担105元。\n如不服本判决，可在判决书送达之日起十五日内，向本院递交上诉状，并按对方当事人或者代表人的人数提出副本，上诉于濮阳市中级人民法院",
    "s28": "审判员王刚\n二〇二一年一月二十一日\n书记员丁同豪",
    "s17": [
      "刘合秋",
      "台前县五星蔬菜制品有限公司",
      "刘红军"
    ],
    "s45": [
      "利息",
      "建设工程"
    ],
    "s11": [
      "建设工程施工合同纠纷"
    ],
    "wenshuAy": [
      {
        "key": "s14",
        "value": "9208",
        "text": "建设工程施工合同纠纷"
      }
    ],
    "s47": [
      {
        "tkx": "第一百四十四条",
        "fgmc": "《中华人民共和国民事诉讼法》",
        "fgid": "3779249"
      }
    ],
    "relWenshu": [],
    "qwContent": [
      "河南省台前县人民法院",
      "民 事 判 决 书",
      "（2021）豫0927民初89号",
      "原告：刘合秋，男，1988年9月28日出生，汉族，住河南省濮阳市台前县。",
      "委托诉讼代理人：王化俭，河南濮东律师事务所律师。",
      "被告：台前县五星蔬菜制品有限公司，住所地河南省濮阳市台前县侯庙镇孙洼村。",
      "法定代表人：刘红军，该公司经理。",
      "被告：刘红军，男，1967年8月24日出生，汉族，住河南省濮阳市台前县。",
      "原告刘合秋与被告台前县五星蔬菜制品有限公司、被告刘红军建设工程施工合同纠纷一案，本院于2021年1月12日立案后，依法适用简易程序，公开开庭进行了审理。原告刘合秋的委托诉讼代理人王化俭到庭参加诉讼，被告台前县五星蔬菜制品有限公司、被告刘红军经本院合法传唤无正当理由拒不到庭。本案现已审理终结。",
      "原告刘合秋诉称，2018年4月7日，其与被告刘红军签订《建设工程合同》，约定由原告承建被告位于台前县侯庙镇孙洼村南的厂房，合同就建设工程地址、价位、建设标准、工程款、建设工期、付款方式等均作了明确约定。合同签订后，原告按照合同约定将厂房建设完毕并交付被告使用。2019年1月20日，被告刘红军签订《协议书》一份，认可刘红军欠原告工程款23万元。《协议书》签订后，被告刘红军仅偿还了2万元，剩余21万元工程款经多次催要未果。原告刘合秋诉至法院，请求判令：1.二被告共同偿还原告工程款210000元及逾期利息（按照全国银行间同业拆借中心公布的一年期贷款报价利率计算，自2019年1月20日起计算至实际还清之日止）；2.二被告承担本案诉讼费用。",
      "被告台前县五星蔬菜制品有限公司未作答辩。",
      "被告刘红军未作答辩。",
      "经审理查明，2018年4月7日，原告刘合秋（乙方）与被告台前县五星蔬菜制品有限公司（甲方）签订《建设施工合同》，约定由原告刘合秋为被告台前县五星蔬菜制品有限公司建设厂房及生活区配房、道路地面硬化、绿化等；双方约定工程款按照市场价位结算，分期支付，且剩余工程款不存在利息。2019年1月20日，被告刘红军向原告刘合秋出具《协议书》，写明其欠原告刘合秋23万元工程款，自愿用设备和厂房来顶欠款。后经催要，被告刘红军共支付33000元，剩余197000元未付。",
      "以上事实，有原告方提交的《建设施工合同》《协议书》，及其在庭审中的陈述记录在卷予以证实。",
      "本院认为，原告刘合秋提交的证据，能够证实其为被告台前县五星蔬菜制品有限公司建设工程后，被告台前县五星蔬菜制品有限公司尚欠工程款197000元未付的事实，以及被告刘红军对案涉197000元欠款亦予认可的事实，应予认定。原告刘合秋虽无建筑施工资质，但被告刘红军所出具的《协议书》写明欠工程款230000元，其应承担还款责任。关于原告方所主张的利息，因原、被告在《建设施工合同》中约定“剩余工程款不存在利息”，本院不予支持。被告刘红军、被告台前县五星蔬菜制品有限公司经本院合法传唤无正当理由拒不到庭，视为自动放弃质证及答辩权利。依照《中华人民共和国民法典》第七百九十三条第一款、第八百零七条，《最高人民法院关于审理建设工程施工合同纠纷案件适用法律问题的解释（一）》第二十五条，《中华人民共和国民事诉讼法》第一百四十四条规定，判决如下：",
      "（2021）被告台前县五星蔬菜制品有限公司支付原告刘合秋工程款197000元，于本判决生效之日起十日内履行完毕。",
      "（2021）被告刘红军对上述欠款承担连带偿还责任。",
      "（2021）驳回原告刘合秋的其它诉讼请求。",
      "案件受理费2225元，由被告台前县五星蔬菜制品有限公司、被告刘红军负担2120元，原告刘合秋负担105元。",
      "如不服本判决，可在判决书送达之日起十五日内，向本院递交上诉状，并按对方当事人或者代表人的人数提出副本，上诉于濮阳市中级人民法院。",
      "审判员 王 刚",
      "二〇二一年一月二十一日",
      "书记员 丁同豪"
    ],
    "directory": [
      "1",
      "2",
      "2",
      "2",
      "2",
      "2",
      "2",
      "2",
      "2",
      "7"
    ],
    "globalNet": "outer",
    "viewCount": "65"
  }
    """


def get_prompt(text_content):
    return f"""
    你是一位**法律信息抽取的专家**，现在请你从下面提供的**法律文书**中提取信息，并严格按照我给定的JSON格式输出，**不要输出任何额外内容或解释**。

    ## 任务要求  
    1. 只返回**合法JSON**，不要有任何额外内容（如“好的”或“如下”）。  
    2. JSON的结构必须完全与示例一致：包含`_type`, `_source`, `_id`, `_index`, `_score`等字段。  
    3. `_source`中各字段key固定，如`meta_案件名称`、`section_落款`等，不要改动。  
    4. 如无法提取某字段，请返回空字符串`""`或空列表`[]`。
    5. 布尔字段如`info_同意离婚`必须为`true`或`false`。
    6. 日期请尽量提取为`YYYY-MM-DD`格式。
    7. _index的value全为es_fdlawcase_all。
    8. _id的value对应docId。

    ## 输出格式示例  
    返回内容请严格按照以下JSON格式（不要添加任何其它标记或注释）：
    {{
        "_type": "_doc",
        "_source": {{
            "meta_案件名称": "",
            "section_落款": "",
            "meta_法院层级": "",
            "meta_判决层级": "",
            "meta_关键词2": "",
            "meta_审判员": [],
            "info_同意离婚": false,
            "meta_法院_市": "",
            "meta_审理程序类型": "",
            "meta_法院_省": "",
            "meta_案号": "",
            "caseId": "",
            "meta_案件来源": "",
            "meta_文书名称": "",
            "meta_判决书名字": "",
            "section_文书首部": "",
            "meta_开庭情况": "",
            "meta_案由": "",
            "meta_判决类型": "",
            "section_标题": "",
            "section_理由": "",
            "section_文书尾部": "",
            "version": "",
            "meta_法院名称": "",
            "meta_法院_区县": "",
            "meta_裁判日期": "",
            "meta_案件类型": "",
            "meta_书记员": "",
            "section_判决主文": "",
            "section_裁判依据": "",
            "meta_关键词": [],
            "meta_法律条款": []
        }},
        "_id": "",
        "_index": "",
        "_score": 1
    }}

    ## 法律文书
    {text_content}
    """
