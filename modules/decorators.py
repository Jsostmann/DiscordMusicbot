from discord.ext import commands
from guildmanager import GuildManager

def is_owner(func):
    async def decorator(*args):
        ctx: commands.Context = args[1]
        if ctx.guild.owner_id == ctx.message.author.id:
            await func(*args)
        else:
            await ctx.send("Not Authorized to execute this command")
    return decorator

def check_cooldown(func):
    async def decorator(*args):
        ctx: commands.Context = args[1]
        author_id = ctx.message.author.id

        settings_controller = GuildManager.get_manager(ctx.guild).get_settings_controller()
        
        if not settings_controller.user_has_cooldown(author_id):
            await func(*args)
        else:
            await ctx.send("Cannot execute Command, Cool down in effect")
    return decorator