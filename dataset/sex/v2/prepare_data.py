import json
import sys
import os
import traceback

pdf = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(pdf)
print(f"pdf:{pdf}")

from dataset.data_utils import *

# ------------------------------------------------
# 之前实验发现表情错误问题，返回重新纠正
# 1.修复表情符号跟上下文不相符问题
# 2.去掉连续表情符号问题
# ------------------------------------------------


base_dir = "/mnt/cephfs/hjh/common_dataset/nlp/biaozhu_sex_data/v2"
save_f = f"{base_dir}/merged_data.json"
all_example_list = []

f_list = [
    f"{base_dir}/data_01_0626_1_Jerrold.json",
    f"{base_dir}/data_01_0626_2_Natasha.json",
    f"{base_dir}/data_01_0626_3_Wenxin.json",
    f"{base_dir}/data_02_0626_1_Aliff.json",
    f"{base_dir}/data_02_0626_2_Crisann.json",
    f"{base_dir}/data_02_0626_4_PeiFen.json",
    f"{base_dir}/data_02_0626_5_Marianne.json",
]

# -------------------------
# 处理为from value格式
# -------------------------

print("-" * 100)
print("处理为from value格式")
print("-" * 100)

for f in f_list:
    print(f"reading :{f}")
    with open(f, 'r') as fr:
        narrative_flag = False
        human_name = None
        bot_name = None
        qas_list = []
        i = 0
        for line in fr:
            try:

                line = line.replace("\n", "").strip()

                if line == "":
                    continue

                if 'Scene' in line:
                    if i > 0:
                        qas_list[0]['narrative'] = narrative
                        all_example_list.append(qas_list)

                        narrative_flag = False
                        human_name = None
                        bot_name = None
                        qas_list = []

                    narrative_flag = True
                    narrative = ""
                    continue

                if narrative_flag:
                    narrative += line

                if "They start a conversation" in line:
                    assert narrative != ""
                    narrative_flag = False
                    continue

                if line.startswith("###"):
                    from_name = line.split(":")[0].replace("###", "").replace(":", "").strip()
                    value_v = line.split(":")[1].strip()
                    qa = {"from": from_name, "value": value_v}
                    qas_list.append(qa)

                i += 1
            except Exception as e:
                print(f"Error line:{line}")
                traceback.print_exc(e)

# -------------------------
# 处理为qas格式
# -------------------------


print("-" * 100)
print("处理为qas格式")
print("-" * 100)

dataset_name = CROWDSOURCE_SEX_DATASET_NAME

skip_example_n = 0
sexy_data = []
for turns_data in tqdm(all_example_list):

    if len(turns_data) < 2:
        print("-*" * 30)
        skip_example_n += 1
        continue

    skip_example_flag = False
    background = None
    qas = {}
    human_name = turns_data[0]['from']
    bot_name = turns_data[1]['from']
    turn_i = 0
    for i, td in enumerate(turns_data):
        if i == 0:
            background = td['narrative']
        if (i + 1) % 2 == 1:
            if human_name != td['from']:
                skip_example_flag = True  # 对话里面，有可能有多人对话，所以会出现不一致问题
                print("-*" * 100)
                print(json.dumps(turns_data))
                print("-*" * 100)
                break
            assert human_name == td['from']
            qas[f"turn_{turn_i}"] = {QUESTION_KEY: td['value']}
        else:
            if bot_name != td['from']:
                skip_example_flag = True
                break
            assert bot_name == td['from']
            qas[f"turn_{turn_i}"][ANSWER_KEY] = td['value']
            turn_i += 1

    if skip_example_flag:
        skip_example_n += 1
        continue

    turn_n = len(qas)
    if QUESTION_KEY not in qas[f"turn_{turn_n - 1}"] or ANSWER_KEY not in qas[f"turn_{turn_n - 1}"]:
        qas.pop(f"turn_{turn_n - 1}")

    if len(qas) < 1:
        continue

    assert background is not None
    sexy_data.append(
        {BACKGROUND_KEY: background,
         DATASET_KEY: dataset_name, HUMAN_NAME_KEY: human_name, BOT_NAME_KEY: bot_name,
         QAS_KEY: qas})

print(
    f"dataset name:{dataset_name},all_n:{len(sexy_data)}, skip_example_n:{skip_example_n}")

json.dump(sexy_data, open(save_f, 'w'))
print(f"save to:{save_f}")
