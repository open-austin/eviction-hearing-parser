CREATE VIEW filings_archive AS
 SELECT case_detail.case_number,
    case_detail.status,
    case_detail.precinct,
    case_detail.style,
    case_detail.plaintiff,
    case_detail.defendants,
    case_detail.plaintiff_zip,
    case_detail.defendant_zip,
    case_detail.case_type,
    case_detail.date_filed,
    case_detail.active_or_inactive,
    case_detail.judgment_after_moratorium,
    disposition.type,
    disposition.date,
    disposition.amount,
    disposition.awarded_to,
    disposition.awarded_against,
    disposition.judgement_for,
    disposition.attorneys_for_plaintiffs,
    disposition.attorneys_for_defendants
   FROM case_detail,
    disposition
  WHERE case_detail.case_number = disposition.case_number;
