import struct

# Глобальная переменная (txt_buf), буфер, в который полностью
# считывается весь файл с текстовыми данными сегмента следов
addr_buf = bytes()


# Заполнение буфера данными
def text_init(text_file_name):
    global addr_buf
    with open(text_file_name, 'rb') as f:
        txt_buf = f.read()


# Извлекаем номер следокарточки и номер следа (t:201 t:202) по смещению (text_offset)
def get_lm_card_number(text_offset):

    # В начале блока данных (text_offset) находится длина самого блока,
    # чуть дальше - количество записей в оглавлении тегов (len_toc)

    s_1 = struct.Struct('@ I 14B H')
    len_blk, *field_1, len_toc = s_1.unpack_from(addr_buf, text_offset)
    # print(f'{len_blk}  {field_1}  {len_toc}')

    # Оглавление тегов (toc) состоит из записей постоянной длины:
    # код тега (teg_cod), теги отсортированы по возрастанию кода 201, 202, ...
    # длина данных этого тега (teg_len) и
    # смещение до данных от начала блока данных (text_offset)

    s_2 = struct.Struct('@ H H I')
    toc_offset = text_offset + 0x14
    item_offset = toc_offset

    # Бежим по оглавлению, извлекаем номер следокарточки и номер следа (t:201 t:202)

    for i in range(len_toc):
        teg_cod, teg_len, teg_ofs =  s_2.unpack_from(addr_buf, item_offset)
        # print(f'{i}  {teg_cod}  {teg_len}  {teg_ofs}')

        if teg_cod == 201:
            lm_self_number = addr_buf[text_offset + teg_ofs:text_offset + teg_ofs + teg_len - 1]
            str_lm_self_number = lm_self_number.decode()
            # print(f'{lm_self_number}   {str_lm_self_number}')

        if teg_cod == 202:
            lm_card_number = addr_buf[text_offset + teg_ofs:text_offset + teg_ofs + teg_len - 1]
            str_lm_card_number = lm_card_number.decode()
            # print(f'{lm_card_number}   {str_lm_card_number}')

        if teg_cod > 202:
            return str_lm_card_number, str_lm_self_number

        item_offset += s_2.size


# text_init('/papillon1.db/00258000.i/text.dat')
text_init('/papillon1.db/00228001.i/text.dat')

for offs in 0x0100, 0x05bf, 0x0a7e, 0x0f3d, 0x13fc, 0x18bb, 0x1d89, 0x2257, 0x2723, 0x2bf1:
    SK, SL = get_lm_card_number(offs)
    print(f'след:  {SK}:{SL}')
