import os
from pathlib import Path
from tqdm import tqdm

# ------------------------------------
# 标注数据回收
# ------------------------------------

# 标注完合格的图片路径
label_file_path = ""

replace_dir = ""
# 保存目录
save_dir = ""

# --------------
# 拿回文案
# --------------

with open(label_file_path, 'r') as fr:
    for img_p in tqdm(fr.readlines()):
        cur_save_dir = str(Path(img_p).parent).replace(replace_dir, save_dir)
        description_f = str(Path(img_p).parent.joinpath("new_description.txt"))
        en_description_f = str(Path(img_p).parent.joinpath("new_description_en.txt"))

        assert os.path.exists(description_f), f"{description_f} not exist!"
        assert os.path.exists(en_description_f), f"{en_description_f} not exist!"

        if not os.path.exists(cur_save_dir):
            os.makedirs(cur_save_dir)

        os.system(f"cp -rf {label_file_path} {cur_save_dir}")
        os.system(f"cp -rf {description_f} {cur_save_dir}")
        os.system(f"cp -rf {en_description_f} {cur_save_dir}")

print(f"save to:{save_dir}")
