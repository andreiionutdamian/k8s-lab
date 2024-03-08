import os
import psycopg2

from app_utils import safe_jsonify

class _PostgresMixin(object):
  def __init__(self):
    super(_PostgresMixin, self).__init__()
    
    self.__pg = None
    self.__connects = 0
    self.__config = self.__get_postgres_config()
    self._has_postgres = False
    self.P("Postgres init-config done: {} keys".format(len(self.__config)))
    return
    
    
  def __get_postgres_config(self):
    dct_pg = {k : v for k, v in os.environ.items() if k.startswith("POSTGRES_")}
    return dct_pg


  @property
  def postgres_alive(self):
    alive = False
    if self._has_postgres:
      self.postgres_maybe_reconnect()
      alive = self._has_postgres
    return alive

  
  @property
  def postgres_config_available(self):
    return len(self.__config) > 0

  
  def postgres_get_tables_definitions(self): 
    """
    This method returns a dictionary with table names as keys and the fields as values
    so that the tables can be created if they do not exist.
    
    OBS: This method should be implemented in the class that uses this mixin.
    """
    raise NotImplementedError("Method `postgres_get_tables_definitions` not implemented")

  
  def __maybe_create_tables(self):
    # first get methods for table definition:
    SIGNATURE_PREFIXES = ['postgres_get_table', 'postgres_get_ddl']
    props = dir(self)
    ddl_func = None
    methods = []
    for prop in props:
      for prefix in SIGNATURE_PREFIXES:
        if prop.startswith(prefix):
          methods.append(prop)
    if len(methods) > 1:
      raise ValueError("Multiple methods found for table definition: {}".format(methods))
    elif len(methods) == 1:
      ddl_func = getattr(self, methods[0])
    if self._has_postgres and ddl_func is not None:      
      dct_tables = ddl_func()
      for table in dct_tables:
        fields = dct_tables[table]
        self.P("Maybe creating postgres table '{}' with fields {}".format(table, fields))
        query = "CREATE TABLE IF NOT EXISTS {} ({});".format(table, fields)
        with self.__pg.cursor() as cur:
          cur.execute(query)
          self.__pg.commit()        
    return

  
  def _maybe_setup_postgres(self):
    self._has_postgres = False
    self.__connects += 1
    if self.postgres_config_available:
      try:
        dct_pg = self.__config
        self.P("Setting up Postgres with configuration:\n{}".format(safe_jsonify(dct_pg)))
        postgres_host = dct_pg.get("POSTGRES_SERVICE_HOST")
        postgres_port = dct_pg.get("POSTGRES_SERVICE_PORT")
        postgres_user = dct_pg.get("POSTGRES_USER")
        postgres_password = dct_pg.get("POSTGRES_PASSWORD")
        postgres_db = dct_pg.get("POSTGRES_DB")
        if postgres_host is None or postgres_port is None or postgres_user is None or postgres_password is None or postgres_db is None:
          self.P("Incomplete Postgres configuration. Skipping Postgres setup.")
        else:
          self.__config_available = True
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
          self._has_postgres = True
          self.__maybe_create_tables()
          # now we get the tables from the database
          tables = self.postgres_get_tables()
          self.P("Tables in the database: {}".format(tables))
          #end with cursor check tables
        #end if posgres env vars
      except Exception as e:
        self.P("Error in _maybe_setup_postgres: {}".format(e))    
    return  
  
  
  def postgres_maybe_connect(self):
    if not self._has_postgres and self.postgres_config_available:
      if self.__connects == 0:
        self.P("First time connecting attempt to Postgres...")
      else:
        self.P("Connecting attempt {} to Postgres...".format(self.__connects))
      self._maybe_setup_postgres()
    return
  
  def is_connection_still_alive(self):
    result = False
    try:
      # Use a simple query to check the connection
      with self.__pg.cursor() as cur:
        cur.execute("SELECT 1")
      result = True
    except Exception as exc:
      self.P("Connection to Postgres is dead. Reconnecting is required...")
      self._has_postgres = False
    return result
  
  
  def postgres_maybe_reconnect(self):
    if self._has_postgres:
      if not self.is_connection_still_alive():
        self.postgres_maybe_connect()
    return
  
  
  
  def postgres_insert_data(self, table_name: str, **kwargs):
    if self._has_postgres:
      try:
        self.postgres_maybe_reconnect()
        columns = ', '.join(kwargs.keys())
        placeholders = ', '.join(['%s'] * len(kwargs))
        values = tuple(kwargs.values())
        str_sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        with self.__pg.cursor() as cur:
          cur.execute(str_sql, values)
          self.__pg.commit()
      except Exception as exc:
        self.P("Error in postgres_insert_data: {}".format(exc))     
        raise ValueError("Postgres issue")   
    return

  
  def postgres_select_data(self, table_name: str, **kwargs):
    result = None
    if self._has_postgres:
      try:
        self.postgres_maybe_reconnect()
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
      except Exception as exc:
        self.P("Error in postgres_select_data: {}".format(exc))
        raise ValueError("Postgres issue")
    return result


  def postgres_select_counts(self, table_name : str, group_by : str):
    result = None
    if self._has_postgres:
      try:
        self.postgres_maybe_reconnect()
        str_sql = f"SELECT {group_by}, COUNT(*) FROM {table_name} GROUP BY {group_by};"
        with self.__pg.cursor() as cur:
          cur.execute(str_sql)
          rows = cur.fetchall()
          result = rows
      except Exception as exc:
        self.P("Error in postgres_select_counts: {}".format(exc))
        raise ValueError("Postgres issue")
    return result
    
  
  def postgres_get_count(self, table_name : str):
    result = None
    if self._has_postgres:
      try:
        self.postgres_maybe_reconnect()
        str_sql = f"SELECT COUNT(*) FROM {table_name};"
        with self.__pg.cursor() as cur:
          cur.execute(str_sql)
          rows = cur.fetchall()
          result = rows[0][0]
      except Exception as exc:
        self.P("Error in postgres_get_count: {}".format(exc))
        raise ValueError("Postgres issue")
    return result
  
  
  def postgres_get_tables(self):
    result = {}
    if self._has_postgres:
      try:
        self.postgres_maybe_reconnect()
        with self.__pg.cursor() as cur:
          cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
          rows = cur.fetchall()
          for row in rows:
            table_name = row[0]
            cur.execute(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table_name}';")
            fields = cur.fetchall()
            result[table_name] = fields
      except Exception as exc:
        self.P("Error in postgres_get_tables: {}".format(exc))
        raise ValueError("Postgres issue")
    return result
  
  
  
  def postgres_insert(self, table_name : str, **kwargs):
    return self.postgres_insert_data(table_name, **kwargs)
  
  def postgres_select(self, table_name : str, **kwargs):
    return self.postgres_select_data(table_name, **kwargs)

  def postgres_group_count(self, table_name : str, group_by : str):
    return self.postgres_select_counts(table_name, group_by)
  
  