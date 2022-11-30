# Установка

Загрузите репозиторий

```sh
git clone https://github.com/maxc0der/photolab
```

Установите требуемые библиотеки
```sh
pip install -r requirements.txt
```

В случае использования прокси, создайте файл proxy_list.txt в корневом каталоге, и разместите там прокси в формате `ip:port:login:password`, каждый адрес начиная с новой строки.

#### Класс worker
Cодержит в себе конфигурацию сессии, прокси, файлов ввода-вывода, методы для взаимодействия с photolab. 
Инициализация объекта worker:
`worker = Worker(in_path, out_path, use_proxy=True)`
`in_path` - путь исходного изображения
`out_path` - путь для сохранния результата (если требуется)
`user_proxy` - требуется ли использование proxy (если True, берется случайный из файла proxy_list.txt)

#### Функция go
В файл main.py располагается основная функция `go(worker, dockid, need_save=False)`, отвечающая за коммуникацию с photolab. 
**Она принимает н вход три параметра:**
`worker` - элемент класса Worker
`dockid` - идентификатор эффекта с photolab типа string
`need_save` - требуется ли загрузка изображения результата. Т.к. Cloudlfare ограничивает исходящий от сервера трафик, по-умолчанию принимает значение False. Если need_save = false, функция возвращает ссылку на изображение результата. Если need_save = true, возвращает boolean *(удалось ли сохранить изображение в out_path)*

#### Примеры вызова функции go:

```sh
worker = Worker('1.jpg')
print('ответ: ', go(worker, '25199589'))
---------------------------------------------------------------------------------------------
отвтет: https://images-photolabme.ws.pho.to/t/r/ac9e3b5a9f5b112ae655f1fc2b77e76c324969fd.jpeg
```

```sh
worker = Worker('1.jpg', 'result.jpg')
print('ответ: ', go(worker, '25199589', need_save=False))
---------------------------------------------------------------------------------------------
отвтет: True
```
использование proxy:
```sh
worker = Worker('1.jpg', 'result.jpg', use_proxy=True)
print('ответ: ', go(worker, '25199589', need_save=False))
---------------------------------------------------------------------------------------------
отвтет: True
```


#### Запрос статуса:
Так как время выполнения всех итераций может занимать порядка 10-15 секунд, предусмотрена возможность асинхронного запроса статуса выполнения задачи, путём обращения к переменной `status` объекта класса `Worker`. 
Например:
```sh
worker = Worker('1.jpg', 'result.jpg')
thread = threading.Thread(target=go, args=(worker, '25199589', True, ))
thread.start()

while worker.status != 'OK' and worker.status != 'Error':
    print(datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S') + ' ' + worker.status)
    time.sleep(1)
---------------------------------------------------------------------------------------------
Ответ:

2022-11-25 17:00:56 Uploading photo
1.jpg result.jpg Uploaded: https://temp-images.ws.pho.to/3562d7912d7c44525fbbf5e19be898542b91a35e.jpeg
1.jpg result.jpg Confirming
2022-11-25 17:00:57 Confirming
2022-11-25 17:00:58 Confirming
2022-11-25 17:00:59 Confirming
2022-11-25 17:01:00 Confirming
2022-11-25 17:01:01 Confirming
2022-11-25 17:01:02 Confirming
2022-11-25 17:01:03 Confirming
2022-11-25 17:01:04 Confirming
1.jpg result.jpg Rendering Result will be here: https://photolab.me/r/YVeoBMd
1.jpg result.jpg Rendering 1/7
2022-11-25 17:01:05 Rendering 1/7
2022-11-25 17:01:06 Rendering 1/7
2022-11-25 17:01:07 Rendering 1/7
1.jpg result.jpg Loading result...
2022-11-25 17:01:08 Loading result...
2022-11-25 17:01:09 Loading result...
2022-11-25 17:01:10 Loading result...
2022-11-25 17:01:11 Loading result...
2022-11-25 17:01:12 Loading result...
2022-11-25 17:01:13 OK
OK
```
