from tkinter import filedialog
from PIL import Image
from threading import Thread, Semaphore
from moviepy.video.fx import resize
from ffmpeg import audio, video
import subprocess
import re
import moviepy.editor as mp
import tkinter
import os
import shutil
import sys

class insert_file:
    def __init__(self, filename = "", ffmpegPath = "", limitSem = None) -> None:
        self.file = filename
        self.framesDir = os.path.splitext(self.file)[0]
        self.limitSem = limitSem
        self.ffmpegPath = ffmpegPath

        if filename != "" and not os.path.exists(self.framesDir):
            os.mkdir(self.framesDir)
            image = Image.open(self.file)

            try:
                while True:
                    frame = image.tell()
                    image.save(self.framesDir + "\\" + str(frame) + '.png')
                    image.seek(frame + 1)
            except EOFError:
                pass

    def __setDurationTime__(self):
        if self.videoFile.duration < 3:
            self.indicateTime = self.videoFile.duration
        elif self.videoFile.duration / 5 < 3:
            self.indicateTime = 3
        else:
            self.indicateTime = self.videoFile.duration / 5

    def __changeSpd__(self, percent = 100):
        fileName = os.path.splitext(self.videoFile)[0]
        speed = percent / 100
        video.separate_audio(self.ffmpegPath, "\"" + self.videoFile + "\"", "\"1" + fileName + ".mp4" + "\"")
        audio.separate_video(self.ffmpegPath, "\"" + self.videoFile + "\"", "\"1" + fileName + ".mp3" + "\"")

        video.playback_speed(self.ffmpegPath, "\"1" + fileName + ".mp4" + "\"", speed, "\"2" + fileName + ".mp4" + "\"")
        audio.a_speed(self.ffmpegPath, "\"1" + fileName + ".mp3" + "\"", speed, "\"2" + fileName + ".mp3" + "\"")

        subprocess.call("%s\\ffmpeg -i %s -i %s -c:v copy -c:a aac -strict experimental %s"\
            %(self.ffmpegPath, "\"2" + fileName + ".mp4" + "\"", "\"2" + fileName + ".mp3" + "\"", "\"3" + fileName + ".mp4" + "\""),
            shell=True)

        os.remove("1" + fileName + ".mp4")
        os.remove("1" + fileName + ".mp3")
        os.remove("2" + fileName + ".mp4")
        os.remove("2" + fileName + ".mp3")

        os.remove(self.videoFile)
        os.rename("3%s" %fileName + ".mp4", self.videoFile)

        self.videoFile = mp.VideoFileClip(self.videoFile)
        return

    def getSupportVideoFormat(self):
        return [".mp4", ".ffmpeg", ".ogv", ".mpeg", ".avi", ".mov"]

    def getSupportImageFormat(self):
        return [".png", ".tiff", ".jpeg", ".gif"]

    def __getFileType__(self, file):
        supportVideoFormat = self.getSupportVideoFormat()
        supportImageFormat = self.getSupportImageFormat()

        if any(re.search(os.path.splitext(file)[-1], videoFormat, re.IGNORECASE) for videoFormat in supportVideoFormat):
            return "video"
        elif any(re.search(os.path.splitext(file)[-1], imageFormat, re.IGNORECASE) for imageFormat in supportImageFormat):
            return "picture"

        return None

    def __insertVideo__(self):
        self.sourceFile = resize.resize((mp.ImageClip(self.file)
            .set_duration(self.indicateTime)
            .set_pos((0.5, 0.7), relative=True)), height = self.videoFile.size[1] / 5)

        self.finalFileHandle = mp.CompositeVideoClip([self.videoFile, self.sourceFile])

    def __getPictureSrcFile__(self):
        if os.path.splitext(self.file)[-1] == ".gif":
            clip = mp.ImageSequenceClip(self.framesDir, 2)
            totalTime = 0
            clips = []

            while totalTime < self.indicateTime:
                clips.append(clip)
                totalTime += clip.duration

            return mp.concatenate_videoclips(clips)
        else:
            return mp.ImageClip(self.file, True)

    def __insertPicture__(self):
        self.sourceFile = resize.resize((self.__getPictureSrcFile__()
            .set_start(self.videoFile.duration - self.indicateTime)
            .set_end(self.videoFile.duration)
            .set_fps(2)
            .set_pos((0.5, 0.7), relative=True)), height = self.videoFile.size[1] / 5)

        self.finalFileHandle = mp.CompositeVideoClip([self.videoFile, self.sourceFile], [630, 1120])

    def __saveFile__(self):
        if os.path.exists(".%s" %self.videoFile.filename):
            os.remove(".%s" %self.videoFile.filename)
        self.finalFileHandle.write_videofile(".%s" %self.videoFile.filename, codec="libx264", bitrate="1000000")

        os.remove(self.videoFile.filename)
        os.rename(".%s" %self.videoFile.filename, self.videoFile.filename)

    def insertFile(self, fileName):
        self.videoFile = fileName

        self.__changeSpd__(120)
        self.__setDurationTime__()

        srcFileType = self.__getFileType__(self.file)
        if srcFileType == "video":
            self.__insertVideo__()
        elif srcFileType == "picture":
            self.__insertPicture__()

        self.__saveFile__()
        self.limitSem.release()

    def quit(self):
        if os.path.exists(self.framesDir):
            shutil.rmtree(self.framesDir)

def getSupportVideos(supportVideoFormat, workDir):
    supportVideos = []

    for file in os.listdir(workDir):
        fileExt = os.path.splitext(file)[-1]
        for videoFormat in supportVideoFormat:
            if fileExt != "" and re.search(fileExt, videoFormat, re.IGNORECASE):
                supportVideos.append(file)
                break

    return supportVideos

def ffmpegGetDir():
    dirName = "ffmpeg"

    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, dirName)
    else:
        return os.path.join(r"%s\VideoProcessing\bin" %os.path.abspath(os.curdir), dirName)

def main():
    root = tkinter.Tk()
    root.withdraw()

    srcFile = filedialog.askopenfile(mode ='r',
        filetypes =[('source File', '*.png'), ('source File', '*.jpeg'), ('source File', '*.gif')],
        title = "select the file which you want to insert")
    workDir = filedialog.askdirectory(title = "select the dirctory where the videos are")
    threadLimitSem = Semaphore(5)
    threads = []
    ffmpegPath = ffmpegGetDir()
    os.chdir(workDir)
    insert_file(srcFile.name)

    for dstFile in getSupportVideos(insert_file().getSupportVideoFormat(), workDir):
        threadLimitSem.acquire()
        thread = Thread(target = insert_file(srcFile.name, ffmpegPath, threadLimitSem).insertFile,
            args = (dstFile, ), name = dstFile)
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    insert_file(srcFile.name).quit()
    input("按任意键退出\n")

if __name__=='__main__':
    main()
