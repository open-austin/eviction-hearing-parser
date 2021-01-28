CREATE VIEW eviction_events AS
 SELECT case_detail.case_number,
    case_detail.case_type,
    event.event_number,
    event.date,
    event."time",
    event.officer,
    event.result,
    event.type,
    event.all_text
   FROM case_detail,
    event
  WHERE case_detail.case_number = event.case_number AND case_detail.case_type = 'Eviction'::text;
