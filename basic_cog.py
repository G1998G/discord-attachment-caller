from discord.ext import commands # Bot Commands Frameworkのインポート
import main as main
import discord
class BasicCommands(commands.Cog):

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
            await main.Msg.no_arg(ctx)
        else:
            arg = ' '.join(arg)
            res = main.sql.search_keyword(guild_id = _id,keyword = arg)
            print(res)
            if ctx.message.attachments:
                if len(arg) > 20:
                     # キーワードが10文字以上の場合は拒否
                    await main.Msg.len_over(ctx)
                
                elif res:
                    # キーワードで登録がある場合は上書きするか尋ねる
                    await ctx.reply(f'>>> キーワード:{arg}は既にこのファイルが登録されています。ファイルを置き換える場合は {ctx.prefix}okと入力してください。置き換えない場合は{ctx.prefix}noと入力してください。\n >>> {res["content"]}')
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
                        main.sql.insert_dt(guild_id=_id,keyword=arg,content=attachment,userid=ctx.author.id)
                        await ctx.reply(f'>>> キーワード:{arg}でファイルを登録しました。')
                        print(f'新規登録:{arg},url:{attachment},by{ctx.author.id}')
                        break

            
            elif not res:
                # アタッチメントが無く、登録もない場合はその旨を伝える
                await main.Msg.no_img(ctx,arg)
            
            else:
                # アタッチメントが無く、登録がある場合は登録画像を表示
                await ctx.reply(f'{res["content"]}')
                print(f'表示:{arg}')
        main.postc(ctx,arg)

    @commands.command()
    async def ok(self,ctx,*arg):
        '''
        登録済みファイルの置き換え確認 OK
        '''
        _id = ctx.guild.id
        if str(_id) in self.update_file:
            keyword = self.update_file[str(_id)][0]
            attachment = self.update_file[str(_id)][1]
            main.sql.update_dt(guild_id=_id, keyword=keyword, content=attachment, userid=ctx.author.id)
            await ctx.reply(content=f'>>> キーワード:{keyword}の既存アタッチメントを指定ファイルで置き換えしました。')
            del self.update_file[str(_id)]
        main.postc(ctx=ctx)

    @commands.command()
    async def no(self,ctx,*arg):
        '''
        登録済みファイルの置き換え確認　NO
        '''
        _id = ctx.guild.id
        if  str(_id) in self.update_file:
            keyword = self.update_file[str(_id)][0]
            await ctx.reply(content=f'>>> キーワード:{keyword}に登録された既存ファイルを指定されたファイルで置き換えしません。')
            del self.update_file[str(_id)]
        main.postc(ctx,arg)

async def setup(bot: commands.Bot):
    print('BasicCommands読み込み')
    await bot.add_cog(BasicCommands(bot))