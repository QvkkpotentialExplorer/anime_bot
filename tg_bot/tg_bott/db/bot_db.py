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
        self.connection = self.get_connection()


    def get_connection(self):
         return sqlite3.connect(self.path_to_db)

    def execute(self, sql : str, params = None, fetchone = False, fetchall = False,commit = False ):
        if not params:
            params=()
        conn = self.connection
        parameters=params
        cursor = conn.cursor()
        conn.set_trace_callback(logger)
        data = None
        cursor.execute(sql,params)

        if commit:
            conn.commit()
            conn.close()
            self.connection = self.get_connection()
        if fetchone:
            data = cursor.fetchone()
        if fetchall:
            data =  cursor.fetchall()



        return data

    def create_table(self):
        sql_cmd = ["""
        CREATE TABLE IF NOT EXISTS users(
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        chat_id INTEGER NOT NULL
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS anime(
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        href TEXT,
        anime_name TEXT,
        episodes TEXT,
        flag BOOL
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS users_anime(
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        anime_id INTEGER,
        FOREIGN KEY ('user_id') REFERENCES users('id'),
        FOREIGN KEY ('anime_id') REFERENCES anime('id') 
        );
        """]
        for sql in sql_cmd:
            self.execute(sql = sql,commit=True)

    def add_user(self,chat_id:int):
        sql = """SELECT * FROM users where chat_id = ?"""

        if not self.execute(sql=sql,fetchone=True,params = (chat_id,)) :
            print(self.execute(sql=sql,fetchone=True,params = (chat_id,)))
            user_id = self.execute(sql="""
                INSERT INTO users(chat_id) VALUES({?}) RETURNING id ;
                """, params=(chat_id,), fetchone=True)[0]
            return user_id
        else:
            user_id = self.execute(sql = """SELECT id FROM users where chat_id = ?""",fetchone=True,params = (chat_id,))[0]
            return user_id


        # else:
        #
    def add_anime(self,href : str):
        if not self.execute(sql = """SELECT * FROM anime where href = ? """,fetchone=True,params=(href,)):
            anime_id = self.execute(sql="""INSERT INTO anime(href) VALUES(?) RETURNING id ;
                        """, params=(href,),fetchone=True)[0]

            return anime_id
        else :
            anime_id = self.execute(sql=""""SELECT id FROM anime where href = ?""", fetchone=True, params=(href,))[0]
            return anime_id

    def add_users_anime(self,user_id,anime_id):
        if not self.execute(sql = "SELECT * FROM users_anime where user_id = ? and anime_id = ? ",fetchone=True,params=(user_id,anime_id,)):
            self.execute(sql="""INSERT INTO users_anime(user_id,anime_id) VALUES(?,?) ;
                        """, params=(user_id,anime_id),commit = True)

    def get_info(self,chat_id):
        if not self.execute(sql = "SELECT * FROM ")







