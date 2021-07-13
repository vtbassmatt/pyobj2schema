# pyobj2schema
Generate relational database schemas from Python objects.
Uses [SQLAlchemy](https://sqlalchemy.org) under the hood, to ensure you can use it with the database of your choice.

## Basic usage

```python
from pyobj2schema import convert
from sqlalchemy.schema import CreateTable
from sqlalchemy.dialects import sqlite

o = {
  'foo': 'this is clearly a string',
  'bar': 42,
  'baz': True,
  'other': {
    'one': 1.0,
    'two': 'two',
  },
}

metadata = convert(o)
for table in metadata.sorted_tables:
    ct = CreateTable(table)
    print(ct.compile(dialect=sqlite.dialect()))
```

This will give you a result of:

```sql
CREATE TABLE objects (
	id INTEGER NOT NULL, 
	foo TEXT, 
	bar INTEGER, 
	baz BOOLEAN, 
	PRIMARY KEY (id)
)

CREATE TABLE other (
	id INTEGER NOT NULL, 
	one FLOAT, 
	two TEXT, 
	objects_id INTEGER NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(objects_id) REFERENCES objects (id)
```

## Extended usage

### Naming tables

In any `dict`, you can add a `__name` key which will be used to name the resulting table.

### Hints

You can give the parser some hints about how to convert your objects.
The `convert` function takes an optional `hints` parameter.
`hints` is a `dict` of `f"{table_name}.{column_name}` -> `dict` mappings.

Currently, the only supported hint is `type`, which must be a SQLAlchemy type.

```python
o = {
  'foo': 'this is clearly a string',
  'bar': 42,
}
hints = {
	'objects.bar': sqlalchemy.Numeric,
}

metadata = convert(o, hints)
for table in metadata.sorted_tables:
    ct = CreateTable(table)
    print(ct.compile(dialect=sqlite.dialect()))
```

yields

```sql
CREATE TABLE objects (
	id INTEGER NOT NULL, 
	foo TEXT, 
	bar NUMERIC, 
	PRIMARY KEY (id)
)
```

Two caveats:
1. There's no checking or comparison against the data in the field.
If you say it's a `Numeric` when it's actually `Text`, the parser trusts the hint.
2. You can use SQLAlchemy types that the parser otherwise won't emit.
For example, it makes no attempt to detect dates, UUIDs, or other structured data.
