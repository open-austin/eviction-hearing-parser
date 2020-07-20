import sqlite3


def get_case(case_id: str):
    conn = sqlite3.connect("cases.db")
    conn.row_factory = sqlite3.Row
    curs = conn.cursor()
    curs.execute("SELECT * FROM CASE_DETAIL WHERE ID = ?", (case_id,))
    case = curs.fetchone()
    curs.close()
    return dict(case)


def rest_case(case):
    """
    Takes a dictionary representation of a case and maps it in to a sqlite DB
    """
    conn = sqlite3.connect("cases.db")
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
    # TODO scrape all event types in a similar way (writs should be consolidated in)
    # Types should mirror the values from the HTML table headers, HR/ER/SE/etc.
    for hearing in case["hearings"]:
        curs.execute(
            """
            INSERT OR REPLACE INTO EVENT
            (CASE_DETAIL_ID, DATE, TIME, OFFICER, RESULT, TYPE)
            VALUES (?, ?, ?, ?, ?, 'HR')
            """,
            (
                case["case_number"],
                hearing["hearing_date"],
                hearing["hearing_time"],
                hearing["hearing_officer"],
                hearing["appeared"],
            ),
        )
    conn.commit()
    curs.close()
