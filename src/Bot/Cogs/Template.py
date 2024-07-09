from discord.ext import commands
from discord.ext.commands import Context


class Template(commands.Cog, name="Template"):
  def __init__(self, bot) -> None:
    self.bot = bot


  @commands.hybrid_command(
    name="test",
    description="This is a testing command that does nothing.",
  )
  async def testcommand(self, ctx: Context):
    return await ctx.send("Template расширение работает!")


async def setup(bot) -> None:
  print("Loading cog!")
  await bot.add_cog(Template(bot))