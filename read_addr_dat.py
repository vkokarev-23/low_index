# Работаем с addr.dat
# Этот файл знает, какие файлы удалены.
#

file_name_addr = '/papillon1.db/00228001.i/addr.dat'
file_name_addr = '/papillon1.db/00258000.i/addr.dat'
file_name_addr = '/papillon1.db/00229001.i/addr.dat'
file_name_addr = '/papillon1.db/00229002.i/addr.dat'

print(file_name_addr)

len_head = 0x100
len_record = 0x10

with open(file_name_addr, 'rb') as f:
    buf = f.read()
len_buf = len(buf)


def refs_print_all_records():
offs = len_head
while offs < len_buf:
    beg_field_1 = offs
    end_field_1 = beg_field_1 + 2

    beg_field_2 = offs + 2
    end_field_2 = beg_field_2 + 2

    beg_field_3 = offs + 4
    end_field_3 = beg_field_3 + 2

    beg_field_4 = offs + 6
    end_field_4 = beg_field_4 + 2

    beg_fil_num = offs + 8  # положение поля номер файла
    end_fil_num = beg_fil_num + 4

    beg_fil_cod = offs + 12  # положение поля код (???) файла
    end_fil_cod = beg_fil_cod + 4

    field_1 = int.from_bytes(buf[beg_field_1:end_field_1], byteorder='little')
    field_2 = int.from_bytes(buf[beg_field_2:end_field_2], byteorder='little')
    field_3 = int.from_bytes(buf[beg_field_3:end_field_3], byteorder='little')
    field_4 = "".join(map(chr, buf[beg_field_4:end_field_4]))

    fil_num = int.from_bytes(buf[beg_fil_num:end_fil_num], byteorder='little')
    fil_cod = int.from_bytes(buf[beg_fil_cod:end_fil_cod], byteorder='little')


    print(f'{field_1:04x}  {field_2:04x}  {field_3:04x}  {field_4}  {fil_num:08x}  {fil_cod:08x}')

    offs = offs + len_record



