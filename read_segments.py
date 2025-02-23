import subprocess


# Единичный сегмент следов, для отладки
def lm_seg_list_one():
    segment_list = ['/papillon1.db/00548001.i',]
    for seg in segment_list:
        yield seg

# Возвращает список сегментов по заданному образцу
def get_seg_list(pattern: list) -> list:
    result = subprocess.run(pattern, capture_output=True, text=True)
    output = result.stdout  # Здесь сохраняется вывод команды
    seg_list = output.split()
    return seg_list


# Список сегментов следов: пальцев и ладоней, i - части
def lt_seg_list():
    l_pattern = ['/home/p8bin/a8.dbh', '--ppln', '/papillon1', '--iattr', 'l', '--eattr', 'ej', '--idir',]
    t_pattern = ['/home/p8bin/a8.dbh', '--ppln', '/papillon1', '--iattr', 't', '--eattr', 'ej', '--idir',]
    segment_list = []
    segment_list.extend(get_seg_list(l_pattern))
    segment_list.extend(get_seg_list(t_pattern))
    for seg in segment_list:
        yield seg


# Список сегментов дактилокарт, w - части
def fp_seg_list():
    f_pattern = ['/home/p8bin/a8.dbh', '--ppln', '/papillon1', '--iattr', 'f', '--eattr', 'egx', '--wdir',]
    segment_list = []
    segment_list.extend(get_seg_list(f_pattern))
    for seg in segment_list:
        yield seg



# ========================================
# Тест
#
# if __name__ == '__main__':
#
#     print('-' * 40)
#     for seg in lt_seg_list():
#         print(seg)
#
#     print('-' * 40)
#     for seg in fp_seg_list():
#         print(seg)
#
