from importlib import import_module
#from tornado.web import _O

#class Map(_O):
#    pass


def import_class(class_path):
    '''
    Given a class name as: "foo.bar.Xpto"
    returns the "Xpto" class from "foo.bar" module
    '''
    class_path = class_path.split('.')
    path = '.'.join(class_path[0:-1])
    klass = class_path[-1]
    module = import_module(path)
    return getattr(module, klass)
