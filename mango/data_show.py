from PyQt5.QtWidgets import QDialog, QTableWidgetItem, QAbstractItemView, QFileDialog

from sign_indata import Ui_Dialog

class sign_data(Ui_Dialog, QDialog):
    def __init__(self, signdata, parent=None):
        super(sign_data, self).__init__()
        self.setupUi(self)
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        for i in signdata.values():
            info = i['user_info'].split('\n')
            info_name = info[0].split('：')
            info_class = info[1].split('：')
            rowcount = self.tableWidget.rowCount()
            self.tableWidget.insertRow(rowcount)
            self.tableWidget.setItem(rowcount,0,QTableWidgetItem(info_name[1]))
            self.tableWidget.setItem(rowcount,1,QTableWidgetItem(info_class[1]))
            self.tableWidget.setItem(rowcount,2,QTableWidgetItem(i['datetime']))

        self.pushButton.clicked.connect(self.save_data)
        # self.pushButton_2.clicked

    def save_data(self):
        # 打开对话框，获取要导出的数据文件名
        filename = QFileDialog.getSaveFileName(self, "导出数据", ".", "TXT(*.txt)")
        print(filename)
        self.accept()

