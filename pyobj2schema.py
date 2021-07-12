'Convert a Python object into a relational schema.'
from decimal import Decimal
import logging

import sqlalchemy

logger = logging.getLogger(__name__)

def convert(object):
    metadata = sqlalchemy.MetaData()

    if isinstance(object, dict):
        _convert_dict(object, metadata)
    elif isinstance(object, list):
        _convert_list(object, metadata)
    else:
        raise NotImplementedError('only dicts and lists are supported')

    return metadata


class RedefineKeyError(RuntimeError):
    pass


def _convert_list(object, metadata, name=None):
    assert isinstance(object, list)

    if name:
        table_name = name
    else:
        table_name = 'objects'

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
        if name:
            # if this is not the outer-most object,
            # then it's an ordered array and we need
            # to track that
            table.append_column(
                sqlalchemy.Column(
                    '_order',
                    sqlalchemy.Integer,
                )
            )
    
    # TODO: for now, assume that the first item is representative
    if len(object) > 0:
        first = object[0]
        if _handle_scalar('data', first, metadata.tables[table_name]):
            pass
        elif isinstance(first, dict):
            if '__name' not in first:
                first_prime = { '__name': table_name }
                first_prime.update(first)
                first = first_prime
            _convert_dict(first, metadata)
        elif isinstance(first, list):
            # TODO: is there a better way to cook up a nested table name?
            nest_name = f"{table_name}_nested"
            sub_table_name = _convert_list(first, metadata, name=nest_name)
            metadata.tables[sub_table_name].append_column(
                sqlalchemy.Column(
                    f"{table_name}_id",
                    sqlalchemy.Integer,
                    sqlalchemy.ForeignKey(f"{table_name}.id"),
                    nullable=False,
                )
            )
        else:
            raise NotImplementedError(f'items in table "{table_name}" are not in a format we understand')
    
    return table_name


def _convert_dict(object, metadata):
    assert isinstance(object, dict)

    table_name = object.get('__name', 'objects')
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

    for key, value in object.items():
        if key.startswith('__'):
            continue

        if key in table.columns:
            raise RedefineKeyError(key)

        if _handle_scalar(key, value, metadata.tables[table_name]):
            pass
        elif isinstance(value, dict):
            if '__name' not in value:
                v_prime = { '__name': key }
                v_prime.update(value)
                value = v_prime
            sub_table_name = _convert_dict(value, metadata)
            metadata.tables[sub_table_name].append_column(
                sqlalchemy.Column(
                    f"{table_name}_id",
                    sqlalchemy.Integer,
                    sqlalchemy.ForeignKey(f"{table_name}.id"),
                    nullable=False,
                )
            )
        elif isinstance(value, list):
            sub_table_name = _convert_list(value, metadata, name=key)
            metadata.tables[sub_table_name].append_column(
                sqlalchemy.Column(
                    f"{table_name}_id",
                    sqlalchemy.Integer,
                    sqlalchemy.ForeignKey(f"{table_name}.id"),
                    nullable=False,
                )
            )
        else:
            raise NotImplementedError(f'item at key "{key}" is not a format we understand')
    
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
    elif isinstance(value, Decimal):
        table.append_column(
            sqlalchemy.Column(
                key,
                sqlalchemy.Numeric,
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
