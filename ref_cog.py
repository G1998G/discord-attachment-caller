from discord.ext import commands # Bot Commands Frameworkのインポート
import discord
from typing import Union
import main as main


#リストを分割する関数
def ls_split(ls):
    
    #配列の要素数をカウント
    length = len(ls)
    #開始位置を指定
    n = 0
    #分割する変数の個数を指定
    s = 20
    #分割したリストを格納
    splited_ls = list()
    #配列を指定した個数で分割していくループ処理
    for i in ls:
        splited_ls.append(ls[n:n+s:1])
        n += s
        #カウント数が配列の長さを超えたらループ終了
        if n >= length:
            break
    return splited_ls


class ReferenceCommands(commands.Cog):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    @commands.command()
    async def list(self,ctx,*arg):
        '''
        登録一覧を表示
        '''
        
        _id = ctx.guild.id
        res = main.sql.registered_list(guild_id=_id,bot=self.bot)

        if res:
            embeds = []
            ls = ls_split(res)
            page = 0
            for l in ls:
                page +=1
                embeds.append( discord.Embed(title=f"登録一覧(登録数:{len(res)}) {page}ページ目",description=f"{''.join(l)}") )
            for embed in embeds:
                await ctx.reply(embed=embed)
            

        else:
            await main.Msg.no_register_at_all(ctx)
        main.postc(ctx,arg)

    @commands.command()
    async def search(self,ctx,*args):
        '''
        部分一致を含む検索
        '''
        if not args:
            await main.Msg.no_key(ctx)
        else:
            args = ' '.join(args)
            if len(args) > 20:
                await main.Msg.len_over(ctx)
                main.postc()
                return

            _id = ctx.guild.id
            res = main.sql.search_keyword_partial(guild_id=_id,keyword=args,bot=self.bot)
            if res:
                embeds = []
                ls = ls_split(res)
                page = 0
                for l in ls:
                    page +=1
                    embeds.append( discord.Embed(title=f"登録一覧(登録数:{len(res)}) {page}ページ目",description=f"{''.join(l)}") )
                for embed in embeds:
                    await ctx.reply(embed=embed)               


            else:
                await ctx.reply(content= f'>>> キーワード:{args} で部分一致含む検索をした結果、ヒット件数0件でした。')
        main.postc(ctx,args)

    @commands.command()
    async def author(self,ctx,arg: Union[discord.Member,int,str,None]):
        '''
        指定ユーザーの登録一覧を表示。無指定の場合書き込み者の登録一覧

        '''
        if not arg:
            res = main.sql.search_author(guild_id=ctx.guild.id,userid=ctx.author.id)
        elif type(arg) is discord.Member:
            print(type(arg))
            res = main.sql.search_author(guild_id=ctx.guild.id,userid=arg.id)
        else:
            await ctx.reply(f'>>> 検索するユーザーを１ユーザーのみ指定するか、貴方自身を検索する場合は何も入力しないでください。')
            return

        if not res:
            if arg:
                name = arg.name
            else:
                name = ctx.author.name
            await ctx.reply(f'>>> ユーザー名:{name}で検索した結果、ヒット件数0件でした。')

        elif res:
            embeds = []
            if not arg:
                name = ctx.author.name
            elif type(arg) is discord.Member:
                name = arg.name
            if res:
                embeds = []
                ls = ls_split(res)
                page = 0
                for l in ls:
                    page +=1
                    embeds.append( discord.Embed(title=f"{name}さんの登録一覧\n(登録数:{len(res)}) {page}ページ目",description=f"{''.join(l)}") )
                for embed in embeds:
                    await ctx.reply(embed=embed)  

        main.postc(ctx,arg)

    @commands.command()
    async def count(self,ctx,*args):
        '''
        登録数を表示

        '''
        _id = ctx.guild.id
        res = main.sql.registered_list(guild_id = _id,bot=self.bot)
        # 登録がある場合は登録数を表示
        if res:
            await ctx.send(f'>>> このサーバーでの登録数は{len(res)}個です。')
        # キーワード登録がない場合はそのことを伝える。
        else:
            await main.Msg.no_register_at_all(ctx)
        main.postc(ctx,args)

    @commands.command()
    async def random(self,ctx,*args):
        '''
        サーバー登録からランダム表示

        '''
        _id = ctx.guild.id
        res = main.sql.random_quote(guild_id = _id)
        # 登録がある場合は表示
        if res:
            await ctx.reply(f'{"".join(res)}')
        # キーワード登録がない場合はそのことを伝える。
        else:
            await main.Msg.no_register_at_all(ctx)
        main.postc(ctx,args)

    @commands.command()
    async def profile(self,ctx,*args):
        '''
        bot作成者の紹介
        '''
        embed= discord.Embed(title="bot作成者", description=f"趣味でbot等を作っています。\n [GitHubプロフィールページ](https://github.com/G1998G)")
        embed.set_thumbnail(url="https://avatars.githubusercontent.com/u/60283066?s=400&v=4")
        await ctx.reply(embed=embed)
        main.postc(ctx,args)

async def setup(bot: commands.Bot):
    print('ReferenceCommands読み込み')
    await bot.add_cog(ReferenceCommands(bot))