import os
from pathlib import Path
from PIL import Image
from joblib import Parallel, delayed
from tqdm import tqdm


def png2jpg(args):
    img_path, description_path, save_path = args
    save_dir = Path(save_path).parent
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    description_f = f"{save_dir}/description.txt"
    if not os.path.exists(description_f):
        os.system(f"cp -rf {description_path} {description_f}")

    img = Image.open(img_path)
    img.save(save_path, quality=95)


if __name__ == '__main__':

    base_dir = "/mnt/cephfs/hjh/train_record/images/dataset/imo_aipet"
    png_dir = f'{base_dir}/journey_imgs'
    jpg_dir = f"{base_dir}/journey_imgs2jpg"

    print("reading png ...")
    args_list = []
    for img_path in tqdm([str(f) for f in Path(png_dir).rglob("*.png")]):
        save_path = f"{jpg_dir}/{img_path.replace(png_dir, '').replace('.png', '.jpg')}"
        description_f = f"{Path(img_path).parent}/description.txt"
        if not os.path.exists(save_path):
            args_list.append((img_path, description_f, save_path))

    print("reading done!")
    n_job = 10
    results = Parallel(n_jobs=n_job, backend="multiprocessing")(delayed(png2jpg)(pts) for pts in tqdm(args_list))
    for _ in results:
        pass
