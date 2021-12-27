from discord.ext import commands # Bot Commands Frameworkのインポート
import discord
import main as mainpy

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
        _id = ctx.guild.id
        if arg:
            arg = ' '.join(arg)
            if len(arg) > 20:
                await mainpy.Msg.len_over(ctx)
                mainpy.postc()
                return

            res = mainpy.search_keyword(serverid = _id,keyword = arg)
            if res:
                await ctx.send(content=f'`キーワード:{arg}に登録されたこのファイルを削除しますか？　削除する場合は {ctx.prefix}delok, しない場合は {ctx.prefix}delnoと入力してください。`\n{res["content"]}')
                self.deletekeyword[str(_id)] = arg
            else:
                await mainpy.Msg.no_img(ctx,arg)
        else:
            await mainpy.Msg.no_key(ctx)
        mainpy.postc(arg)

    @commands.command()
    async def delok(self,ctx,*arg):
        '''
        登録削除を確認 OK
        '''
        _id = ctx.guild.id
        if str(_id) in self.deletekeyword:
            keyword = self.deletekeyword[str(_id)]
            mainpy.delete_dt(serverid=_id, keyword=keyword)
            await ctx.send(content=f'`キーワード:{keyword}に登録されたファイルを削除しました。`')
            del self.deletekeyword[str(_id)]
        else:
            await ctx.send(content=f'`このコマンドは登録削除実行用コマンドです。まずは{ctx.prefix}delキーワードで削除する登録を指定してください`')
        mainpy.postc()

    @commands.command()
    async def delno(self,ctx,*arg):
        '''
        登録削除を確認 NO
        '''
        _id = ctx.guild.id
        if str(_id) in self.deletekeyword:
            keyword = self.deletekeyword[str(_id)]
            await ctx.send(content=f'`キーワード:{keyword}に登録されたファイルを削除しません。`')
            del self.deletekeyword[str(_id)]
        else:
            await ctx.send(content=f'`このコマンドは登録削除実行用コマンドです。まずは{ctx.prefix}del キーワードで削除する登録を指定してください`')
        mainpy.postc(arg)

def setup(bot):
    print('DeleteCommands読み込み')
    return bot.add_cog(DeleteCommands(bot))