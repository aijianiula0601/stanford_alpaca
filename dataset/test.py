import re

cleaned_line = """Human: What are our closest genetic relatives in the animal kingdom?
Assistant: Chimpanzees
Human: I've also heard the bonobo. What do you know about bonobo?
Assistant: Oh, the bonobo! That's a great suggestion. Bonobos have many similarities to humans. They have a lot of sex, and they have sex for fun. And also, they are very sweet and sweet is a nice characteristic, right?
Human: Yes, I herd they are more peaceful than chimpanzees and have sex for social reasons, not just procreation, which is very similar to humans.
Assistant:  Bonobos are also very smart, and they use tools.  Some of their social skills are very similar to human skills, too. They make fire."""

a = re.split('(Human:|Assistant:)', cleaned_line)

print(a)