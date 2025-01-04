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
def addr_init(addr_file_name):
    global addr_buf
    with open(addr_file_name, 'rb') as f:
        addr_buf = f.read()


# Извлекаем номер сегмента, номер файла, ссылку на запись в refs.dat
def get_seg_file_refs():
    s_1 = struct.Struct('@ H H H H H H I')

    addr_offset = 0x0100
    while addr_offset < len(addr_buf):
        field_1, active, field_2, marker, file, seg, refs_link = s_1.unpack_from(addr_buf, addr_offset)
        print(f'{addr_offset:08x}: {field_1:04x} {active:04x} {field_2:04x} {marker:04x} {file:04x} {seg:04x} {refs_link:08x}')
        # здесь обработка active seg file refs_link
        addr_offset += s_1.size


addr_init('/papillon1.db/00228001.i/addr.dat')
get_seg_file_refs()
