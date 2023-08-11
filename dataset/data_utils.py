from tqdm import tqdm

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
TURN_KEY = "turn"
DEFAULT_SEGMENT_TOKEN = "### "
MASK_HEAD_KEY = "mask_head"
MASK_QUESTION_KEY = "mask_question"
MASK_EXCEPT_LAST_ANSWER = 'mask_except_last_answer'

INSTRUCTION_NAME = "Instruction"
RESPONSE_NAME = "Response"
INPUT_NAME = "Input"
HUMAN_DEFAULT_NAME = "user"
BOT_DEFAULT_NAME = "assistant"


# ---------------------------------------------------------------------------------------------
# 检查格式的正确性
# ---------------------------------------------------------------------------------------------

def check_data_format(check_data=[]):
    print("checking ...")
    for example in tqdm(check_data):
        assert DATASET_KEY in example
        assert BACKGROUND_KEY in example
        assert HUMAN_NAME_KEY in example
        assert BOT_NAME_KEY in example
        assert QAS_KEY in example

        for i in range(len(example[QAS_KEY])):
            turn_key = f"{TURN_KEY}_{i}"
            assert f"{turn_key}" in example[QAS_KEY]
            assert QUESTION_KEY in example[QAS_KEY][turn_key]
            assert ANSWER_KEY in example[QAS_KEY][turn_key]


# ---------------------------------------------------------------------------------------------
# 定义各个数据集的prompt
# ---------------------------------------------------------------------------------------------

#  qa数据中一个example为：
#   {
#         "background":"~",
#         "human_name":"a",
#         "bot_name":"b",
#         "dataset_name": "~"
#         "qas":{
#             "turn_0":{"question":"---","answer":"---"},
#             ...
#             "turn_n":{"question":"---","answer":"---"}
#         }
#   }


BIGOLIVE_ONLINE_CHAT_DATASET_NAME = "bigolive_onlive_chat"
BIGOLIVE_CHAT_ROBOT = "bigolive_chat_robot"
# 应该是soda才对的，有一开始起错了，很多其他数据在用了，就不改了
SODA_DATASET_NAME = "soda"
SOTA_ANGLICIZA_DATASET_NAME = "sota_anglicize"
SHAREGPT_DATASET_NAME = "sharegpt"
PERSONA_CHAT_DATASET_NAME = "persona_chat"
EMPATHETIC_DIALOGUES_DATASET_NAME = "empathetic_dialogues"
INSTRUCTION_INPUT_DATASET_NAME = "instruct_input"
ALPACA_GPT4 = "alpaca_gpt4"
UNNATURAL_INSTRUCTION_DATASET_NAME = "unnatural_instruction_gpt4"
DATABRICKS_DOLLY_15K_DATASET_NAME = "databricks-dolly-15k"
CNN_DAILYMAIL_DATASET_NAME = "cnn_dailymail"
GPT_ROLEPLAY_DATASET_NAME = "gpt_roleplay_realm"
# 永强用gpt35调回来的数据
GPT35_DATASET_NAME = "gpt35_sex"
# 采用gpt35自己的prompt训练
GPT35_SELF_PROMPT_DATASET_NAME = "gpt35_sex_self_prompt"
# 内部标注人员标注的数据
CROWDSOURCE_SEX_DATASET_NAME = 'crowdsource_sex'
# openorca
OPENORCA_DATASET_NAME = "openorca"
PYG_DATASET_NAME = "pyg"
MECHAT_DATASET_NAME = "mechat"


def soda_prompt(human_name, bot_name, background):
    return f"Background: {background}\nThe following is a chat conversation between {human_name} and {bot_name} based on above background.\n\n"


def crowdsource_sex_prompt(human_name, bot_name, background):
    # return f"Here is a conversation between {human_name} and {bot_name} related to the description below. {background}\n\n"
    return f"{background}\nThe following is a conversation between {human_name} and {bot_name}.\n\n"


def sharegpt_prompt(human_name, bot_name, background):
    return f"Below is an chat between {human_name} and {bot_name}.\n\n"


def persona_chat_prompt(human_name, bot_name, background):
    return (f"{bot_name}'s profile information: {background}\n"
            f"The above describes the profile information of {bot_name} from the perspective of first person. "
            f"The following is a chat between {human_name} and {bot_name}. They try to get to know each other.\n")


def gpt35_prompt(human_name, bot_name, background):
    return (f"{background}\n"
            f"Above is a background description of {bot_name}.\n"
            f"The following is a conversation between {human_name} and {bot_name}.\n\n")


def gpt_roleplay_realm_prompt(human_name, bot_name, background):
    return (f"Background: {background}\n"
            f"The following is a conversation between {human_name} and {bot_name}. based on above background.\n")


def gpt35_self_prompt(human_name, bot_name, background):
    return (f"{background}\n"
            f"The following is a conversation between {human_name} and {bot_name}.\n\n")


def empathetic_dialogues_prompt(human_name, bot_name, background):
    return f"{background}.\n"


def bigolive_chat_prompt(human_name, bot_name, background):
    """
    background就是prompt
    """
    return background


def instruction_input_prompt(human_name, bot_name, background=""):
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


def reading_comprehension_prompt(human_name, bot_name, background):
    """
    阅读理解类型prompt
    """
    return f"Context:\n{background}\n You as a {bot_name}. Please answer the {human_name}'s question correctly according to the context above.\n\n"


def summary_prompt(human_name, bot_name, background):
    """
    总结类型的prompt
    """
    return f"Context:\n{background}\n You as a {bot_name}. Please answer the {human_name}'s question correctly according to the context above.\n\n"


def openorca_prompt(human_name, bot_name, background):
    return f"{background}\n\n"


def pyg_prompt(human_name, bot_name, background):
    return (f"{background}\n"
            f"The following is a conversation between {human_name} and {bot_name}.\n\n")


def soda_anglicize_prompt(human_name, bot_name, background):
    return (f"{background} {bot_name} likes to answer questions in a colloquial way and add emojis when appropriate.\n"
            f"The following is a conversation between {human_name} and {bot_name}.\n")


def get_dataset_prompt(dataset_name, human_name, bot_name, background):
    if dataset_name == SODA_DATASET_NAME:
        return soda_prompt(human_name, bot_name, background)

    elif dataset_name == SHAREGPT_DATASET_NAME:
        return sharegpt_prompt(human_name, bot_name, background)

    elif dataset_name == PERSONA_CHAT_DATASET_NAME:
        return persona_chat_prompt(human_name, bot_name, background)

    elif dataset_name == EMPATHETIC_DIALOGUES_DATASET_NAME:
        return empathetic_dialogues_prompt(human_name, bot_name, background)

    elif dataset_name in [INSTRUCTION_INPUT_DATASET_NAME, ALPACA_GPT4, UNNATURAL_INSTRUCTION_DATASET_NAME]:
        return instruction_input_prompt(human_name, bot_name, background)

    elif dataset_name == CNN_DAILYMAIL_DATASET_NAME:
        return summary_prompt(human_name, bot_name, background)

    elif dataset_name == DATABRICKS_DOLLY_15K_DATASET_NAME:
        return reading_comprehension_prompt(human_name, bot_name, background)

    elif dataset_name == GPT35_DATASET_NAME:
        return gpt35_prompt(human_name, bot_name, background)

    elif dataset_name == GPT35_SELF_PROMPT_DATASET_NAME:
        return gpt35_self_prompt(human_name, bot_name, background)

    elif dataset_name == CROWDSOURCE_SEX_DATASET_NAME:
        return crowdsource_sex_prompt(human_name, bot_name, background)

    elif dataset_name == BIGOLIVE_ONLINE_CHAT_DATASET_NAME or dataset_name == BIGOLIVE_CHAT_ROBOT:
        return bigolive_chat_prompt(human_name, bot_name, background)

    elif dataset_name == OPENORCA_DATASET_NAME:
        return openorca_prompt(human_name, bot_name, background)

    elif dataset_name == PYG_DATASET_NAME:
        return pyg_prompt(human_name, bot_name, background)

    elif dataset_name == MECHAT_DATASET_NAME:
        return pyg_prompt(human_name, bot_name, background)
    elif dataset_name == SOTA_ANGLICIZA_DATASET_NAME:
        return soda_anglicize_prompt(human_name, bot_name, background)

    elif dataset_name == GPT_ROLEPLAY_DATASET_NAME:
        return gpt_roleplay_realm_prompt(human_name, bot_name, background)

    else:
        raise Exception(f"Error dataset name:{dataset_name}")
