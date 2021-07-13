'Convert a Python object into a relational schema.'
from decimal import Decimal
import logging
import os

import sqlalchemy

log_level = os.environ.get('LOGLEVEL', None)
if log_level:
    numeric_level = getattr(logging, log_level.upper(), None)
    if numeric_level:
        logging.basicConfig(level=numeric_level)
    else:
        logging.warning(f'{log_level} is not a valid log level')

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


class ColumnAlreadyExists(RuntimeError): pass


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
        if _handle_if_scalar('data', first, metadata.tables[table_name]):
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
            _handle_if_list(nest_name, first, metadata, table_name)
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

        if _handle_if_scalar(key, value, metadata.tables[table_name]):
            pass
        elif _handle_if_list(key, value, metadata, table_name):
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
        else:
            raise NotImplementedError(f'item at key "{key}" is not a format we understand')
    
    return table_name


def _handle_if_scalar(key, value, table):
    column_exists = (key in table.columns)
    new_type = None

    if isinstance(value, bool):
        new_type = sqlalchemy.Boolean
    elif isinstance(value, int):
        new_type = sqlalchemy.Integer
    elif isinstance(value, float):
        new_type = sqlalchemy.Float
    elif isinstance(value, Decimal):
        new_type = sqlalchemy.Numeric
    elif isinstance(value, str):
        new_type = sqlalchemy.Text
    else:
        return False
    
    if column_exists:
        # check that the type is compatible
        if key == 'id':
            # upgrade the `id` column to whatever the data has
            logger.info(f"changing '{key}' type to '{new_type}'")
            table.columns[key].type = new_type()
            return True

        # TODO: check more details like nullability
        if new_type == table.columns[key].type:
            return True

        if new_type == sqlalchemy.Numeric and table.columns[key].type == sqlalchemy.Integer:
            # it's safe to upgrade an integer to a decimal
            table.columns[key].type = new_type()
            return True

        raise ColumnAlreadyExists(key)

    else:
        table.append_column(sqlalchemy.Column(key, new_type))
    
    return True


def _handle_if_list(key, value, metadata, table_name):
    if not isinstance(value, list):
        return False

    sub_table_name = _convert_list(value, metadata, name=key)
    metadata.tables[sub_table_name].append_column(
        sqlalchemy.Column(
            f"{table_name}_id",
            sqlalchemy.Integer,
            sqlalchemy.ForeignKey(f"{table_name}.id"),
            nullable=False,
        )
    )

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
