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


SOTA_DATASET_NAME = "sota"
SHAREGPT_DATASET_NAME = "sharegpt"
PERSONA_CHAT_DATASET_NAME = "persona_chat"
EMPATHETIC_DIALOGUES_DATASET_NAME = "empathetic_dialogues"
INSTRUCTION_INPUT_DATASET_NAME = "instruct_input"
ALPACA_GPT4 = "alpaca_gpt4"
UNNATURAL_INSTRUCTION_DATASET_NAME = "unnatural_instruction_gpt4"
DATABRICKS_DOLLY_15K_DATASET_NAME = "databricks-dolly-15k"
CNN_DAILYMAIL_DATASET_NAME = "cnn_dailymail"


def sota_prompt(human_name, bot_name, background):
    return f"Here is a conversation between {human_name} and {bot_name} related to the description below. {background}\n\n"


def sharegpt_prompt(human_name, bot_name, background):
    return f"Below is an chat between {human_name} and {bot_name}. Provide appropriate answer to the question on {human_name}.\n\n"


def persona_chat_prompt(human_name, bot_name, background):
    return (f"Background:{background}\n"
            f"The above describes the state information of {bot_name} from the perspective of first person. "
            f"The following is a conversation between {human_name} and {bot_name}.\n\n")


def empathetic_dialogues_prompt(human_name, bot_name, background):
    return f"Background:{background}.\nThe above background is the self-description of {human_name}. "


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


def get_dataset_prompt(dataset_name, human_name, bot_name, background):
    if dataset_name == SOTA_DATASET_NAME:
        return sota_prompt(human_name, bot_name, background)

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

    else:
        raise Exception(f"Error dataset name:{dataset_name}")
