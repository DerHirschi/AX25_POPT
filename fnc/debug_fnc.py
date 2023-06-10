import sys

def show_mem_size(var_items, compare=True, depth=0, previous_sizes={}):
    indent = "  " * depth
    local_vars = list(var_items.items())
    local_vars.sort(key=lambda x: sys.getsizeof(x[1]))
    for var, obj in local_vars:
        size = sys.getsizeof(obj)
        if compare:
            if var in previous_sizes and previous_sizes[var] != size:
                print(f"{indent}{var}".ljust(30) + f": {size} (changed from {previous_sizes[var]})")
            #else:
            #    print(f"{indent}{var}".ljust(30) + f": {size}")
        #else:
           # print(f"{indent}{var}".ljust(30) + f": {size}")

        # Objekte rekursiv überprüfen
        if isinstance(obj, dict):
            print(f"{indent}Sub-Objects of {var}:")
            show_mem_size(obj, compare, depth + 1)
        elif isinstance(obj, list) or isinstance(obj, tuple):
            print(f"{indent}Elements of {var}:")
            for index, element in enumerate(obj):
                if isinstance(element, dict) or isinstance(element, list) or isinstance(element, tuple):
                    print(f"{indent}  Element {index}:")
                    show_mem_size({f"Element {index}": element}, compare, depth + 2)

    return {var: sys.getsizeof(obj) for var, obj in local_vars}
