# import json
#
# with open('check_followed_sortedlist_in_followed.json') as f:
#   df = json.load(f)
#
# print(len(df))
# import datetime
#
# time = 1588348105
#
# # dt = datetime.datetime.fromtimestamp(time)
#
# JST = datetime.timezone(datetime.timedelta(hours=+9), 'JST')
# dt = datetime.datetime.fromtimestamp(time).replace(tzinfo=datetime.timezone.utc).astimezone(tz=JST)
# print(dt.strftime('%Y-%m-%d %H:%M:%S'))
#
# print(dt)
# # ISO8601表記
# print(dt.isoformat())

# あるいは任意のフォーマット

import pandas as pd

#変換したいJSONファイルを読み込む
df = pd.read_json("../../tmp/files/get_post_date_results.json")

#CSVに変換して任意のファイル名で保存
df.to_csv("../../tmp/files/get_post_date_results.csv")