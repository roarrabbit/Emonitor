import pymysql
from pymysql.cursors import DictCursor
from bin.Emonitor_log import Logger


def Emonitor_insert_sql(save_dict, host="127.0.0.1", port=3306, user='root',
                       pwd='root', db='emonitor', charset='utf8',log=''):
    """

    :param save_dict: 包含数据的字典
    :param host: 数据库的IP地址
    :param port: 数据库的端口
    :param user: 数据库的用户名
    :param pwd: 数据库的密码
    :param db: 数据库名
    :param charset: 编码
    :param log: 日志核心部件
    :return: 从数据库中放回的数据
    """
    if not log:
        log.logger.debug('正在保存至sql')
    conn = pymysql.connect(host=host,
                           port=port,
                           user=user,
                           passwd=pwd,
                           db=db,
                           charset=charset)
    # 建立游标，指定游标类型，返回字典
    cur = conn.cursor(DictCursor)
    sql = f'''INSERT INTO `eswitch_log`(`sw_name`, `sw_ip`, `last_run_time`, `last_inside_time`, `loop_time`, `loop_port`, `loop_text`) 
            VALUES ("{save_dict['sw_name']}",
            "{save_dict['log_ip']}",
            "{save_dict['last_run_time']}",
            "{save_dict['last_inside_time']}",
            "{save_dict['loop_time']}",
            "{save_dict['loop_port']}",
            "{save_dict['loop_text']}")'''
    # 执行sql语句
    cur.execute(sql)
    # 关闭游标
    cur.close()
    # 关闭连接
    conn.close()
    # 获取查询的所有结果
    res = cur.fetchall()
    log.logger.info('res')
    return res

def Emonitor_select_sql(ip, host="127.0.0.1", port=3306, user='root',
                       pwd='root', db='emonitor', charset='utf8'):
    conn = pymysql.connect(host=host,
                           port=port,
                           user=user,
                           passwd=pwd,
                           db=db,
                           charset=charset)
    # 建立游标，指定游标类型，返回字典
    cur = conn.cursor(DictCursor)
    sql = f'select last_inside_time from eswitch_log where sw_ip = "{ip}"'
    # 执行sql语句
    cur.execute(sql)
    # 关闭游标
    cur.close()
    # 关闭连接
    conn.close()
    # 获取查询的所有结果
    res = cur.fetchall()
    return res
