import os
import sqlite3
import socket

import read_addr_dat
import read_refs_dat
import read_text_dat
import read_segments

otladka = r'/home/st/tmp/low_index/otladka/otladka.txt'
otladka = ''

def make_papillon_db(papillon_db_name):

    # Готовим каталог под БД: ./data
    dir_data = os.path.dirname(papillon_db_name)
    if os.path.exists(dir_data):
        if os.path.isfile(dir_data):
            os.remove(dir_data)
            os.mkdir(dir_data)
    else:
        os.mkdir(dir_data)

    # Удаляем старую БД, если сохранилась
    if os.path.exists(papillon_db_name):
        os.remove(papillon_db_name)

    # Проверяем наличие порта 8800 - файловый сервер АДИС
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(("localhost", 8800))
    if result != 0:
        print("Порт 8800 закрыт. Запусти /home/p8bin/a8.fs &")
        exit()

    connection = sqlite3.connect(f'{papillon_db_name}')
    cursor = connection.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sled (
    bamasefi TEXT PRIMARY KEY,
    ncard TEXT NOT NULL,
    nsled TEXT NOT NULL)
    ''')

    connection.commit()
    connection.close()


def lm_list():

    for seg_path in read_segments.lt_seg_list():
        print(f'make_lm_list.seg_path --> сегмент: {seg_path}')

        base_seg = list(filter(lambda n: '.i' in n, seg_path.split('/')))[0][:8]

        # Пустые сегменты (длина 256) тоже встречаются
        if read_addr_dat.addr_init(seg_path) == 256:
            continue
        if read_refs_dat.refs_init(seg_path) == 256:
            continue
        if read_text_dat.text_init(seg_path) == 256:
            continue

        list_refs = read_addr_dat.get_link_to_refs()
        i = 0
        for seg, file, refs_link in list_refs:
            i += 1
            # print(f'{i}:    {seg:04x}:{file:04x}    --> {refs_link: 08x}')
            text_link = read_refs_dat.refs_get_text_link(refs_link)
            # print(f'{i}:    {seg:04x}:{file:04x}    --> {text_link: 08x}')

            try:
                str_lm_card_number, str_lm_self_number = read_text_dat.get_lm_card_number(text_link)
            except TypeError:    # cannot unpack non-iterable NoneType object
                str_lm_card_number = 'TypeError'
                str_lm_self_number = 'try'
                print('\nисключение TypeError в make_lm_list.lm_list()')
                print(f'seg:{seg:04x}  file:{file:04x}  refs_link:{refs_link:08x}  text_link:{text_link:08x}')
                print(f'str_lm_card_number:{str_lm_card_number}  str_lm_self_number:{str_lm_self_number}')

            # print(f'{i:6}:   {seg:04x}:{file:04x}    --> {str_lm_card_number}:{str_lm_self_number}')
            seg_file = f'{seg:04x}{file:04x}'
            full_key = f'{base_seg}.{seg_file}'

            yield full_key, str_lm_card_number, str_lm_self_number


# Загружаем в БД данные обо всех следах
def load_papillon_db(papillon_db_name):

    global otladka
    if otladka:
        fout = open(otladka, 'w')

    connection = sqlite3.connect(f'{papillon_db_name}')
    cursor = connection.cursor()
    i = 0
    for key, card, sled in lm_list():
        if otladka:
            i += 1
            print(f'load_papillon_db {i:6} ->   key:{key}   card:{card:20}  sled:{sled}', file=fout)
        cursor.execute(
            'INSERT INTO sled (bamasefi, ncard, nsled) VALUES (?, ?, ?)',
            (f'{key}', f'{card}', f'{sled}' ))

    connection.commit()
    connection.close()

    if otladka:
        fout.close()


# Удаляет таблицу 'sled', при этом занятый объем не уменьшается
def clear_papillon_db(papillon_db_name):

    connection = sqlite3.connect(f'{papillon_db_name}')
    cursor = connection.cursor()
    cursor.execute('DROP TABLE IF EXISTS sled')
    connection.commit()
    connection.close()


def get_sled_papillon_db(papillon_db_name, db_key):

    connection = sqlite3.connect(f'{papillon_db_name}')
    cursor = connection.cursor()
    cursor.execute(
            f'SELECT ncard, nsled  FROM sled  WHERE bamasefi = "{db_key}" '
            )

            # f'SELECT ncard, nsled  FROM sled  WHERE bamasefi IN ("{db_key}") '
            # f'SELECT ncard, nsled  FROM sled  WHERE bamasefi IN ( '00228001.00000007', )',
            # f'{db_key}')
    card_sled = cursor.fetchall()

    connection.commit()
    connection.close()
    return card_sled

# ================================================
# Отладка. Внимание! Запусти /home/p8bin/a8.fs &
# papillon_db_name = './data/papillon.sqlite.db'
# make_papillon_db(papillon_db_name)
# load_papillon_db(papillon_db_name)

# full_key = '00228001.00000008'
# res = get_sled_papillon_db(papillon_db_name, full_key)
# print(f'{type(res)}   {res}')


