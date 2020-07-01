from netmiko import ConnectHandler
from time import sleep, strftime, localtime
from sys import stdout
from re import search
from bin.Emonitor_log import Logger


def Emonitor_connect(sw_list,loop_keys, log):
    """
    执行日志命令并按照格式输出一个字典`save_dict_inside`
    :param sw_list: 一个列表，[IP, 用户名, 登陆密码]，从csv中获得
    :param log: 日志核心部件
    :return: save_dict_inside['sw_ip']
            save_dict_inside['sw_name']
            save_dict_inside['log_text']
    """
    # save output_text dict
    cisco_logging = 'show logging'
    save_dict_inside = {}
    now_time = strftime('%Y-%m-%d %H:%M:%S', localtime())
    device = {
        'device_type': 'cisco_ios',
        'ip': sw_list[0],
        'username': sw_list[1],
        'password': sw_list[2]
    }
    # if have error, do not exit to print info
    try:
        log.logger.debug(f'正在连接交换机：{sw_list[0]}')
        switch_connect = ConnectHandler(**device)
        log.logger.debug(f'{sw_list[0]}：登陆成功')
    except Exception as err_info:
        log.logger.warning(f'【{err_info}】cannot connect, please check the network config')
        log.logger.warning(f'连接交换机：{sw_list[0]}失败！')
        return 0
    # get switch name
    switch_name = switch_connect.find_prompt()[:-1]
    log.logger.debug(f'{switch_name}：正在查看日志')
    # default use cisco command
    log_command = cisco_logging
    # HUAWEI MODE
    if '<' in switch_name:
        return 1
    # CISCO MODE
    else:
        try:
            # send the command to see the log
            output_text_more = switch_connect.send_command(log_command, expect_string='', delay_factor=1.5)
        except Exception as e:
            log.logger.debug('不支持分屏输出，正在等待交换机将数据逐步传入，请耐心等待')
            output_text_more = switch_connect.send_command(log_command, expect_string='#', delay_factor=20)
        # output_text_more = switch_connect.send_command(log_command, expect_string=r'More', delay_factor=2)
    # separate out the `more`
    output_text = output_text_more[:output_text_more.rfind('--More--')]
    # output num
    output_watch = 0
    # while `More` in text then run
    while '--More--' in output_text_more:
        stdout.flush()
        if not output_watch:
            print('show more times:', end='')
            output_watch += 1
        else:
            print('\b' * len(str(output_watch)), end='')
            output_watch += 1
        print(output_watch, end='')
        stdout.flush()
        sleep(0.1)
        # send the ` `to see next page
        output_text_more = switch_connect.send_command_timing(' ', strip_prompt=False, strip_command=False,
                                                              normalize=False)
        # separate out the `more`
        output_text_more_del = output_text_more[:output_text_more.rfind('--More--') - 1]
        # output push more
        output_text += output_text_more_del
    print('\b' * (17 + len(str(output_watch))), end='')
    stdout.flush()
    output_text = output_text[:output_text.rfind('\n%s#' % switch_name)]
    log.logger.debug(f'{switch_name}：正在断开连接')
    # disconnect the connect
    switch_connect.disconnect()
    log.logger.debug(f'已断开连接-{switch_name}')
    # if has loop
    if search(loop_keys, output_text):
        # load data to dict
        save_dict_inside['log_ip'] = sw_list[0]
        save_dict_inside['sw_name'] = switch_name
        save_dict_inside['log_text'] = output_text
        save_dict_inside['last_run_time'] = now_time
        return save_dict_inside
    else:
        return 1
