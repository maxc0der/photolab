import requests
import storage
from http.cookies import SimpleCookie
import json
import time
import logging
from logging import StreamHandler, FileHandler, Formatter
import sys
logging.basicConfig(filename='log.log', filemode='a', format='%(asctime)s - %(message)s', datefmt='%H:%M:%S')
logger = logging.getLogger('logger')
logger.setLevel(logging.DEBUG)
handler = StreamHandler(stream=sys.stdout)
logger.addHandler(handler)


class Worker:
    def __init__(self, in_path, out_path=None):
        session = requests.session()
        session.headers['User-agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15'
        session.headers['Referer'] = 'https://photolab.me/r/eeRAWgQ'
        session.headers['Accept'] = '*/*'
        session.headers['Accept-Encoding'] = 'gzip, deflate, br'
        session.headers['Accept-Language'] = 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7'
        session.headers['Host'] = 'photolab.me'
        session.headers['Pragma'] = 'no-cache'
        session.headers['sec-ch-ua'] = '"Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"'
        session.headers['sec-ch-ua-mobile'] = '?0'
        session.headers['sec-ch-ua-platform'] = '"Windows"'
        session.headers['Sec-Fetch-Dest'] = 'empty'
        session.headers['Sec-Fetch-Mode'] = 'cors'
        session.headers['Sec-Fetch-Site'] = 'same-origin'
        session.headers['X-Requested-With'] = 'XMLHttpRequest'
        proxy = storage.get_random_proxy()
#ви        print(proxy)
        session.proxies = {'https': 'http://' + proxy, 'http': 'http://' + proxy}
        self.in_path = in_path
        self.out_path = out_path
        self.session = session
        self.cookies = None
        self.status = 'Initialized'
        logger.debug(f'{self.in_path} {self.out_path} {self.status} {proxy}')
        self.csrf = None
        self.parse_cookies()

    def upload_photo(self):
        try:
            self.status = 'Uploading photo'
            logger.debug(f'{self.in_path} {self.out_path} {self.status}')
            url = 'https://photolab.me/upload'
            fp = open(self.in_path, 'rb')
            files = {'file': fp}
            img_url = self.session.post(url, files=files).text
            fp.close()
            logger.debug(f'{self.in_path} {self.out_path} Uploaded: {img_url}')
            return img_url
        except Exception as e:
            print(e)
            return False

    def parse_cookies(self):
        csrf = requests.utils.quote(
            '_F1a1oXQ4qjvXsP-GghNjIaneX-zTH3aaZd5hJWhTbfDK_FznG2q9n0SWW2ZDBTCDOYTOYLSgPABEwA2kxX-hA==')
        cookies_source = 'sess=8pr6cru31dhtqhfanisb5spohb; device_f_1034742850=de333f18371f546030abff98cf8bf5374537e732134f8b89dbcd416022422630a%3A2%3A%7Bi%3A0%3Bs%3A19%3A%22device_f_1034742850%22%3Bi%3A1%3Bi%3A1%3B%7D; _csrf=ded9d7e7305a45a8b911fc29d9d86757c1192e06ce0a88b53cf07ccf1aff2380a%3A2%3A%7Bi%3A0%3Bs%3A5%3A%22_csrf%22%3Bi%3A1%3Bs%3A32%3A%22%9C%C1%A5%CF%F8%C1-%1F%27%B2%16%E6%2C%08%B6%EF%BA%3A%89%CAr%DD%3B%0C%23%21%D7%09%8B%BB%9B%87%22%3B%7D; _ga=GA1.2.799556653.1669063100; _gid=GA1.2.1849070002.1669063100; device_3527247757=b790f4a841c7c3f970ce2bc8abc6c995d73ff6a72f90a9033e76823b80e2a720a%3A2%3A%7Bi%3A0%3Bs%3A17%3A%22device_3527247757%22%3Bi%3A1%3Bi%3A1%3B%7D; cookie_policy=1; user_id=ac446813a13dd22423309368871319e6458682eb5edd99fc05f899c59e2f97e1a%3A2%3A%7Bi%3A0%3Bs%3A7%3A%22user_id%22%3Bi%3A1%3Bi%3A55377403%3B%7D; __atuvc=4%7C47; __atuvs=637be71b21906596000'
        cookie = SimpleCookie()
        cookie.load(cookies_source)
        cookies = {k: v.value for k, v in cookie.items()}
        self.cookies = cookies
        self.csrf = csrf
        return True

    def confirm_load(self, img_name, dockid):
        try:
            self.status = 'Confirming'
            logger.debug(f'{self.in_path} {self.out_path} {self.status}')
            response = self.session.get('https://photolab.me/effect/apply-combo?docId=' + dockid + '&images%5B%5D=https%3A%2F%2Ftemp-images.ws.pho.to%2F' + img_name + '&crops%5B0%5D%5B%5D=0&crops%5B0%5D%5B%5D=0&crops%5B0%5D%5B%5D=1&crops%5B0%5D%5B%5D=1&step=0&stepPos=0&tpl=0&skipStep=0&_csrf=' + self.csrf, cookies=self.cookies).text
            url = 'https://photolab.me' + json.loads(response)['result_url']
            self.status = 'Rendering'
            logger.debug(f'{self.in_path} {self.out_path} {self.status} Result will be here: {url}')
            return url
        except:
            print(Exception)
            return False

    def wait_result(self):
        retry_counter = 0
        status = ''
        while "status\":\"done" not in status:
            self.status = 'Rendering ' + str(retry_counter + 1) + '/7'
            logger.debug(f'{self.in_path} {self.out_path} {self.status}')
            status = self.session.get('https://photolab.me/effect/apply-combo-status').text
            time.sleep(1)
            retry_counter = retry_counter + 1
            assert retry_counter <= 7
        return True

    def get_result_photo_url(self, result_url):
        try:
            self.status = 'Loading result...'
            logger.debug(f'{self.in_path} {self.out_path} {self.status}')
            photo_html = self.session.get(result_url).text
            photo = photo_html[photo_html.find('https://images-photolabme.ws.pho.to/t/r/'):]
            photo = photo[:photo.find('"')]
            return photo
        except Exception as e:
            print(e)
            return False

    def load_photo(self, photo_url):
        self.status = 'Saving...'
        logger.debug(f'{self.in_path} {self.out_path} {self.status}')
        p = self.session.get(photo_url)
        if 'ERROR' in p.text:
            print(p.text)
            logger.error(f'{self.in_path} {self.out_path} {self.status} \n {p.text}')
            self.status = 'Error'
            return False

        out = open(self.out_path, "wb")
        out.write(p.content)
        self.status = 'OK'
        logger.debug(f'{self.in_path} {self.out_path} {self.status}')
        out.close()
        return True
