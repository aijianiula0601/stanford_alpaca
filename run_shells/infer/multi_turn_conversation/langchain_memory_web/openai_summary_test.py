# Note: you need to be using OpenAI Python v0.27.0 for the code below to work
import openai

# export OPENAI_API_KEY='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'

from langchain.llms import OpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory, CombinedMemory, ConversationSummaryMemory, \
    ConversationSummaryBufferMemory


llm = OpenAI(temperature=0)
conversation_with_summary = ConversationChain(
    llm=llm,
    memory=ConversationSummaryMemory(llm=OpenAI()),
    verbose=True
)
print(conversation_with_summary.predict(input="Hi, what's up?"))

print(conversation_with_summary.predict(input="Tell me more about it!"))