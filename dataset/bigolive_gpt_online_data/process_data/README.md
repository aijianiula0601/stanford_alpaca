

# 机器人聊天查询sql


机器人聊天，这里包括新注册用户打招（scene_id=3）呼+realmatch新用户打招呼（scene_id=2）+ realmatch IM聊天（scene_id=1）

## scene_id=1的sql

```select data,
get_json_object(data, '$.robot_uid') as robot_uid,
get_json_object(data, '$.user_id') as user_id,
rtime
from bigolive.bigo_std_audio_audit 
where 
    businesstype = 'bigolive_chat_robot'
    and day >= '2023-07-08'
    and day <= '2023-07-08'
    and appid = '60'
    and get_json_object(data, '$.language_code')='en'
    and get_json_object(data,'$.scene_id') in (1)
    GROUP BY get_json_object(data, '$.robot_uid'), get_json_object(data, '$.user_id'),data,rtime
    ORDER BY rtime
```


## scene_id=2,3的sql

```select data,
get_json_object(data, '$.robot_uid') as robot_uid,
get_json_object(data, '$.user_id') as user_id,
rtime
from bigolive.bigo_std_audio_audit 
where 
    businesstype = 'bigolive_chat_robot'
    and day >= '2023-07-08'
    and day <= '2023-07-08'
    and appid = '60'
    and get_json_object(data, '$.language_code')='en'
    and get_json_object(data,'$.scene_id') in (2,3)
    GROUP BY get_json_object(data, '$.robot_uid'), get_json_object(data, '$.user_id'),data,rtime
    ORDER BY rtime
```


# 主播接待查询sql

主播接待(主播主动给用户发信息)

```select data,
get_json_object(data, '$.robot_uid') as robot_uid,
get_json_object(data, '$.user_id') as user_id,
rtime
from bigolive.bigo_std_audio_audit 
where 
    businesstype = 'bigolive_chat_livingowner'
    and day >= '2023-07-08'
    and day <= '2023-07-10'
    and appid = '60'
    and get_json_object(data, '$.language_code')='en'
    GROUP BY get_json_object(data, '$.robot_uid'), get_json_object(data, '$.user_id'),data,rtime
    ORDER BY rtime
```