# DuckdbIS

This package allows for easier transactions with Duckdb databases.  The class is used to link to the database file path.  

## Install

Install with pip from the wheel at the directory

`pip install DuckdbIS-x.x.x-py3-none-any.whl` 

Create new wheels with

`python setup.py bdist_wheel`

### Dependencies

- duckdb
- pandas
- time

## Use

``` python
from DuckdbIS import DuckDatabase
mydb = DuckDatabase("path/file.db")
```

As of v0.3 this class can be used with databases in memory (previously the database was disconnected and destroyed after each use).  

``` python
from DuckdbIS import DuckDatabase
mydb = DuckDatabase(":memory:")
```



## Querying the database

Whenever a query is used, (`.query()` or `.execute()`) the class will open and close a connection to the database unless it is in memory.  This is useful as Duckdb databases can only have one simultaneous connection, so this functionality allows for multiple users.  If the database is in use it will attempt to open a connection three times before erroring.

Select queries (using `.query()`) return a pandas dataframe for the results.  
