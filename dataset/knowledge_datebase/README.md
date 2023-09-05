# 说明


目的：建立知识库


# 架构


知识库流程图

![img.png](img.png)


# 步骤


1.给单轮对话打标签

2.筛选话题对于的轮qa

3.人工筛选qa和修改answer

    入口代码：dataset/knowledge_datebase/gradio_vote_result_analysis.py

4.筛选好的qa做embedding提取，入库