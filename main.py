from discord.ext import commands # Bot Commands Frameworkのインポート
import discord
import sqlite3
from contextlib import closing
import sql_setting

# guild内投稿回数カウント用
class C:
    def __init__(self):
        self.x = 0
    def __call__(self,*arg : tuple):
        self.x += 1
        if arg is tuple :
            arg = ''.join(arg)

        elif arg is str or int:
            pass
        else:
            arg =" -コマンド引数なし"
        return print(f'コマンド受け取り🟢{self.x}回目　コマンド引数:{arg}')
postc = C()


class Msg:

    @staticmethod
    async def len_over(ctx):
        await ctx.send(f'>>> キーワードはスペース含め20文字以内で入力してください。')
    
    @staticmethod
    async def no_key(ctx):
        await ctx.send(f'>>> {ctx.prefix}{ctx.invoked_with}入力時は必ずキーワードを指定してください。')
    
    @staticmethod
    async def no_img(ctx,keyword):
        await ctx.send(content=f'>>> キーワード:{keyword}でファイルは登録されてません。')



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
        embed = discord.Embed(title="**呼び出し君bot**",description=f'discordにアップロードしたファイルをいつでも呼び出せるようにしたbotです。 \nコマンドの先頭には「{self.context.prefix}」を付けてください。')
        embed = embed.add_field(name="**コマンドリスト**",value=content)

        await self.get_destination().send(embed=embed)
        postc()


intents = discord.Intents.all()
intents.members = True
bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"),intents=intents,help_command= HelpCommand())
bot.load_extension('basic_cog')
bot.load_extension('del_cog')
bot.load_extension('ref_cog')

# sql起動
sql = sql_setting.SqlSet(dbname = 'database.db',bot=bot)

@bot.event
async def on_ready():
    print(f'🟠ログインしました🟠{len(bot.guilds)}ギルド')

@bot.event
async def on_guild_remove(guild):
    sql.delete_guild(guild.id)


bot.run( 'TOKEN')

    