# -*- coding: utf-8 -*-

# 00000001.flh 00000002.pth
# Файлы рекомендательных списков (рексписков) карта-след (К-С) находятся в каталоге ./recom
# рабочего каталога макросегмента дактилокарт, например, /papillon1.db/00220001.w/recom/.
# Каждая дактилокарта в сегменте хранится в файле с уникальным номером, например, 000100b7.f
# Рексписки для нее, если есть, разделены по типу совпавших объектов на два файла:
# карта - пальцы:  000100b7.flh
# карта - ладони:  000100b7.fph
# Структура обоих этих файлов одинаковая, поэтому мы сливаем их вместе перед анализом.
# Файл рексписка состоит из записей переменной длины, следующих вплотную друг к другу.
# Каждая такая запись описывает единичное совпадение К-С, начинается она
# с поля длины записи, далее из интересного: адреса в базе данных совпавших
# Карты (Q запрос) и Следа (A ответ), еще дальше описание пар совпавших точек.

# 00000000  ce 00 00 00 49 80 66 6c  72 6e 22 00 01 00 81 00  |....I.flrn".....|
# 00000010  01 00 00 09 00 00 ff 7f  30 80 9b 00 3b 80 90 1b  |........0...;...|
# 00000020  03 00 99 15 04 00 00 00  00 00 00 00 00 00 2b 41  |..............+A|
# 00000030  c7 66 00 00 00 00 54 41  c7 66 00 00 00 00 00 08  |.f....TA.f......|
# 00000040  00 00 00 08 00 00 09 08  00 00 00 00 00 00 19 00  |................|
# 00000050  02 02 00 64 00 00 00 65  00 00 00 07 00 05 00 00  |...d...e........|
# 00000060  00 c9 00 00 00 00 00 02  00 01 00 fe ff 02 00 04  |................|
# 00000070  00 03 00 ff ff 04 00 09  00 05 00 fd 00 06 00 0a  |................|
# 00000080  00 07 00 ff ff 08 00 fe  ff 09 00 fe ff 0a 00 0f  |................|
# 00000090  00 0b 00 10 00 0c 00 fe  ff 0d 00 fe ff 0e 00 ff  |................|
# 000000a0  ff 0f 00 fe ff 10 00 fe  ff 11 00 16 00 12 00 fe  |................|
# 000000b0  ff 13 00 fe ff 14 00 1e  00 15 00 1d 00 16 00 19  |................|
# 000000c0  00 17 00 24 00 18 00 21  00 31 35 35 32 00 a1 00  |...$...!.1552...|
# 000000d0  00 00 a0 80 66 6c 72 6e  22 00 01 00 81 00 01 00  |....flrn".......|

# Заголовок 10 байт:
# 00000000  ce 00 00 00 49 80 66 6c  72 6e                    |....I.flrn      |
# ce 00 00 00 (206) - длина записи
# 49 (73) - не знаю
# 80 (8.0) - версия "Папилона"
# 66 6c  72 6e (flrn) - маркер

# Две структуры для совпавших объектов по 12 байт:
# Q - запрос (дактилокарта) и A - ответ (след)
# 0000000a  22 00 01 00 81 00 01 00  00 09 00 00              |"...........    |
# 00000016  ff 7f 30 80 9b 00 3b 80  90 1b 03 00              |..0...;.....    |
# 22 00        (0022) - база (a_base)
# 01 00        (0001) - макросегмент (a_macro)
# 81 00 01 00  (00010081) - файл, где 0001 - сегмент (a_file)
# 00 09 00 00 - не знаю, вероятно, ссылка на 'addr:'
# В этой паре Q-A, интересна A, из которой мы получим номер следокарточки и следа

# Следом за ними индекс совпадения 2 байта:
# 99 15        (5529)

import os
import os.path
import struct

import read_segments
import papillon_db

papillon_db_name = './data/papillon.sqlite.db'


def fp_tp_list():
    pass


def print_interesting(rs, l, rf):
    max_ind = rs[l][2] if rs[l][2] > rs[l+1][2] else rs[l+1][2]
    print(f'\n{rf}.[flh,pth]')
    print(f'good: "{rs[l][0]}" ({rs[l][1]}, {rs[l+1][1]})  {max_ind}')


def find_interesting(rs, rf):
    # rs - список следов в рексписке: СК, СЛ, Инд ['230180Д-16-0028', '5', 4485]
    # rf имя файла рекомендательного списка
    rs.sort()
    for l in range(len(rs) - 1):
        if rs[l][0] != rs[l+1][0]:  # номера СК разные - не интересно
            continue
        if rs[l][1] == rs[l+1][1]:  # СК=СК, но номера следов одинаковые - не интересно
            continue
        print_interesting(rs, l, rf)


def get_sk_list_from_buff(sk_list, rec_buf):

    struct_fptp_record_len = struct.Struct('= I')           # длина записи
    struct_fptp_record_answer = struct.Struct('= H H I')    # база, макросегмент, файл
    struct_fptp_record_index = struct.Struct('= H')         # индекс совпадения

    len_rec_buf = len(rec_buf)
    fptp_offset = 0
    while fptp_offset < len_rec_buf:
        # Читаем из рексписка a_base, a_macro, a_file, a_index.
        fptp_record_len, = struct_fptp_record_len.unpack_from(rec_buf, fptp_offset)
        a_base, a_macro, a_file = struct_fptp_record_answer.unpack_from(rec_buf, fptp_offset + 0x0016)
        a_index = struct_fptp_record_index.unpack_from(rec_buf, fptp_offset + 0x0022)

        # print(f'длина записи {fptp_record_len:08x}')
        # print(f'a_base:{a_base:04x}  a_macro:{a_macro:04x}  a_file:{a_file:08x}')

        # Ищем в базе номера СК, СЛ. Результат - список кортежей [(СК, СЛ),]
        # Можем получить пустой список [], если в базе ничего не нашлось.
        # Получить список из двух и более кортежей невероятно, ключ ведь уникальный.
        full_key = f'{a_base:04x}{a_macro:04x}.{a_file:08x}'
        # print(f'sql_key: {sql_key}')

        # получаем из базы номер СК, номер СЛ, добавляем индекс совпадения
        res = papillon_db.get_sled_papillon_db(papillon_db_name, full_key)

        # делаем такое вот sk_string: ['230180Д-16-0028', '5', 4485]
        if len(res) == 0:
            sk_string = ['', full_key, 0]
        else:
            sk_string = list(res[0])
            sk_string.append(a_index[0])

        # sk_string - декодированная строка: карта-след-индекс
        # print(f'{sk_string}')

        # накапливаем sk_string в sk_list:
        # [['230180Д-16-0028', '5', 4485],
        # ['340000П191105', '1', 3075], ]

        sk_list.append(sk_string)

        fptp_offset += fptp_record_len


def fp_tp_recom_observ(seg_path):
    i = 0
    fs_names = set()    # накопитель неповторяющихся имен файлов
    recom_lists = os.scandir(path=seg_path + '/recom')
    # в каталоге ./recom лежат файлы вида 00000001.ffh .flh .pth .flj
    for file in recom_lists:
        if file.name[8:] in ('.flh', '.pth'):
            fs_names.add(file.name[:8])
            i += 1
            # print(f'{i:2}  {file.name[:8]}')

    i = 0
    fl_names = list(fs_names)
    fl_names.sort()
    for file in fl_names:
        i += 1
        # print(f'{i:2}  {file}')

        # Если мы сюда попали, значит файлы рексписков 'flh' или 'pth', или оба сразу существуют.
        # В них, в секции Answer, ссылки на совпавшие следы: база-макросегмент-сегмент-файл (номера).
        # Мы декодируем номера, найдем соответствующие тексты и накопим их в sk_list
        # в виде: номер_карточки, номер_следа, индекс_совпадения.

        sk_list = []
        for file_ext in 'flh', 'pth':
            recom_file = f'{seg_path}/recom/{file}.{file_ext}'
            if os.path.isfile(recom_file):
                # print(f'{i:2}  {recom_file}')
                with open(recom_file, 'rb') as f:
                    recom_buf = f.read()
                get_sk_list_from_buff(sk_list, recom_buf)

        # Находим случаи, когда человек оставил два или более следов
        reс_file = f'{seg_path}/recom/{file}'   # имя файла без расширения
        find_interesting(sk_list, reс_file)

    recom_lists.close()


# =================================================
# Тесты

# for seg_path in papillon_segments.fp_seg_list():
#     print(seg_path)
#     fp_tp_recom_observ(seg_path)

# seg_path = '/papillon1.db/01fb07a0.w'
# seg_path = '/papillon1.db/002500d0.w'

# for seg_path in ('/papillon1.db/00220001.w', ):
#     fp_tp_recom_observ(seg_path)
#


if __name__ == '__main__':

    # Загружаем в БД данные о следах
    papillon_db.make_papillon_db(papillon_db_name)
    papillon_db.load_papillon_db(papillon_db_name)

    # Бегаем по сегментам ДК, рекспискам К-С, ищем интересные
    for seg_path in read_segments.fp_seg_list():
        if os.path.exists(seg_path + '/recom'):
            fp_tp_recom_observ(seg_path)
