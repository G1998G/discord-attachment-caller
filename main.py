from discord.ext import commands # Bot Commands Frameworkのインポート
import discord
import sql_setting
import asyncio

# guild内投稿回数カウント用
class C:
    def __init__(self):
        self.x = 0
    def __call__(self,ctx,*arg : tuple):
        self.x += 1
        return print(f'コマンド受け取り🟢{self.x}回目　コマンド名:{ctx.invoked_with} コマンド引数:{arg}')
postc = C()


class Msg:

    @staticmethod
    async def len_over(ctx):
        await ctx.reply(f'>>> キーワードはスペース含め20文字以内で入力してください。')
    
    @staticmethod
    async def no_arg(ctx):
        await ctx.reply(f'>>> {ctx.prefix}{ctx.invoked_with}入力時は必ずキーワードを指定してください。')
    
    @staticmethod
    async def no_img(ctx,keyword):
        await ctx.reply(f'>>> キーワード:{keyword}でファイルは登録されてません。')

    @staticmethod
    async def no_registration_in_guild(ctx):
        await ctx.reply(f'>>> このサーバーでは何も登録がないようです。')



class HelpCommand(commands.HelpCommand):
    def __init__(self):
        super().__init__()
        self.no_category = "HelpCommand"

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
        embed = discord.Embed(title="📢呼び出し君bot",description=f' discordにアップロードしたファイルをいつでも呼び出せるようにしたbotです。 \n コマンドの先頭には「{self.context.prefix}」を付けてください。')
        embed = embed.add_field(name="**コマンドリスト**",value=content)

        await self.get_destination().send(embed=embed)
        postc(self.context)

    

async def main(bot):
    await bot.load_extension('basic_cog')
    await bot.load_extension('del_cog')
    await bot.load_extension('ref_cog')
    await bot.start(token='token')

intents = discord.Intents
intents.members = True
bot = commands.Bot(intents=intents.all(), command_prefix='!',help_command=HelpCommand())
sql = sql_setting.SqlSet(dbname ='dbname')
if __name__ == '__main__':
    asyncio.run(main(bot))