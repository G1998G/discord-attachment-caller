from discord.ext import commands # Bot Commands Frameworkのインポート
from discord.ui import button , View , Button
from discord.interactions import Interaction
import main as main

class DelView(View):
    def __init__(self,keyword):
        super().__init__(timeout=None)
        self.keyword = keyword

    
    @button(label='削除する')
    async def delok(self, interaction: Interaction,button: Button):
        main.sql.delete_dt(guild_id=interaction.guild_id, keyword=self.keyword)
        self.delok.disabled = True
        self.delno.disabled = True
        await interaction.response.edit_message(content=f"{interaction.message.content} \n →削除しました。",view=self)


    @button(label='削除しない')
    async def delno(self, interaction: Interaction,button: Button):
        self.delok.disabled = True
        self.delno.disabled = True
        await interaction.response.edit_message(content=f"{interaction.message.content} \n →削除しませんでした。",view=self)

class DeleteCommands(commands.Cog):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    @commands.command(name='del')
    async def _delete(self,ctx,*arg):
        '''
        登録を削除する
        '''
        if arg:
            arg = ' '.join(arg)
            if len(arg) > 20:
                await main.Msg.len_over(ctx)
                main.postc()
                return

            res = main.sql.search_keyword(guild_id = ctx.guild.id,keyword = arg)
            if res:
                await ctx.send(f'キーワード:{arg}に登録されたこのファイルを削除しますか？\n {res["content"]}',view=DelView(arg))

            else:
                await main.Msg.no_img(ctx,arg)
        else:
            await main.Msg.no_arg(ctx)
        main.postc(ctx,arg)

async def setup(bot:commands.Bot):
    print(f'DeleteCommands読み込み')
    await bot.add_cog(DeleteCommands(bot))