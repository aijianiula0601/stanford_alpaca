# 说明

收chain_of_thought的影响，做设计。


# 步骤


1.对用户问题进行意图分析，获取topic


    根据前后一定轮次，而不是当前轮而已。


    Based on the chat between the user and role, analyze the intention of the user's current question using a rigorous logic, and give the topic of the user's question in at most two words. 
    

    Think about it this way:
    step1: Output the user question intent
    step2: Output the topic of the user's question, the topic is maximum two words, according to the user's question and chat history, accurately analyze the topic of the user's current question, and the topic should fit the user's intention of the question.
    step3: Output the user's intent and topic in json mode. The key in json is user_intent and topic

2.对用户历史进行总结

    不要用纯文本进行总结，而是以

    user's actor:
    role's reactivity：

3.设计聊天prompt输出答案

    

