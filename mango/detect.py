from PyQt5.QtCore import QThread, QTimer, pyqtSignal, QDateTime
import requests
import cv2
import base64


# Thread就是PyQt5提供的线程类
# 由于是一个已经完成了的类，功能已经写好，线程的功能需要我们自己完成
# 需要自己完成需要的线程类，创建一个新的线程类（功能可以自己定义），继承QThread，新写的类就是线程类，具备线程功能

# 线程进行执行只会执行线程类中的run函数，如果有新的功能需要实现，重写一个run函数
class detect_thread(QThread):
    transmit_data = pyqtSignal(dict)
    search_data = pyqtSignal(str)
    # 设计布尔值，为了退出while循环
    OK = True
    # 字典用来存放签到数据
    sign_list = {}

    def __init__(self, token):
        super(detect_thread, self).__init__()
        self.access_token = token
        self.condition = False

    # run函数执行结束，代表线程结束
    def run(self):
        # print("run")
        '''
        self.time = QTimer()
        self.time.start(1000)
        self.time.timeout.connect(self.detect_face)
        '''
        while self.OK:
            if self.condition:
                self.detect_face(self.base64_image)
                self.condition = False
        # print("while finish")

    def get_base64(self, base64_image):
        # 当窗口调用产生信号，调用这个槽函数，就把传递的数据，存放在线程变量中
        self.base64_image = base64_image
        self.condition = True

    # 进行人脸检测
    def detect_face(self, base64_image):
        '''
        这是打开对话框获取
        #获取一张图片或一帧画面
        #通过对话框的形式获取一个图片的路径
        path, ret = QFileDialog.getOpenFileName(self, "open picture", ".", "图片格式(*.jpg)")
        print(path)
        #把图片转换成base64编码
        fp = open(path, 'rb')
        base64_image = base64.b64encode(fp.read())
        '''
        # 发送请求的地址
        request_url = "https://aip.baidubce.com/rest/2.0/face/v3/detect"
        # 请求参数，是一个字典，存储了百度AI要识别的图片信息，要识别的属性内容
        params = {"image": base64_image,  # 图片信息字符串
                  "image_type": "BASE64",  # 图片信息的格式
                  "face_field": "gender,age,beauty,expression,face_shape,glasses,mask,emotion",
                  # 请求识别人脸的属性，在各个属性字符串用逗号隔开
                  "max_face_num": 10
                  }
        # 访问令牌
        access_token = self.access_token
        # 把请求地址和访问令牌组成可用的网络请求地址
        request_url = request_url + "?access_token=" + access_token
        # 设置请求格式体
        headers = {'content-type': 'application/json'}
        # 发送网络post请求，请求百度API进行人脸检测,返回检测结果
        # 发送网络请求，会等待一定时间，所以会导致程序在这里阻塞执行
        response = requests.post(request_url, data=params, headers=headers)
        if response:
            # print(response.json())
            data = response.json()
            if data['error_code'] != 0:
                self.transmit_data.emit(data)
                self.search_data.emit(data['error_msg'])
                return
            if data['result']['face_num'] > 0:
                # print("detectface")
                self.transmit_data.emit(dict(data))
                self.face_search()

    # 人脸识别检测，只识别一个人
    def face_search(self):
        request_url = "https://aip.baidubce.com/rest/2.0/face/v3/search"

        params = {
            "image": self.base64_image,
            "image_type": "BASE64",
            "group_id_list": "class_one"  # 从哪些组中进行识别
        }
        access_token = self.access_token
        request_url = request_url + "?access_token=" + access_token
        headers = {'content-type': 'application/json'}
        response = requests.post(request_url, data=params, headers=headers)
        if response:
            data = response.json()
            if data['error_code'] == 0:
                if data['result']['user_list'][0]['score'] > 90:
                    # 存储要保存的签到数据
                    del[data['result']['user_list'][0]['score']]
                    datetime = QDateTime.currentDateTime()
                    datetime = datetime.toString()
                    data['result']['user_list'][0]['datetime'] = datetime
                    key = data['result']['user_list'][0]['group_id'] + data['result']['user_list'][0]['user_id']
                    if key not in self.sign_list.keys():
                        self.sign_list[key] = data['result']['user_list'][0]
                    self.search_data.emit("学生签到成功\n学生信息是：" + data['result']['user_list'][0]['user_info'])
