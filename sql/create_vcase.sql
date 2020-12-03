CREATE VIEW v_case AS
 SELECT DISTINCT
    cd.case_number,
    cd.status,
    cd.register_url,
    cd.precinct,
    cd.style,
    cd.plaintiff,
    cd.defendants,
    cd.plaintiff_zip,
    cd.defendant_zip,
	cd.date_filed as date,
    cd.case_type,
    d.type,
    d.amount,
    d.awarded_to,
    d.awarded_against
   FROM case_detail cd
     LEFT JOIN disposition d ON cd.case_number = d.case_number;
