import MySQLdb



#DB config here
config = {
  'user': 'root',
  'password': 'root',
  'host': '127.0.0.1',
  'database': 'monster',
  'raise_on_warnings': True,
}


#Class to handle database
class MySqlDBFetcher:
  conn = None

  def connect(self):
    self.conn = MySQLdb.connect(
          host=config['host'],
          user=config['user'],
          passwd=config['password'],
          db=config['database']
    )


  def fetchDBdetailsforTimeStamp(self, sql):
    try:
      cursor = self.conn.cursor()
      cursor.execute(sql)
    except (AttributeError, MySQLdb.OperationalError):
      self.connect()
      cursor = self.conn.cursor()
      cursor.execute(sql)

    return cursor



