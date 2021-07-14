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

More examples can be found if you run `examples.py`:
```shell
% LOGLEVEL=info python examples.py
```

## Extended usage

### Naming tables

In any `dict`, you can add a `__name` key which will be used to name the resulting table.

### Hints

You can give the parser some hints about how to convert your objects.
The `convert` function takes an optional `hints` parameter.
`hints` is a `dict` of identifier -> `dict` mappings.

#### Type
The first supported hint is `type`, which must be a SQLAlchemy type.
The expected identifier is `f"{table_name}.{column_name}"`, and the hint name is `type`.

```python
o = {
  'foo': 'this is clearly a string',
  'bar': 42,
}
hints = {
	'objects.bar': {
		'type': sqlalchemy.Numeric,
	},
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
	bar NUMERIC, -- this would have been INTEGER by default
	PRIMARY KEY (id)
)
```

Two caveats:
1. There's no checking or comparison against the data in the field.
If you say it's a `Numeric` when it's actually `Text`, the parser trusts the hint.
2. You can use SQLAlchemy types that the parser otherwise won't emit.
For example, it makes no attempt to detect dates, UUIDs, or other structured data.

#### Naming inner list data

When an object points to data that's a list, a second table is created to hold that list.
By default, the data is stored in a column called `data`, but you can override that with a hint.
The hint identifier is the table name and the hint name is `data_name`.

```python
o = {
  'others': [
		'a',
		'b',
		'c'
	],
}
hints = {
	'others': {
		'data_name': 'letter',
	},
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
	PRIMARY KEY (id)
)

CREATE TABLE others (
	id INTEGER NOT NULL, 
	_order INTEGER, 
	letter TEXT, -- this would have been called `data` by default
	objects_id INTEGER NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(objects_id) REFERENCES objects (id)
)
```
