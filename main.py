import psutil
from Crawler.DownloadSource import crawler, tiktokCrawler
from threading import Thread
from psutil import pids
import time, os, requests

def crawlerDouyinKeywordVideos(douyinCrawler, keyword):
    mainPage = "www.douyin.com"
    dstPath = "."
    dirName = "抖音"

    douyinCrawler.openBrowser(mainPage)
    douyinCrawler.downloadSrc(keyword, dstPath, dirName)
    douyinCrawler.quitBrowser()

def douyin():
    driverPath = "C:\Program Files (x86)\Microsoft\Edge\Application\msedgedriver.exe"
    keywords = ["托尼贾"]
    crawlerThreads = []

    for keyword in keywords:
        thread = Thread(target = crawlerDouyinKeywordVideos,
            args = (crawler(driverPath), keyword, ), name = "抖音爬虫")
        crawlerThreads.append(thread)
        thread.start()

    for thread in crawlerThreads:
        thread.join()

def crawlerTiktokKeywordVideos(douyinCrawler, keyword, userInfo):
    mainPage = "www.tiktok.com"
    dstPath = "."
    dirName = "Tiktok"

    douyinCrawler.openBrowser(mainPage)
    douyinCrawler.logIn(userInfo)
    # douyinCrawler.downloadSrc(keyword, dstPath, dirName)
    # douyinCrawler.quitBrowser()

def quitAdsPower(thread, closeUrl):
    requests.get(closeUrl)
    for pid in pids():
        try:
            if psutil.Process(pid).name() == "AdsPower.exe":
                os.system("taskkill /f /t /pid %d" %pid)
        except: continue

def setupAdsPower():
    apiKey = "10f07b1918a5821589fb0e9f62bedacf"
    adsThread = Thread(target=os.system, args=(r"D:\application\AdsPower\AdsPower.exe" + \
        " --user_id --headless=true --api-key=%s --api-port=50325" %apiKey, ))
    adsThread.start()

    adsId = "i1blmso"
    openUrl = "http://local.adspower.net:50325/api/v1/browser/start?user_id=" + adsId
    closeUrl = "http://local.adspower.net:50325/api/v1/browser/stop?user_id=" + adsId

    retryTimes = 0

    while True:
        try:
            resp = requests.get(openUrl).json()
            if resp["code"] != 0:
                if retryTimes < 5:
                    retryTimes += 1
                    print(resp["msg"])
                    time.sleep(1)
                    continue
                else: quitAdsPower(adsThread, closeUrl)
            break
        except:
            time.sleep(1)
            continue

    return {"driverPath": resp["data"]["webdriver"], "thread": adsThread,\
        "closeUrl": closeUrl, "debuggerAddress":resp["data"]["ws"]["selenium"]}

def tiktok():
    # driverPath = "C:\Program Files\Google\Chrome\Application\chromedriver.exe"
    keywords = ["pop star"]
    crawlerThreads = []
    userInfo = {"username": "18681356521", "password": "Sl2999!!"}
    adsInfo = setupAdsPower()

    for keyword in keywords:
        thread = Thread(target = crawlerTiktokKeywordVideos,
            args = (tiktokCrawler(adsInfo["driverPath"], adsInfo["debuggerAddress"]),
            keyword, userInfo), name = "Tiktok爬虫-%s" %keyword)
        crawlerThreads.append(thread)
        thread.start()

    for thread in crawlerThreads:
        thread.join()

    quitAdsPower(adsInfo["thread"], adsInfo["closeUrl"])

if __name__ == '__main__':
    douyin()
