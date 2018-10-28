import sys
import os
import json
from multiprocessing.dummy import Pool as ThreadPool

from PyQt5.QtWidgets import QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QApplication, QFileDialog, QLabel, \
    QLineEdit, QMainWindow
from PyQt5 import QtGui
from PyQt5.QtCore import QUrl

from Utils.pdf_to_img import PDFConvert

settings = json.loads(open("./config/config.json", 'r').read())


class PDFTool(QMainWindow):

    def __init__(self):
        super().__init__()

        # 创建日志文件夹

        if not os.path.exists(settings['LOG_DIR_PATH']):
            os.mkdir(settings['LOG_DIR_PATH'])
        # 创建缓存文件夹
        if not os.path.exists(settings['TEMP_DIR']):
            os.mkdir(settings['TEMP_DIR'])
        # 创建输出文件夹
        if not os.path.exists(settings['OUT_DIR']):
            os.mkdir(settings['OUT_DIR'])

        self.sc_out_dir = settings['OUT_DIR']

        self.initUI()

    def initUI(self):
        self.statusBar().showMessage('就绪~')

        # 文本框
        # title_convert =  QLabel(" PDF 转图片：")
        sc_text = QLabel("PDF 转图片：")
        bc_text = QLabel("PDF 转图片(批量)：")
        cut_text = QLabel("PDF 截取：")

        # Edit text
        self.cut_start_edit_text = QLineEdit()
        self.cut_start_edit_text.setPlaceholderText("请输出启始页码：")
        self.cut_end_edit_text = QLineEdit()
        self.cut_end_edit_text.setPlaceholderText("请输出终止页码：")

        # 按钮 button
        # single convert
        sc_selectdir_button = QPushButton("选择文件")
        sc_selectdir_button.clicked.connect(self.select_files_Clicked)
        sc_exe_button = QPushButton("执行")
        sc_exe_button.clicked.connect(self.convert_exe_Clicked)
        sc_open_outdir_button = QPushButton("打开输出文件夹")
        sc_open_outdir_button.clicked.connect(self.open_outfile_Clicked)

        # batch convert
        bc_selectdir_button = QPushButton("选择文件夹")
        bc_selectdir_button.clicked.connect(self.select_dir_Clicked)
        bc_exe_button = QPushButton("执行")
        bc_exe_button.clicked.connect(self.convert_exe_Clicked)
        bc_open_outdir_button = QPushButton("打开输出文件夹")
        bc_open_outdir_button.clicked.connect(self.open_outfile_Clicked)

        # cut
        cut_selectfile_button = QPushButton("选择文件")
        cut_selectfile_button.clicked.connect(self.select_file_Clicked)
        cut_exe_button = QPushButton("执行")
        cut_exe_button.clicked.connect(self.cut_exe_Clicked)
        cut_open_outdir_button = QPushButton("打开输出文件夹")
        cut_open_outdir_button.clicked.connect(self.open_outfile_Clicked)

        # 行布局
        # single convert
        sc_line = QHBoxLayout()
        sc_line.addWidget(sc_text)
        sc_line.addWidget(sc_selectdir_button)
        sc_line.addWidget(sc_exe_button)
        sc_line.addWidget(sc_open_outdir_button)

        # batch convert
        bc_line = QHBoxLayout()
        bc_line.addWidget(bc_text)
        bc_line.addWidget(bc_selectdir_button)
        bc_line.addWidget(bc_exe_button)
        bc_line.addWidget(bc_open_outdir_button)

        # cut
        cut_line = QHBoxLayout()
        cut_line.addWidget(cut_text)
        cut_line.addWidget(cut_selectfile_button)
        cut_line.addWidget(self.cut_start_edit_text)
        cut_line.addWidget(self.cut_end_edit_text)
        cut_line2 = QHBoxLayout()
        cut_line2.addWidget(cut_exe_button)
        cut_line2.addWidget(cut_open_outdir_button)

        # 列布局
        vbox = QVBoxLayout()
        vbox.addLayout(sc_line)
        vbox.addLayout(bc_line)
        vbox.addLayout(cut_line)
        vbox.addLayout(cut_line2)
        vbox.addStretch(1)

        # 放置到 QMainWindow 中的QWidget
        centrawidget = QWidget()
        centrawidget.setLayout(vbox)
        self.setCentralWidget(centrawidget)

        self.setGeometry(600, 300, 600, 400)
        self.setWindowTitle('PDF Tools')
        self.show()

    # button 事件
    # 选择多文件
    def select_files_Clicked(self):
        self.convert_files_path = QFileDialog.getOpenFileNames(self, '选取 PDF', settings['SOURCE_DIR'])[0]
        filenames_str = "、".join([x.split("/")[-1] for x in self.convert_files_path])
        self.statusBar().showMessage("已经选中文件：%s" % filenames_str)

    # 选择文件夹
    def select_dir_Clicked(self):
        """
        :return: list
        """
        dir_path = QFileDialog.getExistingDirectory(self, '文件夹选取', settings['SOURCE_DIR'])
        self.convert_files_path = []
        for x in os.listdir(dir_path):
            if x[-4:].lower() == ".pdf":
                self.convert_files_path.append('%s/%s' % (dir_path, x))

    # 执行方法
    # pdf 转换图片
    def convert_exe_Clicked(self):
        self.statusBar().showMessage("处理过程中~~~")
        import time

        time.sleep(1)
        # 创建线程池
        file_num = len(self.convert_files_path)
        processes = file_num if file_num < 4 else 4
        threadpool = ThreadPool(processes=processes)

        for filepath in self.convert_files_path:
            convert = PDFConvert(filepath)
            convert.cut()
            for filename in os.listdir(convert.tmp_path):
                path = convert.tmp_path + filename
                threadpool.apply_async(convert.convert_to_img, (path,))

        # 关闭池，不许再添加线程
        threadpool.close()

        # 等待所有子线程执行结束
        threadpool.join()
        self.statusBar().showMessage("处理完成~~~")

    # cut
    def select_file_Clicked(self):
        self.cut_file_path = QFileDialog.getOpenFileName(self, "选取 PDF 文件", settings["SOURCE_DIR"])[0]

    def cut_exe_Clicked(self):
        file_path = self.cut_file_path
        cuter = PDFConvert(file_path)
        try:
            start_page = int(self.cut_start_edit_text.text())
            end_page = int(self.cut_end_edit_text.text()) + 1
        except:
            self.statusBar().showMessage("起始页 或 终止页输入错误")
        else:
            cuter.cut(start_page=start_page, end_page=end_page, type=2)
            self.statusBar().showMessage("PDF 截取完成:%s" % file_path.split('/')[-1])

    # 打开输出文件夹
    def open_outfile_Clicked(self):
        path = 'file:%s%s' % (os.getcwd(), self.sc_out_dir[1:])
        QtGui.QDesktopServices.openUrl(QUrl(path))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = PDFTool()
    sys.exit(app.exec_())
