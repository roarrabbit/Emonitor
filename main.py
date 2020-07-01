from sys import exit, stdout
from os.path import exists
from os import system, popen, makedirs
from csv import reader
from time import time, ctime, sleep
import router
from configparser import ConfigParser

"""
时间：Wed Jul 1 17:52:21 2020
功能：记录日志并正则出环路日志，出现则写入数据库并通过邮箱通知
目的：
  1. 找出环路情况并通知指定人员减少问题出现的工作量
"""
print('by MLLR')


# ---------BEFORE CONFIG---------------
config = ConfigParser()
# root local file `Emonitor_config.ini`
config.read('Emonitor_config.ini', encoding='utf-8')
# 环路关键字
loop_keys = config['CONFIG']['loop_keys']
# 日志记录等级
log_level = config['CONFIG']['log_level']
# 数据库的IP地址
sql_ip = config['CONFIG']['sql_ip']
# 数据库名称
sql_user = config['CONFIG']['sql_user']
# 数据库密码
sql_pwd = config['CONFIG']['sql_pwd']
# 数据库名称
sql_db = config['CONFIG']['sql_db']
# 阻塞时间（秒） 理想状态下是每小时执行一次，建议使用能被10整除的数字
sleep_time = int(config['CONFIG']['sleep_time'])
log = router.Logger('Econnect_box\\0 log\\Emonitor.log',
                    level=log_level)
# 如果找到环路则再屏幕显示的信息
error_print_text = '''
------------------------------------
|  There have `LINK_DETECT_ERROR`  |
------------------------------------
'''
# write start time to log
log.logger.info('程序执行于：%s' % ctime())
# judgment file exists
if not exists('Econnect_box'):
    print('Econnect_box文件夹创建中...')
    makedirs('Econnect_box')
try:
    with open('Econnect_box\\switch_info.csv') as f:
        reader_csv = reader(f)
        switch_list = list(reader_csv)
except FileNotFoundError:
    print('switch_info.csv文件缺失，正在创建.....', end='')
    sleep(0.5)
    with open('Econnect_box\\switch_info.csv', 'w') as f:
        f.writelines('IP地址,用户名,密码,第一行请勿更改！')
    print('创建成功！请添加完信息后重新打开\n')
    # 打开文件
    print('正在尝试打开')
    popen('cd Econnect_box && start switch_info.csv')
    system('pause')
    exit(1)
# real sleep time
real_sleep_time = sleep_time * 60
# ---------BEFORE CONFIG---------------



def run():
    """
    主程序
    :return:None
    """
    # total use time
    start_time = time()
    run_times = 0
    # switch_list[1] is title
    run_list = switch_list[1:]
    total_run_times = len(run_list)
    try:
        for i in run_list:
            run_times += 1
            run_times_show = f'[{run_times}|{total_run_times}] '
            print('\b' * (len(run_times_show)), end='')
            stdout.flush()
            print(run_times_show, end='')
            stdout.flush()
            # execute the command
            output_dict = router.Emonitor_connect(i, loop_keys, log)
            if output_dict == 0:
                # if output_text is 0, it mean have some error, continue next one
                log.logger.warning(f'【warning】 {i[0]}')
                continue
            elif output_dict == 1:
                # 1. huawei mode, huawei don't support switch loop write in log
                # 2. loop_keys not in log
                continue
            sql_res = router.Emonitor_select_sql(i[0], user=sql_user, pwd=sql_pwd,db=sql_db, host=sql_ip)
            # try to find the error
            output_error_list = router.Emonitor_error_find(output_dict, loop_keys, log, sql_res)
            if output_error_list == 0:
                # 1. if not find loop in log, continue
                # 2. if sql time > switch loop time, continue
                continue
            else:
                print(error_print_text)
                log.logger.error(f'{output_error_list["log_ip"]}--{output_error_list["sw_name"]}')
                for i in output_error_list['loop_text']:
                    log.logger.error(i)
            save_dict[i[0]] = output_error_list
            # insert data to sql
            sql_res = router.Emonitor_insert_sql(save_dict[i[0]], user=sql_user, pwd=sql_pwd,db=sql_db, host=sql_ip, log=log)
            if sql_res:
                log.logger.warning(f'数据库执行返回：{sql_res}')
    except KeyboardInterrupt:
        log.logger.info('手动终止于：%s' % ctime())
    # total use time
    end_time = time()
    log.logger.info(f'total times:{end_time - start_time}')


if __name__ == '__main__':
    # main
    while True:
        try:
            # save error information by switch {{sw_ip_add}:{{sw_name:交换机主机名},{sw_ip:交换机IP地址},{发生的设备:环路信息}}}
            save_dict = {}
            log.logger.info(f'开始于{ctime()}')
            run()
            print(f'total find:{len(save_dict.keys())}')
            log.logger.info(f'结束于{ctime()}')
            # 睡眠机制，10分钟一次
            # Use a round cycle for long-running, block time is `sleep_time`
            log.logger.info(f'休眠中...{sleep_time}分钟后运行')
            # if it cannot be divided by 10 equals 0 then beautiful print
            if (sleep_time % 10) == 0:
                for i in range(0, real_sleep_time + 1, 60):
                    show_time = f'sleep time - {i // 60} | {sleep_time}'
                    print('\b' * (len(show_time)), end='')
                    stdout.flush()
                    print(show_time, end='')
                    stdout.flush()
                    sleep(60)
                print('\b' * (len(show_time)), end='')
                stdout.flush()
            # if it cannot be divided by 10 equals 0,then the blocking time
            else:
                sleep(real_sleep_time)
        except Exception as e:
            log.logger.error(e)
            input('enter to quit')
            continue