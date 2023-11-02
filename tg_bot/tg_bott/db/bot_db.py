import sqlite3

def logger(statement):
    print(f"""
------------------------------------
Executing :
{statement}
------------------------------------
    """)


class DataBase():
    def __init__(self,path_to_db = './bot.db'):
        self.path_to_db = path_to_db

    @property
    def connection(self):
         return sqlite3.connect(self.path_to_db)

    def execute(self, sql : str, parameters = None, fetchone = False, fetchall = False,commit = False ):
        if not parameters:
            parameters=()
        conn = self.connection
        parameters=parameters
        cursor = conn.cursor()
        conn.set_trace_callback(logger)
        data = None
        cursor.execute(sql,parameters)

        if commit:
            conn.commit()
        if fetchone:
            data = cursor.fetchone()
        if fetchall:
            data =  cursor.fetchall()

        conn.close()
        return data

    def create_table(self):
        sql_cmd = """
        CREATE TABLE IF NOT EXISTS Users(
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        chat_id INTEGER NOT NULL
        );
        """
        self.execute(sql = sql_cmd,commit=True)

    def add(self,chat_id:int):
        sql = """SELECT 1 FROM Users where id == {key}""".format(key = chat_id)
        if not self.execute(sql=sql) :
            sql_cmd = """
            INSERT INTO Users(chat_id) VALUES({chat_id});
            """.format(chat_id=chat_id)

            self.execute(sql = sql_cmd,commit = True)
