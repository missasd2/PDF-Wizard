# -*- coding:utf-8 -*-
import os
import json


set  = json.loads(open("config.json", 'r').read())

class Settings():

    def __init__(self):
        s = os.getcwd()
        print(s)
        # settings = json.loads(open("config.json", 'r').read())

        self.SOURCE_DIR = set['SOURCE_DIR']
        self.TEMP_DIR =  set['TEMP_DIR']
        self.LOG_DIR_PATH =  set['LOG_DIR_PATH']
        self.OUT_DIR =  set['OUT_DIR']
        self.CONVERT_SUFFIX =  set['CONVERT_SUFFIX']


if __name__ == "__main__":
    s = os.getcwd()
    print(s)
    settings  = json.loads(open("config.json", 'r').read())
