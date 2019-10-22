
import functools


def change_of_return(change_set):

    def change_to(func):
        @functools.wraps(func)
        def change(*args, **kwargs):
            return change_set(func(*args, **kwargs))
        return change
    return change_to


to_list = change_of_return(list)
to_tuple = change_of_return(tuple)
to_set = change_of_return(set)
to_dict = change_of_return(dict)

