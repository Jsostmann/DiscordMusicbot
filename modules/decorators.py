from discord.ext import commands
from guildmanager import GuildManager

def is_owner(func):
    async def decorator(self, *args):
        ctx: commands.Context = args[0]
        if ctx.guild.owner_id == ctx.message.author.id:
            await func(self, *args)
        else:
            await ctx.send("Not Authorized to execute this command")
    return decorator

def check_cooldown(func):
    async def decorator(self, *args):
        ctx: commands.Context = args[0]
        author_id = ctx.message.author.id

        settings_controller = GuildManager.get_manager(ctx.guild).get_settings_controller()
        
        if not settings_controller.user_has_cooldown(author_id):
            await func(self, *args)
        else:
            time_remaining = settings_controller.get_remaining_cooldown(author_id)
            await ctx.send(f"Cool down in effect please wait {time_remaining}")
    return decorator