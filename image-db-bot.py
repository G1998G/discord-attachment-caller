from discord.ext import commands # Bot Commands Frameworkのインポート
import discord
import sqlite3
from contextlib import closing
from disputils import BotEmbedPaginator
from disputils.pagination import ControlEmojis
from typing import Union

# guild内投稿回数カウント用
class C:
    def __init__(self):
        self.x = 0
    def __call__(self,arg):
        self.x += 1
        return print(f'コマンド受け取り🟢{self.x}回目　コマンド引数:{arg}')
postc = C()

def check_db():
    dbname = 'database.db'
    with closing(sqlite3.connect(dbname)) as connection:
        cursor = connection.cursor()
        # テーブルを作成
        cursor.execute("SELECT * FROM sqlite_master WHERE type='table' and name='discord_table'")
        if not cursor.fetchone():
            sql = 'CREATE TABLE discord_table (serverid INT,keyword VARCHAR(1024), content VARCHAR(1024),userid INT)'
            print('テーブルを作成しました')
            cursor.execute(sql)
            connection.commit()
        else:
            print('既にテーブルはありました')
        connection.close()

def insert_dt(serverid,keyword,content,userid):
    dbname = 'database.db'
    with closing(sqlite3.connect(dbname)) as connection:
        cursor = connection.cursor()
        sql = 'INSERT INTO discord_table (serverid,keyword,content,userid) VALUES (?,?,?,?)'
        data = (int(serverid), keyword, content, userid)
        cursor.execute(sql, data)
        connection.commit()
        connection.close()

def update_dt(serverid,keyword,content,userid):
    dbname = 'database.db'
    with closing(sqlite3.connect(dbname)) as connection:
        cursor = connection.cursor()
        sql = 'UPDATE discord_table SET content=?, userid=? WHERE serverid=? AND keyword=?'
        data = (content, userid, serverid, keyword)
        cursor.execute(sql, data)
        connection.commit()
        connection.close()


def delete_dt(serverid,keyword):
    dbname = 'database.db'
    with closing(sqlite3.connect(dbname)) as connection:
        cursor = connection.cursor()
        sql = 'DELETE FROM discord_table WHERE serverid=? AND keyword=?'
        data = (int(serverid), keyword)
        cursor.execute(sql, data)
        connection.commit()
        connection.close()

def search_keyword(serverid,keyword):
    dbname = 'database.db'
    res = dict()
    with closing(sqlite3.connect(dbname)) as connection:
        # sqlite3.Rowでカラム名での取得を可能にする。
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        sql = 'SELECT * FROM discord_table WHERE serverid=? AND keyword=?'
        data = (serverid,keyword)
        cursor.execute(sql, data)
        for row in cursor:
            res['keyword'] = row['keyword']
            res['content'] = row['content']
            res['userid'] = row['userid']
        connection.close()
    return res
            

def registered_list(serverid):
    dbname = 'database.db'
    res = list()
    with closing(sqlite3.connect(dbname)) as connection:
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        sql = 'SELECT keyword,userid FROM discord_table WHERE serverid= ?'
        data = (serverid,)
        cursor.execute(sql, data)
        for row in cursor:
            res.append(f'**`{row["keyword"]}`** _`{bot.get_user(row["userid"]).name}`_\n')
        connection.close()
    return res  

def partial_match(serverid,keyword):
    dbname = 'database.db'
    res = list()
    keyword = f'%{keyword}%'
    with closing(sqlite3.connect(dbname)) as connection:
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        sql = 'SELECT keyword,userid FROM discord_table WHERE serverid= ? AND keyword LIKE ?'
        data = (serverid,keyword)
        cursor.execute(sql, data)
        for row in cursor:
            res.append(f'**`{row["keyword"]}`** _`{bot.get_user(row["userid"]).name}`_\n')
        connection.close()
    return res  

def search_author(serverid,userid):
    dbname = 'database.db'
    res = list()
    with closing(sqlite3.connect(dbname)) as connection:
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        sql = 'SELECT keyword,userid FROM discord_table WHERE serverid= ? AND userid= ?'
        data = (serverid,userid)
        cursor.execute(sql, data)
        for row in cursor:
            res.append(f'**`{row["keyword"]}`**\n')
        connection.close()
    return res  

class Msg:

    @staticmethod
    async def len_over(ctx):
        await ctx.send(f'```キーワードはスペース含め20文字以内で入力してください。```')
    
    @staticmethod
    async def no_key(ctx):
        await ctx.send(f'```{ctx.prefix}{ctx.invoked_with}入力時は必ずキーワードを指定してください。```')
    
    @staticmethod
    async def no_img(ctx,keyword):
        await ctx.send(content=f'`キーワード:{keyword}でファイルは登録されてません。`')



class HelpCommand(commands.HelpCommand):
    def __init__(self):
        super().__init__()
        self.no_category = "HelpCommand"
        self.command_attrs["description"] = "コマンドリストを表示します。"

    async def send_bot_help(self,mapping):
        '''
        ヘルプを表示するコマンド
        '''
        content = ""
        for cog in mapping:
            # 各コグのコマンド一覧を content に追加していく
            command_list = await self.filter_commands(mapping[cog])
            if not command_list:
                # 表示できるコマンドがないので、他のコグの処理に移る
                continue
            if cog is None:
                # コグが未設定のコマンドなので、no_category属性を参照する
                content += f"\n**{self.no_category}**\n"
            else:
                content += f"\n**{cog.qualified_name}**\n"
            for command in command_list:
                content += f"{self.context.prefix}{command.name}  `{command.help}`\n"
            content += "\n"
        embed = discord.Embed(title="**呼び出し君bot**",description='```discordにアップロードしたファイルをいつでも呼び出せるようにしたbotです。```')
        embed = embed.add_field(name="**コマンドリスト**",value=content)

        await self.get_destination().send(embed=embed)
        postc()


class BasicCommand(commands.Cog):

    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.update_file = dict()

    @commands.command()
    async def call(self,ctx,*arg):
        '''
        新規登録/登録済みファイルの呼び出し

        '''
        _id = ctx.guild.id
        
        if not arg:
            # キーワードが入力されていない場合はその旨を伝える
            await Msg.no_key(ctx)
        else:
            arg = ' '.join(arg)
            res = search_keyword(serverid = _id,keyword = arg)
            if ctx.message.attachments:
                if len(arg) > 20:
                     # キーワードが10文字以上の場合は拒否
                    await Msg.len_over(ctx)
                
                elif res:
                    # キーワードで登録がある場合は上書きするか尋ねる
                    await ctx.send(content=f'`キーワード:{arg}は既にこのファイルが登録されています。ファイルを置き換える場合は {ctx.prefix}okと入力してください。置き換えない場合は{ctx.prefix}noと入力してください。`\n{res["content"]}')
                    # 登録は１枚まで。
                    for attachment in ctx.message.attachments:
                        attachment = str(attachment)
                        self.update_file[str(_id)] = [arg,attachment]
                        print(self.update_file[str(_id)])
                        break
                
                else:
                    # キーワードに登録がない場合は画像登録
                    # 登録は１枚まで。
                    for attachment in ctx.message.attachments:
                        attachment = str(attachment)
                        insert_dt(serverid=_id,keyword=arg,content=attachment,userid=ctx.author.id)
                        await ctx.send(content=f'`キーワード:{arg}でファイルを登録しました。`')
                        print(f'新規登録:{arg},url:{attachment},by{ctx.author.id}')
                        break

            
            elif not res:
                # アタッチメントが無く、登録もない場合はその旨を伝える
                await Msg.no_img(ctx,arg)
            
            else:
                # アタッチメントが無く、登録がある場合は登録画像を表示
                await ctx.send(content=f'{res["content"]}')
                print(f'表示:{arg}')
        postc(arg)

    @commands.command()
    async def ok(self,ctx,*arg):
        '''
        登録済みファイルの置き換え確認 OK
        '''
        _id = ctx.guild.id
        if str(_id) in self.update_file:
            keyword = self.update_file[str(_id)][0]
            attachment = self.update_file[str(_id)][1]
            update_dt(serverid=_id, keyword=keyword, content=attachment, userid=ctx.author.id)
            await ctx.send(content=f'`キーワード:{keyword}の既存アタッチメントを指定ファイルで置き換えしました。`')
            del self.update_file[str(_id)]
        postc()

    @commands.command()
    async def no(self,ctx,*arg):
        '''
        登録済みファイルの置き換え確認　NO
        '''
        _id = ctx.guild.id
        if  str(_id) in self.update_file:
            keyword = self.update_file[str(_id)][0]
            await ctx.send(content=f'`キーワード:{keyword}に登録された既存ファイルを指定されたファイルで置き換えしません。`')
            del self.update_file[str(_id)]
        postc(arg)

class DeleteCommand(commands.Cog):

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
                await Msg.len_over(ctx)
                postc()
                return

            res = search_keyword(serverid = _id,keyword = arg)
            if res:
                await ctx.send(content=f'`キーワード:{arg}に登録されたこのファイルを削除しますか？　削除する場合は {ctx.prefix}delok, しない場合は {ctx.prefix}delnoと入力してください。`\n{res["content"]}')
                self.deletekeyword[str(_id)] = arg
            else:
                await Msg.no_img(ctx,arg)
        else:
            await Msg.no_key(ctx)
        postc(arg)

    @commands.command()
    async def delok(self,ctx,*arg):
        '''
        登録削除を確認 OK
        '''
        _id = ctx.guild.id
        if str(_id) in self.deletekeyword:
            keyword = self.deletekeyword[str(_id)]
            delete_dt(serverid=_id, keyword=keyword)
            await ctx.send(content=f'`キーワード:{keyword}に登録されたファイルを削除しました。`')
            del self.deletekeyword[str(_id)]
        else:
            await ctx.send(content=f'`このコマンドは登録削除実行用コマンドです。まずは{ctx.prefix}delキーワードで削除する登録を指定してください`')
        postc()

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
        postc(arg)



class ReferenceCommand(commands.Cog):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    @commands.command(name="list")
    async def pagenate(self,ctx,*arg):
        '''
        登録一覧を表示
        '''
        embeds = []
        _id = ctx.guild.id
        res = registered_list(serverid=_id)
        if res:
            print(res,len(res))
            page = 1
            embeds.append( discord.Embed(title=f"登録一覧(登録数:{len(res)}) {page}ページ目",description=f"{''.join(res[0:19])}") )
            if len(res) > 20:
                q = len(res) // 20
                mod = len(res) % 20
                x = 1
                _index = 20
                while x < q:
                    page += 1
                    content1 = res[_index:_index+20]
                    embeds.append( discord.Embed(title=f"登録一覧(登録数:{len(res)}) {page}ページ目",description=f"{' '.join(content1)}") )
                    x +=1
                    _index += 20
                if mod > 0:
                    page += 1
                    content2= res[_index:_index+mod-1]
                    embeds.append( discord.Embed(title=f"登録一覧(登録数:{len(res)}) {page}ページ目",description=f"{''.join(content2)}") )

            paginator = BotEmbedPaginator(ctx, pages=embeds,control_emojis=ControlEmojis(first='⏮', previous='◀', next='▶', last='⏭', close=None))
            await paginator.run(timeout_msg='```listコマンドは100秒間だけ表示&操作可能です。再度表示&操作したい場合はもう一度コマンドを実行してください。```')
        else:
            await ctx.send(content='`このサーバーでは何も登録がないようです。`')
        postc(arg)

    @commands.command(name="search")
    async def partialmatch(self,ctx,*args):
        '''
        部分一致を含む検索
        '''
        if not args:
            await Msg.no_key(ctx)
        else:
            args = ' '.join(args)
            if len(args) > 20:
                await Msg.len_over(ctx)
                postc()
                return
            
            embeds = []
            _id = ctx.guild.id
            res = partial_match(serverid=_id,keyword=args)
            if res:
                print(res,len(res))
                page = 1
                embeds.append( discord.Embed(title=f"「{args}」\n 検索結果(登録数:{len(res)}) {page}ページ目",description=f"{''.join(res[0:19])}") )
                if len(res) > 20:
                    q = len(res) // 20
                    mod = len(res) % 20
                    x = 1
                    _index = 20
                    while x < q:
                        page += 1
                        content1 = res[_index:_index+20]
                        embeds.append( discord.Embed(title=f"「{args}」\n 検索結果(登録数:{len(res)}) {page}ページ目",description=f"{' '.join(content1)}") )
                        x +=1
                        _index += 20
                    if mod > 0:
                        page += 1
                        content2= res[_index:_index+mod-1]
                        embeds.append( discord.Embed(title=f"「{args}」\n 検索結果(登録数:{len(res)}) {page}ページ目",description=f"{''.join(content2)}") )

                paginator = BotEmbedPaginator(ctx, pages=embeds,control_emojis=ControlEmojis(first='⏮', previous='◀', next='▶', last='⏭', close=None))
                await paginator.run(timeout_msg='`searchコマンドは100秒間だけ表示&操作可能です。再度表示&操作したい場合はもう一度コマンドを実行してください。`')
            else:
                await ctx.send(content= f'`キーワード:{args} で部分一致含む検索をした結果、ヒット件数0件でした。`')
        postc(args)

    @commands.command()
    async def author(self,ctx,arg: Union[discord.Member,int,str] = None):
        '''
        指定ユーザーの登録一覧を表示。無指定の場合書き込み者の登録一覧

        '''
        print(f'{ctx.author.id}')
        if not arg:
            res = search_author(serverid=ctx.guild.id,userid=ctx.author.id)
        elif type(arg) is discord.Member:
            print(type(arg))
            res = search_author(serverid=ctx.guild.id,userid=arg.id)
        else:
            await ctx.send(f'```検索するユーザーを１ユーザーのみ指定するか、貴方自身を検索する場合は何も入力しないでください。```')
            return

        if res:
            if not arg:
                name = ctx.author.name
            elif type(arg) is discord.Member:
                name = arg.name

            print(res,len(res))
            page = 1
            embeds = []
            embeds.append( discord.Embed(title=f"ユーザー名「{name}」\n 検索結果(登録数:{len(res)}) {page}ページ目",description=f"{''.join(res[0:19])}") )
            if len(res) > 20:
                q = len(res) // 20
                mod = len(res) % 20
                x = 1
                _index = 20
                while x < q:
                    page += 1
                    content1 = res[_index:_index+20]
                    embeds.append( discord.Embed(title=f"ユーザー名「{name}」\n 検索結果(登録数:{len(res)}) {page}ページ目",description=f"{' '.join(content1)}") )
                    x +=1
                    _index += 20
                if mod > 0:
                    page += 1
                    content2= res[_index:_index+mod-1]
                    embeds.append( discord.Embed(title=f"ユーザー名「{name}」\n 検索結果(登録数:{len(res)}) {page}ページ目",description=f"{''.join(content2)}") )

                paginator = BotEmbedPaginator(ctx, pages=embeds,control_emojis=ControlEmojis(first='⏮', previous='◀', next='▶', last='⏭', close=None))
                await paginator.run(timeout_msg='`searchコマンドは100秒間だけ表示&操作可能です。再度表示&操作したい場合はもう一度コマンドを実行してください。`')
        else:
            await ctx.send(content= f'`ユーザー名:{arg.name or ctx.author.id}で検索した結果、ヒット件数0件でした。`')
        postc()

    @commands.command()
    async def count(self,ctx,*args):
        '''
        登録数を表示

        '''
        _id = ctx.guild.id
        res = registered_list(serverid = _id)
        # 登録がある場合は登録数を表示
        if res:
            await ctx.send(content=f'`このサーバーでの登録数は{len(res)}個です。`')
        # キーワード登録がない場合はそのことを伝える。
        else:
            await ctx.send(content=f'`このサーバーで登録はありません。`')
        postc(args)

    @commands.command()
    async def profile(self,ctx,*args):
        '''
        bot作成者の紹介
        '''
        embed= discord.Embed(title="**bot作成者**", description=f"趣味でbot等を作っています。\n [GitHubプロフィールページ](https://github.com/G1998G)")
        embed.set_thumbnail(url="https://avatars.githubusercontent.com/u/60283066?s=400&v=4")
        await ctx.send(embed=embed)
        postc(args)

if __name__ == '__main__':
    intents = discord.Intents.all()
    intents.members = True
    bot = commands.Bot(command_prefix=commands.when_mentioned_or("-"),intents=intents,help_command= HelpCommand())
    bot.add_cog(BasicCommand(bot=bot))
    bot.add_cog(DeleteCommand(bot=bot))
    bot.add_cog(ReferenceCommand(bot=bot))
    @bot.event
    async def on_ready():
        print(f'🟠ログインしました🟠')
    check_db()

bot.run( 'TOKEN')