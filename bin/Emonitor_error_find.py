from re import findall, finditer
from time import strftime, strptime, localtime
from bin.Emonitor_log import Logger

"""

    用于将获得的文本过滤，过滤出参数`LINK_DETECT_ERROR`中的文本
    :param text: 从Emonitor_connect中获得的文本
    :return: 返回一个列表，列表汇总包含着找到的文本
"""


def Emonitor_error_find(output_dict, loop_text, log, sql_res):
    """
    用于找出环路设备并将其作为一个字典输出，没找出则放回一个0作为关键字跳转到下一个设备
    :param output_dict:包含数据的字典，{log_ip, sw_name, log_text, last_run_time}
    :param loop_text:找环路的关键字
    :param log:日志核心部件
    :param sql_res:从数据库内拿到的日志
    :return: 数据的字典｛loop_text, loop_time, loop_port｝
    """
    global rfind_time
    log.logger.debug('正在分析日志')
    text = output_dict['log_text']
    error_port_list = []
    find_error_box = []
    loop_dict = {}
    # find out the 'LINK_DETECT_ERROR' position
    find_error_index = finditer(r'%s' % loop_text, text)
    # save the position
    for i in find_error_index:
        find_error_box.append(i.span())
    # start position -30 | end position +100
    for i in find_error_box:
        error_start_position = int(i[0]) - 30
        error_end_position = int(i[1]) + 100
        error_port = text[error_start_position:error_end_position]
        file_re = findall(r'(\*.*?%s.*?)\n' % loop_text, error_port)
        error_port_list += file_re
    # find last run time (inside the switch)
    cisco_rfind = text.rfind('*')
    if cisco_rfind != -1:
        cisco_rfind_text = findall('\*(.*?):.\%', text[cisco_rfind:])
        cisco_rfind_time = strptime(cisco_rfind_text[0], "%b %d %H:%M:%S")
        rfind_time = strftime('%Y', localtime()) + strftime("-%m-%d %H:%M:%S", cisco_rfind_time)
    else:
        # if not cisco or huawei, then last_inside_time is all 0
        output_dict['last_inside_time'] = '00000000000000'
    output_dict['last_inside_time'] = rfind_time
    for i in error_port_list:
        loop_port = findall('0/(\d.*)\.', i)[0]
        # find out the loop time
        loop_time_text_find = findall('\*(.*?):.\%', i)
        loop_time_text = strptime(loop_time_text_find[0], "%b %d %H:%M:%S")
        loop_time_sql = strftime('%Y', localtime()) + strftime("-%m-%d %H:%M:%S", loop_time_text)
        loop_dict[loop_port] = loop_time_sql
        output_dict['loop_time'] = list(loop_dict.keys())
        output_dict['loop_port'] = list(loop_dict.values())
        if sql_res:
            loop_time_sql_inside = strftime('%Y', localtime()) + strftime("%m%d%H%M%S", loop_time_text)
            sql_inside_time_text = strptime(str(sql_res[0]['last_inside_time']), "%Y-%m-%d %H:%M:%S")
            sql_inside_time = strftime("%Y%m%d%H%M%S", sql_inside_time_text)
            # if sql time > switch loop time, return 0 to continue
            if sql_inside_time > loop_time_sql_inside:
                return 0
            else:
                output_dict['loop_text'] = error_port_list
                return output_dict
        # if not have log in sql, return the dict
        output_dict['loop_text'] = error_port_list
        return output_dict
