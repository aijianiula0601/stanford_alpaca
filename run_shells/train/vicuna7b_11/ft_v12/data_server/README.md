# 数据说明

采用的数据是以下链接汇总的：

https://huggingface.co/datasets/QingyiSi/Alpaca-CoT

# 部署

在202.168.97.165服务器部署es，把数据插入到es中

# es安装教程

https://www.elastic.co/guide/en/kibana/current/docker.html


-   es安装

    ```docker run --name es-node01 --net elastic -p 9200:9200 -p 9300:9300 -t docker.elastic.co/elasticsearch/elasticsearch:
    8.8.2
    
    docker run --name kib-01 --net elastic -p 5601:5601 docker.elastic.co/kibana/kibana:8.8.2```


-   es的supervisor账号密码：

    账号：elastic 
    
    密码：ef_lN4y0B0-3joUJiyeX
    

-   创建账号给kibana

    ```bin/elasticsearch-users useradd kibana_es 
    
    bin/elasticsearch-users roles -a superuser kibana_es bin/elasticsearch-users
    
    roles -a kibana_system kibana_es```
    
    密码：123321jia