class ModelFactory(object):

    def __init__(self, *initial_data, **kwargs):
        for dictionary in initial_data:
            for key in dictionary:
                setattr(self, key, dictionary[key])
            for key in kwargs:
                setattr(self, key, kwargs[key])


class ProjectListFactory(ModelFactory):

    def __init__(self, *initial_data, **kwargs):
        super().__init__(*initial_data, **kwargs)

    def meta_data(self):
        meta_data_dict = {}
        for k,v in self.__dict__.items():
            meta_data_dict[k] = v
        if meta_data_dict["items"]:
            del meta_data_dict["items"]
        return meta_data_dict
