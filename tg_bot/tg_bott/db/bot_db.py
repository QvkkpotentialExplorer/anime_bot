import aiosqlite


def logger(statement):
    print(f"""
------------------------------------
Executing :
{statement}
------------------------------------
    """)


class DataBase:
    def __init__(self, path_to_db='./bot.db'):
        self.path_to_db = path_to_db

    @property
    async def connection(self):
        conn = aiosqlite.connect(self.path_to_db)
        await conn.__aenter__()
        return conn

    async def execute(self, sql: str, params=tuple(), fetchone=False, fetchall=False, commit=False):
        print(sql, params)
        conn = await self.connection
        await conn.set_trace_callback(logger)
        cursor = await conn.cursor()
        data = None
        await cursor.execute(sql, params)

        if fetchone:
            data = await cursor.fetchone()
        if fetchall:
            data = await cursor.fetchall()
        if commit:
            await conn.commit()
        await conn.close()
        return data

    async def create_table(self):
        sql_cmd = [
            "CREATE TABLE IF NOT EXISTS users(id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,chat_id INTEGER NOT NULL);",
            "CREATE TABLE IF NOT EXISTS anime(id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,href TEXT,anime_name TEXT,episodes TEXT,flag BOOL);",
            "CREATE TABLE IF NOT EXISTS users_anime(id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,user_id INTEGER,anime_id INTEGER,FOREIGN KEY ('user_id') REFERENCES users('id'),FOREIGN KEY ('anime_id') REFERENCES anime('id') );"
        ]
        for sql in sql_cmd:
            await self.execute(sql=sql, commit=True)

    async def add_user(self, chat_id: int):
        sql = """SELECT 21 FROM users where chat_id = ?"""

        if not await self.execute(sql=sql, fetchone=True, params=(chat_id,)):
            print(await self.execute(sql=sql, fetchone=True, params=(chat_id,)))
            user_id = await self.execute(sql="""INSERT INTO users(chat_id) VALUES(?) RETURNING id ;""",
                                         params=(chat_id,),
                                         fetchone=True,
                                         commit=True)
            return user_id[0]
        else:
            user_id = await self.execute(sql="""SELECT id FROM users where chat_id = ?""",
                                         fetchone=True,
                                         params=(chat_id,))
            return user_id[0]

    async def add_anime(self, href: str):
        res = await self.execute(sql="""SELECT * FROM anime WHERE href = ? """, fetchone=True, params=(href,))
        if not res:
            anime_id = await self.execute(sql="""INSERT INTO anime(href) VALUES(?) RETURNING id ;""",
                                          params=(href,),
                                          fetchone=True,
                                          commit=True
                                          )
            return anime_id[0]
        else:
            anime_id = await self.execute(sql="""SELECT id FROM anime WHERE href = ?;""", fetchone=True, params=(href,))
            return anime_id[0]

    async def add_users_anime(self, user_id, anime_id):
        check = await self.execute(sql="SELECT * FROM users_anime WHERE user_id = ? and anime_id = ?;",
                                   fetchone=True,
                                   params=(user_id, anime_id,))
        if not check:
            await self.execute(sql="""INSERT INTO users_anime(user_id, anime_id) VALUES(?, ?);""",
                               params=(user_id, anime_id,),
                               commit=True)
            return True
        else:
            return False
