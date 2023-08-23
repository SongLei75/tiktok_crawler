from selenium import webdriver
from urllib.request import quote
# from selenium.webdriver.chrome.options import Options
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from bs4 import BeautifulSoup

import os
import datetime
import shutil
import requests
import time
import sys
sys.path.append("..")
from Verification.CrackVerification import crackVerification

class verification:
    def __init__(self, type):
        self.type = type

    def detectVerification(self, page_source):
        pagewebXML = BeautifulSoup(page_source, 'lxml')
        # captchaLable = pagewebXML.find_all("div", {"id": "captcha_container"})
        captchaLable = pagewebXML.find_all("div", {"id": "tiktok-verify-ele"})
        verificationStatus = captchaLable[0].get("style").split(";")[0]

        return False if "none" in verificationStatus else True

    def __getMockDragDistance__(self, distance):
        traces = []

        while (sum(traces) < distance):
            if (((distance - sum(traces)) / 3) > 1):
                traces.append((distance - sum(traces)) / 3)
            else:
                traces.append(1)

        return traces

    def __mockDragSlide__(self, browser, properSlidePosition):
        traces = self.__getMockDragDistance__(properSlidePosition)

        try:
            slider = WebDriverWait(browser, 1).until(
                expected_conditions.presence_of_element_located((By.CLASS_NAME, "secsdk-captcha-drag-icon")))
        except:
            return

        ActionChains(browser).click_and_hold(slider).perform()
        for trace in traces:
            ActionChains(browser).move_by_offset(xoffset = trace, yoffset = 0).perform()
        ActionChains(browser).release().perform()

    def __slideVerification__(self, browser):
        properSlidePosition = crackVerification(BeautifulSoup(browser.page_source, 'lxml')).getProperSlidePosition()
        if properSlidePosition is not None:
            self.__mockDragSlide__(browser, properSlidePosition * 350)

    def crackVerification(self, browser):
        if self.type == "slide":
            self.__slideVerification__(browser)

class crawler:
    def __init__(self, executablePath, debuggerAddress = ""):
        self.options = Options()
        # self.options.add_argument('--headless')
        # self.options.add_argument('--disable-gpu')
        # self.options.add_argument('--incognito')
        # self.options.add_argument('log-level=3')
        # self.options.add_argument('disable-infobars')
        # self.options.add_argument('user-agent="Mozilla/5.0 (iPhone; CPU iPhone OS 14_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/7.0.18(0x17001231) NetType/4G Language/en_US"')
        # self.options.add_argument('--lang=en-US')
        # self.options.add_experimental_option('excludeSwitches', ['enable-automation'])
        # self.options.add_experimental_option('excludeSwitches', ['enable-logging'])
        if debuggerAddress != "":
            self.options.add_experimental_option("debuggerAddress", debuggerAddress)

        self.browser = webdriver.Chrome(executablePath, options = self.options)
        self.wait = WebDriverWait(self.browser, 5)

    def openBrowser(self, mainPage):
        self.mainPage = mainPage
        while len(self.browser.window_handles) != 1:
            self.browser.switch_to.window(self.browser.window_handles[-1])
            self.browser.close()

        self.browser.switch_to.window(self.browser.window_handles[-1])
        self.browser.get("https://" + self.mainPage)

    def __createRootDir__(self, dirName):
        rootDir = dirName
        if not os.path.exists(rootDir):
            os.mkdir(rootDir)

        return rootDir

    def __createDateDir__(self, rootDir):
        dateDir = rootDir + "/" + str(datetime.date.today())
        if not os.path.exists(dateDir):
            os.mkdir(dateDir)

        return dateDir

    def __createKeywordDir__(self, dateDir, keyword):
        keywordDir = dateDir + "/" + keyword
        if os.path.exists(keywordDir):
            shutil.rmtree(keywordDir)
        os.mkdir(keywordDir)

        return keywordDir

    def __crackVerification__(self):
        douyinMonitor = verification("slide")

        try:
            self.wait.until(expected_conditions.presence_of_element_located((By.ID, "captcha_container")))
            # self.wait.until(expected_conditions.presence_of_element_located((By.CLASS_NAME, "captcha_verify_container")))
        except:
            return

        while True:
            if douyinMonitor.detectVerification(self.browser.page_source) == False:
                return

            douyinMonitor.crackVerification(self.browser)
            time.sleep(1)

    def __openKeywordSearchURL__(self, keyword):
        page = "https://" + self.mainPage + "/search/{}?publish_time=0&sort_type=0&source=switch_tab&type=video"
        self.browser.execute_script("window.open('%s')" %page.format(quote(keyword, encoding="utf-8")))
        self.browser.switch_to.window(self.browser.window_handles[-1])
        self.__crackVerification__()

    def __getVideoURLs__(self):
        videoURLs = []

        while len(videoURLs) == 0:
            time.sleep(1)

            for lable in BeautifulSoup(self.browser.page_source, 'lxml').find_all("a"):
                if lable.get("href") is not None and "//%s/video/" %self.mainPage in lable.get("href"):
                    videoURLs.append("https:" + lable.get("href"))

        return list(set(videoURLs))

    def __getVideoSrcInfo__(self):
        videoSrcInfo = {}
        videoxml = BeautifulSoup(self.browser.page_source, 'lxml')

        for lable in videoxml.find_all("source"):
            if "//%s/" %self.mainPage in lable.get("src"):

                videoSrcInfo["url"] = "https:" + lable.get("src")
                videoSrcInfo["name"] = videoxml.find_all("title")[0].text

        return videoSrcInfo

    def __getVideoSrcInfos__(self, videoURLs):
        videoSrcInfos = []

        for videoURL in videoURLs:
            self.browser.execute_script("window.open('%s')" %videoURL)
            self.browser.switch_to.window(self.browser.window_handles[-1])

            try:
                self.wait.until(expected_conditions.presence_of_element_located((By.TAG_NAME, "source")))
            except:
                break

            videoSrcInfos.append(self.__getVideoSrcInfo__())

            self.browser.close()
            self.browser.switch_to.window(self.browser.window_handles[-1])

        return videoSrcInfos

    def __downloadKeywordVideo__(self, video, keywordDir):
        response = requests.get(video["url"])

        try:
            with open(keywordDir + "/" + video["name"] + ".mp4", 'wb') as video:
                for chunk in response.iter_content(chunk_size=1024):
                    video.write(chunk)
        except:
            return

    def __downloadKeywordSrc__(self, keyword, keywordDir):
        self.__openKeywordSearchURL__(keyword)

        videoURLs = self.__getVideoURLs__()
        videoSrcInfos = self.__getVideoSrcInfos__(videoURLs)

        for videoSrc in videoSrcInfos:
            self.__downloadKeywordVideo__(videoSrc, keywordDir)

        self.browser.close()
        try:
            self.browser.switch_to.window(self.browser.window_handles[-1])
        except:
            return

    def downloadSrc(self, keyword, path, dirName):
        os.chdir(path)

        rootDir = self.__createRootDir__(dirName)
        dateDir = self.__createDateDir__(rootDir)
        keywordDir = self.__createKeywordDir__(dateDir, keyword)
        self.__downloadKeywordSrc__(keyword, keywordDir)

        return

    def quitBrowser(self):
        self.browser.quit()

class tiktokCrawler(crawler):
    def __init__(self, executablePath, debuggerAddress):
        crawler.__init__(self, executablePath, debuggerAddress)

    def __mainPageToLogin__(self):
        while True:
            try:
                menu = [tag for tag in self.browser.find_elements(By.TAG_NAME, "div")
                    if tag.get_attribute("class") != None and "side-hamburger" in tag.get_attribute("class")][0]
                break
            except:
                time.sleep(0.5)

        try: menu.click()
        except:
            while True:
                try:
                    notNowButton = [tag for tag in self.browser.find_elements(By.TAG_NAME, "button")
                        if tag.text != None and "Not now" == tag.text][0]
                    notNowButton.click()
                    time.sleep(0.5)
                    menu.click()
                    break
                except:
                    time.sleep(0.5)

        self.__crackVerification__()

        while True:
            try:
                loginButton = [tag for tag in self.browser.find_elements(By.TAG_NAME, "button")
                    if tag.text != None and "Log in" in tag.text][0]
                loginButton.click()
                break
            except:
                time.sleep(0.5)

    def __findWebPageElementByTagAndText__(self, text):
        while True:
            try:
                element = [tag for tag in self.browser.find_elements(By.TAG_NAME, "div")
                    if tag.text != None and text == tag.text][0]
                return element
            except:
                time.sleep(0.5)

    def __inputUserInfo__(self, userInfo):
        while True:
            try:
                username = [tag for tag in self.browser.find_elements(By.TAG_NAME, "input")
                    if tag.get_attribute("placeholder") != None and "Email or Username" == tag.get_attribute("placeholder")][0]
                password = [tag for tag in self.browser.find_elements(By.TAG_NAME, "input")
                    if tag.get_attribute("placeholder") != None and "Password" == tag.get_attribute("placeholder")][0]
                break
            except:
                time.sleep(0.5)

        username.click()
        time.sleep(0.5)
        for word in userInfo["username"]:
            username.send_keys(word)
            time.sleep(0.1)

        password.click()
        time.sleep(0.5)
        for word in userInfo["password"]:
            password.send_keys(word)
            time.sleep(0.1)

    def logIn(self, userInfo):
        self.__mainPageToLogin__()
        self.__findWebPageElementByTagAndText__("Use phone / email / username").click()
        time.sleep(0.5)
        self.__findWebPageElementByTagAndText__("Email / Username").click()
        time.sleep(0.5)
        self.__inputUserInfo__(userInfo)
        time.sleep(0.5)
        [tag for tag in self.browser.find_elements(By.TAG_NAME, "button")
            if tag.text != None and "Log in" == tag.text][0].click()

        return
