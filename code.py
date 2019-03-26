from PyQt5 import QtCore, QtGui, QtWidgets
import sys, cv2, time
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog,QTabWidget
import cv2,os,shutil
import numpy as np

class Ui_M(object):
    def setupUi(self, TabWidget):
        TabWidget.setObjectName("TabWidget")
        TabWidget.resize(1000, 600)
        self.tab = QtWidgets.QWidget()
        self.timer_camera = QtCore.QTimer()
        self.cap = cv2.VideoCapture()
        global face_cascade
        face_cascade = cv2.CascadeClassifier('./haarcascade_frontalface_default.xml')
        self.__layout_main = QtWidgets.QHBoxLayout()
        self.label_show_camera = QtWidgets.QLabel()
        self.label_show_camera.setFixedSize(641, 481)
        self.label_show_camera.setAutoFillBackground(False)
        self.gridLayoutWidget = QtWidgets.QWidget(self.tab)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(600, 100, 361, 550))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.label_show_pic = QtWidgets.QLabel(self.gridLayoutWidget )
        self.label_show_pic.setAutoFillBackground(False)
        self.gridLayout.addWidget(self.label_show_pic,0, 0, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 0, 1, 1, 1)
        self.pushButton = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout.addWidget(self.pushButton, 2, 0, 1, 2)
        self.pushButton_2 = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.pushButton_2.setObjectName("pushButton_2")
        self.gridLayout.addWidget(self.pushButton_2, 3, 0, 1, 2)
        self.retranslateUi(TabWidget)##操作布局函数如下
        #TabWidget.setCurrentIndex(0)#当前第0页
        self.timer_camera.timeout.connect(self.show_camera)
        self.pushButton.clicked.connect(TabWidget.videoprocessing) #将按键与事件相连
        self.pushButton_2.clicked.connect(TabWidget.close)
        QtCore.QMetaObject.connectSlotsByName(TabWidget)
        self.__flag_work = 0
        self.x = 0
        self.count = 0

    def retranslateUi(self, TabWidget):
        _translate = QtCore.QCoreApplication.translate
        TabWidget.setWindowTitle(_translate("TabWidget", "课堂考勤系统"))
        self.__layout_main.addWidget(self.label_show_camera)
        self.__layout_main.addWidget(self.gridLayoutWidget)
        self.setLayout(self.__layout_main)  # 到这步才会显示所有控件
        self.pushButton.setText(_translate("TabWidget", "开始考勤"))  #showvideo
        self.pushButton_2.setText(_translate("TabWidget", "退出"))
        self.label_3.setText(_translate("MainWindow", "哦豁小老弟"))

class mywindow(QTabWidget,Ui_M): #这个窗口继承了用QtDesignner 绘制的窗口
    def __init__(self):
        super(mywindow,self).__init__()
        self.setupUi(self)

    def videoprocessing(self):
        if self.timer_camera.isActive() == False:
            flag = self.cap.open(0)
            #打不开摄像头的话：
            if flag == False:
                msg = QtWidgets.QMessageBox.warning(self, u"Warning", u"请检测相机与电脑是否连接正确",
                                                    buttons=QtWidgets.QMessageBox.Ok,
                                                    defaultButton=QtWidgets.QMessageBox.Ok)
            else:

                flag, imag = self.cap.read()
                back = cv2.resize(imag, (640, 480))
                global gray_image_1
                gray_image_1 = cv2.cvtColor(back, cv2.COLOR_BGR2GRAY)  # 记录初始值

                #设计其他帧间差分法

                self.timer_camera.start(33) #定时器开始计时33ms，每过33ms从摄像头中取一帧显示 mp4帧率
                self.pushButton.setText(u'暂停考勤')

                #添加人脸识别方法
        else:
            self.timer_camera.stop()
            self.cap.release()
            self.label_show_camera.clear()
            self.pushButton.setText(u'开始考勤')
    def show_camera(self):
        flag, self.image = self.cap.read()
        show1 = cv2.resize(self.image, (640, 480)) # 把读到的帧的大小重新设置为 640x480
        show = cv2.cvtColor(show1, cv2.COLOR_BGR2RGB)# 视频色彩转换回RGB
        gray_image_2 = cv2.cvtColor(show1, cv2.COLOR_BGR2GRAY)

        #差分算法
        d_frame = cv2.absdiff(gray_image_1, gray_image_2)
        d_frame = cv2.GaussianBlur(d_frame, (3, 3), 0)
        ret, d_frame = cv2.threshold(d_frame,10, 255, cv2.THRESH_BINARY)
        kernel = np.ones((10, 10), np.uint8)
        blank=np.zeros((480,640))
        opening = cv2.morphologyEx(d_frame, cv2.MORPH_OPEN, kernel)
        ##对经过开运算的opening提取所在区域
        if not(opening ==blank).all():
            x = 0  # start
            y = 0
            a = 0  # final
            b = 0
            for j in range(640):
                if opening.sum(axis=0)[j] != 0:
                    x = j
                    break
            for j in range(640):
                if opening.sum(axis=0)[639 - j] != 0:
                    y =639 - j
                    break
            for j in range(480):
                if opening.sum(axis=1)[j] != 0:
                    a = j
                    break
            for j in range(480):
                if opening.sum(axis=1)[479 - j] != 0:
                    b = 479 - j
                    break

            gray_image_back = gray_image_2[a:b,x:y]
            cv2.rectangle(show, (x, a), (y, b), (255, 0, 0), 1)
            faces = face_cascade.detectMultiScale(gray_image_back, 1.5, 5) #从灰度读face
            for (m, n, w, h) in faces:
                cv2.rectangle(show, (x + m, a + n), (x + m + w, a + n + h), (0, 255, 0), 2)
                f = cv2.resize(show[a+n:a+n + h, x+m:x+m + w], (92, 112))  #得到人脸并且设置好形状?????与lable符合
                showpic = QtGui.QImage(f.data, f.shape[1], f.shape[0], QtGui.QImage.Format_RGB888)
                self.label_show_pic.setPixmap(QtGui.QPixmap.fromImage(showpic)) #展示人脸
        showImage = QtGui.QImage(show.data, show.shape[1], show.shape[0],
                                 QtGui.QImage.Format_RGB888)  # 把读取到的视频数据变成QImage形式
        self.label_show_camera.setPixmap(QtGui.QPixmap.fromImage(showImage)) # 往显示视频的Label里 显示QImage

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = mywindow()
    window.show()
    sys.exit(app.exec_())
