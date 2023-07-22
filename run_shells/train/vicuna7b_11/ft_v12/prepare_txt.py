import json
import os
import sys
from tqdm import tqdm
from pathlib import Path

pfd = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
sys.path.append(pfd)

from dataset.alpaca_cot.instruction2qas import instruction2example, process_f


def trans2txt(example_list, save_f):
    print(f"tans2txt ...")
    with open(save_f, 'w', buffering=1) as fw:
        for example in tqdm(example_list):
            fw.write(f"{json.dumps(example)}\n")

    print(f"save to:{save_f}")


# ---------------------------------------------------------------
# 挑选Alpaca-CoT的一些数据进行训练
# 原链接：https://huggingface.co/datasets/QingyiSi/Alpaca-CoT
# ---------------------------------------------------------------

base_dir = "/mnt/cephfs/hjh/common_dataset/nlp/QingyiSi_Alpaca-CoT/Alpaca-CoT"
save_base_dir = "/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/vicuna-7b/ft2_v12/txt_files"

glob_f_i = 0

# -------------------
# alpaca
# -------------------
data_file_list = [f"{base_dir}/alpaca/alpaca_data_cleaned.json"]
for f in data_file_list:
    parent_name = Path(f).parent.name
    save_f = f"{save_base_dir}/{parent_name}_{Path(f).name.replace('.json', f'_{glob_f_i}.txt')}"
    glob_f_i += 1
    if os.path.exists(save_f):
        continue
    trans2txt(process_f(f), save_f)

# -------------------
# alpacaGPT4
# -------------------
data_file_list = [f"{base_dir}/alpacaGPT4/alpaca_gpt4_data.json"]
for f in data_file_list:
    parent_name = Path(f).parent.name
    save_f = f"{save_base_dir}/{parent_name}_{Path(f).name.replace('.json', f'_{glob_f_i}.txt')}"
    glob_f_i += 1
    if os.path.exists(save_f):
        continue
    trans2txt(process_f(f), save_f)

# -------------------
# Auto-CoT
# -------------------
auto_coT_dir = f"{base_dir}/Auto-CoT"
data_file_list = [str(f) for f in Path(auto_coT_dir).glob("*.json")]
for f in data_file_list:
    parent_name = Path(f).parent.name
    save_f = f"{save_base_dir}/{parent_name}_{Path(f).name.replace('.json', f'_{glob_f_i}.txt')}"
    glob_f_i += 1
    if os.path.exists(save_f):
        continue
    trans2txt(process_f(f), save_f)

# -------------------
# Chain-of-Thought
# -------------------

chain_of_thought_dir = f"{base_dir}/Chain-of-Thought/formatted_cot_data"
data_file_list = [str(f) for f in Path(auto_coT_dir).glob("*.json")]
for f in data_file_list:
    parent_name = Path(f).parent.name
    save_f = f"{save_base_dir}/{parent_name}_{Path(f).name.replace('.json', f'_{glob_f_i}.txt')}"
    glob_f_i += 1
    if os.path.exists(save_f):
        continue
    trans2txt(process_f(f), save_f)

# -------------------
# CodeAlpaca
# -------------------
codealpaca_dir = f"{base_dir}/CodeAlpaca"
data_file_list = [str(f) for f in Path(auto_coT_dir).glob("*.json")]
for f in data_file_list:
    parent_name = Path(f).parent.name
    save_f = f"{save_base_dir}/{parent_name}_{Path(f).name.replace('.json', f'_{glob_f_i}.txt')}"
    glob_f_i += 1
    if os.path.exists(save_f):
        continue
    trans2txt(process_f(f), save_f)

# -------------------
# ConvAI2
# -------------------
data_file_list = [f"{base_dir}/ConvAI2/persona_train_self_revised.json"]
for f in data_file_list:
    parent_name = Path(f).parent.name
    save_f = f"{save_base_dir}/{parent_name}_{Path(f).name.replace('.json', f'_{glob_f_i}.txt')}"
    glob_f_i += 1
    if os.path.exists(save_f):
        continue
    trans2txt(process_f(f), save_f)

# -------------------
# FLAN-Muffin
# -------------------

data_file_list = [f"{base_dir}/FLAN-Muffin/flan.json"]
for f in data_file_list:
    parent_name = Path(f).parent.name
    save_f = f"{save_base_dir}/{parent_name}_{Path(f).name.replace('.json', f'_{glob_f_i}.txt')}"
    glob_f_i += 1
    if os.path.exists(save_f):
        continue
    trans2txt(process_f(f), save_f)

# -------------------
# FastChat
# -------------------
data_file_list = [f"{base_dir}/FastChat/Vicuna.json"]
for f in data_file_list:
    parent_name = Path(f).parent.name
    save_f = f"{save_base_dir}/{parent_name}_{Path(f).name.replace('.json', f'_{glob_f_i}.txt')}"
    glob_f_i += 1
    if os.path.exists(save_f):
        continue
    trans2txt(process_f(f), save_f)

# -------------------
# GPT4all
# -------------------

# 不要，这里的数据不是Gpt4的，它是一个GPT for all 的项目收集的数据, https://github.com/nomic-ai/gpt4all
# 其数据来源，是其他大模型的。不是gpt-4的
# gpt4all_file_list=[f'{base_dir}/GPT4all/gpt4all_without_p3.json']

# -------------------
# GPTeacher
# -------------------

GPTeacher_dir = f"{base_dir}/GPTeacher"
data_file_list = [str(f) for f in Path(auto_coT_dir).rglob("*.json")]
for f in data_file_list:
    parent_name = Path(f).parent.name
    save_f = f"{save_base_dir}/{parent_name}_{Path(f).name.replace('.json', f'_{glob_f_i}.txt')}"
    glob_f_i += 1
    if os.path.exists(save_f):
        continue
    trans2txt(process_f(f), save_f)

# -------------------
# finance
# -------------------

data_file_list = [f"{base_dir}/finance/finance_en.json"]
for f in data_file_list:
    parent_name = Path(f).parent.name
    save_f = f"{save_base_dir}/{parent_name}_{Path(f).name.replace('.json', f'_{glob_f_i}.txt')}"
    glob_f_i += 1
    if os.path.exists(save_f):
        continue
    trans2txt(process_f(f), save_f)

# -------------------
# Guanaco
# -------------------

data_file_list = [f"{base_dir}/Guanaco//Guanaco_additional_Dataset.json"]
for f in data_file_list:
    parent_name = Path(f).parent.name
    save_f = f"{save_base_dir}/{parent_name}_{Path(f).name.replace('.json', f'_{glob_f_i}.txt')}"
    glob_f_i += 1
    if os.path.exists(save_f):
        continue
    trans2txt(process_f(f), save_f)

# -------------------
# instinwild
# -------------------

data_file_list = [
    f"{base_dir}/instinwild/instinwild_en.json",
    f"{base_dir}/instinwild/instinwild_ch.json",
]
for f in data_file_list:
    parent_name = Path(f).parent.name
    save_f = f"{save_base_dir}/{parent_name}_{Path(f).name.replace('.json', f'_{glob_f_i}.txt')}"
    glob_f_i += 1
    if os.path.exists(save_f):
        continue
    trans2txt(process_f(f), save_f)

# -------------------
# instruct
# -------------------

data_file_list = [f'{base_dir}/instruct/instruct.json']
for f in data_file_list:
    parent_name = Path(f).parent.name
    save_f = f"{save_base_dir}/{parent_name}_{Path(f).name.replace('.json', f'_{glob_f_i}.txt')}"
    glob_f_i += 1
    if os.path.exists(save_f):
        continue
    trans2txt(process_f(f), save_f)
# -------------------
# prosocial dialog
# -------------------

data_file_list = [f"{base_dir}/prosocial-dialog/dialog_safety/train.json"]
for f in data_file_list:
    parent_name = Path(f).parent.name
    save_f = f"{save_base_dir}/{parent_name}_{Path(f).name.replace('.json', f'_{glob_f_i}.txt')}"
    glob_f_i += 1
    if os.path.exists(save_f):
        continue
    trans2txt(process_f(f), save_f)

# ----------------------------
# xP3数据转换
# ----------------------------

org_f = "/mnt/cephfs/hjh/common_dataset/nlp/QingyiSi_Alpaca-CoT/Alpaca-CoT/xP3/en/merged_en.json"
save_f = f"{save_base_dir}/merged_en.txt"

i = 0
with open(save_f, 'w', buffering=1) as fw:
    with open(org_f, 'r') as fr:
        for example in fr:
            clean_example = example.strip().rstrip(",").lstrip("[").rstrip("]")
            qa_example = instruction2example(json.loads(clean_example))
            fw.write(f"{json.dumps(qa_example)}\n")
            i += 1
            if i % 200000 == 0:
                print(i)
print("done!")

new_save_f = save_f.replace(".txt", f"_{i}.txt")
os.system(f"mv {save_f} {new_save_f}")

# 手动把说有文件合并为一个文件train_data.txt
