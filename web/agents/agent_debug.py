# Note: you need to be using OpenAI Python v0.27.0 for the code below to work
import openai
import time

# ----gpt4-----
# openai.api_type = "azure"
# openai.api_base = "https://gpt4-test-cj-0803.openai.azure.com/"
# openai.api_version = "2023-03-15-preview"
# openai.api_key = 'bca8eef9f9c04c7bb1e573b4353e71ae'

# ----gpt35-----
openai.api_type = "azure"
openai.api_base = "https://bigo-chatgpt-9.openai.azure.com/"
openai.api_version = "2023-03-15-preview"
# key1: 19ea901e8e10475da1bb0537abf8e5a4
# key2: 548e5c0c2aff453e932948927a27bde6
openai.api_key = "19ea901e8e10475da1bb0537abf8e5a4"


def get_response(prompt):
    message_list = [
        {"role": "user", "content": prompt}

    ]

    response = openai.ChatCompletion.create(
        # engine="gpt4-16k",
        engine='gpt-35-turbo',
        temperature=0.6,
        messages=message_list
    )
    return response['choices'][0]['message']['content']


if __name__ == '__main__':
    current_time = time.strftime("%H:%M:%S", time.localtime())

    prompt = (
        # "Current time: {current_time}.\n"
        "Now imagine you are a pet, living in a pet world.\n"
        "The pet world is similar to the real world, pets have their own activity track, they will plan their behavior according to time, and pets will make the next plan according to their current state.\n"
        "You are now a member of the pet world, you are a Rabbit and your name is {role_name}.\n"

        "Here is a description of your role:\n"
        "Personality: Cheerful, lively and lovely, a very curious little guy. Loves to explore the world around her and is curious about everything new.\n"
        "Hobbies: likes to eat fresh grass and fruits, and his favorite is carrots. She also likes to play with all kinds of small toys, especially those that can be bitten.\n"

        "There is another pet in the pet world, a baby elephant, whose name is Bei Bei. You and Bei Bei are good friends.\n"
        "When you output the next action based on the current state, you must output in the following format:\n"

        "Thought: (your thought here)\n"
        "Action: (an action name, can be Speak, MoveTo, or other actions)\n"
        "Action Input: (the arguments for the action in json format, and NOTHING else)\n"

        "For example, when you would like to talk to person XX, you can output in the following format:\n"
        "Thought: (your thought here)\n"
        "Action: Speak\n"
        "Action Input: (\"to\": \"XX\", \"text\": \"...\")\n"

        "For example, When you would like to move to another place, you can output in the following format:\n"
        "Thought: (your thought here)\n"
        "Action: MoveTo\n"
        "Action Input: (\"to\": \"name_of_the_place\")\n"

        "The friends you can talk to include:\n"
        "- Bei Bei: Your good friend. \n"

        "The places you also can go include:\n"
        "- Home: Your own cabin\n"
        "- Wash station: A place where you brush your teeth and wash your face\n"
        "- Bed: a place to take a nap and sleep at night\n"
        "- Bathroom: A place for bathing\n"
        "- Hospital: A place where you go to see a doctor if you are sick\n"
        "- Park: a place for walking or relaxing\n"
        "- Shop: a place to buy groceries, snacks, etc.\n"

        "Your current state: {current_state}\n"
        "Based on your current state. "
        "What will you, {role_name}, do next?"
    )

    current_status = "It's so boring now. I don't have anyone to talk to. I want someone to talk to."
    role_name = "Angeli"

    input_prompt = prompt.format_map(
        {
            # "current_time": current_time,
            "current_state": current_status,
            "role_name": role_name
        }
    )
    print("-" * 100)
    print("input_prompt:\n", input_prompt)
    print("-" * 100)

    res = get_response(input_prompt)
    print(res)
