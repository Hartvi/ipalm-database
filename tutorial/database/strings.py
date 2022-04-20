# import models
# from .models import *
# from .serializers import *
# from .views import *


import tokenize
import token
import os
dir_path = os.path.dirname(os.path.realpath(__file__))

# utility functions, not to be called really
def get_class_name(in_str: str):
    ret = in_str.replace('class ', '')
    return ret.split('(')[0]


def to_lower_n_underscore(in_str: str):
    ret = ''

    for k, l in enumerate(in_str):
        if l.islower():
            ret += l
        elif k == 0:
            ret += l.lower()
        else:
            ret += '_' + l.lower()
    return ret


# these functions are actually useful
def generate_class_names():
    with open(os.path.join(dir_path, "models.py"), 'r') as fp:
        # text = fp.read()
        # tokens = tokenize.tokenize()
        # print(tokens)
        lines = fp.readlines()
        lines = [line for line in lines if ("class" in line)]
        ret = list(map(get_class_name, lines))
        ret = [i for i in ret if i.isalnum()]
        return ret


def generate_singular_class_strings(class_names):
    ret = list()
    for c in class_names:
        ret.append(to_lower_n_underscore(c))
    return ret


def generate_plural_class_strings(class_strings):
    ret = list()
    for c in class_strings:
        if c[-1] == 'y':
            ret.append(c[:len(c) - 1] + 'ies')
        else:
            ret.append(c + 's')
    return ret


def get_viewset_names():
    with open(os.path.join(dir_path, "views.py"), 'r') as fp:
        # text = fp.read()
        # tokens = tokenize.tokenize()
        # print(tokens)
        lines = fp.readlines()
        lines = [line for line in lines if ("class" in line)]
        ret = list(map(get_class_name, lines))
        ret = [i for i in ret if i.isalnum()]
        return ret


def get_viewset_urls(viewset_names):
    ret = []
    for v in viewset_names:
        ret.append(v.replace('ViewSet', ''))
    return generate_plural_class_strings(generate_singular_class_strings(ret))


class_names = generate_class_names()
class_strings = generate_singular_class_strings(class_names)
class_plural_strings = generate_plural_class_strings(class_strings)

# viewsets
viewset_classes = get_viewset_names()
viewset_urls = get_viewset_urls(viewset_classes)
viewset_singular = [_[:-1].replace('ie', 'y') for _ in viewset_urls]


if __name__ == "__main__":
    print("class_names:", class_names)
    print("class_strings:", class_strings)
    print("class_plural_strings:", class_plural_strings)
    print("viewset_classes:", viewset_classes)
    print("viewset_urls:", viewset_urls)
    print("viewset_singular:", viewset_singular)
