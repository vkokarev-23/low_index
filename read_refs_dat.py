import struct


# refs.dat
# 00000000  f7 04 00 00 73 06 00 00  00 00 00 00 00 00 00 00  |....s...........|
# 00000010  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
# *
# 00000100  38 00 00 80 17 80 03 00  00 00 20 01 00 00 72 65  |8......... ...re|
# 00000110  66 73 06 00 fb 02 00 01  00 00 a0 0f 00 01 00 00  |fs..............|
# 00000120  a1 0f 49 04 00 00 a2 0f  ab 07 00 00 a3 0f 6f 0b  |..I...........o.|
# 00000130  00 00 32 22 00 01 00 00  38 00 00 80 89 80 04 00  |..2"....8.......|
# 00000140  00 00 30 01 00 00 72 65  66 73 06 00 fb 02 bf 05  |..0...refs......|
#
# len           file     addr.dat                   text.dat
# 2600 0080ff80 94040000 703f0000 72656673 0300fb02 eecb1000 a00f91602c00                                                     3222712a0600
# 3200 00809080 94040000 703f0000 72656673 0500fb02 df861a00 a00f91602c00 a10f79473100 a20f3ef23500                           3222712a0600
# 3800 00000a80 94040000 703f0000 72656673 0600fb02 17331f00 a00f91602c00 a10f79473100 a20f3ef23500 a30f4d623a00              3222712a0600
#
# Заголовок длиной 0x0100, затем записи переменной длины: 32 38 42 48 и так далее кратно 6
# Первые 26 байт - фиксированная структура вплоть до ссылки в text.dat, затем
# 6-байтные структуры каким-то образом связанные с количеством редакций
# a00f, a100f, a200f - это 4000, 4001, 4002 - номера тегов истории редактирования
# Как видно, на каждую редакцию отдельная запись, а нам нужна самая свежая (последняя),
# ведь номер карточки следов тоже подвержен изменениям
# Количество записей в refs.dat такое же, как и в text.dat. Количество редакций > количества следов
# К счастью, в addr.dat только одна ссылка на refs.dat, и выбирать свежую нам не прийдется
#
# 2600     - длина записи (rec_len)
# 0080ff80 - не знаю, что это (field_1)
# 94040000 - номер файла 00000494.l (num_file)
# 703f0000 - ссылка на запись в addr.dat (addr_link)
# 72656673 - маркер 'refs' (marker)
# 0300fb02 - не знаю, что это (field_3)
# eecb1000 - ссылка на запись в text.dat (text_link)


# Глобальная переменная (refs_buf), буфер, в который полностью
# считывается весь файл с адресными данными сегмента следов
refs_buf = bytes()


def refs_init(seg_path):
    global refs_buf
    with open(f'{seg_path}/refs.dat', 'rb') as f:
        refs_buf = f.read()
    return refs_buf.__len__()


def refs_get_text_link(offs: int):
    global refs_buf

    s_1 = struct.Struct('= H I I I I I I')  # '=' упаковка без выравнивания на границу
    rec_len, field_1, num_file, addr_link, marker, field_3, text_link  = s_1.unpack_from(refs_buf, offs)
    return text_link


def refs_print_this_record(offs: int):
    global refs_buf

    s_1 = struct.Struct('= H I I I I I I')  # '=' упаковка без выравнивания на границу
    rec_len, field_1, num_file, addr_link, marker, field_3, text_link  = s_1.unpack_from(refs_buf, offs)
    print(f'{offs:08x}: {rec_len:04x} {field_1:08x} {num_file:08x} {addr_link:08x} {marker:08x} {field_3:08x} {text_link:08x}')


def refs_print_all_headers():
    global refs_buf
    len_buf = len(refs_buf)

    refs_offset = 0x0100
    while refs_offset < len_buf:
        len_record = int.from_bytes(refs_buf[refs_offset:refs_offset + 2], byteorder='little')
        refs_print_this_record(refs_offset)
        refs_offset += len_record

# ===========================================
# Отладка
# '/papillon1.db/00228001.i'
# '/papillon1.db/00229001.i'
# '/papillon1.db/00229002.i'
# '/papillon1.db/00258000.i'
# '/papillon1.db/00548001.i'    # !!! 07.01.2025
#
# refs_init('/papillon1.db/00548001.i')
# refs_init('/papillon1.db/00258020.i')
# refs_init('/papillon1.db/001d8001.i')
#
# refs_print_this_record(0x0100)
# refs_print_this_record(0x0138)
# refs_print_this_record(0x0170)
# refs_print_this_record(0x01a8)
# print()
# print(f'{refs_get_text_link(0x0100):08x}')
# print(f'{refs_get_text_link(0x0138):08x}')
# print(f'{refs_get_text_link(0x0170):08x}')
# print(f'{refs_get_text_link(0x01a8):08x}')

# ab_len = refs_init('/papillon1.db/001d8001.i')
# print(f'длина файла: {ab_len}')
# refs_print_all_headers()
