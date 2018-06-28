def avg(list_):
    list_ = [i for i in list_ if i is not None] or [0]
    return sum(list_) / len(list_)
