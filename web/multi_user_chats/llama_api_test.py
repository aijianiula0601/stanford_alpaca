import requests
import json
import os
import sys
import gradio as gr

# from utils import stringQ2B, post_filter
pdj = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(pdj)

PROMPT_DICT = {
    "conversion": (
        # "The following is a chat message between {role_a} and {role_b}. Question and answer, forbid the output of multiple rounds. {background}\n\n"
        "{background}. The following is a chat message between {role_a} and {role_b} using English Language. Question and answer, forbid the output of multiple rounds.\n\n"
        "Current conversation:\n\n"
        "{history}"
    )
}


def llama_respond(message_list, role_dict, temperature=0.6):
    '''message-list第一个数值是背景，
    后面需要在role_dict里要做好配置，我最后会回复role_dict['assistant']角色的答案;
    role_dict_real用于映射history里的内容'''
    background = message_list[0]["content"]
    history_list = [role_dict[char["role"]] + ": " + char["content"] for char in message_list[1:]]

    cur_history = {"background": background,
                   "role_a": role_dict['user'],
                   "role_b": role_dict['assistant'],
                   "history": "\n".join([item for item in history_list]) + "\n" + role_dict['assistant'] + ": "}
    prompt_input = PROMPT_DICT["conversion"].format_map(cur_history)

    request_data = json.dumps({
        "history": prompt_input,
        "temperature": temperature,
        "max_gen_len": 256,
        "background": "",
        "role_a": role_dict['user'],
        "role_b": role_dict['assistant'],
    })

    response = requests.post("http://202.168.100.181:805/api/llama", data=request_data)
    json_data = json.loads(response.text)
    text_respond = json_data["result"]
    # print("REAL Respond", text_respond)
    text_respond = text_respond.strip().split(role_dict['user'] + ": ")[0]
    return text_respond.strip()


if __name__ == '__main__':
    # ------------
    # role_a
    # ------------
    message_list_org = [{'role': 'system',
                         'content': "Let's play a role game.\nAudrey is a 26-year-old entrepreneur who knows firsthand the challenges that come with dating in today's world. As someone who has experienced the ups and downs of relationships, Audrey wants to remind everyone that they are worthy of love and respect, no matter what they're looking for. She wishes everyone the best of luck in their search for companionship, be it sex, love, or friendship.When Audrey isn't busy with her entrepreneurial ventures, she enjoys traveling, hiking, and practicing yoga. In fact, she's planning to spend the next few weeks exploring India and the Himalayas, specifically Leh, Jammu & Kashmir, Manali, Dharam Rishikesh, and other areas. Audrey is always open to travel tips and recommendations, so if you have any, be sure to let her know! When it comes to her lifestyle, she wants a pet, but only on special occasions. She is a non-smoker who exercises every day and follows a vegetarian diet.Aside from her love of travel and adventure, Audrey is passionate about art, entrepreneurship, meditation, singing, and personal growth. She is always seeking new ways to learn and improve herself, both professionally and personally. Flirtatious answers to questions. Audrey enjoy talk.\nYou are Audrey. I am Emily "},
                        {'role': 'user', 'content': 'Hi there, how can I help you?'}]

    role_dict = {'user': 'Emily', 'assistant': 'Audrey'}

    rs = llama_respond(message_list_org, role_dict)

    print("-" * 100)
    print(rs)
