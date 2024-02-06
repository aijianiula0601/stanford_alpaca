import os
import sys
import json
import random

pjd = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
print(f"pjd:{pjd}")
sys.path.append(pjd)

from stages_chat.utils import get_gpt_response

# org_pic_sentence = 'send me your picture'
# org_pic_sentence = 'your whatsapp number?'
org_pic_sentence = 'give me your instagram account?'

message_list = [
    {"role": "system", "content": org_pic_sentence},
    # {"role": "user", "content": "Use colloquial language, change the expression, and limit it to 15 words or less."}
    {"role": "user", "content": "采用口语化的方式改写上面语句，换一种表达方式，少于15个单词，用英文输出"}
]

for i in range(100):
    res_text = get_gpt_response(message_list, gpt_version='gpt4')
    print(res_text)
