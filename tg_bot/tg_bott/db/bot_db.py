import aiosqlite


def logger(statement):
    print(f"""
------------------------------------
Executing :
{statement}
------------------------------------
    """)


class DataBase:
    def __init__(self, path_to_db='C:/Users/MaxIg/PycharmProjects/anime_bot/tg_bot/bot.db'):
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
            "CREATE TABLE IF NOT EXISTS anime(id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,href TEXT,name TEXT,episodes TEXT,flag BOOL);",
            "CREATE TABLE IF NOT EXISTS users_anime(id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,user_id INTEGER,anime_id INTEGER,FOREIGN KEY ('user_id') REFERENCES users('id'),FOREIGN KEY ('anime_id') REFERENCES anime('id') );",
            "CREATE TABLE IF NOT EXISTS series(id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,href TEXT,name TEXT,episodes TEXT,flag BOOL);",
            "CREATE TABLE IF NOT EXISTS users_series(id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,user_id INTEGER,series_id INTEGER,FOREIGN KEY ('user_id') REFERENCES users('id'),FOREIGN KEY ('series_id') REFERENCES series('id') );"
        ]
        for sql in sql_cmd:
            await self.execute(sql=sql, commit=True)

    async def add_user(self, chat_id: int):
        sql = """SELECT id FROM users where chat_id = ?"""

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

    async def add_title(self, href: str, name: str, episodes: str,type : str):#type - категория , с которой производятся манпиуляции(anime,series)
        res = await self.execute(sql="""SELECT * FROM anime WHERE href = ? """, fetchone=True, params=(href,))
        if not res:
            anime_id = await self.execute(
                sql=f"""INSERT INTO {type}(href, name, episodes) VALUES(?,?,?) RETURNING id ;""",
                params=(href, name, episodes),
                fetchone=True,
                commit=True
            )
            return anime_id[0]
        else:
            anime_id = await self.execute(sql=f"""SELECT id FROM {type} WHERE href = ?;""", fetchone=True, params=(href,))
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

    async def select_users_animes(self, chat_id):
        sql = """SELECT id FROM users where chat_id = ?"""
        print(await self.execute(sql=sql, fetchone=True, params=(chat_id,)))
        if not await self.execute(sql=sql, fetchone=True,
                                  params=(chat_id,)):  # Проверка на то , что у user есть аниме в users_anime
            return False
        else:
            user_id = await self.execute(sql=sql, fetchone=True, params=(chat_id,))
            print(user_id[0])
            anime_id = await self.execute(sql="SELECT anime_id FROM users_anime WHERE user_id = ?", fetchall=True,
                                          params=(user_id[0],))  # Достаем из таблички users_anime все anime_id
            if anime_id:
                animes_id = [id[0] for id in anime_id]
                print(animes_id)
                animes = await self.execute(
                    sql=f"""SELECT name, href, episodes FROM anime WHERE id in ({'?,' * (len(anime_id) - 1)}?)""",
                    fetchall=True,
                    params=(tuple(animes_id) ))# Достаем из таблички anime все аниме , конкретного пользователся
                return animes
            else:
                return False

    async def delete_users_anime(self, chat_id, anime_name):
        user_id = await self.execute(sql="""SELECT id FROM users WHERE chat_id = ?;""", fetchone=True,
                                     params=(chat_id,))
        print(user_id)
        anime_id = await self.execute(sql="""SELECT id FROM anime WHERE name = ?;""", fetchone=True,
                                      params=(anime_name,))
        await self.execute(sql="DELETE FROM users_anime where user_id = ? and anime_id = ?;",
                           fetchone=True, params=(user_id[0], anime_id[0],), commit=True)
        return anime_name

    async def select_anime(self):
        animes = await self.execute(sql="""SELECT * FROM anime;""", fetchall=True)

        # [id,href,anime_name,episodes,flag]
        return animes

    async def write_on_db(self, anime_name, episodes, flag):
        await self.execute(sql=""" UPDATE anime SET episodes = ?, flag = ?   WHERE name = ? """,
                           params=(episodes, flag, anime_name,), commit=True)
        print('s')

    async def for_sounder(self):  # Формирует словарь sound для sounder
        lst_of_users = await self.execute(sql=""" SELECT * FROM users  """, fetchall=True)
        lst_of_animes = await self.execute(sql=""" SELECT * FROM anime WHERE flag = (?)""", params=(True,),
                                           fetchall=True)
        lst_of_users_anime = await self.execute(sql=""" SELECT * FROM users_anime""", fetchall=True)
        if not lst_of_animes:
            print('Новых серий не вышло')
            sound = {}
        else:
            dict_of_users = {user[0]: user[1] for user in lst_of_users}
            dict_of_animes = {anime[0]: {'href': anime[1], 'anime_name': anime[2], 'episodes': anime[3].split('/')[0]}
                              for anime in
                              lst_of_animes if anime[4] == True}  # Преобразуем список кортежей в словарь если
            print(dict_of_animes)
            dict_of_users_anime = {user[0]: user[1] for user in lst_of_users_anime}
            sound = {}
            print(dict_of_users_anime)
            for key, value in dict_of_users_anime.items():
                print(key, value)
                sound[dict_of_users[value]] = dict_of_animes[key]
        print(sound)
        return sound  # {chat_id : {href: href,anime_name : anime_name,episodes : episodes}

    async def delete_anime(self, anime_name):
        anime_id = await self.execute(sql=""" DELETE FROM anime WHERE anime_name = ?  RETURNING id """,
                                      params=(anime_name,), commit=True, fetchone=True)
        await self.execute(sql="DELETE FROM users_anime where anime_id = ?;",
                           fetchone=True, params=(anime_id[0],), commit=True, fetchall=True)


db = DataBase()


async def func():
    print(await db.select_anime())
