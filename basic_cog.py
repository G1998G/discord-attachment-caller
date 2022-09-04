from discord.ext import commands # Bot Commands Frameworkのインポート
import main as main
from discord.ui import button , View , Button
from discord.interactions import Interaction


class OverWriteView(View):
    def __init__(self,keyword,ctx):
        super().__init__(timeout=None)
        self.keyword = keyword
        self.ctx = ctx

    
    @button(label='置き換える')
    async def ok(self, interaction: Interaction,button: Button):
        main.sql.update_dt(guild_id=interaction.guild_id, keyword=self.keyword, content=str(self.ctx.message.attachments[0]), userid=self.ctx.author.id)
        self.ok.disabled = True
        self.no.disabled = True
        await interaction.response.edit_message(content=f"{interaction.message.content} \n →置き換えました。",view=self)


    @button(label='置き換えない')
    async def no(self, interaction: Interaction,button: Button):
        self.ok.disabled = True
        self.no.disabled = True
        await interaction.response.edit_message(content=f"{interaction.message.content} \n →置き換えませんでした。",view=self)


class BasicCommands(commands.Cog):

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    @commands.command()
    async def call(self,ctx,*arg):
        '''
        新規登録/登録済みファイルの呼び出し

        '''
        
        if not arg:
            # キーワードが入力されていない場合はその旨を伝える
            await main.Msg.no_arg(ctx)
        else:
            arg = ' '.join(arg)
            res = main.sql.search_keyword(guild_id = ctx.guild.id,keyword = arg)
            print(res)
            if ctx.message.attachments:
                if len(arg) > 20:
                     # キーワードが特定の文字数以上の場合は拒否
                    await main.Msg.len_over(ctx)
                
                elif res:
                    # キーワードで登録がある場合は上書きするか尋ねる
                    await ctx.send(content=f'キーワード:{arg}は既にこのファイルが登録されています。ファイルを置き換えますか?\n {res["content"]}',view=OverWriteView(keyword=arg,ctx=ctx))
                
                else:
                    # キーワードに登録がない場合は画像登録
                    # 登録は１枚まで。
                        main.sql.insert_dt(guild_id=ctx.guild.id,keyword=arg,content=str(ctx.message.attachments[0]),userid=ctx.author.id)
                        await ctx.send(f'キーワード:{arg}でファイルを登録しました。')
            
            elif not res:
                # アタッチメントが無く、登録もない場合はその旨を伝える
                await main.Msg.no_img(ctx,arg)
            
            else:
                # アタッチメントが無く、登録がある場合は登録画像を表示
                await ctx.send(f'{res["content"]}')
                print(f'表示:{arg}')
        main.postc(ctx,arg)

async def setup(bot: commands.Bot):
    print('BasicCommands読み込み')
    await bot.add_cog(BasicCommands(bot))