import requests
import re


class whuInterface:
    def __init__(self, user, pwd, name):
        self.user = user
        self.pwd = pwd
        self.name = name
        self.id = ''
        self.session = None
        self.sessionID = ''

    def login(self):
        url = "http://metalib.lib.whu.edu.cn/pds"
        d = {'func': 'login', 'calling_system': 'mrbs', 'term1': 'short', 'selfreg': '', 'bor_id': self.user,
             'bor_verification': self.pwd, 'institute': 'WHU',
             'url': 'http://reserv.lib.whu.edu.cn/admin.php?TargetURL=day.php?year=2013&login=1'}
        ret = requests.post(url, d)
        print(ret.text)
        res = re.search("/goto/logon/(.*)=';", ret.text)
        if res is None:
            return 0
        logindata = res.group(0).replace("/goto/logon/", '').replace("';", '')
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0',
            'Host': 'reserv.lib.whu.edu.cn',

        }
        print(logindata)
        self.session = requests.session()
        admin = self.session.get(logindata, headers=headers)
        mrbs_sessid = requests.utils.dict_from_cookiejar(self.session.cookies)['MRBS_SESSID']
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0',
            'Host': 'reserv.lib.whu.edu.cn',
            'cookie': 'MRBS_SESSID=' + mrbs_sessid
        }
        day = self.session.get('http://reserv.lib.whu.edu.cn/day.php?year=2013')
        self.sessionID = mrbs_sessid
        return mrbs_sessid

    def entry_edit(self, hour, month, day, room):
        minute = '00'

        if hour == 8:
            hour = '08'
        if month < 10:
            month = '0' + str(month)
        if day <= 0:
            day = '0' + str(day)
        if hour == 11 or hour == 18:
            minute = '30'

        url = 'http://reserv.lib.whu.edu.cn/edit_entry.php?area=8&room=' + str(room) + '&hour=' + str(
            hour) + '&minute=' + minute + '&year=2022&month='
        url = url + str(month) + '&day=' + str(day)
        returl = url
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0',
            'Host': 'reserv.lib.whu.edu.cn',
            'cookie': 'MRBS_SESSID=' + self.sessionID
        }
        ret = requests.get(url, headers=headers)
        res = """name=\"create_by\" value=\"(.*)\">"""
        #print(ret.text)
        self.id = re.search(res, ret.text).group(0).replace("""name=\"create_by\" value=\"""", "")
        self.id = self.id.replace("""\">""", '')
        print(self.id)
        month = str(month).replace('0', '')
        day = str(day).replace('0', '')
        url = 'http://reserv.lib.whu.edu.cn/edit_entry_handler.php'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0',
            'Host': 'reserv.lib.whu.edu.cn',
            'cookie': 'MRBS_SESSID=' + self.sessionID
        }
        datas = {
            'name': self.name,
            'description': "学习",
            'start_day': str(day),
            'start_month': str(month),
            'start_year': '2022',
            'start_seconds': str(int(hour) * 60 * 60 + int(minute) * 60),
            'all_day': 'no',
            'end_day': str(day),
            'end_month':str(month),
            'end_year': '2022',
            'end_seconds': str(int(hour) * 60 * 60 + int(minute) * 60 + 12600),
            'area': '10',
            'rooms[]': str(room),
            'type': 'I',
            'f_bor_id': self.user,
            'f_entry_tel': '17377747444',
            'f_entry_email': '00000@000.com',
            'f_entry_person1': '',
            'f_entry_person2': '',
            'f_entry_person3': '',
            'returl': returl,
            'create_by': self.id,
            'rep_id': '0',
            'edit_type': 'series'
        }
        print(datas)
        ret = requests.post(url, datas, headers=headers)
