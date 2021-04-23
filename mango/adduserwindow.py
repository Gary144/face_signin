import base64

import cv2
from PyQt5.QtCore import QTimer
from adduser import Ui_Dialog
from PyQt5.QtWidgets import QDialog
from cameravideo import camera


class adduserwindow(Ui_Dialog, QDialog):

    def __init__(self, list, parent=None):
        super(adduserwindow, self).__init__(parent)
        self.setupUi(self)  # 创建界面内容
        self.label.setScaledContents(True)
        # 把组信息显示再列表框中
        self.show_list(list)
        # 启动摄像头
        self.cameravideo = camera()
        # 创建定时器
        self.time = QTimer()
        self.time.timeout.connect(self.show_cameradata)
        self.time.start(50)
        self.pushButton.clicked.connect(self.get_cameradata)
        self.pushButton_2.clicked.connect(self.get_data)
        self.pushButton_3.clicked.connect(self.close_window)

    def show_list(self, list):
        for i in list:
            self.listWidget.addItem(i)

    # 并处作为摄像头，获取数据，显示画面的功能
    # 并只要能够不断重复调用这个函数，不断的从摄像头获取数据进行显示
    # 可以通过信号， 信号关联当前函数。只要信号产生，函数就会被调用
    # 信号需要不断的产生，可以通过定时器，定时时间到达就会产生信号
    def show_cameradata(self):
        # 获取摄像头数据，转换数据
        pic = self.cameravideo.camera_to_pic()
        # 显示数据，显示画面
        self.label.setPixmap(pic)

    def get_cameradata(self):
        # 摄像头获取画面
        camera_data = self.cameravideo.read_camera()
        # 把摄像头画面转换成图片，然后设置编码base64编码格式数据
        _, self.enc = cv2.imencode('.jpg', camera_data)
        self.base64_image = base64.b64encode(self.enc.tobytes())
        # 产生信号，传递数据
        # self.detect_data_signal.emit(bytes(base64_image))
        # 关闭定时器
        self.time.stop()
        # 关闭摄像头
        self.cameravideo.close_camera()

    def get_data(self):
        self.group_id = self.listWidget.currentItem().text()
        self.user_id = self.lineEdit.text()
        self.msg_name = self.lineEdit_2.text()
        self.msg_class = self.lineEdit_3.text()
        # 关闭窗口
        self.accept()

    def close_window(self):
        # 关闭对话框
        pass
