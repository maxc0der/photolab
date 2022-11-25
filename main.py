from work import Worker
import threading
import datetime, time


def go(worker, need_save=False):
    img_url = worker.upload_photo()
    img_name = img_url.split('/')[-1]
    result_url = worker.confirm_load(img_name)
    worker.wait_result()
    photo_url = worker.get_result_photo_url(result_url)
    answer = photo_url
    print(answer)
    if need_save:
        answer = worker.load_photo(photo_url)  # LOAD PHOTO TO OUTPUT PATH, CLOUDFLARE CAN BLOCK. Return TRUE or FALSE
    return answer


worker = Worker('1.jpg', 'result.jpg')
thread = threading.Thread(target=go, args=(worker,))
thread.start()

# Example how to check status
# while worker.status != 'OK' and worker.status != 'Error':
#    print(datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S') + ' ' + worker.status)
#    time.sleep(1)
