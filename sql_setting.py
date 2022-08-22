import sqlite3
from contextlib import closing

class SqlSet:

    def __init__(self,dbname):
        self.dbname = dbname

        with closing(sqlite3.connect(self.dbname)) as connection:
            cursor = connection.cursor()
            # テーブルを作成
            cursor.execute("SELECT * FROM sqlite_master WHERE type='table' and name='discord_table1'")
            if not cursor.fetchone():
                sql = 'CREATE TABLE discord_table1 (guild_id INT,keyword VARCHAR(1024), content VARCHAR(1024),userid INT)'
                print('テーブルを作成しました')
                cursor.execute(sql)
                connection.commit()
            else:
                print('既にテーブルはありました')
            connection.close()

    def insert_dt(self,guild_id,keyword,content,userid):
        with closing(sqlite3.connect(self.dbname)) as connection:
            cursor = connection.cursor()
            sql = 'INSERT INTO discord_table1 (guild_id,keyword,content,userid) VALUES (?,?,?,?)'
            data = (int(guild_id), keyword, content, userid)
            cursor.execute(sql, data)
            connection.commit()
            connection.close()

    def update_dt(self,guild_id,keyword,content,userid):
        with closing(sqlite3.connect(self.dbname)) as connection:
            cursor = connection.cursor()
            sql = 'UPDATE discord_table1 SET content=?, userid=? WHERE guild_id=? AND keyword=?'
            data = (content, userid, guild_id, keyword)
            cursor.execute(sql, data)
            connection.commit()
            connection.close()


    def delete_dt(self,guild_id,keyword):
        with closing(sqlite3.connect(self.dbname)) as connection:
            cursor = connection.cursor()
            sql = 'DELETE FROM discord_table1 WHERE guild_id=? AND keyword=?'
            data = (int(guild_id), keyword)
            cursor.execute(sql, data)
            connection.commit()
            connection.close()

    def delete_guild(self,guild_id):
        with closing(sqlite3.connect(self.dbname)) as connection:
            cursor = connection.cursor()
            sql = 'DELETE FROM discord_table1 WHERE guild_id=?'
            data = (int(guild_id))
            cursor.execute(sql, data)
            connection.commit()
            connection.close()

    # キーワード全一致で検索
    def search_keyword(self,guild_id,keyword):
        res = dict()
        with closing(sqlite3.connect(self.dbname)) as connection:
            # sqlite3.Rowでカラム名での取得を可能にする。
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
            sql = 'SELECT * FROM discord_table1 WHERE guild_id=? AND keyword=?'
            data = (guild_id,keyword)
            cursor.execute(sql, data)
            for row in cursor:
                res['keyword'] = row['keyword']
                res['content'] = row['content']
                res['userid'] = row['userid']
            connection.close()
        return res
                

    def registered_list(self,bot,guild_id):
        res = list()
        with closing(sqlite3.connect(self.dbname)) as connection:
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
            sql = 'SELECT keyword,userid FROM discord_table1 WHERE guild_id= ?'
            data = (guild_id,)
            cursor.execute(sql, data)
            for row in cursor:
                userid = int(row["userid"])
                user = bot.get_user(userid)
                res.append(f'**`{row["keyword"]}`** {user.display_name}\n')
            connection.close()
            return res  

    def search_keyword_partial(self,bot,guild_id,keyword):
        res = list()
        keyword = f'%{keyword}%'
        with closing(sqlite3.connect(self.dbname)) as connection:
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
            sql = 'SELECT keyword,userid FROM discord_table1 WHERE guild_id= ? AND keyword LIKE ?'
            data = (guild_id,keyword)
            cursor.execute(sql, data)
            for row in cursor:
                userid = int(row["userid"])
                user = bot.get_user(userid)
                res.append(f'**`{row["keyword"]}`** {user.display_name}\n')
            connection.close()
            return res  

    def search_author(self,guild_id,userid):
        res = list()
        with closing(sqlite3.connect(self.dbname)) as connection:
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
            sql = 'SELECT keyword,userid FROM discord_table1 WHERE guild_id= ? AND userid= ?'
            data = (guild_id,userid)
            cursor.execute(sql, data)
            for row in cursor:
                res.append(f'**`{row["keyword"]}`**\n')
            connection.close()
        return res  

    def random_quote(self,guild_id):
        res =list()
        with closing(sqlite3.connect(self.dbname)) as connection:
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
            #SELECT * FROM idols ORDER BY RANDOM() LIMIT 10;
            sql = 'SELECT * FROM discord_table1 WHERE guild_id= ? ORDER BY RANDOM() LIMIT 1'
            data = (guild_id,)
            cursor.execute(sql, data)
            for row in cursor:
                res.append(f'{row["content"]}')
            connection.close()
        return res  
