########################### 1.保存部分代码 ##################################
# """用户提问的意图的状态分析"""
# format_map_dic = {
#     'chat_history': chat_history,
#     'user_question': user_question,
# }
# prompt = config.PROMPT_DIC['intention_state'].format_map(format_map_dic)
# message_list = [{"role": "user", "content": prompt}]
# res_text1 = get_gpt_result(self.engine_name, message_list)

# intention = parse_intention(res_text1)
# state = parse_state(res_text1)

# format_map_dic = {
#     'chat_history': chat_history,
#     'user_question': user_question,
# }
# prompt = config.PROMPT_DIC['chat_state'].format_map(format_map_dic)
# message_list = [{"role": "user", "content": prompt}]
# res_text2 = get_gpt_result(self.engine_name, message_list)

# chat_state = parse_chat_state(res_text2)

# "intention_state": (
#     "You are a professional psychoanalyst who can accurately analyze the user's intention and chat state based on the chat history.\n"
#     "Latest chat history:\n"
#     "```\n"
#     "{chat_history}\n"
#     "```\n"
#     "user's question:\n"
#     "```\n"
#     "user: {user_question}\n"
#     "```\n"
#     "According to the latest chat history and the user's question, analyze the user's intention and chat state. You must follow the following steps to analyze.\n"
#     "step1: Give a short summary of the chat history and the user's question, less than 30 words.\n"
#     "step2: Combined with the latest chat history, analyze the cause of the user's current question, and then output the user's intention of the current question, less than 30 words.\n"
#     "step3: Combined with the latest chat history, analyze the cause of the user's current question, and then output the user's state of the current question. less than 30 words.\n"
#     "step4: Output a json object that contains two keys for the user's intention and chat state.\n"
#     "Split each Step with a newline."
# ),
# "chat_state": (
#     "You are a professional psychoanalyst who can accurately analyze the chat state based on the chat history.\n"
#     "Latest chat history:\n"
#     "```\n"
#     "{chat_history}\n"
#     "```\n"
#     "user's question:\n"
#     "```\n"
#     "user: {user_question}\n"
#     "```\n"
#     "Alternative chat states:\n"
#     "1. The user is chatting politely and actively.\n"
#     "2. The user is asking for her whatsapp number.\n"
#     "3. The user is trying to chat about sex.\n"
#     "4. The user is not very willing to chat.\n"
#     "5. The user is asking for her picture.\n"
#     "Now, please help me to analysis the chat history. You must follow the following steps to analyze:\n"
#     "step1: Give a short summary of the chat history and the user's question, less than 30 words.\n"
#     "step2: According to the user's current question, analyze which of the alternative chat states the current question belongs to. Only need to output the index of the state.\n"
#     "step3: Output a json object that contains two keys for the chat topic and chat state.\n"
#     "Split each Step with a newline."
# ),

########################### 2. 编辑距离 ##################################
# def edit_distance_of_sentence(a, b):
#     # b = 'Sure, here is my photo, which is about travel.'

#     a = [x.strip(',.?!\'"') for x in a.lower().strip().split()]
#     b = [x.strip(',.?!\'"') for x in b.lower().strip().split()]

#     m,n = len(a)+1,len(b)+1
#     d = [[0]*n for i in range(m)]

#     d[0][0]=0
#     for i in range(1,m):
#         d[i][0] = d[i-1][0] + 1
#     for j in range(1,n):
#         d[0][j] = d[0][j-1]+1

#     temp = 0
#     for i in range(1,m):
#         for j in range(1,n):
#             if a[i-1]==b[j-1]:
#                 temp = 0
#             else:
#                 temp = 1
            
#             d[i][j]=min(d[i-1][j],d[i][j-1]+1,d[i-1][j-1]+temp)
#     print("edit_distance_of_sentence: ", d[m-1][n-1])
#     return d[m-1][n-1]

# res = edit_distance_of_sentence('Sure. I love the great outdoors and exploring new trails!', 'Sure, here is my photo, which is about travel')
# print(res)

########################### 3. 转图片格式 ##################################
# import os  
# from PIL import Image  
  
# # os.listdir()方法获取文件夹名字，返回数组  
# file_name_list = os.listdir('pictures/naila')  
# for file_name in file_name_list:  
#     file_name = 'pictures/naila/' + file_name
#     if file_name.endswith('.webp'):  
#         im = Image.open(file_name)  
#         if im.mode == "RGBA":  
#             im.load()  # required for png.split()  
#             background = Image.new("RGB", im.size, (255, 255, 255))  
#             background.paste(im, mask=im.split()[3])  
#         save_name = file_name.replace('webp', 'jpg')  
#         if not os.path.exists(save_name):  
#             print("%s -> %s"%(file_name,save_name))  
#             im.save('{}'.format(save_name), 'JPEG')  

# import gradio as gr

# history = [['chang: hello', None], ['chang: are u there', 'yue: yes']]
# with gr.Blocks() as demo:
#     with gr.Row():
#         chatbot = gr.Chatbot(label="history", value=history)

# demo.queue().launch(server_name="0.0.0.0", server_port=8889)

########################### 4. 测试state分类准确性 ##################################
import logging
import openai

openai.api_type = "azure"
openai.api_base = "https://bigo-chatgpt.openai.azure.com/"
openai.api_version = "2023-03-15-preview"
openai.api_key = "0ea6b47ac9e3423cab22106d4db65d9d"
engine_name = "bigo-gpt35"
# openai.api_type = "azure"
# openai.api_base = "https://gpt4-test-cj-0803.openai.azure.com/"
# openai.api_version = "2023-03-15-preview"
# openai.api_key = "bca8eef9f9c04c7bb1e573b4353e71ae"
# engine_name = "gpt4-16k"

user_question = "ok\n"
chat_history = ("Naila: knock knock\n"
                "user: hey\n"
                "Naila: Hi, where are you from?\n"
                "user: can you send me a pic\n"
                "Naila: Here is my photo, which is about selfie.Give you a heart\n")
user_question = "you were wearing mask, let me see your face\n"
pic_topics = "Saudi, selfie, travel"

chat_analysis = (
        "You are a professional psychologist, and you are particularly good at analyzing the intentions and states behind conversations."
        "Now please do an analysis based on the following information:\n"
        "```\n"
        "Latest chat history:\n"
        "{chat_history}\n"
        "```\n"
        "Current user's question:\n"
        "{user_question}\n"
        "```\n"
        "Alternative chat states:\n"
        "1. The user is chatting politely and actively.\n"
        "2. The user is expressing his love.\n"
        "3. The user is trying to chat about sex.\n"
        "4. The user is not very willing to chat.\n"
        "5. The user is asking for her picture.\n"
        "```\n"
        "Alternative topics:\n"
        "{pic_topics}\n"
        "```\n"
        "Now, please help me to analysis the chat history. You must follow the following steps to analyze:\n"
        "step1: Give a short summary of the chat history and the user's question, less than 30 words.\n"
        "step2: According to the user's current question, analyze which of the alternative chat states the current question belongs to. Only need to output the index of the state.\n"
        "step3: Combined with the latest chat history, analyze the cause of the user's current question, and then output the user's intention of the current question, less than 30 words.\n"
        "step4: Combined with the above information, analyze which of the alternative topics the current chat topic is. If there is no correct answer in the optional topics, you need to fill in your answer yourself.\n"
        "step5: Output a json object that contains three keys for the [user_intention], [chat_topic] and [chat_state].\n"
        "Split each Step with a newline."
)

format_map_dic = {
    'chat_history': chat_history,
    'user_question': user_question,
    'pic_topics': pic_topics,
}

prompt = chat_analysis.format_map(format_map_dic)

message_list = [{"role": "user", "content": prompt}]

response = openai.ChatCompletion.create(
        engine=engine_name,
        messages=message_list,
        temperature=0.7,
        max_tokens=800,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None)
res_text = response['choices'][0]['message']['content']

# print("=" * 100)
# print('【1】：意图分析')
# print("=" * 100)
print(f'prompt:\n{prompt}')
print("-" * 100)
print(f"{res_text}")
print("-" * 100)