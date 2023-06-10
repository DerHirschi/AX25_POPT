import sys


def show_mem_size(var_items, compare=True, previous_sizes={}):
    local_vars = list(var_items.items())
    local_vars.sort(key=lambda x: sys.getsizeof(x[1]))
    for var, obj in local_vars:
        size = sys.getsizeof(obj)
        if compare:
            if var in previous_sizes and previous_sizes[var] != size:
                print(str(var).ljust(20), size, "(changed from", previous_sizes[var], ")")
            else:
                print(str(var).ljust(20), size)
        else:
            print(str(var).ljust(20), size)

    return {var: sys.getsizeof(obj) for var, obj in local_vars}
