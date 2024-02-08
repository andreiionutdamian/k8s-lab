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
    
  
  def _maybe_setup_postgres(self):
    dct_pg = {k : v for k, v in os.environ.items() if k.startswith("POSTGRES_")}
    self._has_postgres = False
    if len(dct_pg) > 0:
      self.P("Setting up Postgres with configuration:\n{}".format(safe_jsonify(dct_pg)))
      postgres_host = dct_pg.get("POSTGRES_SERVICE_HOST")
      postgres_port = dct_pg.get("POSTGRES_SERVICE_PORT", 5432)
      postgres_user = dct_pg.get("POSTGRES_USER")
      postgres_password = dct_pg.get("POSTGRES_PASSWORD")
      self.P("Connecting to Postgres at {}:{} with user: {}".format(
        postgres_host, postgres_port, postgres_user
      ))
      self.__pg = psycopg2.connect(
        host=postgres_host, port=postgres_port,
        user=postgres_user, password=postgres_password
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
    return  
  
  
  def postgres_insert_data(self, table_name : str, **kwargs):
    # insert into table_name the key-value pairs in kwargs
    if self._has_postgres:
      str_sql = f"INSERT INTO {table_name} ({','.join(kwargs.keys())}) VALUES ({','.join(kwargs.values())});"
      with self.__pg.cursor() as cur:
        cur.execute(str_sql)
        self.__pg.commit()
    return
  
  def postgres_select_data(self, table_name : str, **kwargs):
    # select from table_name based on the kwargs filter
    result = None
    if self._has_postgres:
      str_sql = f"SELECT * FROM {table_name}"
      if len(kwargs) > 0:
        str_sql += " WHERE {kwargs.keys()} = {kwargs.values()};"
      with self.__pg.cursor() as cur:
        cur.execute(str_sql)
        rows = cur.fetchall()
        result = rows
    return result
  
  def postgres_select_counts(self, table_name : str, group_by : str):
    result = None
    if self._has_postgres:
      str_sql = f"SELECT {group_by}, COUNT(*) FROM {table_name} GROUP BY {group_by};"
      with self.__pg.cursor() as cur:
        cur.execute(str_sql)
        rows = cur.fetchall()
        result = rows
    return result
  
  
  def postgres_get_count(self, table_name : str):
    result = None
    if self._has_postgres:
      str_sql = f"SELECT COUNT(*) FROM {table_name};"
      with self.__pg.cursor() as cur:
        cur.execute(str_sql)
        rows = cur.fetchall()
        result = rows
    return result