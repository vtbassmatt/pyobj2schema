'Convert a Python object into a relational schema.'
import logging

logger = logging.getLogger(__name__)

def convert(object):
    tables = {}

    if isinstance(object, dict):
        _convert_dict(object, tables)
    else:
        raise NotImplementedError('only dicts are supported')

    return tables


def produce_schema(tables):
    sql = []
    for table_name, schema in tables.items():
        cols = [f"{k} {v}" for k, v in schema.items()]
        sql.append(f'CREATE TABLE {table_name} ({", ".join(cols)})')
    return ";\n".join(sql) + ';'


class RedefineKeyError(RuntimeError):
    pass


def _convert_dict(object, tables):
    assert isinstance(object, dict)

    table_name = object.get('__name', 'object')
    if table_name not in tables:
        logger.info(f"creating table {table_name}")
        tables[table_name] = {'id': 'INTEGER PRIMARY KEY' }

    for k, v in object.items():
        if k.startswith('__'):
            continue

        if k in tables[table_name]:
            raise RedefineKeyError(k)

        if isinstance(v, int):
            tables[table_name][k] = "INTEGER"
        elif isinstance(v, str):
            tables[table_name][k] = "TEXT"
        elif isinstance(v, dict):
            if '__name' not in v:
                v_prime = { '__name': k }
                v_prime.update(v)
                v = v_prime
            sub_table_name = _convert_dict(v, tables)
            tables[sub_table_name][f"{table_name}_id"] = f"FOREIGN KEY {table_name}.id"
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
    print(produce_schema(result1))
