#!python

import urllib.request
import urllib.parse
import time
import random

#
# user defined parameters
#

# 程序会在以下定义的时间段内随机选择一个时刻做签到/签出

# 开始签到时间 at 8:15, in minutes
checkin_start = 8 * 60 + 14
# 结束签到时间 at 8:35, in minutes
checkin_end = 8 * 60 + 28

# 开始签出时间 at 17:05, in minutes
checkout_start = 17 * 60 + 35
# 结束签出时间 at 17:35, in minutes
checkout_end = 17 * 60 + 45

# sigma 用于正态分布的分布集中度表示，著名的6 sigma可以让99.99966%覆盖到区间内
# 理论上说，总有可能会落在签到/出的时间区间外面，但概率非常低
# 不过这种小概率事件也被弥补了，超出的会被放到边界时间上，所以不用担心
# sigma越小结果越平均，最好用5, 6, 7等
gSigma = 6

# 星期六是否工作，0表示不工作，其他数字（如1）表示工作
SatIsWork = 0
# 星期天是否工作，0表示不工作，其他数字（如1）表示工作
SunIsWork = 0

# 各种原因引起的签到/出失败，重试次数，0意味着不重试
FAIL_COUNT = 3

password = '6'
username = 'jyf'
# 登录后查看'考勤管理'页面的源代码，可以找到自己的personid
# 具体方法如下：
# 打开签到签出界面，右键点击，选择查看源文件
# 在源文件中搜索 onclick="doAdd
# 出现的结果如下
# <input type="button" id="btnAdd" onclick="doAdd(101);" class="addbutton" value="签到">
# 此处doAdd后面的数字就是你的personid，当然前提是你用自己的账户登录
personid = 101

#
# system variable, don't change
#
checkin_before = 8 * 60 + 40
checkout_after = 17 * 60

URL_first = 'http://192.168.1.223:88/ITSystem'
URL_login = 'http://192.168.1.223:88/ITSystem/jsp/system/style/login.do?method=login'
URL_checkin = 'http://192.168.1.223:88/ITSystem/jsp/jianguan/timeAction.do?method=addSubmit&personID={}'
URL_checkout = 'http://192.168.1.223:88/ITSystem/jsp/jianguan/timeAction.do?method=updateSubmit&personID={}'

FAIL_WAIT_LOW = 37
FAIL_WAIT_HIGH = 61

def findJsessionID(page):
	jsid_start = page.find('jsessionid=') + len('jsessionid=')
	jsessionid = page[jsid_start:jsid_start + 32]
	return jsessionid

def checkinout(username, password, personid):
        opener = urllib.request.build_opener();
        opener.addheaders = [('User-agen', 'Mozilla/5.0')]

        print('fetch initial page')
        try:
                responce = opener.open(URL_first)
        except urllib.error.URLError as reason:
                print('URLError: {}'.format(reason))
                return False
        except urllib.error.HTTPError as code:
                print('HTTPError: {}'.format(code))
                return False
        except urllib.error.ContentTooShortError:
                print('Content too short')
                return False
        except:
                print('unknown error rised')
                return False
        page = responce.read().decode('utf-8')

        print('looking for JSESSIONID...')
        sessionid = findJsessionID(page)
        print(sessionid)

        opener.addheaders = [('Cookie', 'JSESSIONID={}'.format(sessionid))]

        time.sleep(random.randint(2, 5))

        print('Start login...')
        params = urllib.parse.urlencode({'logincode':username, 'password':password})
        params = params.encode('utf-8')
        try:
                responce = opener.open(URL_login, params)
        except urllib.error.URLError as reason:
                print('URLError: {}'.format(reason))
                return False
        except urllib.error.HTTPError as code:
                print('HTTPError: {}'.format(code))
                return False
        except urllib.error.ContentTooShortError:
                print('Content too short')
                return False
        except:
                print('unknown error rised')
                return False

        page = responce.read().decode('utf-8')
        print(page)

        time.sleep(random.randint(2, 5))

        now = time.localtime()
        now_min = now.tm_hour * 60 + now.tm_min

        if now_min < checkin_before - 50:
                print('It is too early, why not check in by yourself')
        elif now_min < checkin_before:
                print('Check in...')
                try:
                        responce = opener.open(URL_checkin.format(personid))
                except urllib.error.URLError as reason:
                        print('URLError: {}'.format(reason))
                        return False
                except urllib.error.HTTPError as code:
                        print('HTTPError: {}'.format(code))
                        return False
                except urllib.error.ContentTooShortError:
                        print('Content too short')
                        return False
                except:
                        print('unknown error rised')
                        return False

                page = responce.read().decode('utf-8')
        elif now_min > checkout_after:
                print('Check out...')
                try:
                        responce = opener.open(URL_checkout.format(personid))
                except urllib.error.URLError as reason:
                        print('URLError: {}'.format(reason))
                        return False
                except urllib.error.HTTPError as code:
                        print('HTTPError: {}'.format(code))
                        return False
                except urllib.error.ContentTooShortError:
                        print('Content too short')
                        return False
                except:
                        print('unknown error rised')
                        return False

                page = responce.read().decode('utf-8')
        else:
                print('working time, do not checkin or checkout')

        return True

def isHoliday(day):
        f = open('holidays.txt')
        while True:
                line = f.readline()
                if len(line) == 0:
                        break
                if len(line) < 8:
                        continue
                if line[0] == '#':
                        continue

                line = line.rstrip('\n')
                line = line.rstrip('\r')

                if line[0] == '!':
                        tm = time.strptime(line[1:], '%Y-%m-%d')
                        if day.tm_year != tm.tm_year:
                                continue
                        if day.tm_mon != tm.tm_mon:
                                continue
                        if day.tm_mday != tm.tm_mday:
                                continue

                        return False
                else :
                        tm = time.strptime(line, '%Y-%m-%d')
                        if day.tm_year != tm.tm_year:
                                continue
                        if day.tm_mon != tm.tm_mon:
                                continue
                        if day.tm_mday != tm.tm_mday:
                                continue

                        return True

        if SatIsWork == 0:
                if day.tm_wday == 5:
                        return True
        if SunIsWork == 0:
                if day.tm_wday == 6:
                        return True
        
        return False

def nextCheck():
        now = time.localtime()
        now_sec = time.mktime(now)
        now_min = now.tm_hour * 60 + now.tm_min

        if isHoliday(now):
                skipdays = 1
                now_sec = now_sec + 3600 * 24
                while isHoliday(time.localtime(now_sec)):
                        skipdays = skipdays + 1
                        now_sec = now_sec + 3600 * 24
        else:
                skipdays = 0
                if now_min < checkin_start:
                        start = checkin_start - now_min
                        end = checkin_end - now_min
                elif now_min < checkout_start:
                        start = checkout_start - now_min
                        end = checkout_end - now_min
                else:
                        skipdays = 1
                        now_sec = now_sec + 3600 * 24
                        while isHoliday(time.localtime(now_sec)):
                                skipdays = skipdays + 1
                                now_sec = now_sec + 3600 * 24

        if skipdays != 0:
                start = (skipdays) * 24 * 60 + checkin_start - now_min
                end = start - checkin_start + checkin_end

        mu = int((start * 60 + end * 60) / 2)
        sigma = int((end * 60 - start * 60) / gSigma)
        t = random.normalvariate(mu, sigma)
        if t < start * 60:
                t = start * 60
        elif t > end * 60:
                t = end * 60

        return t

def displayWait(delay):
        hour = int(delay / 3600)
        minute = int(delay % 3600 / 60)
        second = int(delay % 3600 % 60)
        action = time.asctime(time.localtime(time.time() + delay))
        print('waiting {0}h{1}m{2}s for next check in/out at [{3}]'.format(hour, minute, second, action))

def validation():
        print('======================================================')
        print(' 本程序可以帮助你自动签到和签出。但程序可能有Bug，请谨慎使用')
        print(' 请不要随意把此脚本发给其他人使用，如果出现问题，风险自己承担')
        print(' 请遵守公司规定，不要因此迟到和早退')
        print(' 本程序仅供学习和参考，请在下载后48小时内删除:)')
        print('======================================================')
        print('User={0}, Password={1}, personid={2}'.format(username, password, personid))
        print('如果这个账户不是你的, 请关闭程序, 修改脚本中的变量')
        for i in ('请检查', '用户名对么?', '密码对么?', '知道什么是personid么?', 'personid对么?'):
                print(i),
                #time.sleep(2)
        print('go')

validation()
random.seed()

sleeptime = nextCheck()

while True:
        displayWait(sleeptime)
        time.sleep(sleeptime)

        failtry = 0
        while checkinout(username, password, personid) == False:
                failtry = failtry + 1
                if failtry > FAIL_COUNT:
                        break
                time.sleep(random.randint(FAIL_WAIT_LOW, FAIL_WAIT_HIGH))

        sleeptime = nextCheck()
  
