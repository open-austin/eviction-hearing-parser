import sqlite3


def get_case(case_id: str):
    conn = sqlite3.connect("cases.db")
    conn.execute("pragma journal_mode=wal")

    conn.row_factory = sqlite3.Row
    curs = conn.cursor()
    curs.execute("SELECT * FROM V_CASE WHERE ID = ?", (case_id,))
    case = curs.fetchone()
    curs.close()
    return dict(case)


def rest_case(case):
    """
    Takes a dictionary representation of a case and maps it in to a sqlite DB
    """
    conn = sqlite3.connect("cases.db", isolation_level=None)
    conn.execute("pragma journal_mode=wal")

    curs = conn.cursor()
    curs.execute(
        """
    INSERT OR REPLACE INTO CASE_DETAIL
    (ID, STATUS, REGISTER_URL, PRECINCT, STYLE, PLAINTIFF, DEFENDANTS, PLAINTIFF_ZIP, DEFENDANT_ZIP)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (
            case["case_number"],
            case["status"],
            case["register_url"],
            case["precinct_number"],
            case["style"],
            case["plaintiff"],
            case["defendants"],
            case["plaintiff_zip"],
            case["defendant_zip"],
        ),
    )
    curs.execute(
        """
    INSERT OR REPLACE INTO DISPOSITION
    (CASE_DETAIL_ID, TYPE, DATE, AMOUNT, AWARDED_TO, AWARDED_AGAINST)
    VALUES (?, ?, ?, ?, ?, ?)
    """,
        (
            case["case_number"],
            case["disposition_type"],
            case["disposition_date"],
            str(case["disposition_amount"]),
            case["disposition_awarded_to"],
            case["disposition_awarded_against"],
        ),
    )
    # TODO scrape all event types in a similar way (writs should be consolidated in)
    # Types should mirror the values from the HTML table headers, HR/ER/SE/etc.
    for hearing_number, hearing in enumerate(case["hearings"]):
        curs.execute(
            """
            INSERT OR REPLACE INTO EVENT
            (CASE_DETAIL_ID, EVENT_NUMBER, DATE, TIME, OFFICER, RESULT, TYPE)
            VALUES (?, ?, ?, ?, ?, ?, 'HR')
            """,
            (
                case["case_number"],
                hearing_number,
                hearing["hearing_date"],
                hearing["hearing_time"],
                hearing["hearing_officer"],
                hearing["appeared"],
            ),
        )
    curs.close()

def rest_setting(setting):
    """
    Takes a dictionary representation of a setting and maps it in to a sqlite DB
    """
    conn = sqlite3.connect("cases.db")
    curs = conn.cursor()
    curs.execute(
        """
    INSERT OR IGNORE INTO SETTING
    (CASE_NUMBER, CASE_LINK, SETTING_TYPE, SETTING_STYLE, JUDICIAL_OFFICER, SETTING_DATE, SETTING_TIME, HEARING_TYPE)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
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