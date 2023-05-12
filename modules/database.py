import aiosqlite
import modules.utils as utils
from enum import Enum
 
class Keywords(Enum):
    SELECT = "SELECT"
    INSERT = "INSERT"
    INTO = "INTO"
    STAR = "*"
    WHERE = "WHERE"
    DISTINCT = "DISTINCT"
    FROM = "FROM"
    VALUES = "VALUES"
    IGNORE = "IGNORE"
    OR = "OR"
    AND = "AND"
    
    FAVORITE_SONG = "INSERT OR IGNORE INTO favorite(user_guild_id, song_id) values (?, ?)"
    INSERT_SONG = "INSERT OR IGNORE INTO song(song_id, song_name, song_url) values (?, ?, ?)"
    GET_GUILD_USER = "SELECT id FROM user_guild WHERE guild_id=? AND user_id=?"
    INSERT_GUILD_UESR = "INSERT OR IGNORE INTO user_guild(guild_id, user_id) values (?, ?)"
    CREATE_USER_PLAYLIST = "INSERT OR IGNORE INTO playlist(guild_user_id, playlist_name) values (?, ?)"
    GET_USER_PLAYLIST = "SELECT * FROM playlist WHERE guild_user_id=? AND playlist_name=?"
    GET_USER_PLAYLISTS = "SELECT playlist_name FROM playlist where guild_user_id=?"
    GET_GUILD_SONGS = """SELECT song_name, song_url FROM song
                         JOIN favorite ON favorite.song_id = song.song_id
                         JOIN guild_user ON guild_user.id = favorite.guild_user_id
                         WHERE guild_user.guild_id = 991751386540814438"""
    
    GET_GUILD_USER_SONGS = None
    GET_USER_SONGS = None


def select_query_builder(table, condition=[Keywords.AND, Keywords.OR], fields=None, values=None):
    query = Keywords.SELECT.value

    if not fields:
        query += Keywords.STAR.value
    else:
        query += f"({', '.join(str(field) for field in fields)}) "

    query += f"{Keywords.FROM.value} "
    query += table + " "

    if values:
        query += f"{Keywords.WHERE.value} "
        query += f" {condition.value} ".join(f'{f}=?' for f in fields)

    return query

def insert_query_builder(table, fields):
    query = f"{Keywords.INSERT.value} {Keywords.INTO.value} "
    query += table + " "

    query += f"({', '.join(str(field) for field in fields)}) "

    query += f"{Keywords.VALUES.value} "
    query += f"({', '.join('?' for i in range(0, len(fields)))})"

    return query


async def init_db():
    async with aiosqlite.connect(utils.DB_PATH) as db:
        with open(utils.DB_SCHEMA_PATH) as file:
            await db.executescript(file.read())
        await db.commit()
        

async def get_users_in_guild(guild_id):
    query = "SELECT DISTINCT user_id FROM guild_members WHERE guild_id=?"
    async with aiosqlite.connect(utils.DB_PATH) as db:
        async with db.execute(query, (guild_id,)) as cursor:
            result = await cursor.fetchall()
            print(result)


async def insert_user_guild(guild_id, user_id):
    query = "INSERT OR IGNORE INTO guild_user(guild_id, user_id) values (?, ?)"
    async with aiosqlite.connect(utils.DB_PATH) as db:
        async with db.execute(query, (guild_id, user_id)) as cursor:
            await db.commit()
            return cursor.lastrowid
        
async def get_user_guild(guild_id, user_id):
    query = "SELECT id FROM guild_user WHERE guild_id=? AND user_id=?"
    async with aiosqlite.connect(utils.DB_PATH) as db:
        async with db.execute(query, (guild_id, user_id)) as cursor:
            res = await cursor.fetchone()
            if not res:
                new_user_guild = await insert_user_guild(guild_id, user_id)
                return new_user_guild
            return res[0]

async def insert_song(song):
    query = "INSERT OR IGNORE INTO song(song_id, song_name, song_url) values (?, ?, ?)"

    song_id = utils.to_hash(song.get_value('id'))
    song_title = song.get_value('title')
    song_url = song.get_value('webpage_url')

    async with aiosqlite.connect(utils.DB_PATH) as db:
        async with db.execute(query, (song_id, song_title, song_url,)) as cursor:
            await db.commit()
            duplicate_found = not bool(cursor.lastrowid)

            if duplicate_found:
                print("Song already in DB")
            return song_id
        
async def get_user_playlists(guild_id, user_id):
    query = Keywords.GET_USER_PLAYLISTS.value
    guild_user_id = await get_user_guild(guild_id, user_id)

    async with aiosqlite.connect(utils.DB_PATH) as db:
        async with db.execute(query, (guild_user_id,)) as cursor:
            res = await cursor.fetchall()
            
            return res
        
async def get_user_playlist(guild_id, user_id, playlist_name):
    query = Keywords.GET_USER_PLAYLIST.value
    guild_user_id = await get_user_guild(guild_id, user_id)

    async with aiosqlite.connect(utils.DB_PATH) as db:
        async with db.execute(query, (guild_user_id, playlist_name)) as cursor:
            res = await cursor.fetchone()
            if res:
                return res[0]
            return res


async def create_user_playlist(guild_id, user_id, playlist_name):
    query = Keywords.CREATE_USER_PLAYLIST.value
    user_guild_id = await get_user_guild(guild_id, user_id)
    
    async with aiosqlite.connect(utils.DB_PATH) as db:
        async with db.execute(query, (user_guild_id, playlist_name)) as cursor:
            await db.commit()
            duplicate_found = not bool(cursor.lastrowid)

            if duplicate_found:
                print("Playlist already created")
            return duplicate_found


async def favorite_song(guild_id, user_id, song):
    query = "INSERT OR IGNORE INTO favorite(guild_user_id, song_id) values (?, ?)"

    user_guild_id = await get_user_guild(guild_id, user_id)
    print(user_guild_id)
    song_id = await insert_song(song)

    async with aiosqlite.connect(utils.DB_PATH) as db:
        async with db.execute(query, (user_guild_id, song_id)) as cursor:
            await db.commit()
            duplicate_found = not bool(cursor.lastrowid)

            if duplicate_found:
                print("User Already saved song")
            return duplicate_found
        
async def join(guild_id, user_id):
    #user_guild_id = get_user_guild(guild_id, user_id)
    query = Keywords.GET_GUILD_SONGS.value
    async with aiosqlite.connect(utils.DB_PATH) as db:
        async with db.execute(query) as cursor:
            result = await cursor.fetchall()
            print(result)