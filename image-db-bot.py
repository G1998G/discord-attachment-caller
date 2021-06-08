from discord.ext import commands # Bot Commands Frameworkのインポート
import discord
import sqlite3
from contextlib import closing

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
    with closing(sqlite3.connect(dbname,uri=False)) as connection:
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
    with closing(sqlite3.connect(dbname,uri=False)) as connection:
        cursor = connection.cursor()
        sql = 'INSERT INTO discord_table (serverid,keyword,content,userid) VALUES (?,?,?,?)'
        data = (int(serverid), keyword, content, userid)
        cursor.execute(sql, data)
        connection.commit()
        connection.close()

def update_dt(serverid,keyword,content,userid):
    dbname = 'database.db'
    with closing(sqlite3.connect(dbname,uri=False)) as connection:
        cursor = connection.cursor()
        sql = 'UPDATE discord_table SET content=?, userid=? WHERE serverid=? AND keyword=?'
        data = (content, userid, serverid, keyword)
        cursor.execute(sql, data)
        connection.commit()
        connection.close()


def delete_dt(serverid,keyword):
    dbname = 'database.db'
    with closing(sqlite3.connect(dbname,uri=False)) as connection:
        cursor = connection.cursor()
        sql = 'DELETE FROM discord_table WHERE serverid=? AND keyword=?'
        data = (int(serverid), keyword)
        cursor.execute(sql, data)
        connection.commit()
        connection.close()

def search_keyword(serverid,keyword):
    dbname = 'database.db'
    res = dict()
    with closing(sqlite3.connect(dbname,uri=False)) as connection:
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
            

def resistered_list(serverid):
    dbname = 'database.db'
    res = list()
    with closing(sqlite3.connect(dbname)) as connection:
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        sql = 'SELECT keyword,userid FROM discord_table WHERE serverid= ?'
        data = (serverid,)
        cursor.execute(sql, data)
        for row in cursor:
            res.append(f'> **`{row["keyword"]}`** _`{bot.get_user(row["userid"]).name}`_\n')
        connection.close()
    return res  

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
                    await ctx.send(content='```キーワードはスペース含め15文字以内に収めてください```')
                else:
                    # キーワードで登録がある場合は上書きするか尋ねる
                    if res:
                        await ctx.send(content=f'```キーワード:{arg}は既にこの画像が登録されています。画像を上書きする場合は !okと入力してください。しない場合は!noと入力してください。```\n{res["content"]}')
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
                            await ctx.send(content=f'```キーワード:{arg}で画像を登録しました。```')
                            break

            # アタッチメントが無く、登録もない場合はその旨を伝える
            elif not res:
                await ctx.send(content=f'```キーワード:{arg}で画像は登録されてません。```')
            # アタッチメントが無く、登録がある場合は登録画像を表示
            else:
                await ctx.send(content=f'{res["content"]}')
        # キーワードが入力されていない場合はその旨を伝える
        else:
            await ctx.send(content='```!imgを入力するときは必ずキーワードを指定してください。```')
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
            await ctx.send(content=f'```キーワード:{keyword}の既存画像を指定画像で上書きしました。```')
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
            await ctx.send(content=f'```キーワード:{keyword}に登録された既存画像を指定された画像で上書きしません。```')
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
                await ctx.send(content=f'```キーワード:{arg}に登録されたこの画像を削除しますか？　削除する場合は !delok, しない場合は !delnoと入力してください。```\n{res["content"]}')
                self.deletekeyword[str(_id)] = arg
            else:
                await ctx.send(content=f'```キーワード:{arg}の登録はありません。```')
        else:
            await ctx.send(content='```削除する画像のキーワードを指定してください。```')
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
            await ctx.send(content=f'```キーワード:{keyword}に登録された画像を削除しました。```')
            del keyword
        postc()

    @commands.command()
    async def delno(self,ctx,*arg):
        '''
        登録済み画像削除を確認 NO
        '''
        _id = ctx.guild.id
        if str(_id) in self.deletekeyword:
            keyword = self.deletekeyword[str(_id)]
            await ctx.send(content=f'```キーワード:{keyword}に登録された画像を削除しません。```')
            del keyword
        postc()

class SelectCommand(commands.Cog):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    @commands.command(name='list')
    async def _list(self,ctx):
        '''
        登録一覧を表示
        '''
        _id = ctx.guild.id
        res = resistered_list(serverid=_id)
        if res:
            print(res)
            embed=discord.Embed(title=f"登録一覧 ",description=f"登録数:{len(res)}",color=0xff0000)
            embed.add_field(name="🔻一覧🔻", value=f"{''.join(res[0:29])}", inline=False)
            await ctx.send(embed = embed)
            if len(res) > 30:
                q = len(res) // 30
                mod = len(res) % 30
                x = 0
                _index = 30
                while x <= q:
                    content = res[_index:_index+30]
                    embed=discord.Embed(title=f"登録一覧(続き)",color=0xff0000)
                    embed.add_field(name='_', value=f"{''.join(content)}", inline=False)
                    await ctx.send(embed = embed)
                    x +=1
                    _index += 30
                if mod > 0:
                    content = res[_index:_index+mod-1]
                    embed=discord.Embed(title=f"登録一覧(続き)",color=0xff0000)
                    embed.add_field(name='_', value=f"{''.join(content)}", inline=False)
                    await ctx.send(embed = embed)
        else:
            await ctx.send(content='```このサーバーでは何も登録がないようです。```')
        postc()

if __name__ == '__main__':
    intents = discord.Intents.all()
    intents.members = True
    bot = commands.Bot(command_prefix='!',intents=intents)
    bot.add_cog(BasicCommand(bot=bot))
    bot.add_cog(DeleteCommand(bot=bot))
    bot.add_cog(SelectCommand(bot=bot))
    @bot.event
    async def on_ready():
        print(f'🟠ログインしました🟠')
    check_db()

bot.run( 'TOKEN')