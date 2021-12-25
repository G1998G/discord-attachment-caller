from discord.ext import commands # Bot Commands Frameworkのインポート
import discord
import sqlite3
from contextlib import closing



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

intents = discord.Intents.all()
intents.members = True
bot = commands.Bot(command_prefix=commands.when_mentioned_or("-"),intents=intents,help_command= HelpCommand())
bot.load_extension('basic_cog')
bot.load_extension('del_cog')
bot.load_extension('ref_cog')
@bot.event
async def on_ready():
    print(f'🟠ログインしました🟠')
check_db()
bot.run( 'ODI3ODA3ODU2NjUxNzk2NDkw.YGgaJA.7iQtMY_BmV3PeQ_VuSTY54gQ0RY')



    