# This file is the analysis stage of the pipeline and it reads from output/weather.db, which build_db.py created, and answers a question about the highest temperature.
# get_max() returns a pandas DataFrame with a column for the day and one for the highest temperature.
# The query has no GROUP BY, so it returns one row, the hottest day overall and not one per day.


import sqlite3
from pathlib import Path

import pandas as pd
DB_PATH = Path("output") / "weather.db"
def get_max():
    conn = sqlite3.connect(DB_PATH)
    hottest = pd.read_sql_query(
            "SELECT day, max(high) FROM forecast ", conn
        )
    conn.close()
    return hottest
if __name__=="__main__":
    print(get_max())