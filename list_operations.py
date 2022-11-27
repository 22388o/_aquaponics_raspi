def list_display_dundle(list_in: list, sequence_length: int):
    counter = 0
    times = len(list_in)
    while counter < times:
        line = ""
        sec_times = sequence_length
        loc_counter = 0
        while loc_counter < sec_times:
            if counter + loc_counter < times:
                line += " " + str(list_in[counter + loc_counter])
            loc_counter += 1
        print(line)
        counter += loc_counter


def data_leading_zero(integer: int, digits: int):
    str_integer = str(int(integer))
    act_digits = len(str_integer)
    lead = ""
    for _ in range(digits - act_digits):
        lead += '0'
    return lead + str_integer


def fifo_list(list_in: list, data_in, max_length=False):
    answer = list(list_in)
    if not max_length:
        max_length = len(answer)
    answer.append(data_in)
    while len(answer) > max_length:
        del answer[0]
    return answer


def list_dict_fifo_extend_w_dist(listdict: dict, dict_in: dict, max_length=10):
    answer = {}
    for k, v in list(listdict.items()):
        answer[k] = fifo_list(list_in=v, data_in=dict_in[k], max_length=max_length)
    return answer


def logical_list_combine(list_base, list_add):
    counter = 0
    total = len(list_base)
    answer = []
    while counter < total:
        list_base_i = list_base[counter]
        if list_base_i:
            answer.append(list_base_i)
        else:
            answer.append(list_add[counter])
        counter += 1
    return answer


def logical_list_combine_adv(list_base, list_add, neutral):
    counter = 0
    total = len(list_base)
    answer = []
    while counter < total:
        list_base_i = list_base[counter]
        if list_base_i and list_base_i != neutral:
            answer.append(list_base_i)
        else:
            answer.append(list_add[counter])
        counter += 1
    return answer


def list_flatten(list_in):
    answer = []
    for x in list_in:
        for y in x:
            answer.append(y)
    return answer
