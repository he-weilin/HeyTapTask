# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/9/12
# @Author  : MashiroF
# @File    : ChockInEarly.py
# @Software: PyCharm

'''
cron:  35 0,19 * * * ChockInEarly.py
new Env('欢太早睡打卡');
'''

import os
import re
import sys
import time
import random
import logging

# 日志模块
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logFormat = logging.Formatter("%(message)s")

# 日志模块
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logFormat = logging.Formatter("%(message)s")

# 日志输出流
stream = logging.StreamHandler()
stream.setFormatter(logFormat)
logger.addHandler(stream)

# 第三方库
try:
    import requests
except ModuleNotFoundError:
    logger.info("缺少requests依赖！程序将尝试安装依赖！")
    os.system("pip3 install requests -i https://pypi.tuna.tsinghua.edu.cn/simple")
    os.execl(sys.executable, 'python3', __file__, *sys.argv)

# 检测配置文件并下载(云函数可能不适用)
def checkFile(urlList):
    exitFlag = False
    for url in urlList:
        fileName = url.split('/')[-1]
        fileUrl = f'https://ghproxy.com/{url}'
        try:
            if not os.path.exists(fileName):
                exitFlag = True
                logger.info(f"`{fileName}`不存在,尝试进行下载...")
                content = requests.get(url=fileUrl).content.decode('utf-8')
                with open(file=fileName, mode='w', encoding='utf-8') as fc:
                    fc.write(content)
        except:
            logger.info(f'请手动下载配置文件`{fileName[:-3]}`到 {os.path.dirname(os.path.abspath(__file__))}')
            logger.info(f'下载地址:{fileUrl}\n')
    if os.path.exists('/ql/config/auth.json'):
        # 判断环境，青龙面板则提示
        logger.info(f"CK配置 -> 脚本管理 -> 搜索`HT_config`关键字 -> 编辑\n")
    if exitFlag ==True:
        # 发生下载行为,应退出程序，编辑配置文件
        time.sleep(3)
        sys.exit(0)

# 检测必备文件
fileUrlList = [
    'https://raw.githubusercontent.com/Mashiro2000/HeyTapTask/main/sendNotify.py',
    'https://raw.githubusercontent.com/Mashiro2000/HeyTapTask/main/HT_config.py'
]
checkFile(fileUrlList)

# 配置文件
try:
    from HT_config import notifyBlackList,accounts,text
    logger.info(text)
    lists = accounts
except:
    logger.info('更新配置文件或检测CK')
    lists = []

# 配信文件
try:
    from sendNotify import send
except:
    logger.info('推送文件有误')
finally:
    allMess = ''

# 配信内容格式化
def notify(content=None):
    global allMess
    allMess = allMess + content + '\n'
    logger.info(content)

# 日志录入时间
notify(f"任务:欢太早睡打卡\n时间:{time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())}")

class CheckInEarly:
    def __init__(self,dic):
        self.dic = dic
        self.sess = requests.session()

    # 登录验证
    def login(self):
        url = 'https://store.oppo.com/cn/oapi/users/web/member/check'
        headers = {
            'Host': 'store.oppo.com',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Connection': 'keep-alive',
            'Accept-Language': 'zh-cn',
            'Accept-Encoding': 'gzip, deflate, br',
        }
        response = self.sess.get(url=url,headers=headers).json()
        if response['code'] == 200:
            notify(f"{self.dic['user']}\t登录成功")
            return True
        else:
            notify(f"{self.dic['user']}\t登录失败")
            return False

    # 报名或打卡
    # 报名或打卡是同一个链接，配合Linux定时系统
    def early(self):
        url = 'https://store.oppo.com/cn/oapi/credits/web/clockin/applyOrClockIn'
        headers = {'Host': 'store.oppo.com',
                   'Connection': 'keep-alive',
                   'source_type': '501',
                   'clientPackage': 'com.oppo.store',
                   'Accept': 'application/json, text/plain, */*',
                   'Referer': 'https://store.oppo.com/cn/app/cardingActivities?us=gerenzhongxin&um=hudongleyuan&uc=zaoshuidaka',
                   'Accept-Encoding': 'gzip, deflate',
                   'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7'
                   }
        response = self.sess.get(url=url,headers=headers).json()
        if response['code'] == 200:
            if response['data']['clockInStatus'] == 0:
                if response['data']['applyStatus'] == 0:
                    notify(f"{self.dic['user']}\t积分过少，取消报名!")
                elif response['data']['applyStatus'] == 1:
                    notify(f"{self.dic['user']}\t报名成功!")
                elif response['data']['applyStatus'] == 2:
                    notify(f"{self.dic['user']}\t已报名!")
            elif response['data']['clockInStatus'] == 1:
                notify(f"{self.dic['user']}\t早睡瓜分积分，打卡成功!")
            elif response['data']['clockInStatus'] == 2:
                notify(f"{self.dic['user']}\t早睡瓜分积分,已成功打卡!")
        elif response['code'] == 1000005:
            notify(f"{self.dic['user']}\t{response['errorMessage']}")

    # 执行欢太商城实例对象
    def start(self):
        self.sess.headers.update({
            "User-Agent":self.dic['UA']
        })
        self.sess.cookies.update({
            "Cookie":self.dic['CK']
        })
        if self.login() == True:
            self.early()
        notify('*' * 40 + '\n')

# 检测CK是否存在必备参数
def checkHT(dic):
    CK = dic['CK']
    if len(re.findall(r'source_type=.*?;',CK)) == 0:
        notify(f"{dic['user']}\tCK格式有误:可能缺少`source_type`字段")
        return False
    if len(re.findall(r'TOKENSID=.*?;',CK)) == 0:
        notify(f"{dic['user']}\tCK格式有误:可能缺少`TOKENSID`字段")
        return False
    if len(re.findall(r'app_param=.*?[;]?',CK)) == 0:
        notify(f"{dic['user']}\tCK格式有误:可能缺少`app_param`字段")
        return False
    return True

# # 格式化设备信息Json
# # 由于青龙的特殊性,把CK中的 app_param 转换未非正常格式，故需要此函数
# def transform(string):
#     dic2 = {}
#     dic1 = eval(string)
#     for i in dic1['app_param'][1:-1].split(','):
#         dic2[i.split(':')[0]] = i.split(':')[-1]
#     if dic1['CK'][-1] != ';':
#         dic1['CK'] = dic1['CK'] + ';'
#     dic1['CK'] = dic1['CK'] + f"app_param={json.dumps(dic2,ensure_ascii=False)}"
#     dic1['CK'] = checkHT(dic1['CK'])
#     return dic1

# # 读取青龙CK
# def getEnv(key):
#     lists2 = []
#     notify("尝试导入青龙面板CK...")
#     variable = os.environ.get(key)
#     if variable == None:
#         notify("青龙面板环境变量 TH_COOKIE 不存在！")
#     else:
#         for each in variable.split('&'):
#             result = transform(each)
#             if result:
#                 lists2.append(result)
#     return lists2

# 兼容云函数
def main(event, context):
    global lists
    for each in lists:
        if all(each.values()):
            if checkHT(each):
                checkInEarly = CheckInEarly(each)
                for count in range(3):
                    try:
                        time.sleep(random.randint(2,5))    # 随机延时
                        checkInEarly.start()
                        break
                    except requests.exceptions.ConnectionError:
                        notify(f"{checkInEarly.dic['user']}\t请求失败，随机延迟后再次访问")
                        time.sleep(random.randint(2,5))
                        continue
                else:
                    notify(f"账号: {checkInEarly.dic['user']}\n状态: 取消登录\n原因: 多次登录失败")
                    break
    if not os.path.basename(__file__).split('_')[-1][:-3] in notifyBlackList:
        send('欢太早睡打卡',allMess)

if __name__ == '__main__':
    main(None,None)
