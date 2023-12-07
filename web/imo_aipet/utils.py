import re


def parse_res_text(res_text: str, key: str):
    pattern = r'"{0}"\s*:\s*("[^"]*"|[^",]*)'.format(key)
    # pattern = r'"{0}"：\s*"([^"]*)"'.format(key)

    match = re.search(pattern, res_text)
    if match:
        value = match.group(1)
        return value
    else:
        pattern = r'"{0}"\s*：\s*("[^"]*"|[^",]*)'.format(key)
        match = re.search(pattern, res_text)
        if match:
            value = match.group(1)
            return value
        else:
            return None


api_key_list = ["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",
                "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",
                "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",
                "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",
                "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",
                "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",
                "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",
                "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",
                "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",
                "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",
                "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",
                "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",
                "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",
                "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",
                "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", ]

# save_base_dir = "/Users/jiahong/Downloads/test_pet_sever"
save_base_dir="/home/huangjiahong.dracu/hjh/tmp/aipet"
save_dir = [f"{save_base_dir}/save_bear",
            f"{save_base_dir}/save_berrycat",
            f"{save_base_dir}/save_pumpkincat",
            f"{save_base_dir}/save_rabbit",
            f"{save_base_dir}/save_unicon", ]
