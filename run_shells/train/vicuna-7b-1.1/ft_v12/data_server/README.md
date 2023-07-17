# 数据说明

采用的数据是以下链接汇总的：

https://huggingface.co/datasets/QingyiSi/Alpaca-CoT

# 部署

1.安装supervisor

    apt-get install supervisor

2.安装gunicorn

    apt-get install gunicorn

3.启动

    supervisord -c /etc/supervisor/supervisord.conf

4.配置

    cp qas.conf /etc/supervisor/conf.d

5.更新

    supervisorctl update