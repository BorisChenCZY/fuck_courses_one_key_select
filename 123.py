from GUI_fuck_courses import *
from lxml.html.soupparser import unescape


sustc = SUSTech(11510237, 310034, 'http://jwxt.sustc.edu.cn/jsxsd')
sustc.login()
reconnect(sustc)
a = get_courses_by_type(sustc, 'http://jwxt.sustc.edu.cn/jsxsd/xsxkkc/xsxkKnjxk?kcxx=&skls=&skxq=&skjc=&sfym=false&sfct=false')
# print(unescape(a.decode('utf-8')))