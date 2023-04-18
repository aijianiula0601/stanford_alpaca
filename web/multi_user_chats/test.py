import json

prepared_background_list = json.load(open("prepared_background.json"))

role_list = [None] + list(prepared_background_list.keys())
print(role_list)