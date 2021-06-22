from discord.ext import commands # Bot Commands Frameworkのインポート
import discord
import sqlite3
from contextlib import closing
from disputils import BotEmbedPaginator
from disputils.pagination import ControlEmojis

# guild内投稿回数カウント用
class C:
    def __init__(self):
        self.x = 0
    def __call__(self):
        self.x += 1
        return print(f'コマンド受け取り🟢{self.x}回目')
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

class HelpCommand(commands.HelpCommand):
    def __init__(self):
        super().__init__()
        self.no_category = "HelpCommand"
        self.command_attrs["description"] = "コマンドリストを表示します。"

    async def send_bot_help(self,mapping):
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
        embed = discord.Embed(title="**コマンドリスト**",description=content,color=discord.Colour.dark_orange())
        await self.get_destination().send(embed=embed)
        postc()


class BasicCommand(commands.Cog):

    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.update_file = dict()

    @commands.command()
    async def img(self,ctx,*arg):
        '''
        新規登録機能、登録済み画像表示機能

        '''
        _id = ctx.guild.id
        if arg:
            arg = ' '.join(arg)
            res = search_keyword(serverid = _id,keyword = arg)
            if ctx.message.attachments:
                # キーワードが10文字以上の場合は拒否
                if len(arg) > 15:
                    await ctx.send(content='`キーワードはスペース含め15文字以内に収めてください`')
                # キーワードで登録がある場合は上書きするか尋ねる
                elif res:
                    await ctx.send(content=f'`キーワード:{arg}は既にこの画像が登録されています。画像を上書きする場合は !okと入力してください。しない場合は!noと入力してください。`\n{res["content"]}')
                    # 登録は１枚まで。
                    for attachment in ctx.message.attachments:
                        attachment = str(attachment)
                        self.update_file[str(_id)] = [arg,attachment]
                        print(self.update_file[str(_id)])
                        break
                # キーワードに登録がない場合は画像登録
                else:
                    # 登録は１枚まで。
                    for attachment in ctx.message.attachments:
                        attachment = str(attachment)
                        insert_dt(serverid=_id,keyword=arg,content=attachment,userid=ctx.author.id)
                        await ctx.send(content=f'`キーワード:{arg}で画像を登録しました。`')
                        break

            # アタッチメントが無く、登録もない場合はその旨を伝える
            elif not res:
                await ctx.send(content=f'`キーワード:{arg}で画像は登録されてません。`')
            # アタッチメントが無く、登録がある場合は登録画像を表示
            else:
                await ctx.send(content=f'{res["content"]}')
        # キーワードが入力されていない場合はその旨を伝える
        else:
            await ctx.send(content='`!imgを入力するときは必ずキーワードを指定してください。`')
        postc()

    @commands.command()
    async def ok(self,ctx,*arg):
        '''
        登録済み画像への上書き確認 OK
        '''
        _id = ctx.guild.id
        if str(_id) in self.update_file:
            keyword = self.update_file[str(_id)][0]
            attachment = self.update_file[str(_id)][1]
            update_dt(serverid=_id, keyword=keyword, content=attachment, userid=ctx.author.id)
            await ctx.send(content=f'`キーワード:{keyword}の既存画像を指定画像で上書きしました。`')
            del self.update_file[str(_id)]
        postc()

    @commands.command()
    async def no(self,ctx,*arg):
        '''
        登録済み画像への上書き確認　NO
        '''
        _id = ctx.guild.id
        if  str(_id) in self.update_file:
            keyword = self.update_file[str(_id)][0]
            await ctx.send(content=f'`キーワード:{keyword}に登録された既存画像を指定された画像で上書きしません。`')
            del self.update_file[str(_id)]
        postc()

class DeleteCommand(commands.Cog):

    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.deletekeyword = dict()

    @commands.command(name='del')
    async def _delete(self,ctx,*arg):
        '''
        登録済み画像を削除する
        '''
        _id = ctx.guild.id
        if arg:
            arg = ' '.join(arg)
            res = search_keyword(serverid = _id,keyword = arg)
            if res:
                await ctx.send(content=f'`キーワード:{arg}に登録されたこの画像を削除しますか？　削除する場合は !delok, しない場合は !delnoと入力してください。`\n{res["content"]}')
                self.deletekeyword[str(_id)] = arg
            else:
                await ctx.send(content=f'`キーワード:{arg}の登録はありません。`')
        else:
            await ctx.send(content='`削除する画像のキーワードを指定してください。`')
        postc()

    @commands.command()
    async def delok(self,ctx,*arg):
        '''
        登録済み画像削除を確認 OK
        '''
        _id = ctx.guild.id
        if str(_id) in self.deletekeyword:
            keyword = self.deletekeyword[str(_id)]
            delete_dt(serverid=_id, keyword=keyword)
            await ctx.send(content=f'`キーワード:{keyword}に登録された画像を削除しました。`')
            del self.deletekeyword[str(_id)],keyword
        else:
            await ctx.send(content=f'`このコマンドは登録画像削除実行用コマンドです。まずはdelok キーワードで削除する画像を指定してください`')
        postc()

    @commands.command()
    async def delno(self,ctx,*arg):
        '''
        登録済み画像削除を確認 NO
        '''
        _id = ctx.guild.id
        if str(_id) in self.deletekeyword:
            keyword = self.deletekeyword[str(_id)]
            await ctx.send(content=f'`キーワード:{keyword}に登録された画像を削除しません。`')
            del self.deletekeyword[str(_id)],keyword
        else:
            await ctx.send(content=f'`このコマンドは登録画像削除実行用コマンドです。まずはdelok キーワードで削除する画像を指定してください`')
        postc()



class ReferenceCommand(commands.Cog):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    @commands.command(name="list")
    async def pagenate(self,ctx,*args):
        '''
        登録一覧を表示
        '''
        embeds = []
        _id = ctx.guild.id
        res = registered_list(serverid=_id)
        if res:
            print(res,len(res))
            page = 1
            embeds.append( discord.Embed(title=f"登録一覧(登録数:{len(res)}) {page}ページ目",description=f"{''.join(res[0:19])}",color=discord.Colour.dark_orange()) )
            if len(res) > 20:
                q = len(res) // 20
                mod = len(res) % 20
                x = 1
                _index = 20
                while x < q:
                    page += 1
                    content1 = res[_index:_index+20]
                    embeds.append( discord.Embed(title=f"登録一覧(登録数:{len(res)}) {page}ページ目",description=f"{' '.join(content1)}",color=discord.Colour.dark_orange()) )
                    x +=1
                    _index += 20
                if mod > 0:
                    page += 1
                    content2= res[_index:_index+mod-1]
                    embeds.append( discord.Embed(title=f"登録一覧(登録数:{len(res)}) {page}ページ目",description=f"{''.join(content2)}",color=discord.Colour.dark_orange()) )

            paginator = BotEmbedPaginator(ctx, pages=embeds,control_emojis=ControlEmojis(first='⏮', previous='◀', next='▶', last='⏭', close=None))
            await paginator.run(timeout_msg='```listコマンドは100秒間だけ表示&操作可能です。再度表示&操作したい場合はもう一度コマンドを実行してください。```')
        else:
            await ctx.send(content='`このサーバーでは何も登録がないようです。`')
        postc()


    @commands.command()
    async def author(self,ctx,*arg):
        '''
        入力されたキーワードの登録者を表示

        '''
        _id = ctx.guild.id
        if arg:
            arg = ' '.join(arg)
            res = search_keyword(serverid = _id,keyword = arg)
            # キーワードが20文字以上の場合は拒否
            if len(arg) > 20:
                await ctx.send(content='`登録されているキーワードはスペースキー含め20文字以内のはずです`')
            else:
                if res:
                    await ctx.send(content=f'`キーワード:{arg}に画像を登録した人は{bot.get_user(res["userid"]).name}です`')
                else:
                    await ctx.send(content=f'`キーワード:{arg}で画像は登録されてません。`')

        # キーワードが入力されていない場合はその旨を伝える
        else:
            await ctx.send(content='`!authorを入力するときは必ずキーワードを指定してください。`')
        postc()

    @commands.command()
    async def count(self,ctx,*arg):
        '''
        登録数を表示

        '''
        _id = ctx.guild.id
        res = registered_list(serverid = _id)
        # 登録がある場合は登録数を表示
        if res:
            await ctx.send(content=f'`このサーバーでの登録数は{len(res)}個です。`')
        # キーワードに登録がない場合はそのことを伝える。
        else:
            await ctx.send(content=f'`このサーバーで登録はありません。`')
        postc()

    @commands.command()
    async def profile(self,ctx,*args):
        '''
        bot作成者の紹介
        '''
        embed= discord.Embed(title="**bot作成者**", description=f"趣味でbot等を作っています。\n [GitHubプロフィールページ](https://github.com/G1998G)")
        embed.set_thumbnail(url="https://avatars.githubusercontent.com/u/60283066?s=400&v=4")
        await ctx.send(embed=embed)
        postc()

if __name__ == '__main__':
    intents = discord.Intents.all()
    intents.members = True
    bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"),intents=intents,help_command= HelpCommand())
    bot.add_cog(BasicCommand(bot=bot))
    bot.add_cog(DeleteCommand(bot=bot))
    bot.add_cog(ReferenceCommand(bot=bot))
    @bot.event
    async def on_ready():
        print(f'🟠ログインしました🟠')
    check_db()

bot.run( 'TOKEN')