'Convert a Python object into a relational schema.'
import logging

import sqlalchemy

logger = logging.getLogger(__name__)

def convert(object):
    metadata = sqlalchemy.MetaData()

    if isinstance(object, dict):
        _convert_dict(object, metadata)
    elif isinstance(object, list):
        raise NotImplementedError('WIP - ignore lists')
        _convert_list(object, metadata)
    else:
        raise NotImplementedError('only dicts and lists are supported')

    return metadata


class RedefineKeyError(RuntimeError):
    pass


def _convert_list(object, tables, name=None):
    assert isinstance(object, list)

    if name:
        table_name = name
    else:
        table_name = 'objects'

    if table_name not in tables:
        logger.info(f"creating table {table_name}")
        tables[table_name] = {
            'id': 'INTEGER PRIMARY KEY',
        }
        if name:
            # if this is not the outer-most object,
            # then it's an ordered array and we need
            # to track that
            tables[table_name]['_order'] = 'INTEGER'
    
    # for now, assume that the first item is representative
    if len(object) > 0:
        first = object[0]
        if _handle_scalar('data', first, tables[table_name]):
            pass
        elif isinstance(first, dict):
            if '__name' not in first:
                first_prime = { '__name': table_name }
                first_prime.update(first)
                first = first_prime
            _convert_dict(first, tables)
        elif isinstance(first, list):
            raise NotImplementedError('WIP - ignore lists')
            # TODO: is there a better way to cook up a nested table name?
            nest_name = f"{table_name}_nested"
            sub_table_name = _convert_list(first, tables, name=nest_name)
            tables[sub_table_name][f"{table_name}_id"] = f"FOREIGN KEY {table_name}.id"
        else:
            raise NotImplementedError(f'items in {table_name} are not in a format we understand')
    
    return table_name


def _convert_dict(object, metadata):
    assert isinstance(object, dict)

    table_name = object.get('__name', 'object')
    if table_name not in metadata.tables:
        logger.info(f"creating table {table_name}")
        table = sqlalchemy.Table(table_name, metadata)
        table.append_column(
            sqlalchemy.Column(
                'id',
                sqlalchemy.Integer,
                primary_key=True,
            )
        )
    else:
        table = metadata.tables[table_name]

    for k, v in object.items():
        if k.startswith('__'):
            continue

        if k in table.columns:
            raise RedefineKeyError(k)

        if _handle_scalar(k, v, metadata.tables[table_name]):
            pass
        elif isinstance(v, dict):
            if '__name' not in v:
                v_prime = { '__name': k }
                v_prime.update(v)
                v = v_prime
            sub_table_name = _convert_dict(v, metadata)
            metadata.tables[sub_table_name].append_column(
                sqlalchemy.Column(
                    f"{table_name}_id",
                    sqlalchemy.Integer,
                    sqlalchemy.ForeignKey(f"{table_name}.id"),
                    nullable=False,
                )
            )
        elif isinstance(v, list):
            pass
            # sub_table_name = _convert_list(v, tables, name=k)
            # tables[sub_table_name][f"{table_name}_id"] = f"FOREIGN KEY {table_name}.id"
        else:
            raise NotImplementedError(f'item at {k} is not a format we understand')
    
    return table_name


def _handle_scalar(key, value, table):
    if isinstance(value, bool):
        table.append_column(
            sqlalchemy.Column(
                key,
                sqlalchemy.Boolean,
            )
        )
    elif isinstance(value, int):
        table.append_column(
            sqlalchemy.Column(
                key,
                sqlalchemy.Integer,
            )
        )
    elif isinstance(value, float):
        table.append_column(
            sqlalchemy.Column(
                key,
                sqlalchemy.Float,
            )
        )
    elif isinstance(value, str):
        table.append_column(
            sqlalchemy.Column(
                key,
                sqlalchemy.Text,
            )
        )
    else:
        return False
    
    return True


if __name__ == '__main__':
    from pprint import pprint
    from sqlalchemy.dialects import sqlite

    from examples import EXAMPLES

    for index, example in enumerate(EXAMPLES):
        result = convert(example)

        print(f"-- example {index} -- ")
        print("Original object:")
        pprint(example)
        print("Resulting schema:")
        for table in result.sorted_tables:
            ct = sqlalchemy.schema.CreateTable(table)
            print(ct.compile(dialect=sqlite.dialect()))
