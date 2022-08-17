from discord.ext import commands # Bot Commands Frameworkのインポート
import discord
import main as main

class DeleteCommands(commands.Cog):

    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.deletekeyword = dict()

    @commands.command(name='del')
    async def _delete(self,ctx,*arg):
        '''
        登録を削除する
        '''
        guild_id = ctx.guild.id
        if arg:
            arg = ' '.join(arg)
            if len(arg) > 20:
                await main.Msg.len_over(ctx)
                main.postc()
                return

            res = main.sql.search_keyword(guild_id = guild_id,keyword = arg)
            if res:
                await ctx.send(content=f'>>> キーワード:{arg}に登録されたこのファイルを削除しますか？　削除する場合は {ctx.prefix}delok, しない場合は {ctx.prefix}delnoと入力してください。\n >>> {res["content"]}')
                self.deletekeyword[str(guild_id)] = arg
            else:
                await main.Msg.no_img(ctx,arg)
        else:
            await main.Msg.no_key(ctx)
        main.postc(arg)

    @commands.command()
    async def delok(self,ctx,*arg):
        '''
        登録削除を確認 OK
        '''
        guild_id = ctx.guild.id
        if str(guild_id) in self.deletekeyword:
            keyword = self.deletekeyword[str(guild_id)]
            main.sql.delete_dt(guild_id=guild_id, keyword=keyword)
            await ctx.send(content=f'>>> キーワード:{keyword}に登録されたファイルを削除しました。')
            del self.deletekeyword[str(guild_id)]
        else:
            await ctx.send(content=f'>>> このコマンドは登録削除実行用コマンドです。まずは{ctx.prefix}delキーワードで削除する登録を指定してください')
        main.postc(arg)

    @commands.command()
    async def delno(self,ctx,*arg):
        '''
        登録削除を確認 NO
        '''
        guild_id = ctx.guild.id
        if str(guild_id) in self.deletekeyword:
            keyword = self.deletekeyword[str(guild_id)]
            await ctx.send(content=f'>>>キーワード:{keyword}に登録されたファイルを削除しません。')
            del self.deletekeyword[str(guild_id)]
        else:
            await ctx.send(content=f'>>> このコマンドは登録削除実行用コマンドです。まずは{ctx.prefix}del キーワードで削除する登録を指定してください')
        main.postc(arg)

def setup(bot):
    print('DeleteCommands読み込み')
    return bot.add_cog(DeleteCommands(bot))