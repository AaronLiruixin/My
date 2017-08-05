创建时间：20170328
功能描述：将log文档文档中的数据按字段插入数据库，可按照字段（关键字，请求方式，登录方式，日期，IP地址）查询数据，删除数据库数据，对比文件和数据库中的数据，之后把新增的内容插入数据库，遇到新的Error,Fatal,Warning时按指定的错误等级将transaction和错误的信息发送到指定邮箱，可以更改数据库和邮箱，文件路径等参数。
函数：
__init__()
option()判断指令，指向要执行的函数
printoption()显示指令
conn()连接数据库，执行sql语句，如果有结果集逐行输出
conn_noprint()连接数据库执行sql语句，不管有没有结果集都不输出。
createtable()建表
deletedata()删除数据库信息
SelectOption()判断指令，执行查询的函数
quit()退出程序
email()发送邮件
SendError(),SendFatal(),SendWarning()按照错误等级执行发送邮件的函数
SendMail()发送邮件
LatestDate()获取数据库中Date字段的最大值
process_log()获取Date字段的最大值后与路径中的文件内容对比，把新增的内容插入数据库。
Insertdata（）按路径把文件中的内容插入数据库
Select_value()构造查询语句，执行conn方法
缺陷：
1.发送的邮件中\n原样输出没有换行，尝试发送html类型的邮件也不成功，邮件内容可读性差。
数据库：
表名默认为log_1
Sign varchar(2) log中一行中的第一个字符串
Detail mediumblob 每一个transaction的详细信息
Date varchar(20) 格式化后输入的日期（20170322010101000000年月日时分秒，秒后精确六位小数）
IPaddress varchar(20) 每个事务的IP地址
Accessmode varcher(255)访问方式
Requestmethod varchar(20)请求方式
无主键（有两个transaction的开始时间精确到秒数后六位都是一样的，Date不能作为主键，而且没必要设主键）。
tips：Compare()和insertdata()功能很类似，但是最后我还是没有把他们合并，insertdata()用于数据库为空时，第一次把文件中的内容写入数据库，compare()用于数据库中已经有数据，对比是否有新数据然后插入。因为如果合并，第一次插入文件每行会多两次判断，文件很大时开销大，花费时间长。还有两个极类似的conn方法，因为有的查询功能有结果集但是不希望输出结果集。如果写成一个函数，增加一个变量也可以实现，似乎分开写开销小一点。
—————————————————————————————————————————————————————————————————————————————
更新时间：20170331
更新内容：类变量改为在__init__函数中初始化的普通变量，实例化后传入一个字典config,其中email,level,log_file三个参数是必选的，其他参数可以没有。去掉了一些多余的步骤和相应的函数。
参数：
参数名：config（dict) 
Key:email,level(Enum:0,1,2),log_file,port(int）,user,passwd,db,table
参数名：report_level(Enum)
Warning=0,Error=1,Fatal=2
—————————————————————————————————————————————————————————————————————————————
更新时间：20170404
更新内容：增加了创建summary的功能，统计从当天00：00到当前时间内的所有transaction的概要内容，和每个IP地址的动作，以及该IP地址的所有Error。config中增加了名为create_path的key，create_summary()会根据create_path路径创建一个名为log_summary的文件夹（用于存放summary的txt文件），如果config中没有指明create_path的值，会在当前目录创建文件夹。
参数：
参数名：config(dict)
Key:email,level(Enum:0,1,2),log_file,port(int）,user,passwd,db,table,create_path.
—————————————————————————————————————————————————————————————————————————————
更新时间：20170409
更新内容：增加了创建summary发送邮件的功能(Createsummary)，summary内容包括每个设备和每个用户的活动摘要，如果有错误就报告错误详细内容，数据库增加了	Who和Device_or_user字段。改写插入数据库的两个函数insertlog和processlog以及创建数据表的函数.
数据库：
Sign varchar(2) log中一行中的第一个字符串
Detail mediumblob 每一个transaction的详细信息
Date varchar(20) 格式化后输入的日期（20170322010101000000年月日时分秒，秒后精确六位小数）
IPaddress varchar(20) 每个事务的IP地址
Accessmode varcher(255)访问方式
Requestmethod varchar(20)请求方式
Device_or_user boolean 设备或用户 0表示用户，1表示设备
Who varchar(20)如果是用户即为用户名，是设备即为serial number
缺陷：代码效率低，还有可以合并的函数，insertlog和processlog的差异和效率需要考察，查询功能还没有优化。
—————————————————————————————————————————————————————————————————————————————
更新时间：20170504
更新内容：删除了insertlog功能，优化了processlog功能，修改了数据库的结构。主要改动是将单个的sql语句改为批量写入数据库，由于数据长度的原因每900个transaction执行一次，性能提高了很多，处理5.5m文件用时9.5s.
数据库：
Detail mediumblob 每一个transaction的详细信息
Date varchar(20) 格式化后输入的日期（20170322010101000000年月日时分秒，秒后精确六位小数）
IPaddress varchar(20) 每个事务的IP地址
Accessmode varcher(255)访问方式
Requestmethod varchar(20)请求方式
Device_or_user boolean 设备或用户 0表示用户，1表示设备
Who varchar(20)如果是用户即为用户名，是设备即为serial number
————————————————————————————————————————————————————————————————————————————————更新时间：20170721
更新内容：优化了插入who和device_or_user字段的功能；修复了两次运行程序的间隔时间内只产生一个transaction时报错的bug；修复了每n个transaction执行一次时第n的倍数个transaction的who和device_or_user字段无法写入库的bug；更改了识别serial number的方法。
数据库：
数据库结构没有变化。
————————————————————————————————————————————————————————————————————————————————
更新时间：20170724
更新内容：去掉了与用户互动的部分，修复了没有transaction更新时sql语句报错的bug,修复了用户name可能错误或不完整的bug，更改了数据库结构：调整who字段的长度为varchar(40)。
数据库：
Detail mediumblob 每一个transaction的详细信息
Date varchar(20) 格式化后输入的日期（20170322010101000000年月日时分秒，秒后精确六位小数）
IPaddress varchar(20) 每个事务的IP地址
Accessmode varcher(255)访问方式
Requestmethod varchar(20)请求方式
Device_or_user boolean 设备或用户 0表示用户，1表示设备
Who varchar(40)如果是用户即为用户名，是设备即为serial number
————————————————————————————————————————————————————————————————————————————————
更新时间：20170728
更新内容：合并了插入device_or_user,who,detail三个字段的sql语句，速度有所提升。
增加了set_max_allowed_packet功能，config字典添加了num_transactions索引，即每次添加的transaction数。
写入数据库的速度也受到max_allowed_packet的影响，对应关系：
500个transaction/次需要max_allowed_packet=4M，
2200个transaction/次需要max_allowed_packet=8M，
5500个transactions/次需要max_allowed_packet=16M。
数据库：
数据库结构没有变化
手动输入：set global max_allowed_packet=8388608;(8M)
	set global max_allowed_packet=16777216;(16M) 
	show variables like “%max_allowed_packet%”
//使用命令行手动输入或使用程序中的set_max_allowed_packet功能需要mysql命令行quit后重启方可用此语句查询

