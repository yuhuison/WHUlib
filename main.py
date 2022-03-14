import datetime

import interface
import time
import sched

# 初始化scheduler类
# 第一个参数是一个可以返回时间戳的函数，第二个参数可以在定时未到达之前阻塞。
s = sched.scheduler(time.time, time.sleep)

userf = open('users.txt', encoding="utf-8")
userlist = []
for lines in userf:
    userlist.append(lines.replace('\n', '').split(","))
countf = open('count.txt', "r")
count = int(countf.read())
countf.close()
timePointNear = [8, 0]  # 最近一个任务的执行的时间点
timePoints = list()  # 时间点数组
timePoints.append([8, 0])
timePoints.append([11, 30])
timePoints.append([15, 0])
timePoints.append([18, 30])


# 该函数用于预约研修室，并使得count自动加一，若未预约成功，则提示并还原count
def makeAppointment(hour, day, month):
    global count
    index = (count % 13)
    username = userlist[index][1]
    password = userlist[index][2]
    name = userlist[index][0]
    i = interface.whuInterface(username, password, name)
    try:
        count = count + 1
        i.login()
        i.entry_edit(hour, month, day, 32)
    except:
        print("任务执行失败")
        count = count - 1
        pass
    finally:
        countff = open('count.txt', "w")
        countff.write(str(count))
        countff.close()
        findAndSetNearTask()
        # 无论如何，都将寻找下一任务


# 找到最近的一个需要执行任务的时间点
def findAndSetNearTask():
    timePointsTimes = list()  # 初始化一个时间对象数组
    now = datetime.datetime.now()
    orderDay = datetime.datetime.now() + datetime.timedelta(days=3)  # 预约研修室的时间点
    execDay = datetime.datetime.now()  # 执行任务的时间点
    if (now.hour == 18 and now.minute >= 30) or (now.hour > 18):
        orderDay = datetime.datetime.now() + datetime.timedelta(days=4)
        execDay = datetime.datetime.now() + datetime.timedelta(days=1)
    # 假如当前的时间已经到了18时，则计算时间应推迟一天
    for i in timePoints:
        iTime = datetime.datetime(execDay.year, execDay.month, execDay.day, hour=i[0], minute=i[1])
        timePointsTimes.append(iTime)
    minIndex = 0
    minDelta = 0
    for i in range(4):
        delta = (timePointsTimes[i] - now).seconds  # 获取四个时间点到当前的时间差（秒数）
        if minDelta == 0:
            minDelta = delta
        else:
            if delta < minDelta:
                minDelta = delta
                minIndex = i
    global timePointNear
    timePointNear = timePoints[minIndex]
    print("已经找到下一个任务的执行时间，为：" + timePointsTimes[minIndex].strftime("%Y-%m-%d %H:%M:%S"))
    print("本次任务预约的研修室为 " + str(orderDay.month) + "-" + str(orderDay.day) + " " + str(timePointNear[0]) + ":" + str(
        timePointNear[1]))
    # 之后，设置延迟多少秒之后执行，保险起见，多加几秒
    print("使用账号：")
    print(userlist[count % 13])
    print("该任务将于" + str(minDelta) + "秒后执行，进入等待线程")
    s.enter(minDelta + 10, 0, makeAppointment, (timePointNear[0], orderDay.day, orderDay.month))
    s.run()


def main():
    findAndSetNearTask()
    # test()


def test():
    index = (count % 13)
    username = userlist[index][1]
    password = userlist[index][2]
    name = userlist[index][0]
    i = interface.whuInterface(username, password, name)
    i.login()
    i.entry_edit(11, 3, 13, 32)


if __name__ == '__main__':
    main()
