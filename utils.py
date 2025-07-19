# -*- coding: utf-8 -*-
import csv
import json
from collections import Counter

from bs4 import BeautifulSoup


def field_majority_vote(sample_outputs):
    """
    针对每个key进行投票，支持任意深度嵌套结构。
    最终结果中将删除值为空（""、[]、{}、None）的字段。
    """
    if not sample_outputs:
        return {}

    if not all(isinstance(s, dict) for s in sample_outputs):
        raise ValueError("All samples must be dicts.")

    def is_empty_value(v):
        return v in ("", None, []) or (isinstance(v, dict) and not v)

    def recursive_vote(values_list):
        if all(isinstance(v, dict) for v in values_list):
            merged = {}
            keys = set().union(*[v.keys() for v in values_list])
            for k in keys:
                sub_values = [v.get(k, None) for v in values_list]
                merged_value = recursive_vote(sub_values)
                if not is_empty_value(merged_value):
                    merged[k] = merged_value
            return merged

        if all(isinstance(v, list) for v in values_list):
            if all(len(v) == 0 for v in values_list):
                return []

            if all(all(isinstance(i, dict) for i in v) for v in values_list):
                vtuples = [tuple(json.dumps(i, sort_keys=True) for i in v) for v in values_list]
                count = Counter(vtuples)
                most_common_tuple = count.most_common(1)[0][0]
                return [json.loads(s) for s in most_common_tuple]

            vtuples = [tuple(v) for v in values_list]
            count = Counter(vtuples)
            most_common_tuple = count.most_common(1)[0][0]
            return list(most_common_tuple)

        normalized = []
        for v in values_list:
            if isinstance(v, (bool, int, float)):
                normalized.append(v)
            elif isinstance(v, str):
                normalized.append(v.strip())
            elif v is None:
                normalized.append("")
            else:
                normalized.append(json.dumps(v, sort_keys=True))

        count = Counter(normalized)
        most_common_value = count.most_common(1)[0][0]

        if isinstance(most_common_value, str):
            try:
                result = json.loads(most_common_value)
                return result
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
    "s1": "陈同安、登封市唐庄镇人民政府乡政府再审审查与审判监督行政裁定书",
    "qwContent": [
      "河南省高级人民法院",
      "行 政 裁 定 书",
      "(2019)豫行申1262号",
      "再审申请人(一审原告、二审上诉人)陈同安,男,1950年7月18日出生,汉族,住河南省登封市。",
      "被申请人(一审被告、二审被上诉人)登封市唐庄镇人民政府,住所地河南省登封市唐庄镇唐东村。",
      "法定代表人崔会生,镇长。",
      "委托代理人赵继昌,该镇政府工作人员。",
      "一审第三人中铁十一局集团第四工程有限公司,住所地湖北省武汉市东湖开发区华光大道21号。",
      "法定代表人谭发刚,董事长。",
      "委托代理人张文豪,该公司工作人员。",
      "再审申请人陈同安因诉被申请人登封市唐庄镇人民政府、第三人中铁十一局集团第四工程有限公司不作为及行政赔偿一案,不服郑州市中级人民法院(2018)豫01行终1005号行政判决,向本院申请再审。本院依法组成合议庭,对本案进行了审查。现已审查终结。",
      "再审申请人陈同安申请再审称,陈同安2007年5月10日向被申请人登封市唐庄镇人民政府申请修建上防护工程,登封市唐庄镇人民政府2007年5月29日对陈同安作出修建上防护工程并解决陈同安水损赔偿的承诺,登封市唐庄镇人民政府没有按照承诺修建防护工程,构成行政不作为。一、二审判决认定陈同安主张的修建上防护工程不是登封市唐庄镇人民政府应当履行的法定职责错误,请求对本案进行再审,撤销一审判决中的第二项判决,撤销二审判决。",
      "本院经审查认为,登封市唐庄镇人民政府不存在修建防护工程的法定职责,再审申请人陈同安提供的证据亦不能证明登封市唐庄镇人民政府具有修建防护工程的约定义务,陈同安提起本案诉讼,请求判令登封市唐庄镇人民政府履行修建防护工程的法定职责的诉讼请求,不能成立。原审判决驳回其诉讼请求正确,陈同安的再审申请不符合《中华人民共和国行政诉讼法》第九十一条规定的情形。依照《最高人民法院关于适用〈中华人民共和国行政诉讼法〉的解释》第一百一十六条第二款的规定,裁定如下:",
      "驳回陈同安的再审申请。",
      "审判长  宋炉安",
      "审判员  王凤强",
      "审判员  于红涛",
      "二〇一九年十一月七日",
      "书记员  张 玥"
    ]
  }
    """


def get_prompt(text_content):
    return """
    你是一位**法律信息抽取的专家**，现在请你从下面提供的**法律文书**中抽取信息，并严格按照我给定的JSON格式输出，**不要输出任何额外内容或解释**。

    ## 任务要求  
    1. 只返回**合法JSON**，不要有任何额外内容。  
    2. 下面的输出格式仅为示例，JSON的key可以参考给出的格式，但若有额外未给出的key，则同样提取出来。
    3. 若没有key对应的value，则删除该key，我不希望看到空value的情况。  
    4. 布尔字段如`info_同意离婚`必须为`true`或`false`。
    5. 日期请尽量提取为`YYYY-MM-DD`格式。
    6. _index的value全为es_fdlawcase_all。
    7. key的风格尽量与示例保持一致。

    ## 输出格式示例  
    {{
      "_type": "_doc",                     // 固定为"_doc"
      "_index": "string",                  // 为 "es_fdlawcase_all"
      "_score": 1,                         // 固定为1
      "_source": {{
        "version": "string",              // 数据版本号，例如 "20191101"
        // 案件基本信息
        "meta_案件名称": "string",             // 案件全称
        "meta_案号": "string",                // 案件编号（如 “（2020）沪01民终123号”）
        "meta_案由": "string",                // 案由，如 “民间借贷纠纷”
        "meta_案件类型": "string",             // 案件类型，如 “民事”
        "meta_案件来源": "string",             // 案件来源，如 “上诉”、“其他”
        "meta_判决书名字": "string",           // 判决书名称，如 “民事判决书”
        "meta_判决类型": "string",             // 判决文书类别（如判决书、裁定书）
        "meta_判决层级": "string",             // 判决层级，如“一审”、“二审”
        "meta_裁判日期": "yyyy-mm-dd",        // 判决日期
        "meta_开庭日期": "yyyy-mm-dd",        // 开庭日期
        "meta_立案时间": "yyyy-mm-dd",        // 立案日期
        "meta_审理程序类型": "string",         // 审理程序类型，如 “普通程序”或“简易程序”
        "meta_开庭情况": "string",             // 开庭情况，如 “公开开庭审理”
        // 法院信息
        "meta_法院名称": "string",             // 审理法院名称
        "meta_法院层级": "string",             // 法院层级，如 “基层”、“中级”
        "meta_法院_省": "string",              // 法院所在省
        "meta_法院_市": "string",              // 法院所在市
        "meta_法院_区县": "string",            // 法院所在区县
        // 人员信息
        "meta_原告": ["string"],               // 原告列表
        "meta_被告": ["string"],               // 被告列表
        "meta_律师": ["string"],               // 出庭律师列表
        "meta_律所": ["string"],               // 律师所在律所
        "lawyerInfo": ["string"],              // 律师-律所组合信息
        "meta_审判长": "string",               // 审判长姓名
        "meta_审判员": ["string"],             // 审判员列表
        "meta_书记员": "string",               // 书记员姓名
        "meta_人民陪审员": ["string"],         // 人民陪审员姓名（如有）
        // 当事人信息与关系图谱
        "meta_人物信息": [                     // 结构化当事人列表
          {{
            "pname": "string",                // 姓名或单位名
            "ptype": "string",                // 身份，如 “原告”、“被告”
            "pnameType": 1,                   // 类型编号，被告1、原告2、其它3
            "ptypes": ["string"],             // 所有身份合集
            //人物身份信息，可以根据实际提供的信息自行补充
            "peopleAttrMap": 
            {{                
              "info_性别": "string",            
              "info_当事人所有地位": ["string"],
              "info_居住地址_分类": ["string"]
            }}
          }}
        ],
        "meta_当事人关系": [                  // 人物之间的结构化关系图
          {{
        "sourcePersonName": "string",     // 源人物
            "targetPersonName": "string",     // 目标人物
            "relations": ["string"]           // 关系名称，如“担保”、“借贷”
          }}
        ],
        // 判决结构化内容
        "section_标题": "string",             // 判决文书标题部分
        "section_文书首部": "string",         // 文书首部内容（案由、当事人）
        "section_原告陈述": "string",         // 原告诉称
        "section_被告陈述": "string",         // 被告答辩
        "section_事实构成": "string",         // 审理查明的事实
        "section_理由": "string",             // 法院认定理由
        "section_裁判依据": "string",         // 引用法律依据
        "section_判决主文": "string",         // 判决结果
        "section_文书尾部": "string",         // 文书末尾签署部分
        "section_落款": "string",             // 法官署名与日期
        "meta_案件结果": "string",            // 案件裁判结果
        "info_二审裁判结果": "string",        // 若为二审，记录其裁判结论
        "info_一审立案有误":"bool"            // 判断是否为被认定一审立案有误的案件，若是为true，否为false，无法判断则删除此key
        "info_已生效的案件再审改判或重审":"string"    // 填入已生效的案件为再审改判还是发回重审，若不是终审阶段已生效的案件则删除此key
        "info_违法执行":"bool"               // 判断是否违法执行，若是为true，否为false，无法判断则删除此key
        "info_违法审判":"bool"               // 判断是否违法审判，若是为true，否为false，无法判断则删除此key
        "info_结案":"bool"                  //判断该案件是否结案，一般适用于执行裁定书，若是为true，否为false，无法判断则删除此key
        "info_标的额": ["int"]               //标的额
        "meta_法官":["string"]              //法官名单
        // 法律条文
        "meta_关键词": ["string"],           // 案件关键词列表
        "meta_法律条款": ["string"],         // 法律条文原文
        "meta_法律条款索引": ["string"],     // 法律条文的ID/索引
        // 关联信息（主要出现在二审中）
        "meta_一审案号": "string",            // 原审案号
        "meta_关联案号": ["string"],          // 所有关联案号
        "meta_关联文书": [                    // 所有关联文书（一般为一审）
          {{
        "meta_案号": "string",
            "meta_法院名称": "string"
          }}
        ],
        // 原文
        "pos": []                      // 原文，直接对应传入文书的qwContent字段
      }}
    }}

    ## 法律文书
    {text_content}
    """.format(text_content=text_content)
