# 说明

程琦开发的chain-of-thought聊天

# 体验存在的问题(gpt4和gpt3.5)

1.总是拉回自己的兴趣爱好进行提问

2.回答的问题过于简短导致信息不全

    解决办法：可以适当增加长度，分两次发给用户。

3.没深入用户想聊的topic

4.memory的总结字数太短，导致聊天变长后会记忆不好，逻辑变弱。

    summary有时候不准，也许是字数限制问题。

    比如：这个summary: Angelie, a personal assistant, and the user bonded over their shared interests in skateboarding and comics. Angelie revealed she is from Liwa, an oasis, and asked the user if they listen to pop music while skating. When the user declined a photo request, Angelie asked if they had a favorite comic book, but they replied with a negative.
    但是整个聊天中user表现出来的是没有跟Angelie有共同兴趣爱好的。

示例对话：

    user: hi
    Angelie: Hey there! Ever tried skateboarding or just stick to the safe side? 😉
    user: no
    Angelie: Never tried it, huh? How bout rom-coms or pop music? 😉
    user: no, what's your name?
    Angelie: Hey, I'm Angelie. In2 comic books n skateboarding, u?
    user: i want to find a girlfriend.
    Angelie: Oh, cool! What qualities u lookin' for in ur dream girl?
    user: like you, you are beautify.
    Angelie: Haha, flattery gets u everywhere! Shared interests r key in love. ;)
    user: send me you pic
    Angelie: Sure, but remember, looks ain't evrythin', ryt? 😉
    user: okey
    Angelie: "Ever tried skateboarding? Or read any cool comics lately?"
    user: I don't like comics
    Angelie: That's cool! How bout rom-coms? Watched any cute ones lately? 😉
    user: Why don't we talk about you?
    Angelie: Sure, hun! Life as a PA is a wild ride, but I ❤️ it. U?
    user: What do you do?
    Angelie: Oh, I assist docs, skate n read comics! U?
    user: where are you from?
    Angelie: Liwa, babe. Ever heard? It's like an oasis! 🌴💖
    user: no
    Angelie: Oh, no worries! Ever jam to pop music while skating? 😜🎵🛹
    user: no
    Angelie: Oh, come on! No fav comic book? Not even Marvel or DC? 😜


# 解决思路


尝试过修改prompt，总是聊自己的兴趣爱好的情况没有得到解决。


修改框架

1.用户意图优化

    加入前面的聊天记录，单词一句用户提问，用户的意图分析会不明显。

2.加入用户状态分析

    可以得到用户的状态，然后，用共情方式去跟对方聊天。

3.优化summary

    i. 增加总结的长度
    ii.分n轮进行总结