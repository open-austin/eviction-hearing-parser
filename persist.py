"""Module for writing data to and reading from PostgreSQL database"""

import os
from dotenv import load_dotenv
from connect_to_database import get_database_connection

load_dotenv()
local_dev = os.getenv("LOCAL_DEV") == "true"

def get_case(case_id: str) -> Dict:
    conn = get_database_connection(local_dev=local_dev)

    # conn.row_factory = sqlite3.Row
    curs = conn.cursor()
    curs.execute("SELECT * FROM V_CASE WHERE CASE_NUMBER = ?", (case_id,))
    case = curs.fetchone()
    curs.close()
    return dict(case)


def rest_case(case: Dict):
    """
    Takes a dictionary representation of a case and maps it into the CASE_DETAIL, DISPOSITION,
    and EVENT table of the PostgreSQL database
    """

    conn = get_database_connection(local_dev=local_dev)
    curs = conn.cursor()
    curs.execute(
    """
    INSERT INTO CASE_DETAIL
    (CASE_NUMBER, STATUS, REGISTER_URL, PRECINCT, STYLE, PLAINTIFF, DEFENDANTS, PLAINTIFF_ZIP, DEFENDANT_ZIP, CASE_TYPE, DATE_FILED, ACTIVE_OR_INACTIVE, JUDGMENT_AFTER_MORATORIUM)
    VALUES (%(case_num)s, %(status)s, %(reg_url)s, %(prec_num)s, %(style)s, %(plaint)s, %(defend)s, %(plaint_zip)s, %(defend_zip)s, %(type)s, %(date_filed)s, %(active_or_inactive)s, %(after_moraorium)s)
    ON CONFLICT(CASE_NUMBER)
    DO UPDATE SET
    (STATUS, REGISTER_URL, PRECINCT, STYLE, PLAINTIFF, DEFENDANTS, PLAINTIFF_ZIP, DEFENDANT_ZIP, CASE_TYPE, DATE_FILED, ACTIVE_OR_INACTIVE, JUDGMENT_AFTER_MORATORIUM) =
    (%(status)s, %(reg_url)s, %(prec_num)s, %(style)s, %(plaint)s, %(defend)s, %(plaint_zip)s, %(defend_zip)s, %(type)s, %(date_filed)s, %(active_or_inactive)s, %(after_moraorium)s)
    """,
        {
            'case_num': case["case_number"],
            'status': case["status"],
            'reg_url': case["register_url"],
            'prec_num': case["precinct_number"],
            'style': case["style"],
            'plaint': case["plaintiff"],
            'defend': case["defendants"],
            'plaint_zip': case["plaintiff_zip"],
            'defend_zip': case["defendant_zip"],
            'type': case["type"],
            'date_filed': case["date_filed"],
            'active_or_inactive': case["active_or_inactive"],
            'after_moraorium': case["judgment_after_moratorium"]
        },
    )

    curs.execute(
    """
    INSERT INTO DISPOSITION
    (CASE_NUMBER, TYPE, DATE, AMOUNT, AWARDED_TO, AWARDED_AGAINST,JUDGEMENT_FOR,MATCH_SCORE,ATTORNEYS_FOR_PLAINTIFFS, ATTORNEYS_FOR_DEFENDANTS, COMMENTS)
    VALUES (%(case_num)s, %(disp_type)s, %(disp_date)s, %(disp_amt)s, %(disp_to)s, %(disp_against)s, %(judgement_for)s,%(match_score)s,%(attorneys_for_plaintiffs)s, %(attorneys_for_defendants)s, %(comments)s)
    ON CONFLICT(CASE_NUMBER)
    DO UPDATE SET
    (TYPE, DATE, AMOUNT, AWARDED_TO, AWARDED_AGAINST, JUDGEMENT_FOR, MATCH_SCORE,ATTORNEYS_FOR_PLAINTIFFS, ATTORNEYS_FOR_DEFENDANTS,COMMENTS) =
    (%(disp_type)s, %(disp_date)s, %(disp_amt)s, %(disp_to)s, %(disp_against)s, %(judgement_for)s,%(match_score)s, %(attorneys_for_plaintiffs)s, %(attorneys_for_defendants)s,  %(comments)s)
    """,
        {
            'case_num': case["case_number"],
            'disp_type': case["disposition_type"],
            'disp_date': case["disposition_date"],
            'disp_amt': str(case["disposition_amount"]),
            'disp_to': case["disposition_awarded_to"],
            'disp_against': case["disposition_awarded_against"],
            'judgement_for': case["judgement_for"],
            'match_score': case["match_score"],
            'attorneys_for_plaintiffs': case["attorneys_for_plaintiffs"],
            'attorneys_for_defendants': case["attorneys_for_defendants"],
            'comments': case["comments"]
        },
    )
    # TODO scrape all event types in a similar way (writs should be consolidated in)
    # Types should mirror the values from the HTML table headers, HR/ER/SE/etc.
    for hearing_number, hearing in enumerate(case["hearings"]):
        curs.execute(
            """
            INSERT INTO EVENT
            (CASE_NUMBER, EVENT_NUMBER, DATE, TIME, OFFICER, RESULT, TYPE, ALL_TEXT)
            VALUES (%(case_num)s, %(hearing_num)s, %(hearing_date)s, %(hearing_time)s, %(hearing_officer)s, %(hearing_appeared)s, %(hearing_type)s, %(all_text)s)
            ON CONFLICT(CASE_NUMBER, EVENT_NUMBER)
            DO UPDATE SET
            (EVENT_NUMBER, DATE, TIME, OFFICER, RESULT, TYPE, ALL_TEXT) =
            (%(hearing_num)s, %(hearing_date)s, %(hearing_time)s, %(hearing_officer)s, %(hearing_appeared)s, %(hearing_type)s, %(all_text)s)
            """,
            {
                'case_num': case["case_number"],
                'hearing_num': hearing_number,
                'hearing_date': hearing["hearing_date"],
                'hearing_time': hearing["hearing_time"],
                'hearing_officer': hearing["hearing_officer"],
                'hearing_appeared': hearing["appeared"],
                'hearing_type': hearing["hearing_type"],
                'all_text': hearing["all_text"]
            },
        )
    conn.commit()
    curs.close()
    conn.close()

def rest_setting(setting: Dict):
    """Takes a dictionary representation of a setting and maps it into the SETTING table of the PostgreSQL database"""

    conn = get_database_connection(local_dev=local_dev)
    curs = conn.cursor()
    curs.execute(
    """
    INSERT INTO SETTING
    (CASE_NUMBER, CASE_LINK, SETTING_TYPE, SETTING_STYLE, JUDICIAL_OFFICER, SETTING_DATE, SETTING_TIME, HEARING_TYPE)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT(CASE_NUMBER, SETTING_TYPE, HEARING_TYPE, SETTING_DATE)
    DO NOTHING
    """,
        (
            setting["case_number"],
            setting["case_link"],
            setting["setting_type"],
            setting["setting_style"],
            setting["judicial_officer"],
            setting["setting_date"],
            setting["setting_time"],
            setting["hearing_type"],
        ),
    )
    conn.commit()
    curs.close()
    conn.close()

def get_old_active_case_nums() -> List[str]:
    """Returns list of case numbers in CASE_DETAIL table that are still active (as determined by the STATUS column)."""

    conn = get_database_connection(local_dev=local_dev)
    curs = conn.cursor()

    curs.execute("""SELECT CASE_NUMBER FROM CASE_DETAIL WHERE LOWER(STATUS) NOT IN
                ('final disposition', 'transferred', 'bankruptcy', 'judgment released',
                'judgment satisfied', 'appealed', 'final status', 'dismissed')""")
    active_case_nums = [tup[0] for tup in curs.fetchall()]
    curs.close()
    conn.close()

    return active_case_nums

# not currently being used for anything
def drop_rows_from_table(table_name: str, case_ids: list):
    """Drops all rows with case number in case_ids from table `table_name` - works for CASE_DETAIL, DISPOSITION, and EVENT tables"""

    if len(case_ids) == 1:
        case_ids = str(tuple(case_ids)).replace(",", "")
    else:
        case_ids = str(tuple(case_ids))

    conn = get_database_connection(local_dev=local_dev)
    curs = conn.cursor()

    if table_name == "CASE_DETAIL":
        curs.execute("DELETE FROM %s WHERE CASE_NUMBER IN %s", (table_name, case_ids))
    else:
        curs.execute("DELETE FROM %s WHERE CASE_NUMBER IN %s", (table_name, case_ids))

    conn.commit()
    curs.close()
    conn.close()

def update_first_court_apperance_column():
    """Updates the first_court_appearance column of the CASE_DETAIL table in PostgreSQL using the latest database data."""

    update_query = """
                   UPDATE case_detail
                   SET first_court_appearance =
                        (SELECT MIN
                            (TO_DATE("date", 'MM/DD/YYYY')) FROM event WHERE
                                (event.case_number = case_detail.case_number) AND
                                (LOWER(event.type) IN
                                    ('appearance', 'default hearing', 'eviction hearing', 'exparte hearing', 'hearing',
                                     'indigency hearing', 'motion for dj hearing', 'motion hearing', 'pre-trial hearing',
                                     'trial before court', 'writ hearing'))
                        )
                   """

    conn = get_database_connection(local_dev=local_dev)
    curs = conn.cursor()
    curs.execute(update_query)
    conn.commit()
    curs.close()
    conn.close()
