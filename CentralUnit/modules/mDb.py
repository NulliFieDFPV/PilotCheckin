import MySQLdb
from config import cfg_db as dbconfig


class db(object):
    def __init__(self):

        pass

    def __connect(self):
        self.db = MySQLdb.connect(host=dbconfig.host,  # your host, usually localhost
                             user=dbconfig.user,  # your username
                             passwd=dbconfig.passwd,  # your password
                             db=dbconfig.db)  # name of the data base

        self.db.autocommit( True)

        cur=self.db.cursor(cursorclass=MySQLdb.cursors.DictCursor)

        return cur

    def query(self, sql):
        cur=self.__connect()

        cur.execute(sql)

        if sql[0:6]=="SELECT":
            res= cur.fetchall()
        else:
            res=cur.lastrowid

        self.__disconnect()

        return res

    def __disconnect(self):
        self.db.close()


mydb=db()

sql="SELECT * FROM tpilots"
mydb.query(sql)