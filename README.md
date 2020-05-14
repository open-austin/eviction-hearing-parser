# eviction-hearing-parser

parse registers of actions for eviction hearings

This command line utility takes a register of actions in the HTML format [published by Travis County](odysseypa.traviscountytx.gov), and extracts information about the last scheduled hearing in the register (regardless of whether the hearing is in the past or future). It can output a CSV collecting this information from many HTML files.

To use `eviction-hearing-parser`, download the HTML records that interest you from the county website, and collect them in a folder. (A script to help you do this has not yet been written).

Then, install Python on your computer. Python version 3.8 is suggested.

Make a copy of the `eviction-hearing-parser` repository and navigate to it using the command line.

On the command line in the `eviction-hearing-parser` directory, create a virtual environment with the command:

`python3 -m venv venv`

Activate the virtual environment with the command:

`source venv/bin/activate`

Install the required libraries with:

`pip install -r requirements.txt`

Then execute the command line utility with a command in this format:

`python parse_hearings.py [your input directory] [name of new output file]`

For instance, if you use the following command:

`python parse_hearings.py test_pages result.csv`

...then you'll create a new file called `result.csv` with the following contents:

| style                                           | plaintiff            | defendants                              | case_number     | zip        | hearing_date | hearing_time | hearing_officer         |
| ----------------------------------------------- | -------------------- | --------------------------------------- | --------------- | ---------- | ------------ | ------------ | ----------------------- |
| "JOHN MOE vs. Jane Roe,Unnamed Person,Jean Roe" | "MOE, JOHN"          | "Person, Unnamed; Roe, Jane; Roe, Jean" | J2-CV-20-001839 | 78759      | 05/14/2020   | 11:00 AM     | "Slagle, Randall"       |
| XYZ Group LLC vs. John G Doe                    | XYZ Group LLC        | "Doe, John G."                          | J1-CV-20-001590 | 78724      | 05/14/2020   | 11:00 AM     | "Williams, Yvonne M."   |
| UMBRELLA CORPORATION vs. Ann Noe                | UMBRELLA CORPORATION | "Noe, Ann"                              | J4-CV-20-000198 | 78741-0000 | 06/05/2020   | 2:00 PM      | "Gonzalez, Raul Arturo" |
