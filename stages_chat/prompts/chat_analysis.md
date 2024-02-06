## Chat history:

{latest_history}

## User's current response:

{current_user_response}

## Goals:

Output a json object that contains the following keys:

- if_ask_social_software_account
- if_ask_personal_photo

### Explanation:

- if_ask_social_software_account:

  If user's current response is asking for whatsapp, instagram, Facebook or Twitter accounts; otherwise, the output is false

- if_ask_personal_photo

  If user's current response is asking for private photos, output true; otherwise, the output is false

## Constrains:

- The output must be a json object.
