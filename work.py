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
    def __init__(self, in_path, out_path=None, use_proxy=False):
        session = requests.session()
        session.headers['User-agent'] = 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Mobile Safari/537.36'
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
        proxy = 'None'
        if use_proxy:
            proxy = storage.get_random_proxy()
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
        cookies_source = 'device_f_1034742850=de333f18371f546030abff98cf8bf5374537e732134f8b89dbcd416022422630a%3A2%3A%7Bi%3A0%3Bs%3A19%3A%22device_f_1034742850%22%3Bi%3A1%3Bi%3A1%3B%7D; _ga=GA1.2.799556653.1669063100; device_3527247757=b790f4a841c7c3f970ce2bc8abc6c995d73ff6a72f90a9033e76823b80e2a720a%3A2%3A%7Bi%3A0%3Bs%3A17%3A%22device_3527247757%22%3Bi%3A1%3Bi%3A1%3B%7D; _gid=GA1.2.1034175670.1669163547; _csrf=8786b8a3164df541609ee1c14097e319e399ea2baf25da78fd3c83f53a01d0bda%3A2%3A%7Bi%3A0%3Bs%3A5%3A%22_csrf%22%3Bi%3A1%3Bs%3A32%3A%22u%E4%0A%98%F4%BC%136%3D%9F%FEo%F3%FA%18%24Fm%DBT%EFhcQ%15%DD%22C%A5%8DA%C4%22%3B%7D; _gat=1; sess=76qes5rjhnkpbe77qdtcl3pefh; __atuvc=26%7C47; __atuvs=6380f6918275f2fb000; cookie_policy=1; device_3774165503=5d36490dcd021393e912d5791d087bf12e4226d107ea7b257927e536bfe95b76a%3A2%3A%7Bi%3A0%3Bs%3A17%3A%22device_3774165503%22%3Bi%3A1%3Bi%3A2%3B%7D; user_id=515a22adff1a3cbba94f1f5ea12af7f8399849bebc2b733834c17ffedbe2a7b5a%3A2%3A%7Bi%3A0%3Bs%3A7%3A%22user_id%22%3Bi%3A1%3Bi%3A55601818%3B%7D'
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
            time.sleep(2)
            retry_counter = retry_counter + 1
            assert retry_counter <= 4
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
        self.session.headers = {
            "accept": 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            "accept-encoding": 'gzip, deflate, br',
            "accept-language": 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            "cache-control": 'max-age=0',
            "sec-ch-ua": '"Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"',
            "sec-ch-ua-mobile": '?0',
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": 'document',
            "sec-fetch-mode": 'navigate',
            "sec-fetch-site": 'none',
            "sec-fetch-user": '?1',
            "upgrade-insecure-requests": '1',
            "user-agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
        }
        self.status = 'Saving...'
        logger.debug(f'{self.in_path} {self.out_path} {self.status}')
        p = self.session.get(photo_url)
        if 'ERROR' in p.text:
            print(p.content)
            logger.error(f'{self.in_path} {self.out_path} {self.status} \n {p.text}')
            self.status = 'Error'
            return False

        out = open(self.out_path, "wb")
        out.write(p.content)
        self.status = 'OK'
        logger.debug(f'{self.in_path} {self.out_path} {self.status}')
        out.close()
        return True


#worker = Worker('1.jpg', 'result.jpg', use_proxy=True)
#worker.load_photo('https://images-photolabme.ws.pho.to/t/r/7d875ae3697a1cef1dd973bc13251860899675ad.jpeg')