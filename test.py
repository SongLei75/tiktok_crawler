import cv2, numpy
from selenium import webdriver
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from bs4 import BeautifulSoup
import threading
import time
import signal
import os
from multiprocessing.dummy import Process, Queue
import time
from multiprocessing import Lock
from multiprocessing import Process
from multiprocessing import shared_memory
import multiprocessing

def line_detection_demo():
    image = cv2.imread(r"C:\Users\95788\Desktop\verifyImage.jpg")
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 700, 1000)
    lines = cv2.HoughLinesP(edges, 50, numpy.pi/180, 20)
    xMin = image.shape[1]

    for line in lines:
        x1, y1, x2, y2 = line[0]
        xMin = xMin if x1 > xMin and x2 > xMin else min([x1, x2])
        cv2.line(image, (x1,y1), (x2,y2), (0,0,0), 5)

    print(xMin)
    cv2.imshow("image_lines", image)
    cv2.waitKey()

def isPageReady():
    browser = webdriver.Edge("C:\Program Files (x86)\Microsoft\Edge\Application\msedgedriver.exe")
    browser.get("https://www.douyin.com/video/7035131354232786217")
    wait = WebDriverWait(browser, 20)

    aa = BeautifulSoup(browser.page_source, 'lxml').find_all("title")[0].text
    slider = wait.until(expected_conditions.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div[2]/div/div[1]/div[1]/div[2]/div/div[1]/div/div[2]/div[2]")))
    return

def downloadVideo():
    url = "https://www.douyin.com/aweme/v1/play/?aid=6383&app_name=aweme&channel=channel_pc_web&device_platform=web&did=0&file_id=3b123b3e98244f29aab25775abdfe274&fp=&is_play_url=1&line=0&referer=&sign=6d28f66354cc74590b188d6efdc4630c&source=PackSourceEnum_AWEME_DETAIL&target=6919021309179596036&user_agent=Mozilla%2F5.0%20%28Windows%20NT%2010.0%3B%20Win64%3B%20x64%29%20AppleWebKit%2F537.36%20%28KHTML%2C%20like%20Gecko%29%20Chrome%2F96.0.4664.55%20Safari%2F537.36%20Edg%2F96.0.1054.43&video_id=v0300fa60000c02iq9dmpcjb7g0j2ucg&webid=7037533696992298529"
    import requests
    res = requests.get(url, stream=True)
    with open('test.mp4', 'wb') as f:
        for chunk in res.iter_content(chunk_size=10240):
            f.write(chunk)

class Job(threading.Thread):
    def __init__(self, *args, **kwargs):
        super(Job, self).__init__(*args, **kwargs)
        self.__flag = threading.Event()     # 用于暂停线程的标识
        self.__flag.set()       # 设置为True
        self.__running = threading.Event()      # 用于停止线程的标识
        self.__running.set()      # 将running设置为True

    def run(self):
        while self.__running.is_set():
            self.__flag.wait()      # 为True时立即返回, 为False时阻塞直到内部的标识位为True后返回
            print(time.time())
            time.sleep(1)

    def pause(self):
        self.__flag.clear()     # 设置为False, 让线程阻塞

    def resume(self):
        self.__flag.set()    # 设置为True, 让线程停止阻塞

    def stop(self):
        self.__flag.set()       # 将线程从暂停状态恢复, 如何已经暂停的话
        self.__running.clear()        # 设置为False

def threadOpt():
    a = Job()
    a.start()
    time.sleep(3)
    a.pause()
    time.sleep(3)
    a.resume()
    time.sleep(3)
    a.pause()
    time.sleep(2)
    a.stop()

import time
import psutil

def run_proc(name):
    for i in range(20):
        print('我是子进程，我正在运行中')
        time.sleep(1)

def procopt():
    #创建并启动子进程
    a = "test"
    p = Process(target=run_proc, args=(a,), name = "进程暂停/恢复测试")
    p.start()
    pid = p.pid   #获取子进程的pid

    #测试暂停子进程
    time.sleep(5)
    pause = psutil.Process(pid)  #传入子进程的pid
    pause.suspend()   #暂停子进程
    print('子进程暂停运行')
    time.sleep(5)
    pause.resume()   #恢复子进程
    print('\n子进程已恢复运行')

def crawlerDouyin(msgQueue):
    pid = os.getpid()
    ppid = os.getppid()
    print("douyinCrawer pid: %s, ppid: %s" %(str(pid), str(ppid)))

def monitorDouyin(msgQueue):
    pid = os.getpid()
    ppid = os.getppid()
    print("douyinMonitor pid: %s, ppid: %s" %(str(pid), str(ppid)))

def douyin():
    from multiprocessing import Process, Queue

    pid = os.getpid()
    ppid = os.getppid()
    print("main pid: %s, ppid: %s" %(str(pid), str(ppid)))
    msgQueue = Queue()

    crawlerProcess = Process(target = crawlerDouyin, args = (msgQueue, ), name = "抖音爬虫")
    crawlerProcess.start()

    Process(target = monitorDouyin, args = (msgQueue, ), name = "抖音验证").start()
    crawlerProcess.join()

def process1(lock1, lock2):
    """构造共享内存的进程"""
    lock1.acquire()
    print("step1...")
    shm1 = shared_memory.SharedMemory(name="shm_name", create=True, size=4000)
    print("构造新的共享内存，实例化SharedMemory对象{}".format(shm1))
    lock2.release()

    lock1.acquire()
    print("step3...")
    shm1 = None
    lock2.release()

    lock1.acquire()
    print("step5...")
    shm3 = shared_memory.SharedMemory(name="shm_name")
    print("构造新的共享内存，实例化SharedMemory对象{}".format(shm3))
    lock2.release()

    lock1.acquire()
    print("step7...")
    lock2.release()


def process2(lock1, lock2):
    """使用修改共享内存的进程"""
    lock2.acquire()
    print("step2...")
    shm2 = shared_memory.SharedMemory(name="shm_name")
    print("使用现有共享内存，实例化SharedMemory对象{}".format(shm2))
    lock1.release()

    lock2.acquire()
    print("step4...")
    time.sleep(1)  # 添加延迟保证需要被销毁的共享内存块已被回收
    lock1.release()

    lock2.acquire()
    print("step6...")
    shm2 = None
    lock1.release()

    lock2.acquire()
    print("step8...")
    time.sleep(1)  # 添加延迟保证需要被销毁的共享内存块已被回收
    shm4 = shared_memory.SharedMemory(name="shm_name")
    print("使用现有共享内存，实例化SharedMemory对象{}".format(shm4))

def worker(procnum, return_dict):
    print(str(procnum) + ' represent!')
    return_dict[procnum] = procnum

if __name__ == '__main__':
    pass
