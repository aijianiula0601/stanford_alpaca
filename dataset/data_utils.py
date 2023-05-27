# ---------------------------------------------------------------------------------------------
# 定义qa数据格式使用的特定字符
# ---------------------------------------------------------------------------------------------
HUMAN_NAME_KEY = "human_name"
BOT_NAME_KEY = "bot_name"
BACKGROUND_KEY = "background"
QAS_KEY = "qas"
QUESTION_KEY = "question"
ANSWER_KEY = "answer"
DATASET_KEY = "dataset_name"


# ---------------------------------------------------------------------------------------------
# 定义各个数据集的prompt
# ---------------------------------------------------------------------------------------------

#  qa数据中一个example为：
#   {
#         "background":"---",
#         "human_name":"a",
#         "bot_name":"b",
#         "qas":{
#             "turn_0":{"question":"---","answer":"---"},
#             ...
#             "turn_n":{"question":"---","answer":"---"}
#         }
#   }

def sota_prompt(human_name, bot_name, background):
    return f"Here is a conversation between {human_name} and {bot_name} related to the description below. {background}\n\n"


def sharegpt_prompt(human_name, bot_name, background):
    return f"Below is an chat between {human_name} and {bot_name}.\n\n"


def persona_chat_prompt(human_name, bot_name, background):
    return f"{background}\n\n The above describes the state information of {bot_name} from the perspective of first person. The following is a conversation between {human_name} and {bot_name}.\n\n"


def empathetic_dialogues_prompt(human_name, bot_name, background):
    return f"Here is a conversation between {human_name} and {bot_name}.\n\n"


def stanford_52k_prompt(human_name, bot_name, background=""):
    """
    PROMPT_DICT = {
        "prompt_input": (
            "Below is an instruction that describes a task, paired with an input that provides further context. "
            "Write a response that appropriately completes the request.\n\n"
            "### Instruction:\n{instruction}\n\n### Input:\n{input}\n\n### Response:"
        ),
        "prompt_no_input": (
            "Below is an instruction that describes a task. "
            "Write a response that appropriately completes the request.\n\n"
            "### Instruction:\n{instruction}\n\n### Response:"
        ),
    }
    原型是这样的，所以在处理为qa格式的时候，human_name="Instruction"  bot_name="Response", background的值为input的值。

    这里需要特殊处理
    1. background为空，也就是input==""时候
        qa数据集中的某个question的值应该连着input，比如："{instruction} ### Input: {input}" 这样才对。
    2. background不为空，也就是没有inpput=="~"时候
        qa数据集中的某个question的值应该为Instruction的值，比如："{instruction}" 这样才对。
    """

    if background == "":
        return "Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.\n\n"
    else:
        return "Below is an instruction that describes a task. Write a response that appropriately completes the request.\n\n"


def get_dataset_prompt(dataset_name, human_name, bot_name, background):
    if dataset_name == "sota":
        return sota_prompt(human_name, bot_name, background)

    elif dataset_name == "sharegpt":
        return sharegpt_prompt(human_name, bot_name, background)

    elif dataset_name == "persona_chat":
        return persona_chat_prompt(human_name, bot_name, background)

    elif dataset_name == "empathetic_dialogues":
        return empathetic_dialogues_prompt(human_name, bot_name, background)

    elif dataset_name == "stanford_52k":
        return stanford_52k_prompt(human_name, bot_name, background)
    else:
        raise Exception(f"Error dataset name:{dataset_name}")
