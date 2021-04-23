import cv2
import numpy as np
from PyQt5.QtGui import QPixmap, QImage

'''
摄像头操作：创建类对象完成摄像头操作，使用可以把打开摄像头与创建类对象操作合并
     __init__函数完成摄像头的配置打开
'''


class camera():
    # 摄像头的配置打开与创建类对象合并
    def __init__(self):
        # VideoCapture类对视频或调用摄像头进行读取操作
        # 参数 filename;device
        # 0表示默认的摄像头，进行打开
        #创建摄像头对象，打开摄像头
        #self.capture表示打开摄像头的对象
        self.capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if self.capture.isOpened():
            print("isopenned")
        #定义一个多维数组，用来存储获取的数据
        self.currentframe = np.array([])

    # 读取摄像头数据
    def read_camera(self):
        ret, pic_data = self.capture.read()
        if not ret:
            print("获取摄像头数据失败")
            return None
        return pic_data

    # 把数据转换成界面能显示的数据格式
    def camera_to_pic(self):
        pic = self.read_camera()
        # 摄像头是BGR方式存储，需要转换成RGB
        # 调用cvtColor完成后才是RGB格式的画面数据
        self.currentframe = cv2.cvtColor(pic, cv2.COLOR_BGR2RGB)
        # 设置宽高
        #self.currentframe = cv2.cvtColor(self.currentframe, (640, 480))

        # 转换为界面能够显示的格式
        # 获取画面的宽度与高度
        height, width = self.currentframe.shape[:2]
        # 先转换为QImage类型图片（画面），创建QImage类对象，使用摄像头画面数据
        # QImage(data,width,height,format)创建：数据，宽度，高度，格式
        qimg = QImage(self.currentframe, width, height, QImage.Format_RGB888)
        qpixmap = QPixmap.fromImage(qimg)
        return qpixmap

    # 摄像头关闭
    def close_camera(self):
        self.capture.release()
