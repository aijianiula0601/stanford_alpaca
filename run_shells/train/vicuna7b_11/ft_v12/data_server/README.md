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

    参考：https://www.elastic.co/guide/en/kibana/current/docker.html#run-kibana-on-docker-for-dev



-   里面的docker安装改为 
    

    //elasticsearch

    docker run --privileged=true --gpus all --name es-node01  --net elastic -p 9200:9200 -p 9300:9300 -it \
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


    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    ✅ Elasticsearch security features have been automatically configured!
    ✅ Authentication is enabled and cluster connections are encrypted.
    
    ℹ️  Password for the elastic user (reset with `bin/elasticsearch-reset-password -u elastic`):
      2ut3w2mCU=v2athExEXc
    
    ℹ️  HTTP CA certificate SHA-256 fingerprint:
      3107fb8baa04840628e32f8d184ba1c1d2a902f65314172a9e30da856a2a7ec5
    
    ℹ️  Configure Kibana to use this cluster:
    • Run Kibana and click the configuration link in the terminal when Kibana starts.
    • Copy the following enrollment token and paste it into Kibana in your browser (valid for the next 30 minutes):
      eyJ2ZXIiOiI4LjguMiIsImFkciI6WyIxOTIuMTY4LjMyLjI6OTIwMCJdLCJmZ3IiOiIzMTA3ZmI4YmFhMDQ4NDA2MjhlMzJmOGQxODRiYTFjMWQyYTkwMmY2NTMxNDE3MmE5ZTMwZGE4NTZhMmE3ZWM1Iiwia2V5Ijoidm4zcWFJa0JReHVkMk5BZm1Kbko6U0lYbk1RbjdUOVNuMXhqWUxhVDkwUSJ9
    
    ℹ️ Configure other nodes to join this cluster:
    • Copy the following enrollment token and start new Elasticsearch nodes with `bin/elasticsearch --enrollment-token <token>` (valid for the next 30 minutes):
      eyJ2ZXIiOiI4LjguMiIsImFkciI6WyIxOTIuMTY4LjMyLjI6OTIwMCJdLCJmZ3IiOiIzMTA3ZmI4YmFhMDQ4NDA2MjhlMzJmOGQxODRiYTFjMWQyYTkwMmY2NTMxNDE3MmE5ZTMwZGE4NTZhMmE3ZWM1Iiwia2V5IjoidjMzcWFJa0JReHVkMk5BZm1Kbko6WExybEhHdmNSOEtfdWh2djg4b21OdyJ9
    
      If you're running in Docker, copy the enrollment token and run:
      `docker run -e "ENROLLMENT_TOKEN=<token>" docker.elastic.co/elasticsearch/elasticsearch:8.8.2`
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


-   打开kibana

    http://202.168.97.165:5601