from multiprocessing import Pool
from tqdm import tqdm
import threading
import main
import time


def progress():
    while True:
        time.sleep(3)
        print(f'total: {pbar.total} finish:{pbar.n} good: {goods} bad: {bads}')


if __name__ == '__main__':
    tasks = [('1.jpg', 'result/' + str(n) + '.jpg') for n in range(1, 1000)]
    pbar = tqdm(total=len(tasks))
    goods, bads = 0, 0

    pbar.update(0)
    pool = Pool(processes=15)
    thread = threading.Thread(target=progress)
    thread.start()
    results = []

    for result in pool.starmap(main.go, tasks):
        results.append(result)
        print(result)
        if result == 'OK':
            goods = goods + 1
        else:
            bads = bads + 1
            print(result)
        pbar.update(1)

    print(results)
    pool.close()
    pool.join()
    pbar.close()