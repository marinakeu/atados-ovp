def present_in_list(q_list, key, value):
    for i in q_list:
        if i[key] == value:
            return True
    return False
