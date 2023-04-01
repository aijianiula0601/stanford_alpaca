# 说明



采用docker环境运行，docker镜像路径：/mnt/cephfs/hjh/tmp/docker/sda.tar



## 部署环境

步骤：

1.导入镜像

 sudo nvidia-docker import sda.tar sda


2.创建容器


```angular2html
sudo nvidia-docker run --privileged=true --gpus all --name sda  --network host -it \
-v /etc/localtime:/etc/localtime \
-w /workspace \
-v /data1/hjh:/workspace/hjh \
-v /home/huangjiahong.dracu:/home/huangjiahong.dracu \
-v /mnt/cephfs:/mnt/cephfs \
--shm-size=1024m \
sda:latest  \
/bin/bash
```


3.进入容器

    使用环境sda: conda activate sda 




## 训练


    sh ft_llama7B_52k.sh