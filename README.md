# pyobj2schema
Generate relational database schemas from Python objects.
Uses [SQLAlchemy](https://sqlalchemy.org) under the hood, to ensure you can use it with the database of your choice.

## Usage

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

```
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
