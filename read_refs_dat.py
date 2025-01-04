
buf = bytes()


def refs_init(refs_file_name):
    global buf
    print(refs_file_name)
    with open(refs_file_name, 'rb') as f:
        buf = f.read()


def refs_print_this_record(offs: int):
    global buf

    beg_fnum = offs + 6
    end_fnum = beg_fnum + 4

    beg_txt = offs + 22
    end_txt = beg_txt + 4

    fil_num = int.from_bytes(buf[beg_fnum:end_fnum], byteorder='little')
    adr_txt = int.from_bytes(buf[beg_txt:end_txt], byteorder='little')

    print(f'{offs:08x}:   {fil_num:08x}   {adr_txt:08x}')


def refs_print_all_records():
    global buf
    len_head = int('0x100', base=16)
    len_buf = len(buf)

    offs = len_head
    while offs < len_buf:
        len_record = int.from_bytes(buf[offs:offs + 2], byteorder='little')
        refs_print_this_record(offs)
        offs = offs + len_record

# ===========================================
# '/papillon1.db/00228001.i/refs.dat'
# '/papillon1.db/00229001.i/refs.dat'
# '/papillon1.db/00229002.i/refs.dat'
# '/papillon1.db/00258000.i/refs.dat'

refs_init('/papillon1.db/00258000.i/refs.dat')

refs_print_this_record(0x100)
refs_print_this_record(0x126)
refs_print_this_record(0x14c)
print()
refs_print_all_records()

# refs_print_all_records()