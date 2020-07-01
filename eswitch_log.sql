

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- 数据库： `emonitor`
--

-- --------------------------------------------------------

--
-- 表的结构 `eswitch_log`
--

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

--
-- 转储表的索引
--

--
-- 表的索引 `eswitch_log`
--
ALTER TABLE `eswitch_log`
  ADD PRIMARY KEY (`log_id`);

--
-- 在导出的表使用AUTO_INCREMENT
--

--
-- 使用表AUTO_INCREMENT `eswitch_log`
--
ALTER TABLE `eswitch_log`
  MODIFY `log_id` int(11) NOT NULL AUTO_INCREMENT COMMENT '日志id，唯一的', AUTO_INCREMENT=55;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
