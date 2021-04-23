import base64
import cv2
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QMessageBox, QInputDialog
from PyQt5.QtCore import QTimer, QDateTime, QDate, QTime, pyqtSignal
from mainwindow import Ui_MainWindow
from cameravideo import camera
import requests, json
from detect import detect_thread
from adduserwindow import adduserwindow
from data_show import sign_data


class mywindow(Ui_MainWindow, QMainWindow):
    detect_data_signal = pyqtSignal(bytes)
    camera_status = False

    def __init__(self):
        super(mywindow, self).__init__()
        self.setupUi(self)
        self.label.setScaledContents(True)
        self.label.setPixmap(QPixmap("./3.jpg"))
        # 创建一个时间定时器
        self.datetime = QTimer()
        # 启动获取系统时间/日期定时器,定时时间为10ms，10ms产生一次信号
        self.datetime.start(10)
        # 创建窗口就应该完成进行访问令牌的申请（获取）
        self.get_accesstoken()
        # 信号与槽的关联
        # self.actionopen：指定对象
        # triggered：信号
        # connect：关联（槽函数）
        # self.on_actionopen():关联的函数
        self.actionopen.triggered.connect(self.on_actionopen)
        self.actionclose.triggered.connect(self.on_actionclose)

        # 添加用户组信号槽
        self.actionaddgroup.triggered.connect(self.add_group)
        # 删除用户组信号槽
        self.actiondelgroup.triggered.connect(self.del_group)
        # 查询用户组信号槽
        self.actiongetlist.triggered.connect(self.getgrouplist)
        # 添加用户信号槽
        self.actionadduser.triggered.connect(self.add_user)
        # 删除用户信号槽
        self.actiondeluser.triggered.connect(self.del_user)
        # 关联时间/日期的定时器信号与槽函数
        self.datetime.timeout.connect(self.data_time)

    # data_time函数获取日期与时间，添加到对应的定时器
    def data_time(self):
        # 获取日期
        date = QDate.currentDate()
        # print(date)
        # self.dateEdit.setDate(date)
        self.label_3.setText(date.toString())
        # 获取时间
        time = QTime.currentTime()
        # print(time)
        # self.timeEdit.setTime(time)
        self.label_2.setText(time.toString())
        # 获取日期时间
        datetime = QDateTime.currentDateTime()
        # print(datetime)

    def on_actionclose(self):
        # 清除学生人脸信息(False)
        # self.plainTextEdit_2.setPlainText("  ")
        # 关闭定时器，不再设置检测画面获取
        self.facedetecttime.stop()
        #self.facedetecttime.timeout.disconnect(self.get_cameradata)
        #self.detect_data_signal.disconnect(self.detectThread.get_base64)
        #self.detectThread.transmit_data.connect(self.get_detectdata)
        # 关闭检测线程
        self.detectThread.OK = False
        self.detectThread.quit()
        self.detectThread.wait()
        #print(self.detectThread.isRunning())
        # 关闭定时器，不再去获取摄像头的数据
        self.timeshow.stop()
        self.timeshow.timeout.disconnect(self.show_cameradata)
        # 关闭摄像头
        self.cameravideo.close_camera()
        self.camera_status = False

        # 显示本次签到的情况
        # self.detectThread.sign_list
        self.signdata = sign_data(self.detectThread.sign_list, self)
        self.signdata.exec_()
        # 画面设置为初始状态
        if self.timeshow.isActive() == False and self.facedetecttime.isActive() == False:
            self.label.setPixmap(QPixmap("./3.jpg"))
            self.plainTextEdit.clear()
            self.plainTextEdit_2.clear()
        else:
            QMessageBox.about(self, "错误", "关闭签到失败\n")

    '''
    信号槽功能：
        当某个组件设计了信号槽功能（关联信号槽）时，当信号产生，会主动调用槽函数，去完成对应的一个功能
        信号：当以某种特点的操作，操作到这个组件时，就会主动产生对应操作的信号
    '''

    def on_actionopen(self):
        # 启动摄像头
        self.cameravideo = camera()
        self.camera_status = True
        # 启动定时器，进行定时，每个多长时间进行一次获取摄像头数据进行显示，用作流畅显示画面
        self.timeshow = QTimer(self)
        self.timeshow.start(10)
        # 10ms的定时器启动，每到10ms就会产生一个信号timeout,信号没有（）
        self.timeshow.timeout.connect(self.show_cameradata)
        # self.timeshow.timeout().connect(self.show_cameradata)
        # self.show_cameradata()

        # 创建检测线程
        self.create_thread()
        # 当开启启动签到时，创建定时器，500ms，用作获取要检测的画面

        self.facedetecttime = QTimer(self)
        self.facedetecttime.start(500)
        self.facedetecttime.timeout.connect(self.get_cameradata)
        # facedetecttime定时器设置检测画面获取
        self.detect_data_signal.connect(self.detectThread.get_base64)

        self.detectThread.transmit_data.connect(self.get_detectdata)
        self.detectThread.search_data.connect(self.get_search_data)

    def get_search_data(self, data):
        self.plainTextEdit.setPlainText(data)

    # 创建线程完成检测
    def create_thread(self):
        self.detectThread = detect_thread(self.access_token)
        self.detectThread.start()

    def get_cameradata(self):
        # 摄像头获取画面
        camera_data = self.cameravideo.read_camera()
        # 把摄像头画面转换成图片，然后设置编码base64编码格式数据
        _, enc = cv2.imencode('.jpg', camera_data)
        base64_image = base64.b64encode(enc.tobytes())
        # 产生信号，传递数据
        self.detect_data_signal.emit(bytes(base64_image))

    # 并处作为摄像头，获取数据，显示画面的功能
    # 并只要能够不断重复调用这个函数，不断的从摄像头获取数据进行显示
    # 可以通过信号， 信号关联当前函数。只要信号产生，函数就会被调用
    # 信号需要不断的产生，可以通过定时器，定时时间到达就会产生信号
    def show_cameradata(self):
        # 获取摄像头数据，转换数据
        pic = self.cameravideo.camera_to_pic()
        # 显示数据，显示画面
        self.label.setPixmap(pic)

    # 获取进行网络请求的访问令牌
    def get_accesstoken(self):
        # host对象是字符串对象存储是授权的服务地址-----获取accesstoken的地址
        host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=7QWxwbwt2EKq6j7ckceOAFSo&client_secret=6Gj9TMnb2SOGdEloFjEHVURqQVpPnsqW'
        # 发送网络请求   requests网络库
        # 使用get函数发送网络请求，参数为网络请求的地址，执行时会产生返回结果，结果就是请求的结果
        response = requests.get(host)
        if response:
            # print(response.json())
            data = response.json()
            self.access_token = data.get('access_token')

    # 槽函数，获取检测数据
    def get_detectdata(self, data):
        if data['error_code'] != 0:
            self.plainTextEdit_2.setPlainText(data['error_msg'])
        elif data['error_msg'] == 'SUCCESS':
            # 在data字典中，键为'result'对应的值才是返回的检查结果
            # data['result']才是检测结果
            # 人脸数目
            self.plainTextEdit_2.clear()
            face_num = data['result']['face_num']
            if face_num == 0:
                self.plainTextEdit_2.appendPlainText("未测到检人脸")
                return
            else:
                self.plainTextEdit_2.appendPlainText("测到检人脸")
            # 人脸信息data['result']['face_list']，是列表，每个数据就是一个人脸信息，需要取出每个列表数据
            # 每个人脸信息：data['result']['face_list'][0~i]人脸信息字典
            for i in range(face_num):
                # 通过for循环，分别取出列表的每一个数据
                # data['result']['face_list'][i]，就是一个人脸信息的字典

                age = data['result']['face_list'][i]['age']
                beauty = data['result']['face_list'][i]['beauty']
                gender = data['result']['face_list'][i]['gender']['type']
                expression = data['result']['face_list'][i]['expression']['type']
                face_shape = data['result']['face_list'][i]['face_shape']['type']
                glasses = data['result']['face_list'][i]['glasses']['type']
                emotion = data['result']['face_list'][i]['emotion']['type']
                mask = data['result']['face_list'][i]['mask']['type']
                # 往窗口中添加文本，参数就是需要的文本信息
                self.plainTextEdit_2.appendPlainText("-----------------")
                self.plainTextEdit_2.appendPlainText("第" + str(i + 1) + "个学生信息：")
                self.plainTextEdit_2.appendPlainText("-----------------")
                self.plainTextEdit_2.appendPlainText("年龄: " + str(age))
                self.plainTextEdit_2.appendPlainText("颜值分数: " + str(beauty))
                self.plainTextEdit_2.appendPlainText("性别: " + str(gender))
                self.plainTextEdit_2.appendPlainText("表情: " + str(expression))
                self.plainTextEdit_2.appendPlainText("脸型: " + str(face_shape))
                self.plainTextEdit_2.appendPlainText("是否佩戴眼镜: " + str(glasses))
                self.plainTextEdit_2.appendPlainText("情绪: " + str(emotion))
                if mask == 0:
                    mask = "否"
                else:
                    mask = "是"
                self.plainTextEdit_2.appendPlainText("是否佩戴口罩: " + str(mask))
                self.plainTextEdit_2.appendPlainText("-----------------")

    def add_group(self):
        # 打开对话框，进行输入用户组
        group, ret = QInputDialog.getText(self, "添加用户组", "请输入用户组（由数字、字母、下划线组成）")

        request_url = "https://aip.baidubce.com/rest/2.0/face/v3/faceset/group/add"
        params = {
            "group_id": group
        }
        access_token = self.access_token
        request_url = request_url + "?access_token=" + access_token
        headers = {'content-type': 'application/json'}
        response = requests.post(request_url, data=params, headers=headers)
        if response:
            message = response.json()
            if message['error_msg'] == 'SUCCESS':
                QMessageBox.about(self, "用户组创建结果", "用户组创建成功")
            else:
                QMessageBox.about(self, "用户组创建结果", "用户组创建失败\n" + message['error_msg'])

    def del_group(self):
        request_url = "https://aip.baidubce.com/rest/2.0/face/v3/faceset/group/delete"
        list = self.getlist()
        group, ret = QInputDialog.getText(self, "用户组列表", "用户组信息\n" + str(list['result']['group_id_list']))
        # 删除，需要知道那些组
        params = {
            "group_id": group  # 要删除的用户组的id
        }
        access_token = self.access_token
        request_url = request_url + "?access_token=" + access_token
        headers = {'content-type': 'application/json'}
        response = requests.post(request_url, data=params, headers=headers)
        if response:
            data = response.json()
            if data['error_msg'] == 'SUCCESS':
                QMessageBox.about(self, "用户组删除结果", "用户组删除成功")
            else:
                QMessageBox.about(self, "用户组删除结果", "用户组删除失败\n" + data['error_msg'])

    # 获取用户组
    def getlist(self):
        request_url = "https://aip.baidubce.com/rest/2.0/face/v3/faceset/group/getlist"

        params = {
            "start": 0, "length": 100
        }
        access_token = self.access_token
        request_url = request_url + "?access_token=" + access_token
        headers = {'content-type': 'application/json'}
        response = requests.post(request_url, data=params, headers=headers)
        if response:
            return response.json()

    def getgrouplist(self):
        list = self.getlist()
        str = ''
        for i in list['result']['group_id_list']:
            str = str + '\n' + i
        QMessageBox.about(self, '用户组列表', str)

    def add_user(self):
        request_url = "https://aip.baidubce.com/rest/2.0/face/v3/faceset/user/add"
        if self.camera_status:
            QMessageBox.about(self, "摄像头状态", "摄像头已打开，正在进行人脸签到\n请关闭签到，再添加用户")
            return
        list = self.getlist()
        # 创建一个窗口来选择这些内容
        window = adduserwindow(list['result']['group_id_list'], self)
        # 新创建窗口，通过exec()函数一直执行，阻塞执行，窗口不进行关闭
        # exec()函数不会退出，关闭窗口才会结束
        window_status = window.exec_()
        # 进行判断，判断是否点击确定进行关闭
        if window_status != 1:
            return

        # 请求参数，需要获取人脸：转换人脸编码，添加的组id，添加的用户id，新用户的id信息
        params = {
            "image": window.base64_image,  # 人脸图片
            "image_type": "BASE64",  # 人脸图片编码
            "group_id": window.group_id,  # 组id
            "user_id": window.user_id,  # 新用户id
            "user_info": '姓名：' + window.msg_name + '\n'
                         + '班级：' + window.msg_class  # 用户信息
        }
        access_token = self.access_token
        request_url = request_url + "?access_token=" + access_token
        headers = {'content-type': 'application/json'}
        response = requests.post(request_url, data=params, headers=headers)
        if response:
            data = response.json()
            if data['error_msg'] == 'SUCCESS':
                QMessageBox.about(self, "人脸创建结果", "人脸创建成功")
            else:
                QMessageBox.about(self, "人脸创建结果", "用户组创建失败\n" + data['error_msg'])

    # 获取用户列表
    def get_userlist(self, group):
        request_url = "https://aip.baidubce.com/rest/2.0/face/v3/faceset/group/getusers"

        params = {
            "group_id": group
        }
        access_token = self.access_token
        request_url = request_url + "?access_token=" + access_token
        headers = {'content-type': 'application/json'}
        response = requests.post(request_url, data=params, headers=headers)
        if response:
            return response.json()

    # 获取用户人脸列表
    def user_face_list(self, group, user):
        request_url = "https://aip.baidubce.com/rest/2.0/face/v3/faceset/face/getlist"

        params = {
            "user_id": user,
            "group_id": group
        }
        access_token = self.access_token
        request_url = request_url + "?access_token=" + access_token
        headers = {'content-type': 'application/json'}
        response = requests.post(request_url, data=params, headers=headers)
        if response:
            return response.json()

    # 删除人脸
    def del_face_token(self, group, user, face_token):
        request_url = "https://aip.baidubce.com/rest/2.0/face/v3/faceset/face/delete"

        params = {
            "user_id": user,
            "group_id": group,
            "face_token": face_token
        }
        access_token = self.access_token
        request_url = request_url + "?access_token=" + access_token
        headers = {'content-type': 'application/json'}
        response = requests.post(request_url, data=params, headers=headers)
        if response:
            data = response.json()
            if data['error_msg'] == 'SUCCESS':
                QMessageBox.about(self, "人脸删除结果", "人脸删除成功")
            else:
                QMessageBox.about(self, "人脸删除结果", "用户组删除失败\n" + data['error_msg'])

    def del_user(self):
        # 查询用户人脸信息(face_token)
        # 获取用户组
        list = self.getlist()
        group, ret = QInputDialog.getText(self, "用户组获取", "用户组信息\n" + str(list['result']['group_id_list']))
        # 获取用户
        userlist = self.get_userlist(group)
        user, ret = QInputDialog.getText(self, "用户获取", "用户信息\n" + str(userlist['result']['user_id_list']))
        # 获取用户人脸列表
        face_list = self.user_face_list(group, user)
        for i in face_list['result']['face_list']:
            self.del_face_token(group, user, i['face_token'])

