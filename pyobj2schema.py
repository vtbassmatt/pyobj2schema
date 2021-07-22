'Convert a Python object into a relational schema.'
from decimal import Decimal
import logging

import sqlalchemy

logger = logging.getLogger(__name__)

def convert(object, hints={}):
    metadata = sqlalchemy.MetaData()

    if isinstance(object, dict):
        _convert_dict(object, metadata, hints)
    elif isinstance(object, list):
        _convert_list(object, metadata, hints)
    else:
        raise NotImplementedError('only dicts and lists are supported')

    return metadata


class ColumnAlreadyExists(RuntimeError): pass


def _convert_list(object, metadata, hints, name=None):
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
    
    for current in object:
        if scalar_name := hints.get(table_name, {}).get('data_name', None):
            logger.info(f"{table_name} data will be called {scalar_name}")
        else:
            scalar_name = 'data'

        if _handle_if_scalar(scalar_name, current, metadata.tables[table_name], hints):
            pass
        elif isinstance(current, dict):
            if '__name' not in current:
                first_prime = { '__name': table_name }
                first_prime.update(current)
                current = first_prime
            _convert_dict(current, metadata, hints)
        elif isinstance(current, list):
            # TODO: is there a better way to cook up a nested table name?
            nest_name = f"{table_name}_nested"
            _handle_if_list(nest_name, current, metadata, table_name, hints)
        else:
            raise NotImplementedError(f'items in table "{table_name}" are not in a format we understand')
    
    return table_name


def _convert_dict(object, metadata, hints):
    assert isinstance(object, dict)

    table_name = object.get('__name', 'objects')
    if table_name not in metadata.tables:
        logger.info(f"creating table {table_name}")
        table = sqlalchemy.Table(table_name, metadata)

        # determine if there's a non-default name for the primary key
        id_name = object.get('__id', 'id')
        hints.setdefault(table_name, {})
        hints[table_name]['id_name'] = id_name

        table.append_column(
            sqlalchemy.Column(
                id_name,
                sqlalchemy.Integer,
                primary_key=True,
            )
        )
    else:
        table = metadata.tables[table_name]

    for key, value in object.items():
        if key.startswith('__'):
            continue

        if _handle_if_scalar(key, value, metadata.tables[table_name], hints):
            pass
        elif _handle_if_list(key, value, metadata, table_name, hints):
            pass
        elif isinstance(value, dict):
            if '__name' not in value:
                v_prime = { '__name': key }
                v_prime.update(value)
                value = v_prime
            sub_table_name = _convert_dict(value, metadata, hints)
            id_name = hints.get(table_name, {}).get('id_name', 'id')
            metadata.tables[sub_table_name].append_column(
                sqlalchemy.Column(
                    f"{table_name}_id",
                    sqlalchemy.Integer,
                    sqlalchemy.ForeignKey(f"{table_name}.{id_name}"),
                    nullable=False,
                )
            )
        else:
            raise NotImplementedError(f'item at key "{key}" is not a format we understand')
    
    return table_name


def _handle_if_scalar(key, value, table, hints):
    column_exists = (key in table.columns)
    new_type = None

    hint_key = f"{table.name}.{key}"
    hint_type = hints.get(hint_key, {}).get('type', None)

    if hint_type:
        logger.info(f"{hint_key} using hinted type {hint_type}")
        new_type = hint_type
    elif isinstance(value, bool):
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
            logger.info(f"changing '{key}' type to '{new_type()}'")
            table.columns[key].type = new_type()
            return True

        # TODO: check more details like nullability
        if isinstance(table.columns[key].type, new_type):
            return True

        if new_type == sqlalchemy.Numeric and isinstance(table.columns[key].type, sqlalchemy.Integer):
            # it's safe to upgrade an integer to a decimal
            logger.info(f"upconverting '{key}' type from '{table.columns[key].type}' to '{new_type()}'")
            table.columns[key].type = new_type()
            return True

        raise ColumnAlreadyExists(key)

    else:
        table.append_column(sqlalchemy.Column(key, new_type))
    
    return True


def _handle_if_list(key, value, metadata, table_name, hints):
    if not isinstance(value, list):
        return False

    sub_table_name = _convert_list(value, metadata, hints, name=key)
    id_name = hints.get(table_name, {}).get('id_name', 'id')
    metadata.tables[sub_table_name].append_column(
        sqlalchemy.Column(
            f"{table_name}_id",
            sqlalchemy.Integer,
            sqlalchemy.ForeignKey(f"{table_name}.{id_name}"),
            nullable=False,
        )
    )

    return True
