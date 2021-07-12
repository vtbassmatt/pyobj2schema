'Convert a Python object into a relational schema.'

def convert(object):
    tables = {}

    if isinstance(object, dict):
        _convert_dict(object, tables)
    else:
        raise NotImplementedError('only dicts are supported')

    return tables


def _convert_dict(object, tables):
    assert isinstance(object, dict)

    table_name = object.get('__name', 'object')
    if table_name not in tables:
        print(f"creating table {table_name}")
        tables[table_name] = ['id INTEGER PRIMARY KEY']

    for k, v in object.items():
        if k.startswith('__'):
            continue

        if isinstance(v, int):
            tables[table_name].append(
                f"{k} INTEGER"
            )
        elif isinstance(v, str):
            tables[table_name].append(
                f"{k} TEXT"
            )
        elif isinstance(v, dict):
            if '__name' not in v:
                v_prime = { '__name': k }
                v_prime.update(v)
                v = v_prime
            sub_table_name = _convert_dict(v, tables)
            tables[sub_table_name].append(
                f"{table_name}_id FOREIGN KEY {table_name}.id"
            )
        elif isinstance(v, list):
            # TODO: handle lists
            pass
        else:
            raise NotImplementedError(f'item at {k} is not a format we understand')
    
    return table_name


if __name__ == '__main__':
    from pprint import pprint

    example1 = {
        '__name': 'example1',
        'foo': 'is a string',
        'bar': 42,
        'zab': [ 'a', 'b', 'c' ],
        'tab': {
            'bongo': 'boingo',
        },
    }
    result1 = convert(example1)

    print("-- example 1 -- ")
    print("Original object:")
    pprint(example1)
    print("Resulting schema:")
    pprint(result1)
