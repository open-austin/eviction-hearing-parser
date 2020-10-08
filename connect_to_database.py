import os
import psycopg2
from dotenv import load_dotenv
load_dotenv()

def get_database_connection(local_dev=True):
    if local_dev:
        conn = psycopg2.connect(os.getenv("LOCAL_DATABASE_URL"))
    else:
        conn = psycopg2.connect(os.getenv("DATABASE_URL"))

    return conn



# example of using function
# conn = get_database_connection()
# cur = conn.cursor()
# cur.execute("SELECT * from case_detail")
# rows = cur.fetchall()
# for row in rows:
#     print(row)
#     print(type(row))
# print("Operation done successfully")
# conn.close()



# conn = get_database_connection()
# # conn.execute("pragma journal_mode=wal")
#
# curs = conn.cursor()
# curs.execute(
#     """
#     INSERT INTO CASE_DETAIL
#     (ID, STATUS, REGISTER_URL, PRECINCT, STYLE, PLAINTIFF, DEFENDANTS, PLAINTIFF_ZIP, DEFENDANT_ZIP)
#     VALUES (%(case_num)s, %(status)s, %(reg_url)s, %(prec_num)s, %(style)s, %(plaint)s, %(defend)s, %(plaint_zip)s, %(defend_zip)s)
#
#     """,
#     {
#         'case_num': "j-ccs",
#         'status': "done",
#         'reg_url': "www.com",
#         'prec_num': 2,
#         'style': "good style",
#         'plaint': "landlord bob",
#         'defend': "defendent A",
#         'plaint_zip': "123",
#         'defend_zip': "456",
#     },
# )
# curs.commit()
# conn.close()
