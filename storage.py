import random


def get_proxy():
    file = open('proxy_list2.txt', 'r', encoding='utf-8')
    lines = file.readlines()
    for line in lines:
        items = line.split(':')
        ip, port, user, password = [x.replace('\n', '') for x in items]
        yield user + ':' + password + '@' + ip + ':' + port


def get_random_proxy():
    return random.choice(list(get_proxy()))