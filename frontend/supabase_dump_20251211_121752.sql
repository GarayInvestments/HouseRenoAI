--
-- PostgreSQL database dump
--

-- Dumped from database version 17.6
-- Dumped by pg_dump version 17.2

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: public; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA public;


--
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON SCHEMA public IS 'standard public schema';


--
-- Name: generate_client_business_id(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.generate_client_business_id() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
        BEGIN
            IF NEW.business_id IS NULL THEN
                NEW.business_id := 'CL-' || LPAD(nextval('client_business_id_seq')::TEXT, 5, '0');
            END IF;
            RETURN NEW;
        END;
        $$;


--
-- Name: generate_inspection_business_id(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.generate_inspection_business_id() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
        BEGIN
            IF NEW.business_id IS NULL THEN
                NEW.business_id := 'INS-' || LPAD(nextval('inspection_business_id_seq')::TEXT, 5, '0');
            END IF;
            RETURN NEW;
        END;
        $$;


--
-- Name: generate_invoice_business_id(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.generate_invoice_business_id() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
        BEGIN
            IF NEW.business_id IS NULL THEN
                NEW.business_id := 'INV-' || LPAD(nextval('invoice_business_id_seq')::TEXT, 5, '0');
            END IF;
            RETURN NEW;
        END;
        $$;


--
-- Name: generate_payment_business_id(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.generate_payment_business_id() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
        BEGIN
            IF NEW.business_id IS NULL THEN
                NEW.business_id := 'PAY-' || LPAD(nextval('payment_business_id_seq')::TEXT, 5, '0');
            END IF;
            RETURN NEW;
        END;
        $$;


--
-- Name: generate_permit_business_id(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.generate_permit_business_id() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
        BEGIN
            IF NEW.business_id IS NULL THEN
                NEW.business_id := 'PER-' || LPAD(nextval('permit_business_id_seq')::TEXT, 5, '0');
            END IF;
            RETURN NEW;
        END;
        $$;


--
-- Name: generate_project_business_id(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.generate_project_business_id() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
        BEGIN
            IF NEW.business_id IS NULL THEN
                NEW.business_id := 'PRJ-' || LPAD(nextval('project_business_id_seq')::TEXT, 5, '0');
            END IF;
            RETURN NEW;
        END;
        $$;


--
-- Name: generate_site_visit_business_id(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.generate_site_visit_business_id() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
        BEGIN
            IF NEW.business_id IS NULL THEN
                NEW.business_id := 'SV-' || LPAD(nextval('site_visit_business_id_seq')::TEXT, 5, '0');
            END IF;
            RETURN NEW;
        END;
        $$;


--
-- Name: set_client_business_id(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.set_client_business_id() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
        BEGIN
          IF NEW.business_id IS NULL THEN
            NEW.business_id := generate_client_business_id();
          END IF;
          RETURN NEW;
        END;
        $$;


--
-- Name: set_payment_business_id(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.set_payment_business_id() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
        BEGIN
          IF NEW.business_id IS NULL THEN
            NEW.business_id := generate_payment_business_id();
          END IF;
          RETURN NEW;
        END;
        $$;


--
-- Name: set_permit_business_id(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.set_permit_business_id() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
        BEGIN
          IF NEW.business_id IS NULL THEN
            NEW.business_id := generate_permit_business_id();
          END IF;
          RETURN NEW;
        END;
        $$;


--
-- Name: set_project_business_id(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.set_project_business_id() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
        BEGIN
          IF NEW.business_id IS NULL THEN
            NEW.business_id := generate_project_business_id();
          END IF;
          RETURN NEW;
        END;
        $$;


--
-- Name: sync_user_from_auth(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.sync_user_from_auth() RETURNS trigger
    LANGUAGE plpgsql SECURITY DEFINER
    AS $$
BEGIN
    -- When a user is created in auth.users, create corresponding app user
    INSERT INTO public.users (supabase_user_id, email, full_name, is_email_verified)
    VALUES (
        NEW.id,
        NEW.email,
        COALESCE(NEW.raw_user_meta_data->>'full_name', NEW.raw_user_meta_data->>'name'),
        NEW.email_confirmed_at IS NOT NULL
    )
    ON CONFLICT (supabase_user_id) DO UPDATE
    SET 
        email = EXCLUDED.email,
        full_name = EXCLUDED.full_name,
        is_email_verified = EXCLUDED.is_email_verified,
        updated_at = CURRENT_TIMESTAMP;
    
    RETURN NEW;
END;
$$;


--
-- Name: update_users_updated_at(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.update_users_updated_at() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


--
-- Name: client_business_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.client_business_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: clients; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.clients (
    client_id uuid DEFAULT gen_random_uuid() NOT NULL,
    full_name character varying(255),
    email character varying(255),
    phone character varying(50),
    address text,
    city character varying(100),
    state character varying(50),
    zip_code character varying(20),
    status character varying(50),
    client_type character varying(50),
    qb_customer_id character varying(50),
    qb_display_name character varying(255),
    qb_sync_status character varying(50),
    qb_last_sync timestamp with time zone,
    extra jsonb,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    business_id character varying(20)
);


--
-- Name: inspection_business_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.inspection_business_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: inspections; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.inspections (
    inspection_id uuid DEFAULT gen_random_uuid() NOT NULL,
    business_id character varying(20),
    permit_id uuid NOT NULL,
    project_id uuid NOT NULL,
    inspection_type character varying(100),
    status character varying(50),
    scheduled_date timestamp with time zone,
    completed_date timestamp with time zone,
    inspector character varying(255),
    assigned_to uuid,
    result character varying(50),
    notes text,
    photos jsonb,
    deficiencies jsonb,
    extra jsonb,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


--
-- Name: invoice_business_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.invoice_business_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: invoices; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.invoices (
    invoice_id uuid DEFAULT gen_random_uuid() NOT NULL,
    business_id character varying(20),
    project_id uuid NOT NULL,
    client_id uuid,
    qb_invoice_id character varying(50),
    invoice_number character varying(50),
    invoice_date timestamp with time zone,
    due_date timestamp with time zone,
    subtotal numeric(12,2),
    tax_amount numeric(12,2),
    total_amount numeric(12,2),
    balance numeric(12,2),
    status character varying(50),
    line_items jsonb,
    sync_status character varying(50),
    sync_error text,
    last_sync_attempt timestamp with time zone,
    notes text,
    extra jsonb,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    amount_paid numeric(12,2) DEFAULT '0'::numeric,
    balance_due numeric(12,2)
);


--
-- Name: jurisdictions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.jurisdictions (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    name character varying(255) NOT NULL,
    state character varying(2) NOT NULL,
    requirements jsonb DEFAULT '{}'::jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


--
-- Name: payment_business_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.payment_business_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: payments; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.payments (
    payment_id uuid DEFAULT gen_random_uuid() NOT NULL,
    client_id uuid,
    project_id uuid,
    amount numeric(12,2),
    payment_date timestamp with time zone,
    payment_method character varying(50),
    status character varying(50),
    check_number character varying(50),
    transaction_id character varying(100),
    qb_payment_id character varying(50),
    notes text,
    extra jsonb,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    business_id character varying(20),
    invoice_id uuid,
    reference_number character varying(50),
    sync_status character varying(50),
    sync_error text,
    last_sync_attempt timestamp with time zone
);


--
-- Name: permit_business_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.permit_business_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: permits; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.permits (
    permit_id uuid DEFAULT gen_random_uuid() NOT NULL,
    project_id uuid,
    client_id uuid,
    permit_number character varying(100),
    permit_type character varying(100),
    status character varying(50),
    application_date timestamp with time zone,
    approval_date timestamp with time zone,
    expiration_date timestamp with time zone,
    issuing_authority character varying(255),
    inspector_name character varying(255),
    notes text,
    extra jsonb,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    business_id character varying(20),
    status_history jsonb,
    approved_by character varying(255),
    approved_at timestamp with time zone
);


--
-- Name: project_business_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.project_business_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: projects; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.projects (
    project_id uuid DEFAULT gen_random_uuid() NOT NULL,
    client_id uuid,
    project_name character varying(255),
    project_address text,
    project_type character varying(100),
    status character varying(50),
    budget numeric(12,2),
    actual_cost numeric(12,2),
    start_date timestamp with time zone,
    end_date timestamp with time zone,
    completion_date timestamp with time zone,
    description text,
    notes text,
    qb_estimate_id character varying(50),
    qb_invoice_id character varying(50),
    extra jsonb,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    business_id character varying(20)
);


--
-- Name: quickbooks_customers_cache; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.quickbooks_customers_cache (
    qb_customer_id character varying(50) NOT NULL,
    display_name character varying(255),
    company_name character varying(255),
    given_name character varying(255),
    family_name character varying(255),
    email character varying(255),
    phone character varying(50),
    qb_data jsonb,
    cached_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


--
-- Name: quickbooks_invoices_cache; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.quickbooks_invoices_cache (
    qb_invoice_id character varying NOT NULL,
    customer_id character varying(50),
    doc_number character varying(50),
    total_amount numeric(12,2),
    balance numeric(12,2),
    due_date timestamp with time zone,
    qb_data jsonb,
    cached_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


--
-- Name: quickbooks_tokens; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.quickbooks_tokens (
    id integer NOT NULL,
    realm_id character varying(50) NOT NULL,
    access_token text NOT NULL,
    refresh_token text NOT NULL,
    access_token_expires_at timestamp with time zone NOT NULL,
    refresh_token_expires_at timestamp with time zone NOT NULL,
    environment character varying(20) NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


--
-- Name: quickbooks_tokens_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.quickbooks_tokens_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: quickbooks_tokens_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.quickbooks_tokens_id_seq OWNED BY public.quickbooks_tokens.id;


--
-- Name: site_visit_business_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.site_visit_business_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: site_visits; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.site_visits (
    visit_id uuid DEFAULT gen_random_uuid() NOT NULL,
    business_id character varying(20),
    project_id uuid NOT NULL,
    client_id uuid,
    visit_type character varying(100),
    status character varying(50),
    scheduled_date timestamp with time zone,
    start_time timestamp with time zone,
    end_time timestamp with time zone,
    attendees jsonb,
    gps_location character varying(100),
    photos jsonb,
    notes text,
    weather character varying(100),
    deficiencies jsonb,
    follow_up_actions jsonb,
    created_by uuid,
    assigned_to uuid,
    extra jsonb,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


--
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    supabase_user_id uuid NOT NULL,
    email character varying(255) NOT NULL,
    full_name character varying(255),
    phone character varying(50),
    role character varying(50) DEFAULT 'client'::character varying NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    is_email_verified boolean DEFAULT false NOT NULL,
    last_login_at timestamp with time zone,
    last_activity_at timestamp with time zone,
    app_metadata jsonb,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT check_valid_role CHECK (((role)::text = ANY ((ARRAY['admin'::character varying, 'pm'::character varying, 'inspector'::character varying, 'client'::character varying, 'finance'::character varying])::text[])))
);


--
-- Name: quickbooks_tokens id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.quickbooks_tokens ALTER COLUMN id SET DEFAULT nextval('public.quickbooks_tokens_id_seq'::regclass);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.alembic_version (version_num) FROM stdin;
1fd9ea7652d5
recreate_users_supabase
\.


--
-- Data for Name: clients; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.clients (client_id, full_name, email, phone, address, city, state, zip_code, status, client_type, qb_customer_id, qb_display_name, qb_sync_status, qb_last_sync, extra, created_at, updated_at, business_id) FROM stdin;
9f9990c1-e217-4dd4-a68b-f983a726113c	Gustavo Roldan	groldan1@yahoo.com	3059844577	13595 SW 134th Ave 201, Miami, FL 33186, USA	\N	\N	\N	5. Active	\N	\N	\N	\N	\N	{"Role": "Owner", "Company Name": "Allazo Holdings LLC", "QBO Client ID": "161"}	2025-12-10 21:05:03.051408+00	2025-12-11 03:30:52.939951+00	CL-00001
c38f08e7-ad9e-407f-a9c9-76a1f95272fa	Howard Nordin	dialaglass@hotmail.com	631-433-6322	16 Harbor Ridge Dr, Centerport, NY 11721, USA	\N	\N	\N	5. Active	\N	\N	\N	\N	\N	{"Role": "Owner", "Company Name": "Dial A Glass", "QBO Client ID": "162"}	2025-12-10 21:05:04.175595+00	2025-12-11 03:30:52.939955+00	CL-00002
493f8b53-ab37-4943-a18a-a68f36cc30a3	Ajay Nair	ajay@2statescarolinas.com	7047064549	7156 Weddington Rd, Concord, NC 28027, USA	\N	\N	\N	5. Active	\N	\N	\N	\N	\N	{"Role": "Owner", "Company Name": "2States Carolinas LLC", "QBO Client ID": "164"}	2025-12-10 21:05:04.676955+00	2025-12-11 03:30:52.939957+00	CL-00003
a9f0df2a-0f80-4030-94eb-e9097ad6f7b4	Javier Martinez	tgbuilding6@gmail.com	828-721-0611		\N	\N	\N	5. Active	\N	\N	\N	\N	\N	{"Role": "Project Manager", "Company Name": "TG Building & Remodeling LLC", "QBO Client ID": "174"}	2025-12-10 21:05:03.68972+00	2025-12-11 03:30:52.939958+00	CL-00004
85d7bfd9-79a5-4fdd-84c7-2811ebe0d569	Steve Jones	propweb247@gmail.com	9802020972		\N	\N	\N	3. Intake Completed	\N	\N	\N	\N	\N	{"Role": "Owner", "QBO Client ID": "165"}	2025-12-10 21:05:05.163367+00	2025-12-11 03:30:52.939959+00	CL-00005
a8ded034-bc67-459c-8617-78ae762776b7	Production Test Client	prodtest@example.com	555-9999	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-10 19:26:49.217243+00	2025-12-11 03:30:52.93996+00	CL-00006
5b58597d-c1ab-4aee-8272-ebdc85316461	Marta Alder	marta@roccacapitalservices.com	704-564-9741		\N	\N	\N	4. GCPC Completed	\N	\N	\N	\N	\N	{"Role": "Owner", "Company Name": "Rocca Capital Investment, LLC", "QBO Client ID": "167"}	2025-12-10 21:05:05.658977+00	2025-12-11 03:30:52.939961+00	CL-00007
569b9f27-def3-4881-aa2e-2e646823a9ff	Brandon Davis	info@premierroofingfl.com	9048004799	671 W US Hwy 19 E, Burnsville, NC 28714, USA	\N	\N	\N	3. Intake Completed	\N	\N	\N	\N	\N	{"Role": "Project Manager", "Notes": "Company link: https://app.companycam.com/galleries/LEim4B9q.", "Company Name": "Premier Roofing", "QBO Client ID": "169"}	2025-12-10 21:05:06.147192+00	2025-12-11 03:30:52.939962+00	CL-00008
\.


--
-- Data for Name: inspections; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.inspections (inspection_id, business_id, permit_id, project_id, inspection_type, status, scheduled_date, completed_date, inspector, assigned_to, result, notes, photos, deficiencies, extra, created_at, updated_at) FROM stdin;
e56c9e08-cf57-4c19-a864-5b7150b32130	INS-00009	5927a0f2-b9d9-49e4-98d7-215a3de06e91	d3e0676c-ea61-4a89-90f2-ddfac4578068	Framing	Completed	2025-12-18 13:15:36.193234+00	\N	\N	\N	Passed	All items checked	[{"url": "https://example.com/photo1.jpg", "caption": "Test photo 1", "timestamp": "2025-12-11T13:15:36.943394+00:00"}, {"url": "https://example.com/photo2.jpg", "caption": "Test photo 2", "timestamp": "2025-12-11T13:15:36.943404+00:00"}]	[]	{}	2025-12-11 13:15:36.463079+00	2025-12-11 13:15:37.433905+00
\.


--
-- Data for Name: invoices; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.invoices (invoice_id, business_id, project_id, client_id, qb_invoice_id, invoice_number, invoice_date, due_date, subtotal, tax_amount, total_amount, balance, status, line_items, sync_status, sync_error, last_sync_attempt, notes, extra, created_at, updated_at, amount_paid, balance_due) FROM stdin;
57b4f6b3-ce93-45ad-879f-c9d34d6e8c84	INV-00007	d3e0676c-ea61-4a89-90f2-ddfac4578068	9f9990c1-e217-4dd4-a68b-f983a726113c	\N	TEST-INV-001	\N	\N	\N	\N	5000.00	\N	Partially Paid	[{"rate": 100, "quantity": 40, "description": "Labor"}, {"rate": 1000, "quantity": 1, "description": "Materials"}]	pending	\N	\N	\N	{}	2025-12-11 13:15:38.28744+00	2025-12-11 13:15:39.183956+00	2000.00	3000.00
\.


--
-- Data for Name: jurisdictions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.jurisdictions (id, name, state, requirements, created_at, updated_at) FROM stdin;
824e5c0c-43d9-4231-9dce-12e3053efdbf	City of Burnsville	MN	{"fees": {"commercial_inspection_base": 75.0, "residential_inspection_base": 50.0, "commercial_building_permit_base": 300.0, "residential_building_permit_base": 150.0}, "contact": {"email": "permits@burnsvillemn.gov", "phone": "952-895-4400", "address": "100 Civic Center Pkwy, Burnsville, MN 55337"}, "required_documents": {"Final": ["certificate_of_occupancy_application"], "Framing": ["structural_plans"], "Rough Electrical": ["electrical_plans"]}, "inspection_sequence": {"Final": ["Insulation"], "Footing": [], "Framing": ["Foundation"], "Foundation": ["Footing"], "Insulation": ["Rough Plumbing", "Rough Electrical", "Rough Mechanical"], "Rough Plumbing": ["Framing"], "Rough Electrical": ["Framing"], "Rough Mechanical": ["Framing"]}, "permit_validity_months": 6}	2025-12-11 13:20:22.350829+00	2025-12-11 13:20:22.350834+00
63c7dd4a-3cba-454f-9077-e514dd7c3c21	City of Minneapolis	MN	{"fees": {"commercial_inspection_base": 100.0, "residential_inspection_base": 60.0, "commercial_building_permit_base": 400.0, "residential_building_permit_base": 200.0}, "contact": {"email": "inspections@minneapolismn.gov", "phone": "612-673-3000", "address": "250 S 4th St, Minneapolis, MN 55415"}, "required_documents": {"Final": ["as_built_plans"], "Framing": ["structural_plans", "energy_calcs"]}, "inspection_sequence": {"Final": ["Insulation"], "Footing": [], "Framing": ["Foundation"], "Rough-In": ["Framing"], "Foundation": ["Footing"], "Insulation": ["Rough-In"]}, "permit_validity_months": 12}	2025-12-11 13:20:22.519398+00	2025-12-11 13:20:22.519402+00
c7503e0e-bb47-4e2f-85b9-e7213eb89af8	City of St. Paul	MN	{"fees": {"commercial_inspection_base": 90.0, "residential_inspection_base": 55.0, "commercial_building_permit_base": 350.0, "residential_building_permit_base": 175.0}, "contact": {"email": "dsi@ci.stpaul.mn.us", "phone": "651-266-8989", "address": "375 Jackson St, Suite 220, St. Paul, MN 55101"}, "required_documents": {"Final": ["truth_in_housing_evaluation"], "Framing": ["structural_plans", "energy_calcs"], "Rough Electrical": ["electrical_plans"]}, "inspection_sequence": {"Final": ["Insulation"], "Footing": [], "Framing": ["Foundation"], "Foundation": ["Footing"], "Insulation": ["Rough Plumbing", "Rough Electrical", "Rough Mechanical"], "Rough Plumbing": ["Framing"], "Rough Electrical": ["Framing"], "Rough Mechanical": ["Framing"]}, "permit_validity_months": 12}	2025-12-11 13:20:22.602135+00	2025-12-11 13:20:22.602138+00
55f8cb5a-5261-4b78-bfa4-5b38a287d1c6	City of Bloomington	MN	{"fees": {"commercial_inspection_base": 80.0, "residential_inspection_base": 50.0, "commercial_building_permit_base": 320.0, "residential_building_permit_base": 160.0}, "contact": {"email": "inspections@bloomingtonmn.gov", "phone": "952-563-8920", "address": "1800 W Old Shakopee Rd, Bloomington, MN 55431"}, "required_documents": {"Framing": ["structural_plans"]}, "inspection_sequence": {"Final": ["Rough-In"], "Footing": [], "Framing": ["Foundation"], "Rough-In": ["Framing"], "Foundation": ["Footing"]}, "permit_validity_months": 6}	2025-12-11 13:20:22.682148+00	2025-12-11 13:20:22.682151+00
79fab2e2-941a-41e9-a43b-1a13e3abf2c8	City of Edina	MN	{"fees": {"commercial_inspection_base": 95.0, "residential_inspection_base": 60.0, "commercial_building_permit_base": 360.0, "residential_building_permit_base": 180.0}, "contact": {"email": "permits@edinamn.gov", "phone": "952-927-8861", "address": "4801 W 50th St, Edina, MN 55424"}, "required_documents": {"Final": ["as_built_plans"], "Framing": ["structural_plans", "truss_plans"]}, "inspection_sequence": {"Final": ["Insulation"], "Footing": [], "Framing": ["Foundation"], "Foundation": ["Footing"], "Insulation": ["Rough Plumbing", "Rough Electrical"], "Rough Plumbing": ["Framing"], "Rough Electrical": ["Framing"]}, "permit_validity_months": 6}	2025-12-11 13:20:22.765894+00	2025-12-11 13:20:22.765897+00
c69011f9-9920-4910-9e2e-cab9abcedc4d	Hennepin County	MN	{"fees": {"commercial_inspection_base": 75.0, "residential_inspection_base": 50.0, "commercial_building_permit_base": 300.0, "residential_building_permit_base": 150.0}, "contact": {"email": "permits@hennepin.us", "phone": "612-348-3000", "address": "A-600 Government Center, Minneapolis, MN 55487"}, "required_documents": {"Framing": ["structural_plans"]}, "inspection_sequence": {"Final": ["Framing"], "Footing": [], "Framing": ["Foundation"], "Foundation": ["Footing"]}, "permit_validity_months": 6}	2025-12-11 13:20:22.845893+00	2025-12-11 13:20:22.845896+00
\.


--
-- Data for Name: payments; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.payments (payment_id, client_id, project_id, amount, payment_date, payment_method, status, check_number, transaction_id, qb_payment_id, notes, extra, created_at, updated_at, business_id, invoice_id, reference_number, sync_status, sync_error, last_sync_attempt) FROM stdin;
4dddc076-c3af-4f55-a8fb-d214962b8979	\N	\N	2000.00	2025-12-11 13:15:38.343858+00	Check	\N	\N	\N	\N	\N	{}	2025-12-11 13:15:38.870982+00	2025-12-11 13:15:39.183973+00	PAY-00007	57b4f6b3-ce93-45ad-879f-c9d34d6e8c84	CHK-12345	pending	\N	\N
\.


--
-- Data for Name: permits; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.permits (permit_id, project_id, client_id, permit_number, permit_type, status, application_date, approval_date, expiration_date, issuing_authority, inspector_name, notes, extra, created_at, updated_at, business_id, status_history, approved_by, approved_at) FROM stdin;
5927a0f2-b9d9-49e4-98d7-215a3de06e91	d3e0676c-ea61-4a89-90f2-ddfac4578068	\N	TEST-PERMIT-001	Building	Approved	2025-12-11 13:15:34.960715+00	\N	\N	\N	\N	\N	{}	2025-12-11 13:15:34.858885+00	2025-12-11 13:15:35.598645+00	PER-00032	[{"notes": "Test approval", "timestamp": "2025-12-11T13:15:35.598659+00:00", "new_status": "Approved", "old_status": "Pending"}]	\N	\N
027f309c-c5f5-4d12-8d0d-d637efce0406	123e4567-e89b-12d3-a456-426614174001	\N	\N	Building	Draft	2025-12-11 14:46:47.3353+00	\N	\N	\N	\N	\N	{"notes": "Phase B.1 test permit - PostgreSQL", "jurisdiction": "City of Burnsville", "inspector_name": null, "issuing_authority": null}	2025-12-11 14:46:47.721245+00	2025-12-11 14:46:47.721245+00	PER-00034	\N	\N	\N
41d193a7-fe3a-4391-87d2-feab16bb678e	123e4567-e89b-12d3-a456-426614174001	\N	\N	Building	Draft	2025-12-11 14:48:16.208418+00	\N	\N	\N	\N	\N	{"notes": null, "jurisdiction": null, "inspector_name": null, "issuing_authority": null}	2025-12-11 14:48:16.681237+00	2025-12-11 14:48:16.681237+00	PER-00035	\N	\N	\N
214cd078-a487-48c7-96f6-34891ee92246	123e4567-e89b-12d3-a456-426614174001	\N	TEST-2025-001	Building	Pending Review	2025-12-11 14:59:19.249577+00	\N	\N	\N	\N	\N	{"notes": null, "jurisdiction": null, "inspector_name": null, "issuing_authority": null}	2025-12-11 14:59:19.646779+00	2025-12-11 14:59:33.474627+00	PER-00036	[{"notes": "Status updated via comprehensive test", "timestamp": "2025-12-11T14:59:30.418413+00:00", "new_status": "Pending Review", "old_status": "Draft"}]	\N	\N
b2c5068b-ecdb-4fc1-a911-33ecb5fdff27	123e4567-e89b-12d3-a456-426614174001	\N	\N	Building	Draft	2025-12-11 15:02:43.490931+00	\N	\N	\N	\N	\N	{"notes": null, "jurisdiction": null, "inspector_name": null, "issuing_authority": null}	2025-12-11 15:02:43.899236+00	2025-12-11 15:02:43.899236+00	PER-00037	\N	\N	\N
a1d15716-b246-4fd5-a65f-2ba9685b8d57	123e4567-e89b-12d3-a456-426614174001	\N	\N	Building	Draft	2025-12-11 15:04:19.097844+00	\N	\N	\N	\N	\N	{"notes": null, "jurisdiction": null, "inspector_name": null, "issuing_authority": null}	2025-12-11 15:04:19.506533+00	2025-12-11 15:04:19.506533+00	PER-00038	\N	\N	\N
4d71a02a-29b4-4610-ad42-b4e2649633dc	123e4567-e89b-12d3-a456-426614174001	\N	\N	Building	Pending Review	2025-12-11 15:05:43.194427+00	\N	\N	\N	\N	\N	{"notes": null, "jurisdiction": null, "inspector_name": null, "issuing_authority": null}	2025-12-11 15:05:43.604636+00	2025-12-11 15:05:54.547106+00	PER-00039	[{"notes": "Status updated via comprehensive test", "timestamp": "2025-12-11T15:05:54.547120+00:00", "new_status": "Pending Review", "old_status": "Draft"}]	\N	\N
6c7bbcc7-b481-4903-b163-c7bf328db591	123e4567-e89b-12d3-a456-426614174001	\N	\N	Electrical	Submitted	2025-12-11 15:06:47.503779+00	\N	\N	\N	\N	\N	{"notes": null, "jurisdiction": null, "inspector_name": null, "issuing_authority": null}	2025-12-11 15:06:47.997994+00	2025-12-11 15:06:50.420887+00	PER-00040	[{"notes": "Submitted for approval", "timestamp": "2025-12-11T15:06:50.420898+00:00", "new_status": "Submitted", "old_status": "Draft"}]	\N	\N
bd64e4ca-9ef2-4234-b1af-beacda780a07	123e4567-e89b-12d3-a456-426614174001	\N	\N	Plumbing	Cancelled	2025-12-11 15:06:53.279279+00	\N	\N	\N	\N	\N	{"notes": null, "jurisdiction": null, "inspector_name": null, "issuing_authority": null}	2025-12-11 15:06:53.773366+00	2025-12-11 15:06:56.205938+00	PER-00041	[{"notes": "Permit cancelled by user", "timestamp": "2025-12-11T15:06:56.205946+00:00", "new_status": "Cancelled", "old_status": "Draft"}]	\N	\N
\.


--
-- Data for Name: projects; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.projects (project_id, client_id, project_name, project_address, project_type, status, budget, actual_cost, start_date, end_date, completion_date, description, notes, qb_estimate_id, qb_invoice_id, extra, created_at, updated_at, business_id) FROM stdin;
d3e0676c-ea61-4a89-90f2-ddfac4578068	569b9f27-def3-4881-aa2e-2e646823a9ff	Burnsville Re-roofing	671 W US Hwy 19 E, Burnsville, NC 28714, USA	Other	Completed	\N	\N	\N	\N	\N	\N		\N	\N	{"City": "Burnsville", "County": "Burnsville", "Photo Album": "https://app.companycam.com/galleries/LEim4B9q", "HR PC Service Fee": "4000", "Project Cost (Materials + Labor)": "700000"}	2025-12-10 21:10:04.64931+00	2025-12-11 03:30:53.281106+00	PRJ-00001
5648825d-15f4-4670-bc78-0a3124a7c0a0	a8ded034-bc67-459c-8617-78ae762776b7	Test Project	\N	\N	Planning	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-10 19:26:49.919358+00	2025-12-11 03:30:53.281118+00	PRJ-00002
cca678d5-f28a-466b-b632-41990b9118e1	5b58597d-c1ab-4aee-8272-ebdc85316461	Norcroft	8343 Norcroft Dr, Charlotte, NC 28269, USA	Renovation	Completed	\N	\N	\N	\N	\N	\N		\N	\N	{"City": "Charlotte", "County": "Mecklenburg", "Jurisdiction": "d351666b", "Scope of Work": "Norcroft Project\\nThe project consists of a kitchen renovation where the existing layout will remain unchanged, but all plumbing, electrical, cabinets, and appliances will be updated. A new 40 square foot pantry will be added behind the kitchen wall, including a mop sink connected to the kitchen’s plumbing. This area will be converted from unheated to heated space. All bathrooms will stay in their current locations, with upgrades to plumbing, electrical, cabinets, showers, and fixtures. On the second floor, an unused attic area will be converted into a bonus room of approximately 153 square feet. This will include the construction of a new 45 square foot hallway, a new wall to separate part of the existing bedroom, and the installation of a new door at the other end of the hallway for access. Adjacent to this space, an existing 80 square foot storage area will also be finished with insulation, drywall, electrical, and HVAC. Both areas will be converted from unheated to heated space. Another storage area connected to a second-floor bedroom will be expanded and finished with drywall, lighting, and foam insulation. All bedrooms will remain as-is. The overall structure of the house will remain the same, with recessed lighting installed throughout and HVAC extended to newly finished spaces. The project also includes new windows throughout, installation of a new roof, and new vinyl siding using Techshield radiant barrier sheathing. The foundation is flat with no basement.", "HR PC Service Fee": "3000", "Project Cost (Materials + Labor)": "210"}	2025-12-10 21:10:04.14559+00	2025-12-11 03:30:53.281103+00	PRJ-00003
dc546b0c-e9aa-44dc-bff7-ca1585c7632a	a9f0df2a-0f80-4030-94eb-e9097ad6f7b4	47 Main	47 N Main St, Marion, NC 28752, USA	Renovation	Completed	\N	\N	\N	\N	\N	\N		\N	\N	{"City": "Marion", "County": "McDowell", "Photo Album": " ", "Jurisdiction": "75862961", "HR PC Service Fee": "4000", "Primary Inspector": "d9485e90", "Owner Name (PM's Client)": "Fernando Uribe", "Project Cost (Materials + Labor)": "200000"}	2025-12-10 21:10:03.163517+00	2025-12-11 03:30:53.281108+00	PRJ-00004
93e74448-5097-4ff7-9110-b8e82ba76aa2	493f8b53-ab37-4943-a18a-a68f36cc30a3	16530-Ardrey_Mecklenburg	16530 Ardrey Pl Dr, Charlotte, NC 28277, USA	Addition	Inspections In Progress	\N	\N	\N	\N	\N	\N		\N	\N	{"City": "Charlotte", "County": "Mecklenburg", "Jurisdiction": "d351666b", "Scope of Work": "Building a new sunroom by expanding the footprint and utilizing existing unheated porch to a sunroom with split AC installed, making it a four season room. Also adding a deck on top of the expanded foot print and extending the dining room space. This work will require electrical, mechanical and plumbing work.", "Owner Name (PM's Client)": "Kandala Venkatatama M", "Project Cost (Materials + Labor)": "38500"}	2025-12-10 21:10:07.117399+00	2025-12-11 03:30:53.281109+00	PRJ-00005
e3eaa00f-c370-4114-911c-b7633cc81927	493f8b53-ab37-4943-a18a-a68f36cc30a3	101-W-5th-Ave_Lexington	101 W 5th Ave, Lexington, NC 27292, USA	Renovation	Permit Under Review	\N	\N	\N	\N	\N	\N		\N	\N	{"City": "Lexington", "County": "Davidson", "Jurisdiction": "1e21ac16", "Scope of Work": "Interior and structural remodeling of a 5,000 sqft single-family residence currently configured as four separate sections. Work includes alterations to walls, framing, layout, and finishes per attached engineered plans. Permit is being requested under residential classification.", "HR PC Service Fee": "3000", "Project Cost (Materials + Labor)": "200000"}	2025-12-10 21:10:02.6713+00	2025-12-11 03:30:53.28111+00	PRJ-00006
12239f59-98f8-4778-ba4a-8d6efa48e139	493f8b53-ab37-4943-a18a-a68f36cc30a3	2906-Longford_Mecklenburg	2906 Longford Ct, Charlotte, NC 28210, USA	Addition	Inspections In Progress	\N	\N	\N	\N	\N	\N		\N	\N	{"City": "Charlotte", "County": "Mecklenberg", "Jurisdiction": "d351666b", "Scope of Work": "Add new room and loft with roofline expansion, structural framing, and related electrical and\\nmechanical work per engineered plans.", "HR PC Service Fee": "3000", "Owner Name (PM's Client)": "Ajay", "Project Cost (Materials + Labor)": "55600"}	2025-12-10 21:10:06.626393+00	2025-12-11 03:30:53.281111+00	PRJ-00007
52195167-d5ee-4fd0-863b-7003eef8accb	493f8b53-ab37-4943-a18a-a68f36cc30a3	733-1-StonyPoint-KingsMountain	733 Stony Point Rd, Kings Mountain, NC 28086, USA	Remodel	Inspections In Progress	\N	\N	\N	\N	\N	\N	Waiting for plans to be approve in order to bill client	\N	\N	{"City": "Kings Mountain", "County": "Kings Mountain", "Jurisdiction": "b8d8d8e4", "Scope of Work": "It's a commercial building and zoning permit for an industrial kitchen plan", "HR PC Service Fee": "3000", "Owner Name (PM's Client)": "Sarathi Properties LLC", "Project Cost (Materials + Labor)": "255000"}	2025-12-10 21:10:05.149734+00	2025-12-11 03:30:53.281112+00	PRJ-00008
ad857828-99ee-41ac-b79d-e516b3b092ea	c38f08e7-ad9e-407f-a9c9-76a1f95272fa	256 Broad	256 Broad St, Lexington, NC 27295, USA	Renovation	Inspections In Progress	\N	\N	\N	\N	\N	\N		\N	\N	{"City": "Lexington", "County": "Davidson", "Jurisdiction": "1e21ac16", "Scope of Work": "Take over renovation from previous Contractor", "HR PC Service Fee": "3000", "Project Cost (Materials + Labor)": "300000"}	2025-12-10 21:10:03.655312+00	2025-12-11 03:30:53.281114+00	PRJ-00009
284f0239-160d-4f9f-a66e-c87f55e025dd	493f8b53-ab37-4943-a18a-a68f36cc30a3	6441-BeattiesFord_Mecklenburg	6441 Beatties Ford Rd, Charlotte, NC 28216, USA	New Construction	Inspections In Progress	\N	\N	\N	\N	\N	\N		\N	\N	{"City": "Charlotte", "County": "Mecklenburg", "Jurisdiction": "d351666b", "Scope of Work": "Construction of pre-engineered metal picnic shelter and separate restroom building for trimurti temple. Includes related electrical (COM-ELEC-25-005310), plumbing, and mechanical permits. Civil scope covers Site grading drainage and landscaping", "HR PC Service Fee": "3000", "Project Cost (Materials + Labor)": "295000"}	2025-12-10 21:10:05.643568+00	2025-12-11 03:30:53.281115+00	PRJ-00010
6e1ff79c-a63d-4f6d-bec4-4c56f3c89612	9f9990c1-e217-4dd4-a68b-f983a726113c	64 Phillips	64 Phillips Ln, Spruce Pine, NC 28777, USA	New Construction	Inspections In Progress	\N	\N	\N	\N	\N	\N		\N	\N	{"City": "Spruce Pine", "County": "Mitchell", "Photo Album": "https://photos.app.goo.gl/Y6asMJMXgHpppEED9", "Jurisdiction": "218ee0c2", "Scope of Work": "Scope of Work – Residential Two-Story Home (4 Bed / 3 Bath)\\n\\nProject Overview\\n\\nThis project involves the completion and renovation of a single-family residence that has been converted into a two-story home. The property includes four bedrooms and three bathrooms. Work will ensure that all construction complies with applicable building codes, zoning regulations, and safety standards.\\n1. Site Preparation\\n\\nInspect existing structure for compliance with local codes.\\n\\nRemove debris, unsafe materials, or unpermitted modifications if present.\\n\\nVerify utilities (water, sewer, gas, electric) for capacity to support expanded square footage.\\n2. Structural Work\\n\\nConfirm structural framing for both stories meets load-bearing requirements.\\n\\nReinforce or replace beams, joists, and headers as needed.\\n\\nInstall or repair subflooring and sheathing.\\n\\nEnsure proper fire blocking, insulation, and wall bracing per code.\\n3. Exterior\\n\\nRoofing: Inspect/replace as required for coverage of new second story.\\n\\nSiding/Stucco/Brick: Install finish system to fully integrate upper and lower levels.\\n\\nWindows & Doors: Supply and install energy-efficient, code-compliant units.\\n\\nExterior paint/sealant to weatherproof entire structure.\\n4. Interior Layout\\n\\nBedrooms (4 total): Framing, drywall, flooring, doors, closets, and trim.\\n\\nBathrooms (3 total): Layout to include shower/tub, toilet, vanity, exhaust fan, GFCI outlets, and tiling.\\n\\nKitchen (if included in scope): Cabinets, countertops, backsplash, plumbing fixtures, appliances (per owner’s selection).\\n\\nLiving & Dining Areas: Framing, drywall, flooring, paint, and trim.\\n\\nStaircase: Installation or code verification for safe access to second floor.\\n5. Mechanical, Electrical, Plumbing (MEP)\\n\\nHVAC: Install/upgrade system sized for two-story layout. Ductwork adjustments as needed.\\n\\nPlumbing: Rough-in and finish for 3 bathrooms, kitchen, and laundry. Verify venting and supply lines.\\n\\nElectrical: Full rewire/upgrade to handle new square footage; install outlets, lighting, smoke detectors, and panel upgrades if required.\\n\\nFire Safety: Smoke/CO detectors installed per code.\\n6. Finishes\\n\\nDrywall & Paint: Smooth finish, primer, and two coats of paint.\\n\\nFlooring: Install per room type (hardwood, tile, carpet, vinyl).\\n\\nTrim & Millwork: Baseboards, door/window casings, crown molding if specified.\\n\\nCabinetry & Fixtures: Install per owner selections.\\n7. Final Work\\n\\nFinal cleaning and debris removal.\\n\\nWalk-through with client for punch-list corrections.\\n\\nCoordinate all required inspections for Certificate of Occupancy (CO).\\nExclusions (to be defined)\\n\\nLandscaping, fencing, driveway, and exterior hardscaping.\\n\\nFurniture and owner-supplied appliances (unless specified).\\n\\nAny work outside original contract or scope creep without approved change order.", "HR PC Service Fee": "3000", "Primary Inspector": "75fbdb01", "Project Cost (Materials + Labor)": "120000"}	2025-12-10 21:10:02.088273+00	2025-12-11 03:30:53.281116+00	PRJ-00011
424fd588-6110-483d-a632-f9817d6da2ad	493f8b53-ab37-4943-a18a-a68f36cc30a3	1105-SandyBottom_Cabarrus	1105 Sandy Bottom Dr NW, Concord, NC 28027, United States	Residential	Inspections In Progress	\N	\N	\N	\N	\N	\N	Heated Sq Ft: 862, Unheated Sq Ft: 0, Total Sq Ft: 862 Square Footage: 862 Parcel Number: 46717413760000 Permit Record Number: PRB2025-02843	\N	\N	{"City": "Concord", "County": "Cabarrus", "Photo Album": "na", "Jurisdiction": "e8fb3422", "Scope of Work": "CN-ZCP-2025-00444.\\nSunroom Extension to existing house and adding square footage to second floor. This project mainly involves building a new sunroom, with an exercise room attached to the existing house. It will be conditioned by a split AC Unit. The current HVAC will need to be moved to the side of the house to accommodate the Sunroom. Additionally, we are extending the second floor room to add 93 square feet inline with the first floor bay window dining area. Also adding will be a 465 square foot patio area.", "HR PC Service Fee": "3000", "Owner Name (PM's Client)": "Menon Prashanth", "Project Cost (Materials + Labor)": "85000"}	2025-12-10 21:10:06.129927+00	2025-12-11 03:30:53.281117+00	PRJ-00012
123e4567-e89b-12d3-a456-426614174001	\N	Phase B.1 Test Project	\N	\N	Active	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-11 14:28:35.602979+00	2025-12-11 14:28:35.602979+00	PRJ-00013
\.


--
-- Data for Name: quickbooks_customers_cache; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.quickbooks_customers_cache (qb_customer_id, display_name, company_name, given_name, family_name, email, phone, qb_data, cached_at) FROM stdin;
\.


--
-- Data for Name: quickbooks_invoices_cache; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.quickbooks_invoices_cache (qb_invoice_id, customer_id, doc_number, total_amount, balance, due_date, qb_data, cached_at) FROM stdin;
\.


--
-- Data for Name: quickbooks_tokens; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.quickbooks_tokens (id, realm_id, access_token, refresh_token, access_token_expires_at, refresh_token_expires_at, environment, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: site_visits; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.site_visits (visit_id, business_id, project_id, client_id, visit_type, status, scheduled_date, start_time, end_time, attendees, gps_location, photos, notes, weather, deficiencies, follow_up_actions, created_by, assigned_to, extra, created_at, updated_at) FROM stdin;
645d0f7d-6f20-4b3d-aa61-43b293f3bbdc	SV-00004	d3e0676c-ea61-4a89-90f2-ddfac4578068	9f9990c1-e217-4dd4-a68b-f983a726113c	Progress Check	Completed	2025-12-14 13:15:39.92868+00	2025-12-11 13:15:40.606207+00	2025-12-11 13:15:42.064159+00	["John Smith", "Jane Doe"]	34.0522,-118.2437	[{"url": "https://example.com/visit1.jpg", "caption": "Before work", "timestamp": "2025-12-11T13:15:41.096053+00:00"}]	Framing complete, ready for inspection	\N	\N	[{"status": "pending", "due_date": "2025-12-13T13:15:41.418866+00:00", "priority": "high", "created_at": "2025-12-11T13:15:41.580136+00:00", "assigned_to": "Foreman", "description": "Order additional materials"}, {"status": "pending", "due_date": "2025-12-16T13:15:41.418882+00:00", "priority": "medium", "created_at": "2025-12-11T13:15:41.580146+00:00", "assigned_to": "Project Manager", "description": "Schedule electrical inspection"}]	\N	\N	{}	2025-12-11 13:15:40.295029+00	2025-12-11 13:15:42.06417+00
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.users (id, supabase_user_id, email, full_name, phone, role, is_active, is_email_verified, last_login_at, last_activity_at, app_metadata, created_at, updated_at) FROM stdin;
937b6be4-2956-47b4-ba39-3314a05df6cb	06d93a4f-b82e-4bb4-941e-cedf2d7dea55	steve@houserenovatorsllc.com	Steve Garay	\N	admin	t	t	\N	\N	\N	2025-12-11 16:04:49.646853+00	2025-12-11 16:04:49.646853+00
\.


--
-- Name: client_business_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.client_business_id_seq', 8, true);


--
-- Name: inspection_business_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.inspection_business_id_seq', 9, true);


--
-- Name: invoice_business_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.invoice_business_id_seq', 7, true);


--
-- Name: payment_business_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.payment_business_id_seq', 7, true);


--
-- Name: permit_business_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.permit_business_id_seq', 41, true);


--
-- Name: project_business_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.project_business_id_seq', 13, true);


--
-- Name: quickbooks_tokens_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.quickbooks_tokens_id_seq', 1, false);


--
-- Name: site_visit_business_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.site_visit_business_id_seq', 4, true);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: clients clients_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.clients
    ADD CONSTRAINT clients_pkey PRIMARY KEY (client_id);


--
-- Name: inspections inspections_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.inspections
    ADD CONSTRAINT inspections_pkey PRIMARY KEY (inspection_id);


--
-- Name: invoices invoices_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.invoices
    ADD CONSTRAINT invoices_pkey PRIMARY KEY (invoice_id);


--
-- Name: jurisdictions jurisdictions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.jurisdictions
    ADD CONSTRAINT jurisdictions_pkey PRIMARY KEY (id);


--
-- Name: payments payments_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT payments_pkey PRIMARY KEY (payment_id);


--
-- Name: permits permits_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.permits
    ADD CONSTRAINT permits_pkey PRIMARY KEY (permit_id);


--
-- Name: projects projects_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.projects
    ADD CONSTRAINT projects_pkey PRIMARY KEY (project_id);


--
-- Name: quickbooks_customers_cache quickbooks_customers_cache_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.quickbooks_customers_cache
    ADD CONSTRAINT quickbooks_customers_cache_pkey PRIMARY KEY (qb_customer_id);


--
-- Name: quickbooks_invoices_cache quickbooks_invoices_cache_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.quickbooks_invoices_cache
    ADD CONSTRAINT quickbooks_invoices_cache_pkey PRIMARY KEY (qb_invoice_id);


--
-- Name: quickbooks_tokens quickbooks_tokens_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.quickbooks_tokens
    ADD CONSTRAINT quickbooks_tokens_pkey PRIMARY KEY (id);


--
-- Name: site_visits site_visits_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.site_visits
    ADD CONSTRAINT site_visits_pkey PRIMARY KEY (visit_id);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users users_supabase_user_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_supabase_user_id_key UNIQUE (supabase_user_id);


--
-- Name: idx_jurisdictions_name; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_jurisdictions_name ON public.jurisdictions USING btree (name);


--
-- Name: idx_jurisdictions_requirements; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_jurisdictions_requirements ON public.jurisdictions USING gin (requirements);


--
-- Name: idx_jurisdictions_state; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_jurisdictions_state ON public.jurisdictions USING btree (state);


--
-- Name: ix_clients_business_id; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_clients_business_id ON public.clients USING btree (business_id);


--
-- Name: ix_clients_email; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_clients_email ON public.clients USING btree (email);


--
-- Name: ix_clients_extra_gin; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_clients_extra_gin ON public.clients USING gin (extra);


--
-- Name: ix_clients_full_name; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_clients_full_name ON public.clients USING btree (full_name);


--
-- Name: ix_clients_full_name_lower; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_clients_full_name_lower ON public.clients USING btree (lower((full_name)::text));


--
-- Name: ix_clients_qb_customer_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_clients_qb_customer_id ON public.clients USING btree (qb_customer_id);


--
-- Name: ix_clients_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_clients_status ON public.clients USING btree (status);


--
-- Name: ix_inspections_business_id; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_inspections_business_id ON public.inspections USING btree (business_id);


--
-- Name: ix_inspections_deficiencies_gin; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_inspections_deficiencies_gin ON public.inspections USING gin (deficiencies);


--
-- Name: ix_inspections_extra_gin; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_inspections_extra_gin ON public.inspections USING gin (extra);


--
-- Name: ix_inspections_inspection_type; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_inspections_inspection_type ON public.inspections USING btree (inspection_type);


--
-- Name: ix_inspections_permit_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_inspections_permit_id ON public.inspections USING btree (permit_id);


--
-- Name: ix_inspections_photos_gin; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_inspections_photos_gin ON public.inspections USING gin (photos);


--
-- Name: ix_inspections_project_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_inspections_project_id ON public.inspections USING btree (project_id);


--
-- Name: ix_inspections_scheduled_date; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_inspections_scheduled_date ON public.inspections USING btree (scheduled_date);


--
-- Name: ix_inspections_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_inspections_status ON public.inspections USING btree (status);


--
-- Name: ix_invoices_business_id; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_invoices_business_id ON public.invoices USING btree (business_id);


--
-- Name: ix_invoices_client_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_invoices_client_id ON public.invoices USING btree (client_id);


--
-- Name: ix_invoices_due_date; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_invoices_due_date ON public.invoices USING btree (due_date);


--
-- Name: ix_invoices_extra_gin; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_invoices_extra_gin ON public.invoices USING gin (extra);


--
-- Name: ix_invoices_invoice_date; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_invoices_invoice_date ON public.invoices USING btree (invoice_date);


--
-- Name: ix_invoices_invoice_number; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_invoices_invoice_number ON public.invoices USING btree (invoice_number);


--
-- Name: ix_invoices_line_items_gin; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_invoices_line_items_gin ON public.invoices USING gin (line_items);


--
-- Name: ix_invoices_project_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_invoices_project_id ON public.invoices USING btree (project_id);


--
-- Name: ix_invoices_qb_invoice_id; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_invoices_qb_invoice_id ON public.invoices USING btree (qb_invoice_id);


--
-- Name: ix_invoices_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_invoices_status ON public.invoices USING btree (status);


--
-- Name: ix_invoices_sync_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_invoices_sync_status ON public.invoices USING btree (sync_status);


--
-- Name: ix_payments_business_id; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_payments_business_id ON public.payments USING btree (business_id);


--
-- Name: ix_payments_client_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_payments_client_id ON public.payments USING btree (client_id);


--
-- Name: ix_payments_extra_gin; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_payments_extra_gin ON public.payments USING gin (extra);


--
-- Name: ix_payments_invoice_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_payments_invoice_id ON public.payments USING btree (invoice_id);


--
-- Name: ix_payments_payment_date; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_payments_payment_date ON public.payments USING btree (payment_date);


--
-- Name: ix_payments_project_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_payments_project_id ON public.payments USING btree (project_id);


--
-- Name: ix_payments_qb_payment_id; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_payments_qb_payment_id ON public.payments USING btree (qb_payment_id);


--
-- Name: ix_payments_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_payments_status ON public.payments USING btree (status);


--
-- Name: ix_payments_sync_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_payments_sync_status ON public.payments USING btree (sync_status);


--
-- Name: ix_permits_business_id; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_permits_business_id ON public.permits USING btree (business_id);


--
-- Name: ix_permits_client_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_permits_client_id ON public.permits USING btree (client_id);


--
-- Name: ix_permits_extra_gin; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_permits_extra_gin ON public.permits USING gin (extra);


--
-- Name: ix_permits_permit_number; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_permits_permit_number ON public.permits USING btree (permit_number);


--
-- Name: ix_permits_project_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_permits_project_id ON public.permits USING btree (project_id);


--
-- Name: ix_permits_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_permits_status ON public.permits USING btree (status);


--
-- Name: ix_projects_business_id; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_projects_business_id ON public.projects USING btree (business_id);


--
-- Name: ix_projects_client_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_projects_client_id ON public.projects USING btree (client_id);


--
-- Name: ix_projects_dates; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_projects_dates ON public.projects USING btree (start_date, end_date);


--
-- Name: ix_projects_extra_gin; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_projects_extra_gin ON public.projects USING gin (extra);


--
-- Name: ix_projects_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_projects_status ON public.projects USING btree (status);


--
-- Name: ix_qb_customers_cached_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_qb_customers_cached_at ON public.quickbooks_customers_cache USING btree (cached_at);


--
-- Name: ix_quickbooks_customers_cache_cached_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_quickbooks_customers_cache_cached_at ON public.quickbooks_customers_cache USING btree (cached_at);


--
-- Name: ix_quickbooks_invoices_cache_cached_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_quickbooks_invoices_cache_cached_at ON public.quickbooks_invoices_cache USING btree (cached_at);


--
-- Name: ix_quickbooks_invoices_cache_customer_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_quickbooks_invoices_cache_customer_id ON public.quickbooks_invoices_cache USING btree (customer_id);


--
-- Name: ix_quickbooks_tokens_realm_id; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_quickbooks_tokens_realm_id ON public.quickbooks_tokens USING btree (realm_id);


--
-- Name: ix_site_visits_attendees_gin; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_site_visits_attendees_gin ON public.site_visits USING gin (attendees);


--
-- Name: ix_site_visits_business_id; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_site_visits_business_id ON public.site_visits USING btree (business_id);


--
-- Name: ix_site_visits_client_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_site_visits_client_id ON public.site_visits USING btree (client_id);


--
-- Name: ix_site_visits_deficiencies_gin; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_site_visits_deficiencies_gin ON public.site_visits USING gin (deficiencies);


--
-- Name: ix_site_visits_extra_gin; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_site_visits_extra_gin ON public.site_visits USING gin (extra);


--
-- Name: ix_site_visits_follow_up_actions_gin; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_site_visits_follow_up_actions_gin ON public.site_visits USING gin (follow_up_actions);


--
-- Name: ix_site_visits_photos_gin; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_site_visits_photos_gin ON public.site_visits USING gin (photos);


--
-- Name: ix_site_visits_project_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_site_visits_project_id ON public.site_visits USING btree (project_id);


--
-- Name: ix_site_visits_scheduled_date; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_site_visits_scheduled_date ON public.site_visits USING btree (scheduled_date);


--
-- Name: ix_site_visits_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_site_visits_status ON public.site_visits USING btree (status);


--
-- Name: ix_site_visits_visit_type; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_site_visits_visit_type ON public.site_visits USING btree (visit_type);


--
-- Name: ix_users_active; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_users_active ON public.users USING btree (is_active) WHERE (is_active = true);


--
-- Name: ix_users_app_metadata_gin; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_users_app_metadata_gin ON public.users USING gin (app_metadata);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: ix_users_email_lower; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_users_email_lower ON public.users USING btree (lower((email)::text));


--
-- Name: ix_users_role; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_users_role ON public.users USING btree (role);


--
-- Name: ix_users_supabase_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_users_supabase_user_id ON public.users USING btree (supabase_user_id);


--
-- Name: clients client_business_id_trigger; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER client_business_id_trigger BEFORE INSERT ON public.clients FOR EACH ROW EXECUTE FUNCTION public.generate_client_business_id();


--
-- Name: inspections inspection_business_id_trigger; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER inspection_business_id_trigger BEFORE INSERT ON public.inspections FOR EACH ROW EXECUTE FUNCTION public.generate_inspection_business_id();


--
-- Name: invoices invoice_business_id_trigger; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER invoice_business_id_trigger BEFORE INSERT ON public.invoices FOR EACH ROW EXECUTE FUNCTION public.generate_invoice_business_id();


--
-- Name: payments payment_business_id_trigger; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER payment_business_id_trigger BEFORE INSERT ON public.payments FOR EACH ROW EXECUTE FUNCTION public.generate_payment_business_id();


--
-- Name: permits permit_business_id_trigger; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER permit_business_id_trigger BEFORE INSERT ON public.permits FOR EACH ROW EXECUTE FUNCTION public.generate_permit_business_id();


--
-- Name: projects project_business_id_trigger; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER project_business_id_trigger BEFORE INSERT ON public.projects FOR EACH ROW EXECUTE FUNCTION public.generate_project_business_id();


--
-- Name: site_visits site_visit_business_id_trigger; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER site_visit_business_id_trigger BEFORE INSERT ON public.site_visits FOR EACH ROW EXECUTE FUNCTION public.generate_site_visit_business_id();


--
-- Name: clients trigger_set_client_business_id; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trigger_set_client_business_id BEFORE INSERT ON public.clients FOR EACH ROW EXECUTE FUNCTION public.set_client_business_id();


--
-- Name: payments trigger_set_payment_business_id; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trigger_set_payment_business_id BEFORE INSERT ON public.payments FOR EACH ROW EXECUTE FUNCTION public.set_payment_business_id();


--
-- Name: permits trigger_set_permit_business_id; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trigger_set_permit_business_id BEFORE INSERT ON public.permits FOR EACH ROW EXECUTE FUNCTION public.set_permit_business_id();


--
-- Name: projects trigger_set_project_business_id; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trigger_set_project_business_id BEFORE INSERT ON public.projects FOR EACH ROW EXECUTE FUNCTION public.set_project_business_id();


--
-- Name: users users_updated_at_trigger; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER users_updated_at_trigger BEFORE UPDATE ON public.users FOR EACH ROW EXECUTE FUNCTION public.update_users_updated_at();


--
-- PostgreSQL database dump complete
--

