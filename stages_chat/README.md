# 说明

采用分阶段的方式来做

# 聊天prompt说明

- i<=5：stage1_greeting.md

  这个阶段是打招呼阶段

- 5<i<=10: stage2_know_each_other.md

  这个阶段是互相了解阶段，问对方来自哪里、名字等

    - prompt内部会做whatsapp/picture判断
    - 为防止gpt3.5判断有误，根据内部分析结果，如果为true，将采用gpt4二次分析

- 10<i<=20: stage3_familiar.md

  这个阶段，互相了解得差不多了，聊得内容更多，比如各自的童年经历等

    - prompt内部会做whatsapp/picture判断
    - 为防止gpt3.5判断有误，根据内部分析结果，如果为true，将采用gpt4二次分析

- i>20: stage4_hot.md

  这个阶段，大家比较熟悉了，进入互相吸引阶段，可以聊对方的恋爱经历等

# 补充

识别用户状态，如果用户当前说自己很烦，或者