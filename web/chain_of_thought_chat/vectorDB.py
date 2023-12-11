import json
import openai
import re
import time
import copy
from numpy import dot
from numpy.linalg import norm


# --------------------------------------
# 定义简单的向量数据库对象
# --------------------------------------
class Mem_Emb_DB():
    def __init__(self, db_name='emb_db'):
        self.db_name = db_name
        self.mem_list = []

    def add_mem(self, mem: str):
        # --------------------------------------
        # 在向量数据库中添加词向量记忆
        # mem:记忆文本 mem_emb:记忆文本对应的词向量
        # --------------------------------------
        emb = get_embedding(mem)
        self.mem_list.append((mem, emb))


# --------------------------------------
# 获得一段文字的词向量
# save_path:生成的状态和图片prompt的存储路径，country jour_place：国家和地区, api_key：openai的key
# text：需要转化为向量的文本
# 输出：一个词向量的list->[0.35, 0.82, ...]
# --------------------------------------

def get_embedding(text: str, model="text-embedding-ada-002"):
    openai_api_key = "548e5c0c2aff453e932948927a27bde6"
    openai.api_key = openai_api_key
    openai.api_type = "azure"
    # openai.api_version = "2023-06-15-preview"
    openai.api_version = "2023-03-15-preview"
    openai.api_base = "https://bigo-chatgpt-9.openai.azure.com/"
    res = openai.Embedding.create(
        input=[text], deployment_id="text-embedding-ada-002")['data'][0]['embedding']
    return res


# --------------------------------------
# 给定一段文字，从向量数据库中取出相关联的k段文字
# text：要查找的文字    db：向量数据库     top_k:top_k个最相关的文字
# 返回：找到的文本（list）， 在向量数据库中最相关的k个记忆的idx(list)，以及文本的embedding
# --------------------------------------
def get_revelant_mem(text, db: Mem_Emb_DB, top_k=2):
    sim_score = [0 for _ in range(len(db.mem_list))]
    text_emb = get_embedding(text)
    prev_mem_emb = [pair[1] for pair in db.mem_list]

    for i in range(len(prev_mem_emb)):
        sim_score[i] = cos_sim(text_emb, prev_mem_emb[i])
    relevent_idx, _ = get_top_k_idx(sim_score, top_k=top_k)
    reterived_text = []

    for i in range(len(relevent_idx)):
        reterived_text.append(db.mem_list[relevent_idx[i]][0])
    return reterived_text, relevent_idx, text_emb


def cos_sim(a, b):
    ## 返回一个值 0-1
    return dot(a, b) / (norm(a) * norm(b))


def get_top_k_idx(scores, top_k=2):
    t = copy.deepcopy(scores)
    # 求m个最大的数值及其索引
    max_number = []
    max_index = []
    for _ in range(top_k):
        number = max(t)
        index = t.index(number)
        t[index] = 0
        max_number.append(number)
        max_index.append(index)
    return max_index, max_number


db = Mem_Emb_DB()
str1 = '用户喜欢旅行'
str2 = '我告诉用户我也喜欢旅行，我上个月去了巴黎'
str3 = '用户昨天妹妹病了住院'
db.add_mem(str1)
db.add_mem(str2)
db.add_mem(str3)
print(get_revelant_mem('用户问我去上个月去哪里旅行了', db))
