import os
from pathlib import Path
from tqdm import tqdm

# 把生成图片中的文案全部复制出来

org_dir = "/mnt/cephfs/hjh/train_record/images/dataset/imo_aipet/journey_imgs2jpg"

save_dir = "/mnt/cephfs/hjh/train_record/images/dataset/imo_aipet/journey_imgs2jpg_description"

for file in tqdm([f for f in Path(org_dir).rglob("new_description.txt")]):
    file_name = file.name

    cur_save_dir = str(file.parent).replace(org_dir, save_dir)
    if not os.path.exists(cur_save_dir):
        os.makedirs(cur_save_dir)
        os.system(f"cp -rf {str(file)} {cur_save_dir}/new_description.txt ")

print(f"done! save to:{save_dir}")
