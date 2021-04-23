import sys
from PyQt5.QtWidgets import QApplication
from mywindow import mywindow
'''
程序的解释执行文件
'''

if __name__ == '__main__':
    #创建应用程序对象
    app = QApplication(sys.argv)
    #创建窗口
    ui = mywindow()
    #显示窗口
    ui.show()
    #应用执行
    app.exec_()
    sys.exit(0)