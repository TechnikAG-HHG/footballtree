from sqlite3 import *

conn = connect("data/settings.db")
cursor = conn.cursor()

modify = """UPDATE settingsData
            SET bestScorerActive = 1
            WHERE ID = 1
            """
            
cursor.execute(modify)
conn.commit()