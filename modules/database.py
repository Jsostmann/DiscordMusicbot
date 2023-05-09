import aiosqlite
import modules.utils as utils

async def init_db():
    async with aiosqlite.connect(utils.DB_PATH) as db:
        with open(utils.DB_SCHEMA_PATH) as file:
            await db.executescript(file.read())
        await db.commit()

async def init_guilds(guilds):
    current_guilds = await get_current_guilds()
    new_guilds = [(guild.id, guild.name, guild.owner.id, guild.owner.name) for guild in guilds if guild.id not in current_guilds]
    print("New Guilds:" + str(new_guilds))
    await add_guilds(new_guilds)

async def init_guild_members(guilds):
    current_guild_member_map = await get_current_guild_members()
    new_guild_members = [(guild.id, member.id) for guild in guilds for member in guild.members if not member.bot and (guild.id not in current_guild_member_map or member.id not in current_guild_member_map[guild.id])]
    print("New Guild Members:" + str(new_guild_members))
    await add_guild_members(new_guild_members)

async def get_current_guild_members():
    query = "SELECT guild_id, user_id FROM guild_members"
    async with aiosqlite.connect(utils.DB_PATH) as db:
        async with db.execute(query) as cursor:
            result = await cursor.fetchall()
            guild_member_map = dict()
            for value in result:
                if value[0] in guild_member_map:
                    guild_member_map[value[0]].append(value[1])
                else:
                    guild_member_map[value[0]] = [value[1]]

            print("Current Guild Members:" + str(guild_member_map))
            return guild_member_map
        
async def get_current_guilds():
    query = "SELECT guild_id FROM guild"
    async with aiosqlite.connect(utils.DB_PATH) as db:
        async with db.execute(query) as cursor:
            result = await cursor.fetchall()
            guild_ids = [id[0] for id in result]
            print("Current Guilds:" + str(guild_ids))
            return guild_ids

async def add_guilds(guild_data):
    query = "INSERT INTO guild(guild_id, guild_name, owner_id, owner_name) values (?,?,?,?)"
    async with aiosqlite.connect(utils.DB_PATH) as db:
        await db.executemany(query, guild_data)
        await db.commit()

async def add_guild_members(guild_members_data):
    query = "INSERT INTO guild_members(guild_id, user_id) values (?,?)"
    async with aiosqlite.connect(utils.DB_PATH) as db:
        await db.executemany(query, guild_members_data)
        await db.commit()
    
async def get_tables():
    query = "SELECT name FROM sqlite_master WHERE type='table'"
    async with aiosqlite.connect(utils.DB_PATH) as db:
        async with db.execute(query) as cursor:
            result = await cursor.fetchall()
            print(result)

async def get_users_in_guild(guild_id):
    query = "SELECT DISTINCT user_id FROM guild_members WHERE guild_id=?"
    async with aiosqlite.connect(utils.DB_PATH) as db:
        async with db.execute(query, (guild_id,)) as cursor:
            result = await cursor.fetchall()
            print(result)