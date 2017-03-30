import MySQLdb
import time
import datetime

#
#DB-schema config here
#
config = {
  'user': 'root',
  'password': 'root',
  'host': '127.0.0.1',
  'database': 'monster',
  'raise_on_warnings': True
}


#
#Class to handle database
#
class MySqlDBFetcher:
  conn = None

  def connect(self):
    self.conn = self.conn or MySQLdb.connect(
          host=config['host'],
          user=config['user'],
          passwd=config['password'],
          db=config['database']
    )




#
#
#
  def fetchDBdetailsforTimeStamp(self, sql):
    try:
      cursor = self.conn.cursor()
      cursor.execute(sql)
    except (AttributeError, MySQLdb.OperationalError):
      self.connect()
      cursor = self.conn.cursor()
      cursor.execute(sql)
    return cursor




#
#
#
  def fillDBwithDetails(self,jobDetailList):

    self.connect()
    cursor = self.conn.cursor()
    ts = time.time()
    print('Trying insert!!')
    listInsert = []
    jobDetailList= self.filterInputData(jobDetailList)
    for row in jobDetailList:
        job_title = row[1]
        company = row[2]
        location = row[3]
        timestamp = row[4]
        fileName = row[5]
        timestamp = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M")

        listInsert.append((0, str(job_title), str(company), str(location), timestamp.strftime('%Y-%m-%d'),
                           str(fileName), "monster"))

    sql = """ insert ignore into jobs_raw (
                id, job_title, company_name, location, register_date,text_file,source )
                values (%s,%s,%s,%s,%s,%s,%s)
            """

    try:
        cursor.executemany(sql,listInsert)
        print('inserted all trying commit')
        print('commit success')
        self.conn.commit()
    except (AttributeError, MySQLdb.OperationalError):
        self.rollbackandReconnect()
        cursor = self.conn.cursor()
        cursor.executemany(sql, listInsert)
    except Exception as e:
        print('Exception as '+str(e))
        self.rollbackandReconnect()
        cursor = self.conn.cursor()
        cursor.executemany(sql, listInsert)
        print(e)
    return cursor



  def rollbackandReconnect(self):
    self.conn.rollback()
    self.connect()

  def disconnect(self):
      self.conn.close()



  def filterInputData(self,inputDataList):
      for i in range(len(inputDataList)):
          if(len(inputDataList(i))!=6):
              print('Cleaning item - ')
              print(inputDataList[i])
              inputDataList.pop(i)
      return  inputDataList


# if __name__ == '__main__':
#     db=MySqlDBFetcher()
#     db.connect()
#     cur = db.conn.cursor()
#     jobDetailList=[]
#     jobDetailList.append([0, "J2eeJava Softwanasdre Developer required ASAP", "Magnuasdm Hunt", "North asdYork, ON", "J2ee.txt"])
#
#     listInsert=[]
#     for row in jobDetailList:
#         job_title = row[1]
#         company = row[2]
#         location = row[3]
#         fileName = row[4]
#         listInsert.append((0,str(job_title), str(company),str(location), "STR_TO_DATE('1-01-2012', '%d-%m-%Y')",str(fileName), "monster"))
#
#
#     batchInsertQuery = """ insert ignore into jobs_raw (
#             id, job_title, company_name, location, register_date,text_file,source )
#             values (%s,%s,%s,%s,%s,%s,%s)
#         """
#
#
#     try:
#         print("Batch Insert - "+batchInsertQuery)
#         print(listInsert)
#
#         cur.executemany(q, listInsert)
#         db.conn.commit()
#     except Exception as e:
#         print(e)
#         db.conn.rollback()
