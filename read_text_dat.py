import struct

# text.dat
# 00000000  f7 04 00 00 73 06 00 00  00 00 00 00 00 00 00 00  |....s...........|
# 00000010  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
# *
# 00000100  bf 04 00 80 16 80 03 00  00 00 20 01 00 00 6c 74  |.......... ...lt|
# 00000110  78 74 2c 00 c9 00 02 00  74 01 00 00 ca 00 10 00  |xt,.....t.......|
# 00000120  76 01 00 00 cb 00 09 00  86 01 00 00 cc 00 03 00  |v...............|
#
# Файл text.dat содержит текстовые данные следов, в записях длиной 1-2 килобайта
#
# За заголовком файла длиной 0x0100, следуют записи длиной 1-2 килобайта
# У каждой записи есть свой заголовок (record_header), его длина 0x0014, например:
# 00000100  bf 04 00 80 16 80 03 00  00 00 20 01 00 00 6c 74  |.......... ...lt|
# 00000110  78 74 2c 00                                       |xt,.            |
# 000005bf  bf 04 00 80 02 80 04 00  00 00 30 01 00 00 6c 74  |..........0...lt|
# 000005cf  78 74 2c 00                                       |xt,.            |
# bf 04 - (1215) - длина записи
# 00 80 - возможно, версия "Папилона" 8.0
# 16 80  - не знаю
# 03 00 00 00 (0003)- номер (имя) файла: 00000003.l
# 20 01 00 00 (0288) - не знаю
# 6c 74 78 74 - маркер 'ltxt'
# 2c 00 - (44) количество элементов в оглавлении (toc)
#
# К заголовку записи примыкает оглавление (toc), к нему - z-строки
# переменной длины, которые и содержат собственно текстовые данные
# Оглавление (toc) состоит из описателей тегов (items) фиксированной длины 0x0008
# Теги упорядочены по возрастанию кода 201, 202, ...
#
# Оглавление (toc):
# 00000114  c9 00 02 00 74 01 00 00  ca 00 10 00 76 01 00 00  |....t.......v...|
# 00000124  cb 00 09 00 86 01 00 00  cc 00 03 00 8f 01 00 00  |................|
# 00000134  cd 00 05 00 92 01 00 00  ce 00 09 00 97 01 00 00  |................|
# c9 00 - (201) - тег t:201 - номер следа в следокарточке
# ca 00 - (202) - тег t:202 - номер самой следокарточки и так далее
# 02 00 - (2) - длина данных тега, в частности длина z-строки
# 74 01 00 00 - смещение данных относительно начала записи
#
# z-строки:
# 00000274  32 00                                             |2.              |
# 00000276  32 33 30 31 37 30 2e 31  33 2e 30 34 2e 32 33 00  |230170.13.04.23.|
# 00000286  35 31 37 37 65 61 39 35  00                       |5177ea95.       |
# 0000028f  61 65 00                                          |ae.             |
# 0000038d  31 33 31 37 30 32 34 37  20 31 37 2f 30 34 32 33  |13170247 17/0423|
# 0000039d  38 20 32 33 2e 30 34 2e  31 33 00                 |8 23.04.13.     |


# Глобальная переменная (txt_buf), буфер, в который полностью
# считывается весь файл с текстовыми данными сегмента следов
text_buf = bytes()


# Заполнение буфера данными
def text_init(seg_path):
    global text_buf
    with open(f'{seg_path}/text.dat', 'rb') as f:
        text_buf = f.read()
    return text_buf.__len__()


# Извлекаем номер следокарточки и номер следа (t:201 t:202) по смещению (text_offset)
def get_lm_card_number(text_offset):
    global text_buf

    # значения на тот случай, когда у следа нет тегов t:201 t:202
    # а что, такое разве бывает ?
    str_lm_card_number = f'txt_offs:{text_offset:08x}'
    str_lm_self_number = '00_00'

    record_header = struct.Struct('= I 14B H')  # '=' упаковка без выравнивания на границу
    len_blk, *field_1, len_toc = record_header.unpack_from(text_buf, text_offset)

    toc = struct.Struct('= H H I')  # '=' упаковка без выравнивания на границу
    toc_offset = text_offset + 0x14
    item_offset = toc_offset

    for i in range(len_toc):
        teg_cod, teg_len, teg_ofs =  toc.unpack_from(text_buf, item_offset)

        if teg_cod == 201:
            lm_self_number = text_buf[text_offset + teg_ofs:text_offset + teg_ofs + teg_len - 1]
            try:
                str_lm_self_number = lm_self_number.decode()
            except UnicodeDecodeError:
                str_lm_self_number = f'UniDecodeErr:{text_offset:08x}'

        if teg_cod == 202:
            lm_card_number = text_buf[text_offset + teg_ofs:text_offset + teg_ofs + teg_len - 1]
            try:
                str_lm_card_number = lm_card_number.decode()
            except UnicodeDecodeError:
                str_lm_card_number = f'UniDecodeErr:{text_offset:08x}'

                # print(f'{lm_card_number}   {str_lm_card_number}')

        if teg_cod > 202:
            return str_lm_card_number, str_lm_self_number

        item_offset += toc.size


# Отладка, печатаем заголовки и их offset
def text_print_all_headers():
    global text_buf
    len_buf = len(text_buf)

    text_header = struct.Struct('= H H H I I I H')  # '=' упаковка без выравнивания на границу
    text_offset = 0x0100
    while text_offset < len_buf:
        rlen, ver, f_1, file, f_2, ltxt, ntoc = text_header.unpack_from(text_buf, text_offset)
        print(f'{text_offset:08x}: {rlen:04x} {ver:04x} {f_1:04x} {file:08x} {f_2:08x} {ltxt:08x} {ntoc:04x}')
        text_offset += rlen

# ======================================================
# Отладка
# text_init('/papillon1.db/00258000.i')
# text_init('/papillon1.db/00228001.i')
# text_init('/papillon1.db/00548001.i')
# text_init('/papillon1.db/00258020.i')
#

# ab_len = text_init('/papillon1.db/001d8001.i')
# print(f'длина файла: {ab_len}')
# text_print_all_headers()


# for offs in 0x0100, 0x05bf, 0x0a7e, 0x0f3d, 0x13fc, 0x18bb, 0x1d89, 0x2257, 0x2723, 0x2bf1:
#     SK, SL = get_lm_card_number(offs)
#     print(f'след:  {SK}:{SL}')

# offs = 0x00283a5e
# SK, SL = get_lm_card_number(offs)
# print(f'след:  {SK}:{SL}')
