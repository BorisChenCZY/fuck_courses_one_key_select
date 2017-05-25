__ver__ = 'beta 0.1'
__is_test__ = False

import requests
import re
from bs4 import BeautifulSoup
import html
from lxml.html.soupparser import unescape
import json
import time
from selenium import webdriver
import selenium
import PyQt5
from PyQt5 import QtCore, QtGui, uic, QtWidgets
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QTableWidgetSelectionRange, QMessageBox
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow
from PyQt5.QtCore import pyqtSignal
import sys
from functools import partial
import threading
import os

import sys
import untitled
import login_confirm
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog
from multiprocessing import Pool
import time

SERVER_URL = 'http://borischen.me:3000'

if __is_test__:
    SERVER_URL = 'http://localhost:3000'
    import login_confirm_test_only as login_confirm

class SUSTech(object):

    """
    docstring for Sakai,
    this code is to get Sakai page for SUSTC students, they can get necessary
    information such as course slices or assignments from this modual
    """

    def __init__(self, username, password, site):

        """
        to init Sakai, username and password is in need
        """
        self.site = site
        self.headers = {
            "User-Agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3)' +
                          ' AppleWebKit/537.36 (KHTML, like Gecko) Chrome/' +
                          '56.0.2924.87 Safari/537.36'}
        self.data = {
            'username': str(username),
            'password': str(password),
            #     'lt': lt,
            #     'excusion': execution,
            '_eventId': 'submit',
            'submit': 'LOGIN',
        }
        self.url = 'https://cas.sustc.edu.cn/cas/login?service='+site
        self.s = requests.session()
        r = self.s.get(self.url, headers = self.headers)
        content = r.content.decode('utf-8')
        self.data['execution'] = self._get_execution(content)
        self.data['lt'] = self._get_lt(content)
        self.loggedIn = False
        self.topped_sites = {}
        self.other_sites = {}
        self.sites = {}
        self.username = username
        self.password = password

    def _get_execution(self, content):
        formula = '<input.*?name="execution".*?value="(.*?)" />'
        pattern = re.compile(formula)
        return re.findall(pattern, content)[0]

    def _get_lt(self, content):
        formula = '<input.*?name="lt".*?value="(.*?)" />'
        pattern = re.compile(formula)
        return re.findall(pattern, content)[0]

    def login(self):
        self.s.post(self.url, self.data)
        text = self._get_home_page()
        self.loggedIn =  'CAS' not in text
        return self.loggedIn

    def _check_logged(self):
        if not self.loggedIn:
            # print('not logged in, permission denied')
            pass
        return self.loggedIn

    def _get_home_page(self):
        r = self.s.get(self.site)
        text = r.content.decode('utf-8')
        txt = unescape(text)
        return txt

    def get_home_page(self):
        if not self._check_logged():
            return
        return self._get_home_page()

    def get_home_soup(self):
        if not self.loggedIn:
            raise Exception('not logged in yet!')
        r = self.s.get(self.site)
        soup = BeautifulSoup(r.text, 'lxml')
        return soup

    def get_cookies(self):
        return self.s.cookies

    def get_website(self, url, paras = None):
        if not self.loggedIn:
            return 
        r = self.s.get(url, params = paras)
        # print(r.url)
        return r.text

    def post_website(self, url, post_data):
        r = self.s.post(url, data = post_data)
        return r.text

    def get(self, *args):
        return self.get_website(*args)

    def post(self, *args):
        return self.post_website(*args)

class ClassInfo():
    TRANSFORMATION = {
        'skls' : 'teacher',
        'kcmc': 'course_name',
        'kch': 'course_id',
        'dwmc': 'course_major',
        'jx0404id': 'course_selector',
        'sksj': 'course_time'
    }

    NAMES = ['course_name', 'course_id', 'teacher', 'course_major', 'course_time', 'course_selector']

    RE_TRANSFORMATION = dict((v,k) for k, v in TRANSFORMATION.items())

    def __init__(self, databox):
        self.teacher = databox['skls']
        self.course_name = databox['kcmc']
        self.course_id = databox['kch']
        self.course_major = databox['dwmc']
        self.course_selector = databox['jx0404id']
        self.course_time = databox['sksj']
        self.data = databox

        
    def __str__(self):
        s = '课程名：{} 课程号：{} 授课教师：{} 所属院系：{} 课程选择号：{} 上课时间:{}'.format(self.course_name, self.course_id, self.teacher, self.course_major, self.course_selector, self.course_time)
        s = s.replace('None', 'Unknown')
        s = html.unescape(s)
        return s

    def contains(self, text):
        info = str(self).upper()
        all_in = True
        for character in text:
            if character not in info:
                all_in = False
                return False

        return True

    def find(self, text):
        info = str(self)
        return text in info

def search(course_list, text):
    if not course_list:
        return
    text = str(text)
    return_list = []
    text = text.upper()
    for course in course_list:
        if course.contains(text):
            return_list.append(course)
    return return_list

def find(course_list, text):
    if not course_list:
        return
    text = str(text)
    return_list = []
    text = text.upper()
    for course in course_list:
        if course.find(text):
            return_list.append(course)
    return return_list

def get_courses_by_type(sustc, type):

    URL_TO_TYPE = {
        'in_major_courses': 'http://jwxt.sustc.edu.cn/jsxsd/xsxkkc/xsxkKnjxk?kcxx=&skls=&skxq=&skjc=&sfym=false&sfct=false',
        'cross_major_courses': 'http://jwxt.sustc.edu.cn/jsxsd/xsxkkc/xsxkFawxk?kcxx=&skls=&skxq=&skjc=&sfym=false&sfct=false',
        'this_term_courses': 'http://jwxt.sustc.edu.cn/jsxsd/xsxkkc/xsxkBxqjhxk?kcxx=&skls=&skxq=&skjc=&sfym=false&sfct=false',
        'public_courses': 'http://jwxt.sustc.edu.cn/jsxsd/xsxkkc/xsxkGgxxkxk?kcxx=&skls=&skxq=&skjc=&sfym=false&sfct=false&szjylb=',
    }

    url = URL_TO_TYPE[type]
    post_data = {
        'sEcho': 1,
        'iColumns':1,
        'sColumns': None ,
        'iDisplayStart':0,
        'iDisplayLength':1000,
        'mDataProp_0':'kch', # 课程号
        'mDataProp_1':'kcmc', # 课程名
        'mDataProp_2':'xf', # 学分
        'mDataProp_3':'skls', # 上课老师
        'mDataProp_4':'sksj', # 上课时间
        'mDataProp_5':'skdd', # 上课地点
        'mDataProp_6':'xkrs', #
        'mDataProp_7':'syrs', # 剩余量
        'mDataProp_8':'ctsm', # 时间冲突
        'mDataProp_9':'czOper', # 操作
    }

    data = json.loads(sustc.post_website(url, post_data))
    cross_major_course_list = []
    for dict_ in data['aaData']:
        # print(dict_)
        cross_major_course_list.append(ClassInfo(dict_))
    return cross_major_course_list


def _select_course(sustc, course_selector):
    reconnect(sustc)
    jx0404id = course_selector
    xkzy = ''
    trjf = ''
    post_data = {
        'jx0404id': jx0404id,
        'xkzy': xkzy,
        'trjf': trjf,
    }
    return (sustc.get_website('http://jwxt.sustc.edu.cn/jsxsd/xsxkkc/fawxkOper', post_data))

def try_to_select(self, course_selector):
    selecor = course_selector
    sustc = self.sustc
    # select_resutl = self.pool.apply_async(_select_course, args=(sustc, course_selector))
    # info = select_resutl.get()
    info = _select_course(sustc, course_selector)
    info = (json.loads(info))

    if info['success']:
        g(self, '成功选上：{} '.format(find(self.courses['all'], selecor)[0].course_name))
    elif '登陆' in info['message']:
        reconnect(self.sustc)
        try_to_select(self, course_selector)
    else:
        add_log(self, '{} {}'.format(find(self.courses['all'], selecor)[0].course_name, info['message']))


def dis_select(sustc, course_selector):
    return (sustc.get_website('http://jwxt.sustc.edu.cn/jsxsd/xsxkjg/xstkOper', {'jx0404id': course_selector}))

def get_selected_course_selector(sustc):
    text = sustc.get('http://jwxt.sustc.edu.cn/jsxsd/xsxkjg/comeXkjglb')
    soup = BeautifulSoup(text, 'lxml')
    tbody = soup.find('tbody')
    trs = tbody.find_all('tr')
    selected_courses_selector = []
    for tr in trs:
        tds = tr.find_all('td')
        formula = '\d+'
        pattern = re.compile(formula)
        jx0404id = (re.search(pattern, tds[-1].a['href']).group())
        selected_courses_selector.append(jx0404id)
    return selected_courses_selector

def get_all_courses(sustc):
    #专业内选课
    in_major_courses = get_courses_by_type(sustc, 'in_major_courses')
    print('hello world')
    #跨专业选课
    cross_major_courses = get_courses_by_type(sustc, 'cross_major_courses')

    #本学期选课计划
    this_term_courses = get_courses_by_type(sustc, 'this_term_courses')

    #公选课计划
    public_courses = get_courses_by_type(sustc, 'public_courses')

    #所有课
    all = in_major_courses + cross_major_courses + this_term_courses + public_courses

    #已选课程
    selecors = get_selected_course_selector(sustc)

    selected = []
    for selecor in selecors:
        selected += find(all, selecor)

    return {'in_major_courses': in_major_courses,
            'cross_major_courses': cross_major_courses,
            'this_term_courses': this_term_courses,
            'public_courses': public_courses,
            'all': all,
            'selected': selected,
            }

def Content_Linker(self, sustc):

    # note that copy code from here

    self.sustc = sustc
    self.courses = {}
    self.display_courses = []
    get_filter(self, None)
    self.pool = Pool(10)

    # self.this_term_courses_Button.clicked.connect(show_this_term_courses)
    self.this_term_courses_Button.clicked.connect(partial(show_courses, self, 'this_term_courses', '本学期选课'))
    self.cross_marjor_courses_Button.clicked.connect(partial(show_courses, self, 'cross_major_courses', '跨专业选课选课'))
    self.in_marjor_courses_Button.clicked.connect(partial(show_courses, self, 'in_major_courses', '专业内选课'))
    self.public_courses_Button.clicked.connect(partial(show_courses, self, 'public_courses', '公选课选课'))
    self.all_courses_Button.clicked.connect(partial(show_courses, self, 'all', '所有课程'))
    self.selected_courses_Button.clicked.connect(partial(show_courses, self, 'selected', '已选课程'))
    self.add_Button.clicked.connect(partial(add_courses_to_operator, self))
    self.delete_Button.clicked.connect(partial(remove_courses_from_operator, self))
    self.choose_Button.clicked.connect(partial(fuck_courses, self))
    self.unchoose_Button.clicked.connect(partial(dis_select_courses_from_table, self))
    self.selected_table.setStyleSheet("background-color: white")
    self.log_textEdit.setStyleSheet("background-color: white")
    self.log_textEdit.setStyleSheet("color: black")
    self.content_table.setStyleSheet("background-color: white")
    self.content_table.cellDoubleClicked.connect(partial(add_courses_to_operator, self))
    self.selected_table.cellDoubleClicked.connect(partial(remove_courses_from_operator, self))
    self.version_label.setText('ver: {}'.format(__ver__))
    # help(self.public_courses_Button.clicked.connect)

    self.search_lineEdit.textChanged.connect(partial(get_filter, self, self.search_lineEdit.text))

    self.select_action.triggered.connect(partial(fuck_courses, self))
    self.dis_select_action.triggered.connect(partial(dis_select_courses_from_table, self))
    self.select_to_death_Button.clicked.connect(partial(fuck_to_death, self))


def fuck_to_death(self):
    # def _helper_function():
    #     pass
    #
    # self.creazy_select_thread = threading(traget= _helper_function, args = ())
    # self.creazy_select_thread.start()
    for i in range(10):
        fuck_courses(self)


def Login_Linker(self, DialogWindow):
    # self.showEvent.connect(partial(check_network, self))
    # self.closeEvent.connect(partial(check_logged_in, self))
    self.login_Button.clicked.connect(partial(login_to_server, self, DialogWindow))
    # (connected_to_internet, connected_to_server) = check_newwork(self)

def login_to_server(self, DialogWindow):
    login_to_server.LoggedIn = pyqtSignal()
    if not self.connected:
        self.warn_label.setText('Not connected to Internet or server!')
        return
    information =  {
        "username" : self.username_lineEdit.text(),
        "password" : self.password_lineEdit.text(),
        "token" : self.token_lineEdit.text(),
    }
    r = requests.post(SERVER_URL, data = information)
    if (r.text == 'true'):
        self.permission = True
    else:
        self.warn_label.setText('Wrong taken, contact author if you have permission')
        return

    self.sustc = SUSTech(information['username'], information['password'], 'http://jwxt.sustc.edu.cn/jsxsd')
    if self.sustc.login():
        self.loggedIn = True
        DialogWindow.close()
    else:
        self.loggedIn = False
        self.warn_label.setText('Wrong password')

def check_network():
    # self.sustc = None
    connected_to_internet = False
    connected_to_server = False
    try:
        r = requests.get('http://www.baidu.com', timeout = 1)
        text = (r.content.decode('utf-8'))
        if '百度' in  text:
            connected_to_internet = True
    except Exception:
        connected_to_internet = False

    try:
        r = requests.get(SERVER_URL, timeout = 1)
        # print(r)
        # print(r.status_code)
        if r.status_code == 200:
            connected_to_server = True
    except Exception:
        connected_to_server = False

    return (connected_to_internet, connected_to_server)

def check_logged_in(self):
    return self.sustc

# to change!
def dis_select_courses_from_table(self):
    add_courses_to_operator(self)
    selectors = []
    Y = ClassInfo.NAMES.index('course_selector')
    for X in range(self.selected_table.rowCount()):
        selectors.append(self.selected_table.item(X, Y).text())

    for selecor in selectors:
        info = (self, dis_select(self.sustc, selecor))[1]
        info = (json.loads(info))
        if info['success']:
            add_log(self, '成功退选：{} '.format(find(self.courses['all'], selecor)[0].course_name))
        else:
            add_log(self, '{} {}'.format(find(self.courses['all'], selecor)[0].course_name, info['message']))
    self.courses = get_all_courses(self.sustc)
    show_courses(self, 'selected', '已选课程')

def fuck_courses(self):
    reconnect(self.sustc)
    add_courses_to_operator(self)

    selectors = []
    Y = ClassInfo.NAMES.index('course_selector')
    for X in range(self.selected_table.rowCount()):
        selectors.append(self.selected_table.item(X, Y).text())

    for selecor in selectors:

        info = try_to_select(self, selecor)


    self.courses = get_all_courses(self.sustc)

    show_courses(self, 'selected', '已选课程')

def remove_courses_from_operator(self):
    ranges = (self.selected_table.selectedRanges())
    rows = set()
    for range_ in ranges:
        bottom_row = range_.bottomRow()
        top_row = range_.topRow()
        rows = rows.union(set([x for x in range(top_row, bottom_row + 1)]))
    rows = sorted(list(rows), reverse = True)
    for row in rows:
        self.selected_table.removeRow(row)

def add_courses_to_operator(self):
    ranges = (self.content_table.selectedRanges())

    rows = set()
    for range_ in ranges:
        bottom_row = range_.bottomRow()
        top_row = range_.topRow()
        rows = rows.union(set([x for x in range(top_row, bottom_row + 1)]))
        self.content_table.setRangeSelected(range_, False)

    #copy a row
    self.selected_table.setColumnCount(self.content_table.columnCount())
    self.selected_table.setHorizontalHeaderLabels(ClassInfo.NAMES)
    for X in rows:
        selected_row = self.selected_table.rowCount()
        self.selected_table.insertRow(selected_row)
        for Y in range(self.content_table.columnCount()):
            self.selected_table.setItem(selected_row, Y, QTableWidgetItem(self.content_table.item(X, Y)))


def show_courses(self, key, label):
    # key = 'this_term_courses'
    if not self.courses:
        self.courses = get_all_courses(self.sustc)
    self.display_courses = self.courses[key]
    set_tables(self,  self.display_courses)
    self.status_label.setText('{}:'.format(label))


def get_filter(self, text):
    if not text:
        text = ""
    else:
        text = text()
    def filter(information):
        filter.text = text
        # add_log(self, 'filter state:{}'.format(text))
        if not text or text == "":
            return information

        return search(information, text)
    self.filter = filter
    # print(self.display_courses)
    set_tables(self, self.display_courses)
    return filter

def set_tables(self, informations):

    names = ClassInfo.NAMES
    self.content_table.clear()
    self.content_table.setColumnCount(len(names))
    informations = self.filter(informations)
    if not informations:
        informations = []
    self.content_table.setRowCount(len(informations))
    self.content_table.setHorizontalHeaderLabels(ClassInfo.NAMES)

    X = 0
    for item in informations:
        Y = 0
        for name in names:
            self.content_table.setItem(X, Y, QTableWidgetItem(item.data[ClassInfo.RE_TRANSFORMATION[name]]))
            Y += 1
        X += 1

def add_log(self, information):
    self.log_textEdit.append('[{:<8}] '.format(time.strftime('%H:%M:%S', time.localtime())) + information)

class MyDialog(QDialog):
    onShow = pyqtSignal()
    onQuit = pyqtSignal()
    def __init__(self, parent=None):
        super(MyDialog, self).__init__(parent)

        # when you want to destroy the dialog set this to True
        # self._want_to_close = False

    def closeEvent(self, evnt):
        self.onQuit.emit()

    def showEvent(self, QShowEvent):
        self.onShow.emit()

def onshow_preparation(self):
    p = threading.Thread(target= _onshow_preparation, args=(self, ))
    p.start()

def _onshow_preparation(self):
    (connected_to_internet, connected_to_server) = check_network()
    self.sustc = None
    self.connected = False
    self.permission = False
    self.loggedIn = False
    self.status_label.setStyleSheet('color:red')
    self.warn_label.setStyleSheet('color:red')
    if not connected_to_internet:
        self.status_label.setText('Not connected to internet')
    elif not connected_to_server:
        self.status_label.setText('Failed to connected to verify server. Please contact the author.')
    else:
        self.status_label.setStyleSheet('color:green')
        self.status_label.setText('Connected')
        self.connected = True

def close_dialog(self):
    DialogWindow.close()

def onQuit_judge(ui_dialog, ui, app, qapplication):
    if ui_dialog.loggedIn:
        ui.sustc = ui_dialog.sustc
        Content_Linker(ui, ui.sustc)
        reconnect(ui.sustc)
        ui.connected = True
        p = threading.Thread(target=_check_network_when_working, args=(qapplication, ui))

        p.start()
    else:
        sys.exit(app.exec_())

def _check_network_when_working(app, self):
    def helper_insider():
        a, connected_to_server = check_network()
        # print(a, b)
        if not connected_to_server :
            # ui.setEnabled(False)
            if self.connected:
                messageBox = QMessageBox()
                messageBox.setText(
                    'Cannot connect to the server of Internet! If RR Internet connection is stable, please contant the author.')
                messageBox.setIcon(QMessageBox.Critical)
                revel = messageBox.exec_()
                app.setEnabled(False)
                self.connected = False
        else:
            if not self.connected:
                self.connected = True
                messageBox = QMessageBox()
                messageBox.setText(
                    'Reconnected')
                messageBox.setIcon(QMessageBox.Information)
                revel = messageBox.exec_()
                app.setEnabled(True)
            # time.sleep(10000000000)

    while self.connected:
        helper_insider()

def reconnect(sustc):
    return(sustc.get_website('http://jwxt.sustc.edu.cn/jsxsd/xsxk/xsxk_index?jx0502zbid=2A018810EA3C4DCFAD5A971752AD1A0D'))

if __name__ == '__main__':
    # sustc = SUSTech(11510237, 310034, 'http://jwxt.sustc.edu.cn/jsxsd')
    # sustc.login()



    app = QApplication(sys.argv)
    DialogWindow = MyDialog()
    MainWindow = QMainWindow()
    ui = untitled.Ui_MainWindow()
    ui_dialog = login_confirm.Ui_Dialog()
    ui_dialog.setupUi(DialogWindow)
    Login_Linker(ui_dialog, DialogWindow)

    #Link dialog window itself
    DialogWindow.onShow.connect(partial(onshow_preparation, ui_dialog))
    DialogWindow.onQuit.connect(partial(onQuit_judge, ui_dialog, ui, app, MainWindow))

    # ui_dialog.exec_()
    ui.setupUi(MainWindow)

    MainWindow.show()



    # MainWindow.setDisabled(True)
    DialogWindow.setWindowFlags(DialogWindow.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
    DialogWindow.show()
    # window.setWindowFlags(window.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
    sys.exit(app.exec_())
