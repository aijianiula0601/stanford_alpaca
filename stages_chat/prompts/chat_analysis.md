## Chat history:

{latest_history}

## User's current response:

{current_user_response}

## Goals:

Output a json object that contains the following keys:

- user_intention
- if_ask_social_software_account
- if_ask_personal_picture
- if_talk_about_sex
- if_not_interested_in_chatting
- question

### Explanation:

- user_intention

  Analyze the inner intention of the user's current response.

- if_ask_social_software_account:

  If user's current response is asking for whatsapp, instagram, Facebook or Twitter accounts; otherwise, the output is false

- if_ask_personal_picture

  If user's current response is asking for private photos, output true; otherwise, the output is false

- if_talk_about_sex

  If the user's current response is talking about sex, output true, otherwise output false.

- if_not_interested_in_chatting

  Analysis the user's current response and user_intention, if the user's current response does not have much information, just such as "ok" or "good", output false otherwise.

- question

  If the user's current response is asking a question, output true, otherwise output false.

## Constrains:

- The output must be a json object.
