from urllib.request import urlretrieve
import cv2
import numpy
import os
import shutil

class crackVerification:
    def __init__(self, pageXML):
        self.pageXML = pageXML

    def __createTempDir__(self):
        dirNanme = "cache"
        if os.path.exists(dirNanme):
            shutil.rmtree(dirNanme)
        os.mkdir(dirNanme)

        return dirNanme

    def __getVerificationImage__(self, verifyImageInfo):
        if not len(verifyImageInfo):
            return

        url = verifyImageInfo[0].get("src")
        imageName = "verifyImage.jpg"

        urlretrieve(url, imageName)

        return cv2.imread(imageName)

    def __getSlideImage__(self, slideImageInfo):
        if not len(slideImageInfo):
            return

        url = slideImageInfo[0].get("src")
        imageName = "slideImage.jpg"

        urlretrieve(url, imageName)

        return cv2.imread(imageName)

    def __getVerifyImageDistancePercent__(self, image):
        # 转灰度图片
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # cv2.imshow("gray", gray)
        # cv2.waitKey(0)
        # 边缘检测
        edges = cv2.Canny(gray, 700, 1200)
        # cv2.imshow("edges", edges)
        # cv2.waitKey(0)
        # 直线检测
        lines = cv2.HoughLinesP(edges, 5, numpy.pi/180, 20)
        # cv2.imshow("lines", numpy.array(lines, dtype=numpy.uint8))
        # cv2.waitKey(0)
        xSum = []

        for line in lines:
            x1, y1, x2, y2 = line[0]
            xSum += [x1, x2]
        #     cv2.line(image, (x1,y1), (x2,y2), (0,0,0), 5)

        # cv2.imshow("image", image)
        # cv2.waitKey(0)

        mid = sum(xSum)/len(xSum)
        return mid / image.shape[1]

    def __getProperSlidePosition__(self, verifyImage, slideImage):
        if verifyImage is None or slideImage is None:
            return

        return self.__getVerifyImageDistancePercent__(verifyImage)

    def getProperSlidePosition(self):
        tempDir = self.__createTempDir__()
        os.chdir(tempDir)

        verifyImage = self.__getVerificationImage__(self.pageXML.find_all("img", {"id": "captcha-verify-image"}))
        slideImage = self.__getSlideImage__(self.pageXML.find_all("img", {"class": "captcha_verify_img_slide"}))
        properSlidePositionPercent = self.__getProperSlidePosition__(verifyImage, slideImage)

        os.chdir("..")
        shutil.rmtree(tempDir)

        return properSlidePositionPercent
