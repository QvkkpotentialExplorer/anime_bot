import asyncio

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

    async def add_title(self, href: str, name: str, episodes: str,
                        content_type: str):  # content_type - категория , с которой производятся манпиуляции(anime,series)
        res = await self.execute(sql=f"""SELECT id FROM {content_type} WHERE href = ? """, fetchone=True,
                                 params=(href,))
        if not res:
            anime_id = await self.execute(
                sql=f"""INSERT INTO {content_type
                }(href, name, episodes) VALUES(?,?,?) RETURNING id ;""",
                params=(href, name, episodes),
                fetchone=True,
                commit=True
            )
            return anime_id[0]
        else:
            anime_id = await self.execute(sql=f"""SELECT id FROM {content_type} WHERE href = ?;""", fetchone=True,
                                          params=(href,))
            return anime_id[0]

    async def add_users_title(self, user_id, title_id, content_type):
        check = await self.execute(
            sql=f"SELECT * FROM users_{content_type} WHERE user_id = ? and {content_type}_id = ?;",
            fetchone=True,
            params=(user_id, title_id,))
        if not check:
            await self.execute(sql=f"""INSERT INTO users_{content_type}(user_id, {content_type}_id) VALUES(?, ?);""",
                               params=(user_id, title_id,),
                               commit=True)
            return True
        else:
            return False

    async def select_users_titles(self, chat_id: str, content_type):
        print(type(chat_id))
        sql = """SELECT id FROM users where chat_id = ?"""
        print(await self.execute(sql=sql, fetchone=True, params=(chat_id,)))
        if not await self.execute(sql=sql, fetchone=True,
                                  params=(chat_id,)):  # Проверка на то , что у user есть тайтл в users_anime
            return False
        else:
            print(content_type)
            user_id = await self.execute(sql=sql, fetchone=True, params=(chat_id,))
            print(user_id[0])
            titles_id = await self.execute(sql=f"SELECT {content_type}_id FROM users_{content_type} WHERE user_id = ?",
                                           fetchall=True,
                                           params=(user_id[0],))  # Достаем из таблички users_anime все anime_id
            print(titles_id)
            if titles_id:
                title_id = [id[0] for id in titles_id]
                print(title_id)
                animes = await self.execute(
                    sql=f"""SELECT id,name, href, episodes FROM {content_type} WHERE id in ({'?,' * (len(title_id) - 1)}?)""",
                    fetchall=True,
                    params=(tuple(title_id)))  # Достаем из таблички anime все аниме , конкретного пользователся
                return animes
            else:
                return False

    async def delete_users_title(self, chat_id,  title_id, content_type):
        name = await self.execute(sql = f"SELECT name FROM anime WHERE id = ?",params=(title_id,),fetchone=True)
        await self.execute(sql=f"DELETE FROM users_{content_type} where user_id = ? and {content_type}_id = ?;",
                           fetchone=True, params=(chat_id,title_id), commit=True)
        return name

    async def select_title(self, content_type):
        animes = await self.execute(sql=f"""SELECT * FROM {content_type};""", fetchall=True)

        # [id,href,anime_name,episodes,flag]
        return animes

    async def write_on_db(self, name, episodes, flag, content_type):
        await self.execute(sql=f""" UPDATE {content_type} SET episodes = ?, flag = ?   WHERE name = ? """,
                           params=(episodes, flag, name,), commit=True)
        print('s')

    async def for_sounder(self):  # Формирует словарь sound для sounder
        sound = {'anime': [], 'series': []}
        users_animes = await self.execute(
            sql="""SELECT chat_id,name,episodes,href FROM anime JOIN users_anime,users ON anime.id = users_anime.anime_id  AND users.id == users_anime.user_id WHERE anime.flag = True ;""",
            fetchall=True)
        users_series = await self.execute(
            sql="""SELECT chat_id,name,episodes,href FROM series JOIN users_series,users ON series.id = users_series.series_id  AND users.id == users_series.user_id WHERE series.flag = True ;""",
            fetchall=True)
        for sound_id in range(len(users_animes)):
            now_title = users_animes[sound_id]
            sound['anime'].append(
                {"chat_id": now_title[0], "name": now_title[1], "episodes": now_title[2], "href": now_title[3]})
        # {anime:[{href: href,name : anime_name,episodes : episodes},...]}

        for sound_id in range(len(users_series)):
            now_title = users_series[sound_id]
            sound['series'].append(
                {"chat_id": now_title[0], "name": now_title[1], "episodes": now_title[2], "href": now_title[3]})
        # {series:[{href: href,name : anime_name,episodes : episodes},...]}

        return sound

    async def delete_anime(self, anime_name):
        anime_id = await self.execute(sql=""" DELETE FROM anime WHERE anime_name = ?  RETURNING id """,
                                      params=(anime_name,), commit=True, fetchone=True)
        await self.execute(sql="DELETE FROM users_anime where anime_id = ?;",
                           fetchone=True, params=(anime_id[0],), commit=True, fetchall=True)
    async def test(self):

        print('--------------------------------------------------------------test_function in DB--------------------------------------------------------------')

db = DataBase()


