--
-- PostgreSQL database dump
--

-- Dumped from database version 12.4 (Ubuntu 12.4-1.pgdg16.04+1)
-- Dumped by pg_dump version 12.4

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: case_detail; Type: TABLE; Schema: public; Owner: xsqpbwotuzlraq
--

CREATE TABLE public.case_detail (
    id text NOT NULL,
    status text NOT NULL,
    register_url text NOT NULL,
    precinct integer NOT NULL,
    style text NOT NULL,
    plaintiff text,
    defendants text,
    plaintiff_zip text,
    defendant_zip text,
    case_type text
);


ALTER TABLE public.case_detail OWNER TO xsqpbwotuzlraq;

--
-- Name: disposition; Type: TABLE; Schema: public; Owner: xsqpbwotuzlraq
--

CREATE TABLE public.disposition (
    id integer NOT NULL,
    case_detail_id text NOT NULL,
    type text,
    date text NOT NULL,
    amount text,
    awarded_to text,
    awarded_against text
);


ALTER TABLE public.disposition OWNER TO xsqpbwotuzlraq;

--
-- Name: disposition_id_seq; Type: SEQUENCE; Schema: public; Owner: xsqpbwotuzlraq
--

CREATE SEQUENCE public.disposition_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.disposition_id_seq OWNER TO xsqpbwotuzlraq;

--
-- Name: disposition_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: xsqpbwotuzlraq
--

ALTER SEQUENCE public.disposition_id_seq OWNED BY public.disposition.id;


--
-- Name: event; Type: TABLE; Schema: public; Owner: xsqpbwotuzlraq
--

CREATE TABLE public.event (
    id integer NOT NULL,
    case_detail_id text NOT NULL,
    event_number integer NOT NULL,
    date text NOT NULL,
    "time" text,
    officer text,
    result text,
    type text NOT NULL
);


ALTER TABLE public.event OWNER TO xsqpbwotuzlraq;

--
-- Name: event_id_seq; Type: SEQUENCE; Schema: public; Owner: xsqpbwotuzlraq
--

CREATE SEQUENCE public.event_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.event_id_seq OWNER TO xsqpbwotuzlraq;

--
-- Name: event_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: xsqpbwotuzlraq
--

ALTER SEQUENCE public.event_id_seq OWNED BY public.event.id;


--
-- Name: setting; Type: TABLE; Schema: public; Owner: xsqpbwotuzlraq
--

CREATE TABLE public.setting (
    id integer NOT NULL,
    case_number text NOT NULL,
    case_link text,
    setting_type text,
    setting_style text,
    judicial_officer text,
    setting_date text,
    setting_time text,
    hearing_type text
);


ALTER TABLE public.setting OWNER TO xsqpbwotuzlraq;

--
-- Name: setting_id_seq; Type: SEQUENCE; Schema: public; Owner: xsqpbwotuzlraq
--

CREATE SEQUENCE public.setting_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.setting_id_seq OWNER TO xsqpbwotuzlraq;

--
-- Name: setting_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: xsqpbwotuzlraq
--

ALTER SEQUENCE public.setting_id_seq OWNED BY public.setting.id;


--
-- Name: v_case; Type: VIEW; Schema: public; Owner: xsqpbwotuzlraq
--

CREATE VIEW public.v_case AS
 SELECT DISTINCT cd.id,
    cd.status,
    cd.register_url,
    cd.precinct,
    cd.style,
    cd.plaintiff,
    cd.defendants,
    cd.plaintiff_zip,
    cd.defendant_zip,
    d.case_detail_id,
    d.type,
    d.date,
    d.amount,
    d.awarded_to,
    d.awarded_against
   FROM (public.case_detail cd
     LEFT JOIN public.disposition d ON ((cd.id = d.case_detail_id)));


ALTER TABLE public.v_case OWNER TO xsqpbwotuzlraq;

--
-- Name: disposition id; Type: DEFAULT; Schema: public; Owner: xsqpbwotuzlraq
--

ALTER TABLE ONLY public.disposition ALTER COLUMN id SET DEFAULT nextval('public.disposition_id_seq'::regclass);


--
-- Name: event id; Type: DEFAULT; Schema: public; Owner: xsqpbwotuzlraq
--

ALTER TABLE ONLY public.event ALTER COLUMN id SET DEFAULT nextval('public.event_id_seq'::regclass);


--
-- Name: setting id; Type: DEFAULT; Schema: public; Owner: xsqpbwotuzlraq
--

ALTER TABLE ONLY public.setting ALTER COLUMN id SET DEFAULT nextval('public.setting_id_seq'::regclass);


--
-- Data for Name: case_detail; Type: TABLE DATA; Schema: public; Owner: xsqpbwotuzlraq
--

COPY public.case_detail (id, status, register_url, precinct, style, plaintiff, defendants, plaintiff_zip, defendant_zip, case_type) FROM stdin;
J1-CV-20-002835	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2304858	1	Michelle Mayberry vs.  Diana McIver & Associates dba DMA Properties	Mayberry, Michelle	Diana McIver & Associates dba DMA Properties	78741	78746	Small Claims
J1-CV-20-002844	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2304873	1	 Portfolio Recovery Associates LLC Assignee Of Barclays Bank Delaware/barclays Bank Delaware vs. Ashok Adhikari	Portfolio Recovery Associates LLC Assignee Of Barclays Bank Delaware/barclays Bank Delaware	Adhikari, Ashok		78753	Debt Claim
J1-CV-20-002845	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2304874	1	 VELOCITY INVESTMENTS LLC ASSIGNEE OF PROSPER FUNDING LLC ASSIGNEE OF WEBBANK vs. SERGIO HERNANDEZ	VELOCITY INVESTMENTS LLC ASSIGNEE OF PROSPER FUNDING LLC ASSIGNEE OF WEBBANK	HERNANDEZ, SERGIO	78230	78754	Debt Claim
J1-CV-20-002846	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2304990	1	Mariana Moosavi vs.  Gtech Fitness	Moosavi, Mariana	Gtech Fitness	78704	77356	Small Claims
J1-CV-20-002847	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2304991	1	 GEICO County Mutual Insurance Company vs. Felisa Fernandez Leyva	GEICO County Mutual Insurance Company	Fernandez Leyva, Felisa	75082	78753	Small Claims
J1-CV-20-002848	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2304992	1	 Midland Credit Management Inc. vs. Eudelia Yarbrough	Midland Credit Management Inc.	Yarbrough, Eudelia	92124	78653-3965	Debt Claim
J1-CV-20-002849	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2304993	1	 Midland Credit Management Inc. vs. Patricia Adan	Midland Credit Management Inc.	Adan, Patricia	92124	78724-5800	Debt Claim
J1-CV-20-002850	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2304994	1	 Midland Credit Management Inc. vs. Lacey A Austin	Midland Credit Management Inc.	Austin, Lacey A	92124	78702-2839	Debt Claim
J1-CV-20-002851	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2304995	1	 Conn Appliances Inc. vs. Kena Loud	Conn Appliances Inc.	Loud, Kena	75011-5220	78660	Debt Claim
J1-CV-20-002852	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2304996	1	 Conn Appliances Inc. vs. Gloria V. Rivera	Conn Appliances Inc.	Rivera, Gloria V.	75011-5220	78724	Debt Claim
J1-CV-20-002853	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2304997	1	 Lvnv Funding Llc vs. Sheila Green	Lvnv Funding Llc	Green, Sheila	75011-5220	78621	Debt Claim
J1-CV-20-002854	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2304998	1	 Lvnv Funding Llc vs. Nita G Williams	Lvnv Funding Llc	Williams, Nita G	75011-5220	78723	Debt Claim
J1-CV-20-002855	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2304999	1	 Lvnv Funding Llc vs. Loren Morgan	Lvnv Funding Llc	Morgan, Loren	75011-5220	78754	Debt Claim
J1-CV-20-002856	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305000	1	 Lvnv Funding Llc vs. Melissa N Unfred	Lvnv Funding Llc	Unfred, Melissa N	75011-5220	78752	Debt Claim
J1-CV-20-002857	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305001	1	 Lvnv Funding Llc vs. Melissa Rivers	Lvnv Funding Llc	Rivers, Melissa	75011-5220	78621	Debt Claim
J1-CV-20-002858	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305002	1	 Lvnv Funding Llc vs. Melissa Rivers	Lvnv Funding Llc	Rivers, Melissa	75011-5220	78621	Debt Claim
J1-CV-20-002859	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305003	1	 Cavalry Spv I, Llc, As Assignee Of Citibank, N.a. vs. Cliff R Obermeyer	Cavalry Spv I, Llc, As Assignee Of Citibank, N.a.	Obermeyer, Cliff R	75080	78752	Debt Claim
J1-CV-20-002860	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305005	1	 Cavalry Spv I, Llc, As Assignee Of Citibank, N.a. vs. Bonifacio Buenrostro	Cavalry Spv I, Llc, As Assignee Of Citibank, N.a.	Buenrostro, Bonifacio	75080	78752	Debt Claim
J1-CV-20-002861	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305010	1	RENA RUBIT,DAIJA WILLIS,JALAN MCFARLAND vs. DAYVONE MALVO	MCFARLAND, JALAN	MALVO, DAYVONE	78725	78725	Eviction
J1-CV-20-002863	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305119	1	 Velocity Investments, Llc Assignee Of Prosper Funding Llc Assignee Of Webbank vs. Sharron Marlow	Velocity Investments, Llc Assignee Of Prosper Funding Llc Assignee Of Webbank	Marlow, Sharron	75080	78660	Debt Claim
J1-CV-20-002864	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305120	1	 Lvnv Funding Llc vs. Magaly Jimenez	Lvnv Funding Llc	Jimenez, Magaly	75080	78754-6071	Debt Claim
J1-CV-20-002865	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305121	1	 Midland Credit Management Inc. vs. Adriana Silva	Midland Credit Management Inc.	Silva, Adriana	75011-5220	78752	Debt Claim
J1-CV-20-002866	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305122	1	 Lvnv Funding Llc vs. Jesus Deluna	Lvnv Funding Llc	Deluna, Jesus	75011-5220	78724	Debt Claim
J1-CV-20-002867	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305123	1	 Cavalry SPV I, LLC assignee of CitiBank, N.A. vs. Elijio Navarro	Cavalry SPV I, LLC assignee of CitiBank, N.A.	Navarro, Elijio		78653-3843	Debt Claim
J1-CV-20-002862	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305096	1	EDWARD CABELLO vs. NATHAN FASULLO,GABRIELLE GERMILLION FASULLO	CABELLO, EDWARD	FASULLO, GABRIELLE GERMILLION; FASULLO, NATHAN	78721	78749	Small Claims
J1-CV-20-002868	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305138	1	CRYSTAL VANCLEAVE vs. FOFO KAJE	VANCLEAVE, CRYSTAL	KAJE, FOFO	77055	78626	Debt Claim
J1-CV-20-002869	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305139	1	KELLY DEMARS vs. DOMAINE REELS	DEMARS, KELLY	REELS, DOMAINE	78660	78634	Small Claims
J1-CV-20-002870	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305141	1	AAB STORE vs. MILTOS G DEVELOPMENTS OF AUSTIN, LLC	AAB STORE	MILTOS G DEVELOPMENTS OF AUSTIN, LLC	78753	78704	Small Claims
J1-CV-20-002871	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305144	1	AAB STORE vs. ISRAEL LOPEZ	AAB STORE	LOPEZ, ISRAEL	78753	78741	Small Claims
J1-CV-20-002872	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305191	1	 Conn Appliances Inc. vs. Maria Rendon	Conn Appliances Inc.	Rendon, Maria	75011-5220	78753	Debt Claim
J1-CV-20-002873	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305192	1	 Conn Appliances Inc. vs. Tyrell Edwards	Conn Appliances Inc.	Edwards, Tyrell	75011-5220	78653	Debt Claim
J1-CV-20-002874	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305193	1	 Portfolio Recovery Associates LLC vs. Lukea Smith,Brianna Smith	Portfolio Recovery Associates LLC	Smith, Brianna; Smith, Lukea	78653	78653	Debt Claim
J1-CV-20-002875	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305288	1	 United Automobile Insurance Services vs. Vanessa Ann Andrada	United Automobile Insurance Services	Andrada, Vanessa Ann	75228	78745	Small Claims
J1-CV-20-002876	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305290	1	 Lvnv Funding Llc vs. Mark Silva	Lvnv Funding Llc	Silva, Mark	75011-5220	78653	Debt Claim
J1-CV-20-002877	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305291	1	 Portfolio Recovery Associates Llc vs. Alexis Rodlyne	Portfolio Recovery Associates Llc	Rodlyne, Alexis	75011-5220	78653	Debt Claim
J1-CV-20-002878	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305292	1	 Portfolio Recovery Associates Llc vs. Pedro Sustaita	Portfolio Recovery Associates Llc	Sustaita, Pedro	75011-5220	78653	Debt Claim
J1-CV-20-002879	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305293	1	 MIDLAND FUNDING LLC vs. BERNICE HERNANDEZ	MIDLAND FUNDING LLC	HERNANDEZ, BERNICE	77056	78754	Debt Claim
J1-CV-20-002880	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305294	1	 MIDLAND CREDIT MANAGEMENT INC. vs. HUGO A HERNANDEZ	MIDLAND CREDIT MANAGEMENT INC.	HERNANDEZ, HUGO A	77056	78753-6874	Debt Claim
J1-CV-20-002881	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305295	1	 Portfolio Recovery Associates, Llc Assignee Of Synchrony Bank / Synchrony Bank / Lowes vs. Ghazi Althuibi	Portfolio Recovery Associates, Llc Assignee Of Synchrony Bank / Synchrony Bank / Lowes	Althuibi, Ghazi		78724	Debt Claim
J1-CV-20-002882	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305296	1	 Portfolio Recovery Associates, Llc Assignee Of Capital One Bank (usa), N.a. / Capital One Bank (usa), N.a. vs. Joseph H Goodrich	Portfolio Recovery Associates, Llc Assignee Of Capital One Bank (usa), N.a. / Capital One Bank (usa), N.a.	Goodrich, Joseph H		78721	Debt Claim
J1-CV-20-002883	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305297	1	 CITIBANK, N.A. vs. PILNAE E FISHER	CITIBANK, N.A.	FISHER, PILNAE E	79452-3340	78753	Debt Claim
J1-CV-20-002884	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305299	1	 UNIFUND CCR, LLC vs. MICHAEL K SIPES	UNIFUND CCR, LLC	SIPES, MICHAEL K		78752	Debt Claim
J1-CV-20-002885	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305489	1	Kayla M Rogers vs. MARQUES P DEVAUGHN	Rogers, Kayla M	DEVAUGHN, MARQUES P	78753	78728	Small Claims
J1-CV-20-002886	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305491	1	Gail R Whitley vs.  GYRM Industry Automotive	Whitley, Gail R	GYRM Industry Automotive	78653	78665	Small Claims
J1-CV-20-002889	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305498	1	 MIDLAND CREDIT MANAGEMENT INC. vs. JARED W ARNOLD	MIDLAND CREDIT MANAGEMENT INC.	ARNOLD, JARED W	77056	78653-4931	Debt Claim
J1-CV-20-002890	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305499	1	 CITIBANK, N.A. vs. RUBY PIERCE	CITIBANK, N.A.	PIERCE, RUBY	79452-3340	78753-9732	Debt Claim
J1-CV-20-002892	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305501	1	 Altair Tech Ridge vs. Jarvis Caldwell	Altair Tech Ridge	Caldwell, Jarvis	78754	78754	Eviction
J1-CV-20-002887	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305494	1	Marcus Lanier Jackson vs. LaTonya Clark	Jackson, Marcus Lanier	Clark, LaTonya	78621	78660	Small Claims
J1-CV-20-002888	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305495	1	 UNIFUND CCR, LLC vs. MICHCAEL T HARGETT	UNIFUND CCR, LLC	HARGETT, MICHCAEL T		78721	Debt Claim
J1-CV-20-002891	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305500	1	 Portfolio Recovery Associates, LLC vs. Sasha Smith	Portfolio Recovery Associates, LLC	Smith, Sasha		78653	Debt Claim
J1-CV-20-002893	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305582	1	BRYCEANL MITCHELL vs. DINA FEARMYE	MITCHELL, BRYCEANL	FEARMYE, DINA	78753	78753	Writ of Re-Entry
J2-CV-20-003192	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2304833	2	 Portfolio Recovery Associates LLC Assignee Of Synrchony Bank/synchrony Bank/wal-mart vs. Andres Arredondo, JR 	Portfolio Recovery Associates LLC Assignee Of Synrchony Bank/synchrony Bank/wal-mart	Arredondo, Andres, Jr.		78660	Debt Claim
J2-CV-20-003193	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2304835	2	 VELOCITY INVESTMENTS LLC vs. RODERICK D SANFORD	VELOCITY INVESTMENTS LLC	SANFORD, RODERICK D	78230	78727	Debt Claim
J2-CV-20-003194	Pending Answer	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2304839	2	 Lvnv Funding Llc vs. Kimberly Peterson	Lvnv Funding Llc	Peterson, Kimberly	75011	78660	Debt Claim
J2-CV-20-003195	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2304886	2	 CITIBANK, N.A. vs. TONY ZARAGOZA	CITIBANK, N.A.	ZARAGOZA, TONY	79464	78758	Debt Claim
J2-CV-20-003196	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2304910	2	 Conn Appliances Inc. vs. Monica M. White	Conn Appliances Inc.	White, Monica M.	75011	78728	Debt Claim
J2-CV-20-003197	Pending Answer	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2304912	2	Midland Credit Management Inc. vs. Karen Blackwood	Midland Credit Management Inc.	Blackwood, Karen	75011	78660	Debt Claim
J2-CV-20-003198	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2304911	2	 Lvnv Funding Llc vs. Marcia Bullock	Lvnv Funding Llc	Bullock, Marcia	75011	78660	Debt Claim
J2-CV-20-003199	Pending Answer	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2304913	2	Lvnv Funding Llc vs. Laura Smoker	Lvnv Funding Llc	Smoker, Laura	75011	78660	Debt Claim
J2-CV-20-003200	Pending Answer	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2304914	2	Lvnv Funding Llc vs. Jacqueline Camargo	Lvnv Funding Llc	Camargo, Jacqueline	75011	78728	Debt Claim
J2-CV-20-003201	Pending Answer	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2304915	2	 Lvnv Funding Llc vs. Marcella Roark	Lvnv Funding Llc	Roark, Marcella	75011	78750	Debt Claim
J2-CV-20-003202	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2304916	2	 Lvnv Funding Llc vs. Charles Brents	Lvnv Funding Llc	Brents, Charles	75011	78664	Debt Claim
J2-CV-20-003203	Pending Answer	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2304949	2	 Cavalry Spv I, Llc, As Assignee Of Citibank, N.a. vs. Jose Marvinmartinez	Cavalry Spv I, Llc, As Assignee Of Citibank, N.a.	Marvinmartinez, Jose	75080	78753-3027	Debt Claim
J2-CV-20-003204	Hearing Set	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2304952	2	AH4R PROPERTIES, LLC vs. JUDY BROWN,SAMUEL CONTRERAS and/or ALL OTHER OCCUPANTS OF 3409 KISSMAN DRIVE AUSTIN,TX 78728	AH4R PROPERTIES, LLC	BROWN, JUDY; CONTRERAS, SAMUEL		78728	Eviction
J2-CV-20-003205	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2304978	2	 CITIBANK, N.A. vs. THUAN C LUONG	CITIBANK, N.A.	LUONG, THUAN C	79452-3340	78758-4203	Debt Claim
J2-CV-20-003206	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2304979	2	 LVNV FUNDING LLC vs. David Thompson Aka David R Thompson	LVNV FUNDING LLC	Thompson Aka David R Thompson, David	79452-3968	78734-1689	Debt Claim
J2-CV-20-003207	Final Status	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305022	2	ERICA BEAVER vs. PHIL BEAVER,Lynn Beaver	BEAVER, ERICA	Beaver, Lynn; BEAVER, PHIL	78758	78758	Writ of Re-Entry
J2-CV-20-003208	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305032	2	 Absolute Resolutions Investments Llc vs. Gilbert M Herrera	Absolute Resolutions Investments Llc	Herrera, Gilbert M	75011	78645	Debt Claim
J2-CV-20-003209	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305038	2	MICHAEL CHAVEZ vs.  LEVITY ENTERTAINMENT GROUP LLC, LEVITY IRVINE CLUB LLC, LEVITY OF BREA LLC	CHAVEZ, MICHAEL	LEVITY ENTERTAINMENT GROUP LLC; LEVITY IRVINE CLUB LLC; LEVITY OF BREA LLC	78758	78758	Small Claims
J2-CV-20-003210	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305039	2	IVONE PEABODY vs.  OXFORD ENTERPRISES MANAGEMENT	PEABODY, IVONE	OXFORD ENTERPRISES MANAGEMENT	78660	78660	Small Claims
J2-CV-20-003211	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305080	2	 AMERICAN EXPRESS NATIONAL BANK F/K/A AMERICAN EXPRESS CENTURION BANK vs. MICHELLE WEBSTER AKA MICHELLE VESTAL	AMERICAN EXPRESS NATIONAL BANK F/K/A AMERICAN EXPRESS CENTURION BANK	WEBSTER AKA MICHELLE VESTAL, MICHELLE	77057	78660	Debt Claim
J2-CV-20-003212	Pending Answer	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305084	2	Lvnv Funding Llc vs. Ashley Hartdegen	Lvnv Funding Llc	Hartdegen, Ashley	75011	78727	Debt Claim
J2-CV-20-003213	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305085	2	 Lvnv Funding Llc vs. Jerry P Belohlavy	Lvnv Funding Llc	Belohlavy, Jerry P	75011	78641	Debt Claim
J2-CV-20-003214	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305087	2	 Lvnv Funding Llc vs. James Gaytan	Lvnv Funding Llc	Gaytan, James	75011	78660	Debt Claim
J2-CV-20-003215	Pending Answer	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305088	2	Lvnv Funding Llc vs. Delmarco Chambers	Lvnv Funding Llc	Chambers, Delmarco	75011	78728	Debt Claim
J2-CV-20-003216	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305131	2	Arturo Perez-Rodriguez vs. Magali Martinez-Amezquita	Perez-Rodriguez, Arturo	Martinez-Amezquita, Magali		78744	Debt Claim
J2-CV-20-003217	Hearing Set	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305145	2	LESLY NAVA vs.FELIZ APARTMENTS,J AND J TOWING	NAVA, LESLY	FELIZ APARTMENTS; J AND J TOWING	78758	78758	Illegal Tow
J2-CV-20-003218	Final Status	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305194	2	EX PARTE vs. RODOLFO MARROQUIN	\N		\N	\N	Occupational Driver's License
J2-CV-20-003219	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305199	2	 Portfolio Recovery Associates Llc vs. Esther Peralez	Portfolio Recovery Associates Llc	Peralez, Esther	75011	78758	Debt Claim
J2-CV-20-003220	Pending Jury Setting	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305220	2	Lvnv Funding Llc vs. Henry Ortega	Lvnv Funding Llc	Ortega, Henry	75011	78728	Debt Claim
J2-CV-20-003221	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305221	2	Credit Corp Solutions Inc. vs. Javier Lainez AKA JAVIER ANTONIO LAINEZ	Credit Corp Solutions Inc.	Lainez, Javier  Also Known As  LAINEZ, JAVIER ANTONIO	75011	78660	Debt Claim
J2-CV-20-003222	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305222	2	 Credit Corp Solutions Inc. vs. Tsehai Tesema	Credit Corp Solutions Inc.	Tesema, Tsehai	75011	78728	Debt Claim
J2-CV-20-003223	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305242	2	Onemain Financial Group, Llc As Servicer for ("ASF") Wilmington Trust N.A., As Issuer Loan Trustee for Onemain Financial Issuance Trust 2018-1 vs. Linda A Hygh	Onemain Financial Group, Llc As Servicer for ("ASF") Wilmington Trust N.A., As Issuer Loan Trustee for Onemain Financial Issuance Trust 2018-1	Hygh, Linda A		78660	Debt Claim
J2-CV-20-003224	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305243	2	Lvnv Funding Llc vs. BRIAN ALANIZ	Lvnv Funding Llc	ALANIZ, BRIAN		78660-5519	Debt Claim
J2-CV-20-003225	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305257	2	 Lvnv Funding Llc vs. Donald K Scofield	Lvnv Funding Llc	Scofield, Donald K	75080	78645-2102	Debt Claim
J2-CV-20-003226	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305258	2	Velocity Investments, Llc Assignee Of Prosper Funding Llc Assignee Of Webbank vs. Charles Lebus AKA CHARLES L. LEBUS	Velocity Investments, Llc Assignee Of Prosper Funding Llc Assignee Of Webbank	Lebus, Charles  Also Known As  LEBUS, CHARLES L	75080	78759	Debt Claim
J2-CV-20-003227	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305259	2	Velocity Investments, Llc Assignee Of Prosper Funding Llc Assignee Of Webbank vs. Bobbie Mack AKA BOBBIE G. MACK	Velocity Investments, Llc Assignee Of Prosper Funding Llc Assignee Of Webbank	Mack, Bobbie  Also Known As  MACK, BOBBIE G	75080	78660	Debt Claim
J2-CV-20-003228	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305260	2	 Lvnv Funding Llc vs. Starlet Shelton	Lvnv Funding Llc	Shelton, Starlet	75080	78660-7302	Debt Claim
J2-CV-20-003229	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305261	2	 Direct Line Development Inc vs.  Stable Foundations	Direct Line Development Inc	Stable Foundations	78759	78744	Debt Claim
J2-CV-20-003230	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305262	2	 Direct Line Development Inc. vs.  Style by Priscilla	Direct Line Development Inc.	Style by Priscilla	78759	78620	Debt Claim
J2-CV-20-003231	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305266	2	 Velocity Investments, Llc As Assignee Of Avant, Inc. Assignee Of Webbank vs. Angelita Villarreal	Velocity Investments, Llc As Assignee Of Avant, Inc. Assignee Of Webbank	Villarreal, Angelita	75080	78758	Debt Claim
J2-CV-20-003232	Eviction Set	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305277	2	 THE MARQUIS AT LADERA VISTA vs. David Shaw	THE MARQUIS AT LADERA VISTA	Shaw, David		78759	Eviction
J2-CV-20-003233	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305280	2	 U.s.bank National Association Dba As Elan Financial Services vs. Sharon J Holmes	U.s.bank National Association Dba As Elan Financial Services	Holmes, Sharon J	75248	78732	Debt Claim
J2-CV-20-003234	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305281	2	 Portfolio Recovery Associates, Llc Assignee Of Synchrony Bank / Synchrony Bank vs. Travis Gibson	Portfolio Recovery Associates, Llc Assignee Of Synchrony Bank / Synchrony Bank	Gibson, Travis		78758	Debt Claim
J2-CV-20-003240	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305394	2	Gail A Pruett vs. Joanne Sowders	Pruett, Gail A	Sowders, Joanne	78102	78727	Small Claims
J2-CV-20-003235	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305317	2	Mahemooda Incorporated dba Mi Pueblito #3 vs. Valentin Gutierrez Hernandez, Sr.	Mahemooda Incorporated dba Mi Pueblito #3	Hernandez, Sr., Valentin Gutierrez	78759-6111	78753-4229	Small Claims
J2-CV-20-003236	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305320	2	Asiya, Inc. dba Pueblito vs. HDZ Swift Construction LLC	Asiya, Inc. dba Pueblito	HDZ Swift Construction LLC	78759-6111	78753-2239	Small Claims
J2-CV-20-003237	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305333	2	SM Sunrise LLC dba Tienda Mexicana vs. Jose Andres Garza Ledezma	SM Sunrise LLC dba Tienda Mexicana	Garza Ledezma, Jose Andres	78759-6111	78550-5651	Small Claims
J2-CV-20-003238	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305366	2	 Excel Finance vs. Aida Barrera	Excel Finance	Barrera, Aida	78757	78664	Debt Claim
J2-CV-20-003239	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305367	2	Khayam Anjam vs. Lian Wang	Anjam, Khayam	Wang, Lian	78727	78754	Small Claims
J2-CV-20-003241	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305412	2	 Excel Finance vs. Dillia Garcia	Excel Finance	Garcia, Dillia	78757	78757	Debt Claim
J2-CV-20-003242	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305433	2	 Kainaat Inc dba Pueblito Express #3 vs.  Chavira Custom Home Painting LLC	Kainaat Inc dba Pueblito Express #3	Chavira Custom Home Painting LLC	78759-6111	78741-5313	Small Claims
J2-CV-20-003243	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305438	2	Kainaat Inc dba Pueblito Express #3 vs. Fernando Villarreal DBA VILLARREAL COMMERCIAL COATINGS	Kainaat Inc dba Pueblito Express #3	Villarreal, Fernando  Doing Business As  VILLARREAL COMMERICAL COATINGS	78759-6111	78634-5260	Small Claims
J2-CV-20-003244	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305442	2	 Rabbil Inc dba Pueblito Express #9 vs.  Canaan Custom Modern Homes LLC	Rabbil Inc dba Pueblito Express #9	Canaan Custom Modern Homes LLC	78759-6111	78734-6346	Small Claims
J2-CV-20-003245	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305480	2	 Unifund CCR, LLC vs. Timothy D Caballero	Unifund CCR, LLC	Caballero, Timothy D		78759	Debt Claim
J3-EV-20-000405	FED Hearing Set	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305081	3	Jeffrey Armstrong vs. Stephen Sam	Armstrong, Jeffrey	Sam, Stephen	78745	78745	Eviction
J3-EV-20-000406	FED Hearing Set	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305380	3	Lamadrid Apartments LLC vs. BONNIE GOMEZ	Lamadrid Apartments LLC	GOMEZ, BONNIE	78748	78748	Eviction
J4-CV-20-002158	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2304877	4	MIDLAND FUNDING LLC vs. RYAN PINTO	MIDLAND FUNDING LLC	PINTO, RYAN	77056	78744-5015	Debt Claim
J4-CV-20-002159	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2304883	4	CITIBANK, N.A. vs. DAVID THOMAS	CITIBANK, N.A.	THOMAS, DAVID		78617-3299	Debt Claim
J4-CV-20-002160	Trial/Hearing Set	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2304893	4	ARTHUR CUELLAR vs. BRANDON SHONE,JESSICA TENEYUQUE	CUELLAR, ARTHUR	SHONE, BRANDON; TENEYUQUE, JESSICA	78612	78612	Eviction
J4-CV-20-002161	Pending Citation	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2304899	4	REBECCA RAMIREZ vs. VILAS OF CORDOBA	RAMIREZ, REBECCA	VILAS OF CORDOBA	78744	78744	Small Claims
J4-CV-20-002162	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2304945	4	 CONN APPLIANCES, INC. vs. Timothy P. Reed	CONN APPLIANCES, INC.	Reed, Timothy P.	75011	78617	Debt Claim
J4-CV-20-002163	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2304946	4	 LVNV FUNDING, LLC vs. Victor M Najera	LVNV FUNDING, LLC	Najera, Victor M	75011-5220	78617	Debt Claim
J4-CV-20-002164	Trial/Hearing Set	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2304947	4	COOL BREEZE RESIDENTIAL PROPERTIES LLC vs. CHRIS J WAGGNER,MATTHEW OKTABA	COOL BREEZE RESIDENTIAL PROPERTIES LLC	OKTABA, MATTHEW; WAGGNER, CHRIS J		78741	Eviction
J4-CV-20-002165	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305036	4	 CONN APPLIANCES, INC. vs. Isidro Garza	CONN APPLIANCES, INC.	Garza, Isidro	75011	78744	Debt Claim
J4-CV-20-002166	Trial/Hearing Set	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305061	4	Connect The Dots, Inc. vs. MARISSA HUNT-BROOKS,REAGAN SORRELS	Connect The Dots, Inc.	HUNT-BROOKS, MARISSA; SORRELS, REAGAN	78720	78744	Eviction
J4-CV-20-002167	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305064	4	 Cavalry SPV I, LLC, as Assignee of Citibank, N.A. vs. Doreen M Garcia	Cavalry SPV I, LLC, as Assignee of Citibank, N.A.	Garcia, Doreen M	75080	78744-3630	Debt Claim
J4-CV-20-002168	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305086	4	 CONN APPLIANCES, INC. vs. Ann M. Rivera	CONN APPLIANCES, INC.	Rivera, Ann M.	75011	78747	Debt Claim
J4-CV-20-002169	Trial/Hearing Set	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305108	4	WATERS AT BLUFF SPRINGS vs. Heather Rochelle Forrest,Teressa Anne Brown	WATERS AT BLUFF SPRINGS	Brown, Teressa Anne; Forrest, Heather Rochelle	78744	78744	Eviction
J4-CV-20-002170	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305135	4	 LVNV FUNDING, LLC vs. Alberto Almanzo Vital	LVNV FUNDING, LLC	Vital, Alberto Almanzo	75011-5220	78617	Debt Claim
J4-CV-20-002171	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305136	4	 LVNV FUNDING, LLC vs. Brenda Cisneros Cabrieles	LVNV FUNDING, LLC	Cisneros Cabrieles, Brenda	75011-5220	78747	Debt Claim
J4-CV-20-002172	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305140	4	 LVNV FUNDING, LLC vs. Jose Tamez	LVNV FUNDING, LLC	Tamez, Jose	75011-5220	78744	Debt Claim
J4-CV-20-002173	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305143	4	 LVNV FUNDING, LLC vs. Melissa Irving	LVNV FUNDING, LLC	Irving, Melissa	75011-5220	78741	Debt Claim
J4-CV-20-002174	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305147	4	 FUND GRAND HARBOR, LLC vs. Ya-Shi Duhon	FUND GRAND HARBOR, LLC	Duhon, Ya-Shi	77494-0672	78744	Debt Claim
J4-CV-20-002175	Trial/Hearing Set	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305169	4	1911 WILLOW CREEK LLC vs. Cameron Kolbe Steadman	1911 WILLOW CREEK LLC	Steadman, Cameron Kolbe		78741	Eviction
J4-CV-20-002176	Pending Citation	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305247	4	 CAVALRY SPV I, LLC ASSIGNEE OF CITIBANK, N.A. vs. Julie C Spruce	CAVALRY SPV I, LLC ASSIGNEE OF CITIBANK, N.A.	Spruce, Julie C		78704-7072	Debt Claim
J4-CV-20-002177	Pending Citation	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305248	4	 LVNV FUNDING, LLC vs. Heather Strole	LVNV FUNDING, LLC	Strole, Heather	75011-5220	78744-6882	Debt Claim
J4-CV-20-002178	Pending Citation	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305250	4	MIDLAND CREDIT MANAGEMENT, INC. vs. KIERRA WHITE	MIDLAND CREDIT MANAGEMENT, INC.	WHITE, KIERRA	77056	78721-2629	Debt Claim
J4-CV-20-002179	Pending Citation	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305253	4	 Lvnv Funding Llc vs. Richard Guerra	Lvnv Funding Llc	Guerra, Richard		78741-4122	Debt Claim
J4-CV-20-002180	Pending Citation	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305254	4	MIDLAND CREDIT MANAGEMENT, INC. vs. CHERYL CHARLESLEWIS aka CHERYL CHARLES	MIDLAND CREDIT MANAGEMENT, INC.	CHARLESLEWIS, CHERYL  Also Known As  CHARLES, CHERYL	77056	78744-5673	Debt Claim
J4-CV-20-002181	Pending Citation	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305255	4	MIDLAND CREDIT MANAGEMENT, INC. vs. TFFANY E MERCER	MIDLAND CREDIT MANAGEMENT, INC.	MERCER, TFFANY E	77056	78617-3613	Debt Claim
J4-CV-20-002182	Pending Citation	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305276	4	LVNV FUNDING LLC vs. ANNIE MACHADO	LVNV FUNDING LLC	MACHADO, ANNIE	75080	78721-2524	Debt Claim
J4-CV-20-002183	Pending Citation	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305279	4	MIDLAND CREDIT MANAGEMENT, INC. vs. Diane Limon	MIDLAND CREDIT MANAGEMENT, INC.	Limon, Diane	77056	78702-3032	Debt Claim
J4-CV-20-002184	Pending Citation	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305298	4	CITIBANK, N.A. vs. IJOHN MANOR, Jr.	CITIBANK, N.A.	MANOR, IJOHN, Jr.		78660-2564	Debt Claim
J4-CV-20-002185	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305511	4	Heriberto Rivera vs. Frank Franklin	Rivera, Heriberto	Franklin, Frank	78741	78752	Repair and Remedy
J4-CV-20-002186	Pending Citation	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305531	4	MIDLAND CREDIT MANAGEMENT, INC. vs. Heather Strole	MIDLAND CREDIT MANAGEMENT, INC.	Strole, Heather	77056	78744-6882	Debt Claim
J5-CV-20-258279	Final Status	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2304834	5	Aaron Servantez	\N		\N	\N	Occupational Driver's License
J5-CV-20-258280	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2304843	5	 MIDLAND CREDIT MANAGEMENT, INC. vs. Thomas Johnson	MIDLAND CREDIT MANAGEMENT, INC.	Johnson, Thomas	77056	78701	Debt Claim
J5-CV-20-258281	Final Status	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2304852	5	Kevin Lassiter	\N		\N	\N	Occupational Driver's License
J5-CV-20-258282	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2304887	5	CITY OF AUSTIN vs. EZ and Simple, LLC d/b/a Mobile Freedom	CITY OF AUSTIN	EZ and Simple, LLC d/b/a Mobile Freedom	78767-1546	78754	Small Claims
J5-CV-20-258283	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2304888	5	CITY OF AUSTIN vs. CHRISTOPHER CONRAD D/B/A TEXAS NATIONAL OUTFITTERS, LLC A/K/A SOCO TNO AUSTIN, LLC	CITY OF AUSTIN	CHRISTOPHER CONRAD D/B/A TEXAS NATIONAL OUTFITTERS, LLC A/K/A SOCO TNO AUSTIN, LLC	78767-1546	78450	Small Claims
J5-CV-20-258284	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2304926	5	 Lvnv Funding Llc vs. Gretchen Beckert	Lvnv Funding Llc	Beckert, Gretchen	75011	78730	Debt Claim
J5-CV-20-258285	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2304956	5	CLAY WILLIAM CARTER vs. POST SOUTH LAMAR II LLC	CARTER, CLAY WILLIAM	POST SOUTH LAMAR II LLC	78704	78704	Small Claims
J5-CV-20-258286	Final Status	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2304958	5	DANIEL RAGETTE	\N		\N	\N	Occupational Driver's License
J5-CV-20-258287	Final Status	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2304962	5	David Flessner	\N		\N	\N	Occupational Driver's License
J5-CV-20-258288	Final Status	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2304963	5	Anthony Clay O'Dell	\N		\N	\N	Occupational Driver's License
J5-CV-20-258289	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2304968	5	Holden Hopkins vs. 705 Graham LLC	Hopkins, Holden	705 Graham LLC		78705	Small Claims
J5-CV-20-258290	Final Status	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305037	5	Chloe Elyse Beard	\N		\N	\N	Occupational Driver's License
J5-CV-20-258291	Final Status	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305062	5	James Harvey	\N		\N	\N	Occupational Driver's License
J5-CV-20-258292	Final Status	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305063	5	Collin Wang	\N		\N	\N	Occupational Driver's License
J5-CV-20-258293	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305067	5	FAMSA INC vs. RODOLFO BUSTAMANTE	FAMSA INC	BUSTAMANTE, RODOLFO	78238	78644	Debt Claim
J5-CV-20-258294	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305068	5	FAMSA INC vs. ANGELICA HERNANDEZ	FAMSA INC	HERNANDEZ, ANGELICA	78238	78753	Debt Claim
J5-CV-20-258295	Final Status	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305091	5	Ryan Pantaleano	\N		\N	\N	Occupational Driver's License
J5-CV-20-258296	Hearing Set	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305092	5	Kenneth Anderson,Angie Cunningham vs. Thomas Stevenson,Freederanique Cannon	Anderson, Kenneth	Cannon, Freederanique; Stevenson, Thomas	78753	78753	Eviction
J5-CV-20-258297	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305099	5	 LVNV FUNDING, LLC vs. Michael Franks	LVNV FUNDING, LLC	Franks, Michael	75011-5220	78731	Debt Claim
J5-CV-20-258298	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305102	5	 LVNV FUNDING, LLC vs. Raquel N Frankenberg	LVNV FUNDING, LLC	Frankenberg, Raquel N	75011-5220	78730	Debt Claim
J5-CV-20-258299	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305103	5	 LVNV FUNDING, LLC vs. Cory Giles	LVNV FUNDING, LLC	Giles, Cory	75011-5220	78757	Debt Claim
J5-CV-20-258300	Final Status	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305109	5	Eliazia Balli Hollan	\N		\N	\N	Occupational Driver's License
J5-CV-20-258301	Final Status	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305126	5	Lillian Jane Mills	\N		\N	\N	Occupational Driver's License
J5-CV-20-258302	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305155	5	 THE STATE OF TEXAS vs. FELICIA VILLAFANA	THE STATE OF TEXAS	VILLAFANA, FELICIA	78711-2548	78112-4739	Debt Claim
J5-CV-20-258303	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305156	5	 THE STATE OF TEXAS vs. CHRISTA M LOLLIS	THE STATE OF TEXAS	LOLLIS, CHRISTA M	78711-2548	77494	Debt Claim
J5-CV-20-258304	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305159	5	 THE STATE OF TEXAS vs. PATRICK DAUGHERTY	THE STATE OF TEXAS	DAUGHERTY, PATRICK	78711-2548	76017	Debt Claim
J5-CV-20-258305	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305160	5	 THE STATE OF TEXAS vs. MICHELLE NGUYEN	THE STATE OF TEXAS	NGUYEN, MICHELLE	78711-2548	78023	Debt Claim
J5-CV-20-258306	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305161	5	 THE STATE OF TEXAS vs. EMET B HUNTSMAN III	THE STATE OF TEXAS	HUNTSMAN III, EMET B	78711-2548	78133-5295	Debt Claim
J5-CV-20-258307	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305162	5	 THE STATE OF TEXAS vs. CLEO SUE HUNTSMAN	THE STATE OF TEXAS	HUNTSMAN, CLEO SUE	78711-2548	78133-5295	Debt Claim
J5-CV-20-258308	Final Status	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305163	5	Melissa Hislop	\N		\N	\N	Occupational Driver's License
J5-CV-20-258309	Final Status	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305168	5	Federico Ramirez	\N		\N	\N	Occupational Driver's License
J5-CV-20-258310	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305174	5	Kristina Kipling vs. MRS BPO, LLC	Kipling, Kristina	MRS BPO, LLC		75201	Small Claims
J5-CV-20-258311	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305178	5	Craig Bailes,Linda Bailes vs. Jiffy Lube / Team Car Care, LLC	Bailes, Craig	Jiffy Lube / Team Car Care, LLC	78705	75062	Small Claims
J5-CV-20-258312	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305197	5	CHRIS AAKER vs.  REGUS CO-WORKING SPACE	AAKER, CHRIS	REGUS CO-WORKING SPACE	78701	78701	Small Claims
J5-CV-20-258313	Hearing Set	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305213	5	Capital Choice Properties vs. Michael Smith	Capital Choice Properties	Smith, Michael	78736	78757	Eviction
J5-CV-20-258314	Final Status	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305215	5	Teodoro Johnston	\N		\N	\N	Occupational Driver's License
J5-CV-20-258315	Final Status	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305238	5	William McDonald	\N		\N	\N	Occupational Driver's License
J5-CV-20-258316	Final Status	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305246	5	CHRISTOPHER DEVA HUFF	\N		\N	\N	Occupational Driver's License
J5-CV-20-258317	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305249	5	 MIDLAND CREDIT MANAGEMENT INC. vs. JOSHUA E MORALES	MIDLAND CREDIT MANAGEMENT INC.	MORALES, JOSHUA E	77056	78751-1630	Debt Claim
J5-CV-20-258318	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305251	5	MARJANNE ELIZABETH FLAHERTY	\N		\N	\N	Occupational Driver's License
J5-CV-20-258319	Final Status	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305256	5	Leonardo Lopez-Cruz	\N		\N	\N	Occupational Driver's License
J5-CV-20-258320	Final Status	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305282	5	Romeo Gonzalez	\N		\N	\N	Occupational Driver's License
J5-CV-20-258321	Final Status	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305284	5	Patsquinel Besa	\N		\N	\N	Occupational Driver's License
J5-CV-20-258322	Final Status	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305285	5	Frederico Rojo	\N		\N	\N	Occupational Driver's License
J5-CV-20-258323	Final Status	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305287	5	Peter Sauvageau	\N		\N	\N	Occupational Driver's License
J5-CV-20-258324	Final Status	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305385	5	Lindsey Hill	\N		\N	\N	Occupational Driver's License
J5-CV-20-258325	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305389	5	Laura Gorsky,David Giannaula vs. Raji Parameswaran	Giannaula, David	Parameswaran, Raji	78751	78745	Small Claims
J5-CV-20-258326	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305392	5	Rice Capital, LLC Series 21 vs. CRESTWAY DRIVE LAND, LLC, AND ALL OTHER OCCUPANTS	Rice Capital, LLC Series 21	CRESTWAY DRIVE LAND, LLC, AND ALL OTHER OCCUPANTS		78731	Eviction
J5-CV-20-258327	Active	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305404	5	IRIS TEAUNDRA YOUNG	\N		\N	\N	Occupational Driver's License
J5-CV-20-258328	Final Status	https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2305543	5	Melissa Christine Clem	\N		\N	\N	Occupational Driver's License
\.


--
-- Data for Name: disposition; Type: TABLE DATA; Schema: public; Owner: xsqpbwotuzlraq
--

COPY public.disposition (id, case_detail_id, type, date, amount, awarded_to, awarded_against) FROM stdin;
146	J1-CV-20-002835				N/A	N/A
147	J1-CV-20-002844				N/A	N/A
148	J1-CV-20-002845				N/A	N/A
149	J1-CV-20-002846				N/A	N/A
150	J1-CV-20-002847				N/A	N/A
151	J1-CV-20-002848				N/A	N/A
152	J1-CV-20-002849				N/A	N/A
153	J1-CV-20-002850				N/A	N/A
154	J1-CV-20-002851				N/A	N/A
155	J1-CV-20-002852				N/A	N/A
156	J1-CV-20-002853				N/A	N/A
157	J1-CV-20-002854				N/A	N/A
158	J1-CV-20-002855				N/A	N/A
159	J1-CV-20-002856				N/A	N/A
160	J1-CV-20-002857				N/A	N/A
161	J1-CV-20-002858				N/A	N/A
162	J1-CV-20-002859				N/A	N/A
163	J1-CV-20-002860				N/A	N/A
164	J1-CV-20-002861				N/A	N/A
165	J1-CV-20-002863				N/A	N/A
166	J1-CV-20-002864				N/A	N/A
167	J1-CV-20-002865				N/A	N/A
168	J1-CV-20-002866				N/A	N/A
169	J1-CV-20-002867				N/A	N/A
170	J1-CV-20-002862				N/A	N/A
171	J1-CV-20-002868				N/A	N/A
172	J1-CV-20-002869				N/A	N/A
173	J1-CV-20-002870				N/A	N/A
174	J1-CV-20-002871				N/A	N/A
175	J1-CV-20-002872				N/A	N/A
176	J1-CV-20-002873				N/A	N/A
177	J1-CV-20-002874				N/A	N/A
178	J1-CV-20-002875				N/A	N/A
179	J1-CV-20-002876				N/A	N/A
180	J1-CV-20-002877				N/A	N/A
181	J1-CV-20-002878				N/A	N/A
182	J1-CV-20-002879				N/A	N/A
183	J1-CV-20-002880				N/A	N/A
184	J1-CV-20-002881				N/A	N/A
185	J1-CV-20-002882				N/A	N/A
186	J1-CV-20-002883				N/A	N/A
187	J1-CV-20-002884				N/A	N/A
188	J1-CV-20-002885				N/A	N/A
189	J1-CV-20-002886				N/A	N/A
190	J1-CV-20-002889				N/A	N/A
191	J1-CV-20-002890				N/A	N/A
192	J1-CV-20-002892				N/A	N/A
193	J1-CV-20-002887				N/A	N/A
194	J1-CV-20-002888				N/A	N/A
195	J1-CV-20-002891				N/A	N/A
196	J1-CV-20-002893				N/A	N/A
197	J2-CV-20-003192				N/A	N/A
198	J2-CV-20-003193				N/A	N/A
199	J2-CV-20-003194				N/A	N/A
200	J2-CV-20-003195				N/A	N/A
201	J2-CV-20-003196				N/A	N/A
202	J2-CV-20-003197				N/A	N/A
203	J2-CV-20-003198				N/A	N/A
204	J2-CV-20-003199				N/A	N/A
205	J2-CV-20-003200				N/A	N/A
206	J2-CV-20-003201				N/A	N/A
207	J2-CV-20-003202				N/A	N/A
208	J2-CV-20-003203				N/A	N/A
209	J2-CV-20-003204				N/A	N/A
210	J2-CV-20-003205				N/A	N/A
211	J2-CV-20-003206				N/A	N/A
212	J2-CV-20-003207				N/A	N/A
213	J2-CV-20-003208				N/A	N/A
214	J2-CV-20-003209				N/A	N/A
215	J2-CV-20-003210				N/A	N/A
216	J2-CV-20-003211				N/A	N/A
217	J2-CV-20-003212				N/A	N/A
218	J2-CV-20-003213				N/A	N/A
219	J2-CV-20-003214				N/A	N/A
220	J2-CV-20-003215				N/A	N/A
221	J2-CV-20-003216				N/A	N/A
222	J2-CV-20-003217				N/A	N/A
223	J2-CV-20-003218				N/A	N/A
224	J2-CV-20-003219				N/A	N/A
225	J2-CV-20-003220				N/A	N/A
226	J2-CV-20-003221				N/A	N/A
227	J2-CV-20-003222				N/A	N/A
228	J2-CV-20-003223				N/A	N/A
229	J2-CV-20-003224				N/A	N/A
230	J2-CV-20-003225				N/A	N/A
231	J2-CV-20-003226				N/A	N/A
232	J2-CV-20-003227				N/A	N/A
233	J2-CV-20-003228				N/A	N/A
234	J2-CV-20-003229				N/A	N/A
235	J2-CV-20-003230				N/A	N/A
236	J2-CV-20-003231				N/A	N/A
237	J2-CV-20-003232				N/A	N/A
238	J2-CV-20-003233				N/A	N/A
239	J2-CV-20-003234				N/A	N/A
240	J2-CV-20-003240				N/A	N/A
241	J2-CV-20-003235				N/A	N/A
242	J2-CV-20-003236				N/A	N/A
243	J2-CV-20-003237				N/A	N/A
244	J2-CV-20-003238				N/A	N/A
245	J2-CV-20-003239				N/A	N/A
246	J2-CV-20-003241				N/A	N/A
247	J2-CV-20-003242				N/A	N/A
248	J2-CV-20-003243				N/A	N/A
249	J2-CV-20-003244				N/A	N/A
250	J2-CV-20-003245				N/A	N/A
251	J3-EV-20-000405				N/A	N/A
252	J3-EV-20-000406				N/A	N/A
253	J4-CV-20-002158				N/A	N/A
254	J4-CV-20-002159				N/A	N/A
255	J4-CV-20-002160				N/A	N/A
256	J4-CV-20-002161				N/A	N/A
257	J4-CV-20-002162				N/A	N/A
258	J4-CV-20-002163				N/A	N/A
259	J4-CV-20-002164				N/A	N/A
260	J4-CV-20-002165				N/A	N/A
261	J4-CV-20-002166				N/A	N/A
262	J4-CV-20-002167				N/A	N/A
263	J4-CV-20-002168				N/A	N/A
264	J4-CV-20-002169				N/A	N/A
265	J4-CV-20-002170				N/A	N/A
266	J4-CV-20-002171				N/A	N/A
267	J4-CV-20-002172				N/A	N/A
268	J4-CV-20-002173				N/A	N/A
269	J4-CV-20-002174				N/A	N/A
270	J4-CV-20-002175				N/A	N/A
271	J4-CV-20-002176				N/A	N/A
272	J4-CV-20-002177				N/A	N/A
273	J4-CV-20-002178				N/A	N/A
274	J4-CV-20-002179				N/A	N/A
275	J4-CV-20-002180				N/A	N/A
276	J4-CV-20-002181				N/A	N/A
277	J4-CV-20-002182				N/A	N/A
278	J4-CV-20-002183				N/A	N/A
279	J4-CV-20-002184				N/A	N/A
280	J4-CV-20-002185				N/A	N/A
281	J4-CV-20-002186				N/A	N/A
282	J5-CV-20-258279				N/A	N/A
283	J5-CV-20-258280				N/A	N/A
284	J5-CV-20-258281				N/A	N/A
285	J5-CV-20-258282				N/A	N/A
286	J5-CV-20-258283				N/A	N/A
287	J5-CV-20-258284				N/A	N/A
288	J5-CV-20-258285				N/A	N/A
289	J5-CV-20-258286				N/A	N/A
290	J5-CV-20-258287				N/A	N/A
291	J5-CV-20-258288				N/A	N/A
292	J5-CV-20-258289				N/A	N/A
293	J5-CV-20-258290				N/A	N/A
294	J5-CV-20-258291				N/A	N/A
295	J5-CV-20-258292				N/A	N/A
296	J5-CV-20-258293				N/A	N/A
297	J5-CV-20-258294				N/A	N/A
298	J5-CV-20-258295				N/A	N/A
299	J5-CV-20-258296				N/A	N/A
300	J5-CV-20-258297				N/A	N/A
301	J5-CV-20-258298				N/A	N/A
302	J5-CV-20-258299				N/A	N/A
303	J5-CV-20-258300				N/A	N/A
304	J5-CV-20-258301				N/A	N/A
305	J5-CV-20-258302				N/A	N/A
306	J5-CV-20-258303				N/A	N/A
307	J5-CV-20-258304				N/A	N/A
308	J5-CV-20-258305				N/A	N/A
309	J5-CV-20-258306				N/A	N/A
310	J5-CV-20-258307				N/A	N/A
311	J5-CV-20-258308				N/A	N/A
312	J5-CV-20-258309				N/A	N/A
313	J5-CV-20-258310				N/A	N/A
314	J5-CV-20-258311				N/A	N/A
315	J5-CV-20-258312				N/A	N/A
316	J5-CV-20-258313				N/A	N/A
317	J5-CV-20-258314				N/A	N/A
318	J5-CV-20-258315				N/A	N/A
319	J5-CV-20-258316				N/A	N/A
320	J5-CV-20-258317				N/A	N/A
321	J5-CV-20-258318				N/A	N/A
322	J5-CV-20-258319				N/A	N/A
323	J5-CV-20-258320				N/A	N/A
324	J5-CV-20-258321				N/A	N/A
325	J5-CV-20-258322				N/A	N/A
326	J5-CV-20-258323				N/A	N/A
327	J5-CV-20-258324				N/A	N/A
328	J5-CV-20-258325				N/A	N/A
329	J5-CV-20-258326				N/A	N/A
330	J5-CV-20-258327				N/A	N/A
331	J5-CV-20-258328				N/A	N/A
\.


--
-- Data for Name: event; Type: TABLE DATA; Schema: public; Owner: xsqpbwotuzlraq
--

COPY public.event (id, case_detail_id, event_number, date, "time", officer, result, type) FROM stdin;
69	J2-CV-20-003204	0	11/17/2020	10:20 AM	Slagle, Randall	false	HR
70	J2-CV-20-003207	0	11/05/2020	2:30 PM	Slagle, Randall	false	HR
71	J2-CV-20-003217	0	11/17/2020	3:00 PM	Slagle, Randall	false	HR
72	J3-EV-20-000405	0	11/19/2020	2:00 PM	Holmes, Sylvia	false	HR
73	J3-EV-20-000406	0	11/19/2020	2:00 PM	Holmes, Sylvia	false	HR
74	J4-CV-20-002160	0	11/16/2020	9:00 AM	Gonzalez, Raul Arturo	false	HR
75	J4-CV-20-002164	0	11/16/2020	9:00 AM	Gonzalez, Raul Arturo	false	HR
76	J4-CV-20-002166	0	11/16/2020	9:00 AM	Gonzalez, Raul Arturo	false	HR
77	J4-CV-20-002169	0	11/20/2020	9:00 AM	Gonzalez, Raul Arturo	false	HR
78	J4-CV-20-002175	0	11/20/2020	9:00 AM	Gonzalez, Raul Arturo	false	HR
79	J5-CV-20-258296	0	11/19/2020	9:30 AM	Chu, Nicholas	false	HR
80	J5-CV-20-258313	0	11/19/2020	9:30 AM	Chu, Nicholas	false	HR
\.


--
-- Data for Name: setting; Type: TABLE DATA; Schema: public; Owner: xsqpbwotuzlraq
--

COPY public.setting (id, case_number, case_link, setting_type, setting_style, judicial_officer, setting_date, setting_time, hearing_type) FROM stdin;
\.


--
-- Name: disposition_id_seq; Type: SEQUENCE SET; Schema: public; Owner: xsqpbwotuzlraq
--

SELECT pg_catalog.setval('public.disposition_id_seq', 331, true);


--
-- Name: event_id_seq; Type: SEQUENCE SET; Schema: public; Owner: xsqpbwotuzlraq
--

SELECT pg_catalog.setval('public.event_id_seq', 80, true);


--
-- Name: setting_id_seq; Type: SEQUENCE SET; Schema: public; Owner: xsqpbwotuzlraq
--

SELECT pg_catalog.setval('public.setting_id_seq', 508, true);


--
-- Name: case_detail case_detail_pkey; Type: CONSTRAINT; Schema: public; Owner: xsqpbwotuzlraq
--

ALTER TABLE ONLY public.case_detail
    ADD CONSTRAINT case_detail_pkey PRIMARY KEY (id);


--
-- Name: disposition disposition_case_detail_id_key; Type: CONSTRAINT; Schema: public; Owner: xsqpbwotuzlraq
--

ALTER TABLE ONLY public.disposition
    ADD CONSTRAINT disposition_case_detail_id_key UNIQUE (case_detail_id);


--
-- Name: disposition disposition_pkey; Type: CONSTRAINT; Schema: public; Owner: xsqpbwotuzlraq
--

ALTER TABLE ONLY public.disposition
    ADD CONSTRAINT disposition_pkey PRIMARY KEY (id);


--
-- Name: event event_case_detail_id_event_number_key; Type: CONSTRAINT; Schema: public; Owner: xsqpbwotuzlraq
--

ALTER TABLE ONLY public.event
    ADD CONSTRAINT event_case_detail_id_event_number_key UNIQUE (case_detail_id, event_number);


--
-- Name: event event_pkey; Type: CONSTRAINT; Schema: public; Owner: xsqpbwotuzlraq
--

ALTER TABLE ONLY public.event
    ADD CONSTRAINT event_pkey PRIMARY KEY (id);


--
-- Name: setting setting_pkey; Type: CONSTRAINT; Schema: public; Owner: xsqpbwotuzlraq
--

ALTER TABLE ONLY public.setting
    ADD CONSTRAINT setting_pkey PRIMARY KEY (id);


--
-- Name: idx_setting_case_setting_hearing_type; Type: INDEX; Schema: public; Owner: xsqpbwotuzlraq
--

CREATE UNIQUE INDEX idx_setting_case_setting_hearing_type ON public.setting USING btree (case_number, setting_type, hearing_type);


--
-- Name: disposition disposition_case_detail_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: xsqpbwotuzlraq
--

ALTER TABLE ONLY public.disposition
    ADD CONSTRAINT disposition_case_detail_id_fkey FOREIGN KEY (case_detail_id) REFERENCES public.case_detail(id);


--
-- Name: event event_case_detail_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: xsqpbwotuzlraq
--

ALTER TABLE ONLY public.event
    ADD CONSTRAINT event_case_detail_id_fkey FOREIGN KEY (case_detail_id) REFERENCES public.case_detail(id);


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: xsqpbwotuzlraq
--

REVOKE ALL ON SCHEMA public FROM postgres;
REVOKE ALL ON SCHEMA public FROM PUBLIC;
GRANT ALL ON SCHEMA public TO xsqpbwotuzlraq;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- Name: LANGUAGE plpgsql; Type: ACL; Schema: -; Owner: postgres
--

GRANT ALL ON LANGUAGE plpgsql TO xsqpbwotuzlraq;


--
-- PostgreSQL database dump complete
--

