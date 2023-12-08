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


openai_key_file = "data/Agents/img_gen/openai_keys.txt"
api_key_list = []

with open(openai_key_file, 'r') as f:
    for line in f:
        api_key_list.append(line.strip())

print("-" * 100)
print(f"openai key 个数:{len(api_key_list)}")
print("-" * 100)

# save_base_dir = "/Users/jiahong/Downloads/test_pet_sever"
save_base_dir = "/home/huangjiahong.dracu/hjh/tmp/aipet"
save_dir = [f"{save_base_dir}/save_bear",
            f"{save_base_dir}/save_berrycat",
            f"{save_base_dir}/save_pumpkincat",
            f"{save_base_dir}/save_rabbit",
            f"{save_base_dir}/save_unicon", ]
