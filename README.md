# 特色

Emonitor由python制作而成，初想是将其挂在服务器上，一直执行查找范围内的交换机日志

* 只适用于win
* 只适用于思科系，不支持华为系。目前只测试了锐捷的交换机
* 使用了配置文件进行核心配置（需要关闭再开启）
* 逻辑
  * 从用户模式中使用`show logging`命令，用一个循环打印出所有分屏信息
  * 正则出数据后找到环路日志并上传数据库
  * 找到环路现象后通过其他联动通知

## 数据库

数据库中只记录环路的设备与记录，正常的设备不记录，需要手动创建一个数据库`emonitor`然后在数据库里执行添加下面数据表即可
* 创建数据库
`CREATE DATEBASE emotion;`
* 创建数据表
``` sql
CREATE TABLE `eswitch_log` (
  `log_id` int(11) NOT NULL COMMENT '日志id，唯一的',
  `sw_name` varchar(25) NOT NULL DEFAULT '' COMMENT '交换机的主机名',
  `sw_ip` varchar(16) NOT NULL DEFAULT '' COMMENT '交换机的IP地址',
  `last_run_time` datetime DEFAULT NULL COMMENT '上一次执行的时间',
  `last_inside_time` datetime DEFAULT NULL COMMENT '交换机内日志的最新时间记录（使用日志最后一个时间记录）',
  `loop_time` text COMMENT '发生环路的时间',
  `loop_port` varchar(40) NOT NULL DEFAULT '0' COMMENT '环路的端口',
  `loop_text` longtext COMMENT '如果is_loop=1则此处有内容，is_loop=0则为空'
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
```

## 其他
### gitee
https://gitee.com/bittrabbit/Emonitor

### ini配置文件
mode ：配置模式，可重新载入此配置文件；执行模式，循环执行监察
loop_text ：环路的关键字，找到的日志根据这个关键字来查找
log_level ：记录日志的等级 [debug、info、warning、error]，默认为info
sleep_time ：执行一轮后的阻塞时间（分钟），默认为40分钟，请输入蠢数字
sql_ip ：数据库的ip地址
sql_user ：数据库的用户名
sql_pwd ：数据库的密码
sql_db ：连接的数据库名

### 华为

* 华为设备不能将环路情况写入日志，所以不支持华为设备
* 华为关闭分屏模式，执行一次命令能将所有内容放回，此分屏模式为一次性所用

``` python
# 关闭分屏模式
switch_connect.send_command('screen-length 0 temporary')
# 等待8s直到出现<
output_text_more = switch_connect.send_command('display logbuffer', expect_string='<', delay_factor=8)
```

