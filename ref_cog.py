from discord.ext import commands # Bot Commands Frameworkのインポート
import discord
from disputils import BotEmbedPaginator
from disputils.pagination import ControlEmojis
from typing import Union
import main as main

class ReferenceCommands(commands.Cog):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    @commands.command(name="list")
    async def pagenate(self,ctx,*arg):
        '''
        登録一覧を表示
        '''
        embed = []
        _id = ctx.guild.id
        res = main.sql.registered_list(guild_id=_id)
        if res:
            print(res,len(res))
            page = 1
            embed.append( discord.Embed(title=f"登録一覧(登録数:{len(res)}) {page}ページ目",description=f"{''.join(res[0:19])}") )
            if len(res) > 20:
                q = len(res) // 20
                mod = len(res) % 20
                x = 1
                _index = 20
                while x < q:
                    page += 1
                    content1 = res[_index:_index+20]
                    embed.append( discord.Embed(title=f"登録一覧(登録数:{len(res)}) {page}ページ目",description=f"{' '.join(content1)}") )
                    x +=1
                    _index += 20
                if mod > 0:
                    page += 1
                    content2= res[_index:_index+mod-1]
                    embed.append( discord.Embed(title=f"登録一覧(登録数:{len(res)}) {page}ページ目",description=f"{''.join(content2)}") )

            paginator = BotEmbedPaginator(ctx, pages=embed,control_emojis=ControlEmojis(first='⏮', previous='◀', next='▶', last='⏭', close=None))
            await paginator.run(timeout_msg='>>> listコマンドは100秒間だけ表示&操作可能です。再度表示&操作したい場合はもう一度コマンドを実行してください。')
        else:
            await ctx.send(content='>>> このサーバーでは何も登録がないようです。')
        main.postc(arg)

    @commands.command(name="search")
    async def partialmatch(self,ctx,*args):
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
            
            embed = []
            _id = ctx.guild.id
            res = main.sql.partial_match(guild_id=_id,keyword=args)
            if res:
                print(res,len(res))
                page = 1
                embed.append( discord.Embed(title=f"「{args}」\n 検索結果(登録数:{len(res)}) {page}ページ目",description=f"{''.join(res[0:19])}") )
                if len(res) > 20:
                    q = len(res) // 20
                    mod = len(res) % 20
                    x = 1
                    _index = 20
                    while x < q:
                        page += 1
                        content1 = res[_index:_index+20]
                        embed.append( discord.Embed(title=f"「{args}」\n 検索結果(登録数:{len(res)}) {page}ページ目",description=f"{' '.join(content1)}") )
                        x +=1
                        _index += 20
                    if mod > 0:
                        page += 1
                        content2= res[_index:_index+mod-1]
                        embed.append( discord.Embed(title=f"「{args}」\n 検索結果(登録数:{len(res)}) {page}ページ目",description=f"{''.join(content2)}") )

                paginator = BotEmbedPaginator(ctx, pages=embed,control_emojis=ControlEmojis(first='⏮', previous='◀', next='▶', last='⏭', close=None))
                await paginator.run(timeout_msg='>>> searchコマンドは100秒間だけ表示&操作可能です。再度表示&操作したい場合はもう一度コマンドを実行してください。')
            else:
                await ctx.send(content= f'>>> キーワード:{args} で部分一致含む検索をした結果、ヒット件数0件でした。')
        main.postc(args)

    @commands.command()
    async def author(self,ctx,arg: Union[discord.Member,int,str,None]):
        '''
        指定ユーザーの登録一覧を表示。無指定の場合書き込み者の登録一覧

        '''
        print(f'{ctx.author.id}')
        if arg is None :
            print(f'Noneが入力されました')
            res = main.sql.search_author(guild_id=ctx.guild.id,userid=ctx.author.id)
        elif type(arg) is discord.Member:
            print(type(arg))
            res = main.search_author(guild_id=ctx.guild.id,userid=arg.id)
        else:
            await ctx.send(f'>>> 検索するユーザーを１ユーザーのみ指定するか、貴方自身を検索する場合は何も入力しないでください。')
            return

        if res:
            embed = []
            if not arg:
                name = ctx.author.name
            elif type(arg) is discord.Member:
                name = arg.name
            print(f'{res}項目数:{len(res)}')
            page = 1
            embed.append( discord.Embed(title=f"{name} さんの登録\n 検索結果(登録数:{len(res)}) {page}ページ目",description=f"{''.join(res[0:19])}") )
            if len(res) > 20:
                q = len(res) // 20
                mod = len(res) % 20
                x = 1
                _index = 20
                while x < q:
                    page += 1
                    content1 = res[_index:_index+20]
                    embed.append( discord.Embed(title=f"{name} さんの登録\n 検索結果(登録数:{len(res)}) {page}ページ目",description=f"{' '.join(content1)}") )
                    x +=1
                    _index += 20
                if mod > 0:
                    page += 1
                    content2= res[_index:_index+mod-1]
                    embed.append( discord.Embed(title=f"{name} さんの登録\n 検索結果(登録数:{len(res)}) {page}ページ目",description=f"{''.join(content2)}") )

            paginator = BotEmbedPaginator(ctx, pages=embed,control_emojis=ControlEmojis(first='⏮', previous='◀', next='▶', last='⏭', close=None))
            await paginator.run(timeout_msg='>>> searchコマンドは100秒間だけ表示&操作可能です。再度表示&操作したい場合はもう一度コマンドを実行してください。')
        else:
            await ctx.send(content= f'>>> ユーザー名:{arg.name or ctx.author.id}で検索した結果、ヒット件数0件でした。')
        main.postc(arg)

    @commands.command()
    async def count(self,ctx,*args):
        '''
        登録数を表示

        '''
        _id = ctx.guild.id
        res = main.sql.registered_list(guild_id = _id)
        # 登録がある場合は登録数を表示
        if res:
            await ctx.send(content=f'>>> このサーバーでの登録数は{len(res)}個です。')
        # キーワード登録がない場合はそのことを伝える。
        else:
            await ctx.send(content=f'>>> このサーバーで登録はありません。')
        main.postc(args)

    @commands.command()
    async def profile(self,ctx,*args):
        '''
        bot作成者の紹介
        '''
        embed= discord.Embed(title="**bot作成者**", description=f"趣味でbot等を作っています。\n [GitHubプロフィールページ](https://github.com/G1998G)")
        embed.set_thumbnail(url="https://avatars.githubusercontent.com/u/60283066?s=400&v=4")
        await ctx.send(embed=embed)
        main.postc(args)

def setup(bot):
    print('ReferenceCommands読み込み')
    return bot.add_cog(ReferenceCommands(bot))