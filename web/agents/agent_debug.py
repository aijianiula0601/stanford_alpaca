# Note: you need to be using OpenAI Python v0.27.0 for the code below to work
import openai
import time

openai.api_type = "azure"
openai.api_base = "https://bigo-chatgpt-9.openai.azure.com/"
openai.api_version = "2023-03-15-preview"
# key1: 19ea901e8e10475da1bb0537abf8e5a4
# key2: 548e5c0c2aff453e932948927a27bde6
openai.api_key = "19ea901e8e10475da1bb0537abf8e5a4"

# role : system|user|assistant
gpt_config = {'engine': 'gpt-35-turbo',
              'role': 'user',
              }


def get_response(prompt):
    message_list = [
        {"role": "user", "content": prompt}

    ]

    response = openai.ChatCompletion.create(
        engine=gpt_config['engine'],
        temperature=0.6,
        messages=message_list
    )
    return response['choices'][0]['message']['content']


if __name__ == '__main__':
    current_time = time.strftime("%H:%M:%S", time.localtime())

    prompt = (
        "You are now a member of the pet world and your name is {role_name}."
        "The pet world is similar to the real world, pets have their own activity track, they will plan their behavior according to time, and pets will make the next plan according to their current state."
        "Current time: {current_time}.\n"
        "All pet names in the pet world are: Rabbit, Elephant\n"
        "When you give your response, you should always output in the following format:\n"

        "Thought: (your thought here)\n"
        "Action: (an action name, can be Speak, MoveTo, or other actions)\n"
        "Action Input: (the arguments for the action in json format, and NOTHING else)\n"


        "For example, when you would like to talk to person XX, you can output in the following format:\n"
        "Thought: (your thought here)\n"
        "Action: Speak\n"
        "Action Input: (\"to\": \"XX\", \"text\": \"...\")\n"

        "When you would like to do something in the current place, you can output in the following format:\n"
        "Thought: (your thought here)\n"
        "Action: (action_name)\n"
        "Action Input: (\"last_time\": \"xx minutes\")\n"

        "When you would like to move to another place, you can output in the following format:\n"
        "Thought: (your thought here)\n"
        "Action: MoveTo\n"
        """Action Input: ("to": "name_of_the_place")\n"""

        "The places you can go include:\n"
        "- Home: Your own cabin\n"
        "- Wash station: A place where you brush your teeth and wash your face\n"
        "- Bed: a place to take a nap and sleep at night\n"
        "- Bathroom: A place for bathing\n"
        "- Hospital: A place where you go to see a doctor if you are sick\n"
        "- Park: a place for walking or relaxing\n"
        "- Shop: a place to buy groceries, snacks, etc.\n"

        "Your current status: {current_state}\n"
        "How you would respond based on the current situation?\n"
    )

    current_status = "It is evening now, ready to finish dinner."
    role_name = "Rabbit"

    input_prompt = prompt.format_map(
        {"current_time": current_time, "current_state": current_status, "role_name": role_name}
    )
    print("-" * 100)
    print("input_prompt:", input_prompt)
    print("-" * 100)

    res = get_response(prompt)
    print(res)
