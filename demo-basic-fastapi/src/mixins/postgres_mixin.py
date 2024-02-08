import os
import psycopg2

from app_utils import safe_jsonify

class _PostgresMixin:
  def __init__(self, *args, **kwargs):
    self.__pg = None
    return
  
# PostgreSQL
    
  def __maybe_create_tables(self):
    if self._has_postgres:
      with self.__pg.cursor() as cur:
        cur.execute("CREATE TABLE IF NOT EXISTS requests (id SERIAL PRIMARY KEY, hostname varchar(200), data varchar(255));")
        self.__pg.commit()
        
    return
  
  def __get_postgres_config(self):
    dct_pg = {k : v for k, v in os.environ.items() if k.startswith("POSTGRES_")}
    return dct_pg
  
  def _maybe_setup_postgres(self):
    dct_pg = self.__get_postgres_config()
    self._has_postgres = False
    if len(dct_pg) > 0:
      try:
        self.P("Setting up Postgres with configuration:\n{}".format(safe_jsonify(dct_pg)))
        postgres_host = dct_pg.get("POSTGRES_SERVICE_HOST")
        postgres_port = dct_pg.get("POSTGRES_SERVICE_PORT")
        postgres_user = dct_pg.get("POSTGRES_USER")
        postgres_password = dct_pg.get("POSTGRES_PASSWORD")
        postgres_db = dct_pg.get("POSTGRES_DB")
        if postgres_host is None or postgres_port is None or postgres_user is None or postgres_password is None or postgres_db is None:
          self.P("Incomplete Postgres configuration. Skipping Postgres setup.")
        else:
          hidden_password = postgres_password[:2] + "*" * (len(postgres_password) - 4) + postgres_password[-2:]
          self.P("Connecting to Postgres at {}:{} on db '{}' with user: `{}`, pass: {}".format(
            postgres_host, postgres_port, postgres_db, 
            postgres_user, hidden_password,
          ))
          self.__pg = psycopg2.connect(
            host=postgres_host, port=postgres_port,
            user=postgres_user, password=postgres_password,
            dbname=postgres_db,
          )
          pg_server_info = self.__pg.get_dsn_parameters()
          self.P("Connected to Postgres at {}:{} with user: {} to database: {}".format(
            pg_server_info['host'], pg_server_info['port'], 
            pg_server_info['user'], pg_server_info['dbname'],
          ))
          self.__maybe_create_tables()
          # now we get the tables from the database
          with self.__pg.cursor() as cur:
            cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
            rows = cur.fetchall()
            self.P("Tables in the database: {}".format(rows))
          self._has_postgres = True
      except Exception as e:
        self.P("Error in _maybe_setup_postgres: {}".format(e))    
    return  
  
  
  def postgres_insert_data(self, table_name: str, **kwargs):
    if self._has_postgres:
      try:
        columns = ', '.join(kwargs.keys())
        placeholders = ', '.join(['%s'] * len(kwargs))
        values = tuple(kwargs.values())
        str_sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        with self.__pg.cursor() as cur:
            cur.execute(str_sql, values)
            self.__pg.commit()
      except Exception as e:
        self.P("Error in postgres_insert_data: {}".format(e))     
        raise ValueError("Postgres issue")   
    return

  
  def postgres_select_data(self, table_name: str, **kwargs):
    result = None
    if self._has_postgres:
      try:
        str_sql = f"SELECT * FROM {table_name}"
        parameters = []
        if kwargs:
          where_clauses = []
          for key, value in kwargs.items():
            where_clauses.append(f"{key} = %s")
            parameters.append(value)
          where_statement = ' AND '.join(where_clauses)
          str_sql += f" WHERE {where_statement}"
        with self.__pg.cursor() as cur:
          cur.execute(str_sql, parameters)
          rows = cur.fetchall()
          result = rows
      except Exception as e:
        self.P("Error in postgres_select_data: {}".format(e))
        raise ValueError("Postgres issue")
    return result


  def postgres_select_counts(self, table_name : str, group_by : str):
    result = None
    if self._has_postgres:
      try:
        str_sql = f"SELECT {group_by}, COUNT(*) FROM {table_name} GROUP BY {group_by};"
        with self.__pg.cursor() as cur:
          cur.execute(str_sql)
          rows = cur.fetchall()
          result = rows
      except:
        self.P("Error in postgres_select_counts: {}".format(e))
        raise ValueError("Postgres issue")
    return result
    
  
  def postgres_get_count(self, table_name : str):
    result = None
    if self._has_postgres:
      try:
        str_sql = f"SELECT COUNT(*) FROM {table_name};"
        with self.__pg.cursor() as cur:
          cur.execute(str_sql)
          rows = cur.fetchall()
          result = rows
      except Exception as e:
        self.P("Error in postgres_get_count: {}".format(e))
        raise ValueError("Postgres issue")
    return result

  
  def postgres_insert(self, table_name : str, **kwargs):
    return self.postgres_insert_data(table_name, **kwargs)
  
  def postgres_select(self, table_name : str, **kwargs):
    return self.postgres_select_data(table_name, **kwargs)

  def postgres_group_count(self, table_name : str, group_by : str):
    return self.postgres_select_counts(table_name, group_by)
  
  