import sqlite3
import pandas as pd
# db = sqlite3.connect("twitter_db.db")
db = sqlite3.connect("test_1.db")

c = db.cursor()
#c.execute("SELECT blockchain_address FROM twitter_db")
# print()
#print(c.fetchall())


# c.execute("SELECT COUNT(blockchain_address) FROM test_1")
# print("Количество blockchain_address в базе данных:", c.fetchone()[0])

# # #################
# c.execute("SELECT * FROM test_1 LIMIT 5")
# print(c.fetchall())

# c.execute("SELECT * FROM tweets_test WHERE date = 'TRX'")
# print(c.fetchall())


c.execute("SELECT COUNT(blockchain_address) FROM test_1 WHERE date = '25/05/2024'")
print(c.fetchall())

######################


# посмотреть кол-во уникальных адресов

c.execute("SELECT * FROM test_1 LIMIT 10")
print(c.fetchall())

#ПОИСК ПО ДАТЕ
#c.execute("SELECT * FROM twitter_db WHERE date = '29/04/2024'")
#print(c.fetchall())

#ПОИСК ПО АДРЕСУ
#c.execute("SELECT * FROM twitter_db WHERE blockchain_address = '0x389a9ae29fbe53cca7bc8b7a4d9d0a04078e1c24'")
#print(c.fetchall())


# data = pd.read_sql_query("SELECT * FROM twitter_db", db)

db.close()

# data.to_excel("twitter_db.xlsx", index=False)