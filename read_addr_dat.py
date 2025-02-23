import struct

# addr.dat
# Этот файл знает, какие файлы удалены, и где находятся неудаленные.
#
# 00000000  69 10 00 00 d9 21 00 00  00 00 00 00 00 00 00 00  |i....!..........|
# 00000010  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
# *
# 00000100  10 00 00 00 15 80 6c 6d  11 00 00 80 00 01 00 00  |......lm........|
# 00000110  10 00 00 80 15 80 6c 6d  12 00 00 80 00 00 00 00  |......lm........|

# 000017a0  10 00 00 00 65 80 6c 6d  e0 03 01 80 32 a0 0c 00  |....e.lm....2...|
# 000017b0  10 00 00 80 0a 80 6c 6d  1b 00 02 80 00 00 00 00  |......lm........|

# Заголовок длиной 0x0100, затем записи фиксированной длины 0x0010
# 0x0010 - не знаю, что это (field_1)
# 0x0000 - активная запись или 0x8000 - удаленная (active)
# 0x8015 - не знаю, что это (field_2)
# 0x6c6d - маркер 'lm' (marker)
# 0x0011 - номер файла (file)
# 0x8001 - номер сегмента (seg)
# 0x00000100 - ссылка на запись в refs.dat (refs_link)


# Глобальная переменная (addr_buf), буфер, в который полностью
# считывается весь файл с адресными данными сегмента следов
addr_buf = bytes()


# Заполнение буфера данными
def addr_init(seg_path):
    global addr_buf
    with open(f'{seg_path}/addr.dat', 'rb') as f:
        addr_buf = f.read()
    return addr_buf.__len__()


# Извлекаем номер сегмента, номер файла, ссылку на запись в refs.dat
def get_link_to_refs():
    s_1 = struct.Struct('= H H H H H H I')  # '=' упаковка без выравнивания на границу

    addr_offset = 0x0100
    while addr_offset < len(addr_buf):
        field_1, active, field_2, marker, file, seg, refs_link = s_1.unpack_from(addr_buf, addr_offset)
        # print(f'{addr_offset:08x}: {field_1:04x} {active:04x} {field_2:04x} {marker:04x} {file:04x} {seg:04x} {refs_link:08x}')
        addr_offset += s_1.size
        if refs_link != 0:
            yield seg, file, refs_link


# Отладка, печатаем заголовки и их offset
def addr_print_all_headers():
    global addr_buf
    len_buf = len(addr_buf)

    addr_header = struct.Struct('= H H H H H H I')  # '=' упаковка без выравнивания на границу
    addr_rec_len = 0x0010
    addr_offset = 0x0100
    while addr_offset < len_buf:
        f_1, active, f_2, lm, file, segm, link = addr_header.unpack_from(addr_buf, addr_offset)
        print(f'{addr_offset:08x}: {f_1:04x} {active:04x} {f_2:04x} {lm:04x} {segm:04x}{file:04x} {link:08x}')
        addr_offset += addr_rec_len

# ===================================================
# Отладка
# addr_init('/papillon1.db/00548001.i')
# addr_init('/papillon1.db/00258020.i')
# ab_len = addr_init('/papillon1.db/001d8001.i')
# print(f'длина файла: {ab_len}')
# addr_print_all_headers()


# for segment in papillon_segments.lm_seg_list():
#     addr_init(segment)

# get_addr_file_refs()
