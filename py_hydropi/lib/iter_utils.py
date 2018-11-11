def avg(list_):
    list_ = [i for i in list_ if i is not None] or [0]
    return sum(list_) / len(list_)


class JSONableDict(dict):
    def to_json(self):
        return {
            k: v.to_json() if hasattr(v, 'to_json') else v for k, v in self.items()
        }


class JSONableList(list):
    def to_json(self):
        return [v.to_json() if hasattr(v, 'to_json') else v for v in self]

    def append_if_not_in(self, o):
        if o not in self:
            self.append(o)

    def extend_if_not_in(self, iterable):
        for o in iterable:
            self.append_if_not_in(o)
