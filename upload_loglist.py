#! /usr/bin/python
#-*- coding: utf-8 -*-
from ConfigParser import ConfigParser
from suds.client import Client
from suds.xsd.doctor import ImportDoctor,Import
from logging.handlers import RotatingFileHandler
import os,datetime,logging

logging.basicConfig(level=logging.ERROR,
                        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        filename='upload_loglist.log',
                        filemode='w')
#################################################################################################
#定义一个RotatingFileHandler，最多备份2个日志文件，每个日志文件最大5M
Rthandler = RotatingFileHandler('upload_loglist.log', maxBytes=2*1024*1024,backupCount=2)
Rthandler.setLevel(logging.ERROR)
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
Rthandler.setFormatter(formatter)
logging.getLogger('').addHandler(Rthandler)
################################################################################################
global list_poststring

def get_confile(dir_confile):
    up_con = ConfigParser()
    s_curpath = os.getcwd()
    s_confile = s_curpath + "/upload_config.ini"
    if os.path.exists(s_confile):
        with open(s_confile) as fd_con:
            try:
                up_con.readfp(fd_con)
                dir_confile["LOG_PATH"] = up_con.get("FILE","LOG_PATH")
            except IOError as err:
                logging.error(err)
                return -1
        logging.critical('Read Config succeed!')
        return 0
    else:
        logging.error('No upload_config.ini file!')
        return -1

def get_date(s_date):
    t_lastdate = datetime.date.today() - datetime.timedelta(days = 1)
    s_date = t_lastdate.strftime('%Y%m%d')
    return s_date

def get_loglist(dir_confile,set_loglist):
    s_parapath = dir_confile.get('LOG_PATH')
    list_filename = []
    s_date = ""
    s_filename = ""
    if not s_parapath:
        logging.error('No LOG_PATH in Condif.ini')
        return -1
    s_date = get_date(s_date)
    list_filename = os.listdir(s_parapath)
    for s_name in list_filename:
        s_filename = os.path.join(s_parapath,s_name)
        set_loglist.add(os.path.join(s_filename,s_date))
    return 0    

def get_liststring(dir_confile,set_loglist):
    for s_parapath in set_loglist:
        logging.critical(s_parapath)
        if not os.path.exists(s_parapath):
            continue
        para_filepath(dir_confile,s_parapath)

def para_filepath(dir_confile,s_parapath):
    s_slash = '/'
    s_semicolon = ';'
    s_conpath = dir_confile.get('LOG_PATH')
    if cmp(s_conpath[-1],s_slash):
        s_conpath += s_slash
    s_path = s_parapath[len(s_conpath):]

    list_filename = os.listdir(s_parapath)
    for s_filename in list_filename:
        s_postname = s_path + s_slash + s_filename + s_semicolon
        list_poststring.append(s_postname)

def post_data():
    #url='http://118.244.210.37:8080/pushtask/DownloadLogWebService.cis?wsdl'
    url='http://172.17.63.48:8080/pushtask/DownloadLogWebService.cis?wsdl'
    imp = Import('http://bean.cdn.excloud.com')
    imp.filter.add('http://services.spring.excloud.com')
    d = ImportDoctor(imp)
    try:
    	client = Client(url,doctor=d,timeout=20)
    	s_updata = ''.join(list_poststring)
        b_result = client.service.saveDownLoadLog(s_updata)
        if b_result:
            logging.critical('Up_load data succeed!')
            return 0
        else:
            logging.error('Up_load data Error!')
            return -1
    except Exception,ex:
        logging.error(ex)
		return -1

if __name__ == "__main__":
    logging.critical('====================Start Upload====================')
    post_string = ''
    dir_confile = {}
    set_loglist = set()
    if get_confile(dir_confile):
        exit()
    if get_loglist(dir_confile,set_loglist):
        exit()
    list_poststring = []
    get_liststring(dir_confile,set_loglist)
    if post_data():
	post_data()
    dir_confile.clear()
    list_poststring = []
    logging.critical('====================End Upload====================')
    
