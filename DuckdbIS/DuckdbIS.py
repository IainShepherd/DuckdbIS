'''
v0.3.0
Last updated: 30/08/2022
Developer: Iain Shepherd

Use
from DuckdbIS import DuckDatabase
'''

import duckdb
import pandas as pd
import time

#duckq = lambda x: duckdb.query(x).to_df()

class DuckDatabase():
    def __init__(self, databaseloc: str):
        self.databaseloc = databaseloc
        self.conn = None
        self.threads = 1
        self.__backup_query = self.query
        if self.databaseloc == ":memory:":
            self.in_memory = True
            self.conn = duckdb.connect(self.databaseloc)
        else:
            self.in_memory = False
        
    def connect(method):
        def inner(self, *args, **kwargs):
            if self.in_memory == True:
                return method(self, *args, **kwargs)

            conn = self.create_conn()
            next(conn)
            try:
                a = method(self, *args, **kwargs)
            except:
                conn = None
                raise
            return a
        return inner
    
    def create_conn(self):      
        # Useful if several users are using the same database to avoid a locked db
        trys = 0
        Ntrys = 3
        while trys < Ntrys:
            try: 
                self.conn = duckdb.connect(self.databaseloc)
                break
            except:
                trys += 1
                if trys == Ntrys:
                    print("Database locked")
                    raise
                print(f"Connection to {self.databaseloc} locked, will try again")
                if trys == Ntrys-1: print("Last attempt")
                time.sleep(trys**2)
                
        if self.threads > 1: self.conn.execute(f"PRAGMA threads={self.threads}")
        try:
            yield
        finally:
            self.conn.close()
            self.conn = None

    def sqlprotect(self, inject:str) -> str:
        r"""use on injections strings to prevent SQL injection attacks on the database
        
        inject: str; string to be injected into a SQL query
        """
        output = inject
        for n, i in enumerate(inject):
            if i == "'":
                output = output[0:n] + "'" + inject[n:] 
        return output
    
    @connect
    def execute(self, query: str):
        self.conn.execute(query)
        self.conn.commit()
        return self.conn.fetchall()
    
    @connect
    def query(self, query: str):
        r"""Returns a pandas dataframe of the select query results
        query: str; SQL select query
        """
        return self.conn.query(query).to_df()
    
    @connect
    def queryNorm(self, query: str):
        r"""Returns the duckdb default for a select query
        query: str; SQL select query
        """
        return self.conn.query(query)
    
    @connect
    def execute_many(self, queries):
        r"""Use to execute many queries via one connection to the database
        queries: list; List of strings of SQL queries
        """
        for q in queries:
            self.conn.execute(q)
        self.conn.commit()
        return self.conn.fetchall()
    
        
    def get_layout(self) -> dict:
        r"""Returns the layout (as a dict) of the database.  
        {Table1: [column1, column2, ], }"""

        prag = "pragma show_tables"
        tbls = [x[0] for x in self.execute(prag)]
        layout = {}
        for t in tbls:
            layout[t] = [x[1] for x in self.execute(f"PRAGMA table_info('{t}')")]
        return layout
    
    def print_layout(self):
        r"""Prints the layout of the database to terminal"""

        dic = self.get_layout()
        for tbl in dic.keys():
            print(tbl, end = "\n-------\n")
            for h in dic[tbl]:
                print(h)
            print("\n")
            
    def append_df(self, _df_: str, tbl_name: str):
        r"""Appends all the data from a dataframe to a table

        _df_: str; the string of the dataframe object; note that no object can be named "_df_"
        tbl_name: str; the string of the existing table name within the database
        """
        if _df_ == "_df_":
            print("ERROR: `_df_` cannot equal '_df_")
            raise
        _df_ = self.sqlprotect(_df_)
        tbl_name = self.sqlprotect(tbl_name)
        return self.execute(f"""insert into "{tbl_name}" select * from {_df_}""")
    
    def createtbl_from_df(self, df: pd.DataFrame, tblName: str):
        r"""Creates a new table in the database from a dataframe including transfering column types
        
        df: pandas dataframe object; the dataframe to create the new table but does not add the data. The index is not used.  
        tblName: str; The name of the new table to create
        """

        tblName = self.sqlprotect(tblName)
        tblName = self.clean_column_names(tblName)
        typelkup = {"object":"text", "float64": "float", 'int64' : 'bigint', 'bool': 'boolean'}
        q = f"Create table {tblName} ("
        for col in df.columns:
            typel=df[col].dtype.__str__()
            col = self.sqlprotect(col)
            self.clean_column_names(col)
            q += f"{col} {typelkup.get(typel, 'text')}, "
        q = q[:-2]
        q += ")"
        print(q)
        return self.execute(q)



    def activate_select_cache(self, deactivate: bool = False):
        def cache_select(f):
            self.cache={}
            def inner(*args):
                if args not in self.cache:
                    self.cache[args]=f(*args)
                else:
                    print("INFO: From memory\n")
                return self.cache[args]
            return inner

        if deactivate:
            self.query = self.__backup_query
            return self
        self.query = cache_select(self.query)
        return self

    def find_replace(self, inject: str, replace: str or list, replace_with: str) -> str:
        if type(replace) is str:
            replace = list(replace)
        output = inject
        for n, L in enumerate(inject):
            if L in replace:
                output = output[0:n] + replace_with + inject[n+1:]
        return output

    def find_replace_defined(self, replace, replace_with):
        def inner(inject):
            return self.find_replace(inject, replace, replace_with)
        return inner
    
    def clean_column_names(self):
        return self.find_replace_defined([" ", "(", ")", "-"], "_")