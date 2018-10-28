# -*- coding:utf-8 -*-
import os
import json
import logging
import datetime

from PyPDF2 import PdfFileReader, PdfFileWriter
from wand.image import Image

CUT_PAGE_NUM = 9
TEMP_DIR = './.tmp/'
SOURCE_DIR = './mypdf/'
OUT_DIR = './outfile/'
LOG_DIR_PATH = './.log/'
IMG_SUFFIX = '.jpg'

settings = json.loads(open("./config/config.json", 'r').read())

LOG_FORMAT = "%(asctime)s %(levelname)s: %(pathname)s:%(lineno)d - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# log
log_file = LOG_DIR_PATH + datetime.datetime.strftime(datetime.date.today(), "%Y-%m-%d")
logging.basicConfig(level=logging.DEBUG, filename=log_file, format=LOG_FORMAT, datefmt=DATE_FORMAT)


class PDFConvert():

    def __init__(self, filepath):
        self.source_path = filepath
        self.fullname = filepath.split('/')[-1]
        self.filename = self.fullname.split('.')[0]
        self.tmp_path = "%s%s/" % (settings['TEMP_DIR'], self.filename)
        self.out_path = "%s%s/" % (settings['OUT_DIR'], self.filename)
        self.img_type = settings['IMG_SUFFIX'].replace(".", "")
        self.img_out_path = "%s%s/" % (self.out_path, self.img_type)

        if not os.path.exists(self.tmp_path):
            os.mkdir(self.tmp_path)
        if not os.path.exists(self.out_path):
            os.mkdir(self.out_path)

    def cut(self, start_page=None, end_page=None, type=1):
        # PyPDF2 对象
        pdf_reader = PdfFileReader(self.source_path)
        # 获取pdf的总页数
        page_num = pdf_reader.getNumPages()

        CUT_PAGE_NUM = int(settings['CUT_PAGE_NUM']) if start_page == None and end_page == None else (1 if type == 1 else 100000)
        real_star_page = 0 if start_page == None else start_page - 1
        real_end_page = page_num if end_page == None else end_page - 1

        for x in range(real_star_page, real_end_page, CUT_PAGE_NUM):

            tmp_end_page = x + CUT_PAGE_NUM if x + CUT_PAGE_NUM < real_end_page else real_end_page
            logging.info("Cuting：%s [%s-%s]" % (self.filename, x, real_end_page))

            # 创建写入pdf的对象
            pdf_writer = PdfFileWriter()
            # 循环写入
            for index in range(x, tmp_end_page):
                pageObj = pdf_reader.getPage(index)
                pdf_writer.addPage(pageObj)

            if start_page == None and end_page == None:
                cut_fullpath = self.tmp_path + '%s[%s-%s].pdf' % (self.filename, x + 1, tmp_end_page)
            elif type != 1:
                cut_fullpath = self.out_path + '%s[%s-%s].pdf' % (self.filename, x + 1, tmp_end_page)
            else:
                cut_fullpath = self.out_path + '%s[%s].pdf' % (self.filename, x + 1)
            # 保存为文件
            pdf_writer.write(open(cut_fullpath, 'wb'))

        if start_page == None and end_page == None:
            return

    def convert_to_img(self, filepath=None, type=1):
        if not os.path.exists(self.img_out_path):
            os.mkdir(self.img_out_path)

        if filepath == None:
            filepath = self.source_path
            type = 0

        image_pdf = Image(filename=filepath, resolution=300)
        image = image_pdf.convert(self.img_type)

        page = int(filepath[filepath.rindex('[') + 1:filepath.rindex(']')].split("-")[0]) if type == 1 else 1

        for img in image.sequence:
            completefilename = "%s%s[%s]%s" % (self.img_out_path, self.filename, str(page), settings['IMG_SUFFIX'])
            img_page = Image(image=img)
            self.save_img(img_page.make_blob(self.img_type), completefilename)
            page += 1

    # 单张保存为图片
    def save_img(self, source, completefilename):
        with open(completefilename, 'wb') as file:
            file.write(source)
        logging.info('Saved： %s' % completefilename)
