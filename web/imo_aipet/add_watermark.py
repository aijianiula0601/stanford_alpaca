import os


# ----------------------------------------------------------------------------
# 添加水印
# 参考：
# https://blog.csdn.net/huapeng_guo/article/details/130152259
# https://blog.csdn.net/WuLex/article/details/94222784
# ----------------------------------------------------------------------------


def add_watermark(img_path, watermark_path, save_path):
    # 左上角
    # cmd = f"ffmpeg -i {img_path} -i {watermark_path} -filter_complex \"overlay=10:10:alpha=0.4\" {save_path}"

    # 右下角
    # cmd = f"ffmpeg -i {img_path} -i {watermark_path} -filter_complex \"overlay=main_w-overlay_w-10:main_h-overlay_h-10:alpha=0.4\" {save_path}"

    # 右上角
    cmd = f"ffmpeg -i {img_path} -i {watermark_path} -filter_complex \"overlay=main_w-overlay_w-10:10:alpha=0.4\" {save_path}"

    os.system(cmd)
