# 数据说明

采用的数据是以下链接汇总的：

https://huggingface.co/datasets/QingyiSi/Alpaca-CoT

# 部署

在202.168.97.165服务器部署es，把数据插入到es中

# es安装教程


-   安装cosign

    参考：https://edu.chainguard.dev/open-source/sigstore/cosign/how-to-install-cosign/

    采用源码安装方式：

    位于页面的: Installing Cosign with the Cosign Binary 


-   es安装

    增大系统内存：sudo sysctl -w vm.max_map_count=262144

    参考：https://www.elastic.co/guide/en/kibana/current/docker.html#run-kibana-on-docker-for-dev



-   里面的docker安装改为 
    

    不要安装官网的采用docker network create elastic的新建网络方式，不然另外节点无法加入

    //elasticsearch

    docker run --privileged=true --gpus all --name es-node01  --net host -p 9200:9200 -p 9300:9300 -it \
    -v /etc/localtime:/etc/localtime \
    -w /workspace \
    -v /home/huangjiahong.dracu/hjh:/workspace/hjh \
    -v /mnt/cephfs:/mnt/cephfs \
    --shm-size=1024m \
    docker.elastic.co/elasticsearch/elasticsearch:8.8.2 \
    /bin/bash

    //kibana
    docker run --privileged=true --gpus all --name kib-01  --net elastic -p 5601:5601 -it \
    -v /etc/localtime:/etc/localtime \
    -w /workspace \
    -v /home/huangjiahong.dracu/hjh:/workspace/hjh \
    -v /mnt/cephfs:/mnt/cephfs \
    --shm-size=1024m \
    docker.elastic.co/kibana/kibana:8.8.2 \
    /bin/bash
    



-   在165上的安装信息

    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    ✅ Elasticsearch security features have been automatically configured!
    ✅ Authentication is enabled and cluster connections are encrypted.
    
    ℹ️  Password for the elastic user (reset with `bin/elasticsearch-reset-password -u elastic`):
      s6JnANyNuXa5PCjjU0dB
    
    ℹ️  HTTP CA certificate SHA-256 fingerprint:
      a080023cc6fcee215cc9c31534a4ee2036c94ca938fb1d5e6281db8742e6879d
    
    ℹ️  Configure Kibana to use this cluster:
    • Run Kibana and click the configuration link in the terminal when Kibana starts.
    • Copy the following enrollment token and paste it into Kibana in your browser (valid for the next 30 minutes):
      eyJ2ZXIiOiI4LjguMiIsImFkciI6WyIyMDIuMTY4Ljk3LjE2NTo5MjAwIl0sImZnciI6IjZmYzcwZTI3NzFjYjM3NjA3YjFkYTEyOGU0YjZiMjg0YzNkZDBiZGE2ODNkNjJkMmQxZjNjYjNmODVhY2Y3N2YiLCJrZXkiOiJhT05EY1lrQmZubWN3aFdaRU9TXzpCOEE0MDBGc1F1R0NrZTdmckEyZUpBIn0=
    
    ℹ️ Configure other nodes to join this cluster:
    • Copy the following enrollment token and start new Elasticsearch nodes with `bin/elasticsearch --enrollment-token <token>` (valid for the next 30 minutes):
      eyJ2ZXIiOiI4LjguMiIsImFkciI6WyIyMDIuMTY4Ljk3LjE2NTo5MjAwIl0sImZnciI6IjZmYzcwZTI3NzFjYjM3NjA3YjFkYTEyOGU0YjZiMjg0YzNkZDBiZGE2ODNkNjJkMmQxZjNjYjNmODVhY2Y3N2YiLCJrZXkiOiJadU5BY1lrQmZubWN3aFdab09RVzpWNHFQTi1wRFJzU2s3QVJwbUowajJRIn0=
    
      If you're running in Docker, copy the enrollment token and run:
      `docker run -e "ENROLLMENT_TOKEN=<token>" docker.elastic.co/elasticsearch/elasticsearch:8.8.2`
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


-  单节点启动es

    进入es的docker，然后 ./bin/elasticsearch

-  单节点启动kibana

    进入kibana，然后 ./bin/kibana

-  多加点启动

    参考上面的'在165上的安装信息'进行启动

-   打开kibana

    http://202.168.97.165:5601


-   操作

    在kibana的左边找到"Dev tools"工具，可以对数据进行操作 