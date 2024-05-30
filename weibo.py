import os
import sys
import time
import wget
import json
import sqlite3
import configparser
from bs4 import BeautifulSoup
from requests_html import HTMLSession

WEIBO_ID = os.environ.get("WEIBO_ID")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

class Weibo:

    def plog(self,content):
        print('{} {}'.format(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time())), content))

    def __init__(self):

        self.BASE_DIR = os.path.split(os.path.realpath(__file__))[0]
        config = configparser.ConfigParser()
        config.read(os.path.join(self.BASE_DIR, 'config.ini'), encoding='utf-8')

        # 存储环境变量到类属性中
        self.WEIBO_ID = os.environ.get("WEIBO_ID")
        self.TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
        self.TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

        self.SESSION = HTMLSession()
        self.SESSION.adapters.DEFAULT_RETRIES = 5  # 增加重连次数
        self.SESSION.keep_alive = False  # 关闭多余连接
        proxy = config.get("CONFIG", "PROXY")
        self.PROXIES = {"http": proxy, "https": proxy}

    def send_telegram_message(self, text, weibo_link):
        """
        給電報發送文字消息
        """
        headers = {
            'Content-Type': 'application/json',
        }
        data = f'{{"chat_id":"{self.TELEGRAM_CHAT_ID}", "text":"{text}", "reply_markup": {{"inline_keyboard":' \
               f' [[{{"text":"🔗點擊查看原微博", "url":"{weibo_link}"}}]]}}}} '
        url = f'https://api.telegram.org/bot{self.TELEGRAM_BOT_TOKEN}/sendMessage'
        try:
            self.SESSION.post(url, headers=headers, data=data.encode('utf-8'), proxies=self.PROXIES)
        except:
            print('    |-網絡代理錯誤，請檢查確認後關閉本程序重試')
            time.sleep(99999)

    def send_telegram_photo(self, img_url):
        """
        給電報發送圖片
        """
        url = f'https://api.telegram.org/bot{self.TELEGRAM_BOT_TOKEN}/sendPhoto'
        data = dict(chat_id=f"{self.TELEGRAM_CHAT_ID}&", photo=img_url)

        self.SESSION.post(url, data=data, proxies=self.PROXIES)

    def send_telegram_photos(self, pics):
        url = f'https://api.telegram.org/bot{self.TELEGRAM_BOT_TOKEN}/sendMediaGroup'
        params = {
            'chat_id': self.TELEGRAM_CHAT_ID,
            'media': [],
        }
        for pic in pics:
            params['media'].append({'type': 'photo', 'media': pic})
        params['media'] = json.dumps(params['media'])
        result = self.SESSION.post(url, data=params, proxies=self.PROXIES)
        if result.status_code != 200: # 如果分組發送失敗 則單獨發送圖片
            for pic in pics:
                self.send_telegram_photo(pic)

class WeiboHandler:
    def __init__(self, base_dir):
        self.BASE_DIR = base_dir
        self.json_file_path = os.path.join(self.BASE_DIR, 'weibo.json')

        # 如果JSON文件不存在，创建一个空的JSON文件
        if not os.path.exists(self.json_file_path):
            with open(self.json_file_path, 'w') as f:
                json.dump({"weibo": []}, f)

    def send_telegram_message(self, message, link):
        # 你的发送Telegram消息的实现
        print(f"Send message: {message} with link: {link}")

    def send_telegram_photo(self, photo):
        # 你的发送单张Telegram图片的实现
        print(f"Send photo: {photo}")

    def send_telegram_photos(self, photos):
        # 你的发送多张Telegram图片的实现
        print(f"Send photos: {photos}")

    def parse_weibo(self, weibo):
        """
        检查当前微博是否已处理过，如果没处理过则发送博文以及配图到Telegram
        """
        with open(self.json_file_path, 'r') as f:
            data = json.load(f)

        # 检查微博是否已处理过
        if not any(entry['link'] == weibo['link'] for entry in data['weibo']):
            self.send_telegram_message(
                '{}@{}:{}'.format(
                    f"[{len(weibo['pics'])}图] " if weibo['pics'] else '',
                    weibo['nickname'],
                    weibo['title'],
                ),
                weibo['link']
            )

            # 把图片URL发送到Telegram中，可以第一时间在Telegram中收到推送
            pics = weibo['pics']
            if len(pics) > 0:
                if len(pics) <= 2:  # 如果配图少于2张，则一张一张独立发送
                    for pic in pics:
                        self.send_telegram_photo(pic)
                elif len(pics) > 10:  # 如果配图多于10张，则分2组发送
                    self.send_telegram_photos(pics[0: int(len(pics) / 2)])
                    self.send_telegram_photos(pics[int(len(pics) / 2):])
                else:
                    self.send_telegram_photos(pics)

            # 配图发送到Telegram后，将配图独立保存到本地一份
            for pic in weibo['pics']:
                filename = pic.split('/')[-1].split('?')[0]
                filename = os.path.join(self.BASE_DIR, 'images', filename)
                wget.download(pic, out=filename)

            # 更新JSON文件，记录新的微博
            data['weibo'].append({
                'summary': weibo['title'],
                'link': weibo['link']
            })
            with open(self.json_file_path, 'w') as f:
                json.dump(data, f, indent=2)

            return True
        else:
            return False

    def test(self):
        print('* 正在檢查微博ID是否配置正確')
        url = f'https://m.weibo.cn/api/container/getIndex?containerid=100505{self.WEIBO_ID}'
        try:
            weibo_name = self.SESSION.get(url).json()['data']['userInfo']['screen_name']
            print(f'【正確】當前設置的微博賬戶為：@{weibo_name}')
        except:
            print('【錯誤】請重新測試或檢查微博數字ID是否正確')

        print('\n* 正在檢查代理是否配置正確')
        try:
            status_code = self.SESSION.get('https://www.google.com',proxies=self.PROXIES, timeout=5).status_code
            if status_code == 200:
                print('【正確】代理配置正確，可正常訪問')
            else:
                print('【錯誤】代理無法訪問到電報服務器')
        except:
            print('【錯誤】代理無法訪問到電報服務器')

    def get_weibo_detail(self, bid):
        url = f'https://m.weibo.cn/statuses/show?id={bid}'
        detail = self.SESSION.get(url).json()
        weibo = {}
        weibo['title'] = BeautifulSoup(detail['data']['text'].replace('<br />', '\n'), 'html.parser').get_text()
        weibo['nickname'] = detail['data']['user']['screen_name']
        weibo_id = detail['data']['user']['id']
        weibo['pics'] = []
        if 'pics' in detail['data']: # 判斷博文中是否有配圖，如果有配圖則做解析
            weibo['pics'] = [pic['large']['url'] for pic in detail['data']['pics']]
        weibo['link'] = self.get_pc_url(weibo_id, bid)
        self.parse_weibo(weibo)

    def get_pc_url(self, weibo_id, bid):
        return 'https://weibo.com/{weibo_id}/{uri}'.format(
            weibo_id = weibo_id,
            uri = bid
        )

if __name__ == '__main__':
    weibo = Weibo()
    argv = sys.argv[1] if len(sys.argv) > 1 else ''
    if argv.lower() == 'test':
        weibo.test()
    else:
        weibo.run()
