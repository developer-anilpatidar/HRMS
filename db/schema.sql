-- ============================================================
-- HRMS Production-shaped schema (PostgreSQL)
-- Single-org v1: core + leave + attendance + tickets + audit
-- ============================================================

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ---------- ENUMS ----------
CREATE TYPE employment_status AS ENUM (
  'active',
  'probation',
  'on_notice',
  'terminated',
  'on_leave'
);

CREATE TYPE workforce_type AS ENUM (
  'full_time',
  'part_time',
  'contract',
  'intern'
);

CREATE TYPE leave_request_status AS ENUM (
  'draft',
  'pending',
  'approved',
  'rejected',
  'cancelled'
);

CREATE TYPE attendance_status AS ENUM (
  'present',
  'absent',
  'half_day',
  'remote',
  'holiday',
  'on_leave'
);

CREATE TYPE ticket_status AS ENUM (
  'open',
  'in_progress',
  'waiting_on_employee',
  'resolved',
  'closed'
);

CREATE TYPE ticket_priority AS ENUM (
  'low',
  'medium',
  'high',
  'urgent'
);

CREATE TYPE approval_action AS ENUM (
  'submitted',
  'approved',
  'rejected',
  'cancelled'
);

-- ============================================================
-- CORE
-- ============================================================
CREATE TABLE organizations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  code VARCHAR(32) NOT NULL UNIQUE,
  name VARCHAR(200) NOT NULL,
  legal_name VARCHAR(255),
  country_code CHAR(2) NOT NULL DEFAULT 'IN',
  timezone VARCHAR(64) NOT NULL DEFAULT 'Asia/Kolkata',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE locations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organizations(id),
  code VARCHAR(32) NOT NULL,
  name VARCHAR(120) NOT NULL,
  city VARCHAR(80),
  state VARCHAR(80),
  country_code CHAR(2) NOT NULL DEFAULT 'IN',
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  UNIQUE (organization_id, code)
);

CREATE TABLE departments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organizations(id),
  parent_id UUID REFERENCES departments(id),
  code VARCHAR(32) NOT NULL,
  name VARCHAR(120) NOT NULL,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  UNIQUE (organization_id, code)
);

CREATE TABLE job_titles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organizations(id),
  code VARCHAR(32) NOT NULL,
  title VARCHAR(120) NOT NULL,
  grade VARCHAR(32),
  UNIQUE (organization_id, code)
);

CREATE TABLE holiday_calendars (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organizations(id),
  location_id UUID REFERENCES locations(id),
  name VARCHAR(120) NOT NULL,
  year INT NOT NULL
);

CREATE TABLE holidays (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  calendar_id UUID NOT NULL REFERENCES holiday_calendars(id) ON DELETE CASCADE,
  holiday_date DATE NOT NULL,
  name VARCHAR(120) NOT NULL,
  UNIQUE (calendar_id, holiday_date)
);

-- ---------- RBAC ----------
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organizations(id),
  email VARCHAR(255) NOT NULL,
  password_hash TEXT,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  last_login_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (organization_id, email)
);

CREATE TABLE roles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organizations(id),
  code VARCHAR(32) NOT NULL,
  name VARCHAR(80) NOT NULL,
  UNIQUE (organization_id, code)
);

CREATE TABLE permissions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  code VARCHAR(64) NOT NULL UNIQUE,
  description TEXT
);

CREATE TABLE role_permissions (
  role_id UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
  permission_id UUID NOT NULL REFERENCES permissions(id) ON DELETE CASCADE,
  PRIMARY KEY (role_id, permission_id)
);

CREATE TABLE user_roles (
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  role_id UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
  PRIMARY KEY (user_id, role_id)
);

-- ---------- EMPLOYEES ----------
CREATE TABLE employees (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organizations(id),
  user_id UUID UNIQUE REFERENCES users(id),
  employee_code VARCHAR(32) NOT NULL,
  first_name VARCHAR(80) NOT NULL,
  last_name VARCHAR(80) NOT NULL,
  work_email VARCHAR(255) NOT NULL,
  personal_email VARCHAR(255),
  phone VARCHAR(32),
  date_of_birth DATE,
  gender VARCHAR(32),
  hire_date DATE NOT NULL,
  termination_date DATE,
  employment_status employment_status NOT NULL DEFAULT 'active',
  workforce_type workforce_type NOT NULL DEFAULT 'full_time',
  location_id UUID REFERENCES locations(id),
  department_id UUID REFERENCES departments(id),
  job_title_id UUID REFERENCES job_titles(id),
  manager_id UUID REFERENCES employees(id),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (organization_id, employee_code),
  UNIQUE (organization_id, work_email)
);

CREATE INDEX idx_employees_manager ON employees(manager_id);
CREATE INDEX idx_employees_dept ON employees(department_id);
CREATE INDEX idx_employees_org ON employees(organization_id);

CREATE TABLE employee_assignments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  employee_id UUID NOT NULL REFERENCES employees(id),
  department_id UUID REFERENCES departments(id),
  job_title_id UUID REFERENCES job_titles(id),
  manager_id UUID REFERENCES employees(id),
  location_id UUID REFERENCES locations(id),
  effective_from DATE NOT NULL,
  effective_to DATE,
  is_current BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE employee_contacts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  employee_id UUID NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
  contact_type VARCHAR(32) NOT NULL,
  name VARCHAR(120) NOT NULL,
  relationship VARCHAR(64),
  phone VARCHAR(32),
  email VARCHAR(255)
);

-- ============================================================
-- LEAVE
-- ============================================================
CREATE TABLE leave_types (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organizations(id),
  code VARCHAR(32) NOT NULL,
  name VARCHAR(80) NOT NULL,
  is_paid BOOLEAN NOT NULL DEFAULT TRUE,
  requires_approval BOOLEAN NOT NULL DEFAULT TRUE,
  annual_quota NUMERIC(5,1),
  UNIQUE (organization_id, code)
);

CREATE TABLE leave_balances (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  employee_id UUID NOT NULL REFERENCES employees(id),
  leave_type_id UUID NOT NULL REFERENCES leave_types(id),
  year INT NOT NULL,
  entitled NUMERIC(5,1) NOT NULL DEFAULT 0,
  used NUMERIC(5,1) NOT NULL DEFAULT 0,
  pending NUMERIC(5,1) NOT NULL DEFAULT 0,
  UNIQUE (employee_id, leave_type_id, year)
);

CREATE TABLE leave_requests (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  employee_id UUID NOT NULL REFERENCES employees(id),
  leave_type_id UUID NOT NULL REFERENCES leave_types(id),
  start_date DATE NOT NULL,
  end_date DATE NOT NULL,
  days NUMERIC(5,1) NOT NULL,
  reason TEXT,
  status leave_request_status NOT NULL DEFAULT 'pending',
  approver_id UUID REFERENCES employees(id),
  decided_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  CHECK (end_date >= start_date)
);

CREATE INDEX idx_leave_requests_employee ON leave_requests(employee_id);
CREATE INDEX idx_leave_requests_status ON leave_requests(status);

CREATE TABLE leave_approvals (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  leave_request_id UUID NOT NULL REFERENCES leave_requests(id) ON DELETE CASCADE,
  actor_employee_id UUID NOT NULL REFERENCES employees(id),
  action approval_action NOT NULL,
  comments TEXT,
  acted_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============================================================
-- ATTENDANCE
-- ============================================================
CREATE TABLE attendance_daily (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  employee_id UUID NOT NULL REFERENCES employees(id),
  work_date DATE NOT NULL,
  status attendance_status NOT NULL,
  check_in TIMESTAMPTZ,
  check_out TIMESTAMPTZ,
  worked_minutes INT,
  UNIQUE (employee_id, work_date)
);

CREATE INDEX idx_attendance_date ON attendance_daily(work_date);

-- ============================================================
-- HELPDESK / DOCS / AUDIT
-- ============================================================
CREATE TABLE tickets (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organizations(id),
  ticket_number VARCHAR(32) NOT NULL,
  requester_employee_id UUID NOT NULL REFERENCES employees(id),
  assignee_employee_id UUID REFERENCES employees(id),
  category VARCHAR(64) NOT NULL,
  subject VARCHAR(200) NOT NULL,
  description TEXT,
  status ticket_status NOT NULL DEFAULT 'open',
  priority ticket_priority NOT NULL DEFAULT 'medium',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (organization_id, ticket_number)
);

CREATE TABLE ticket_comments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  ticket_id UUID NOT NULL REFERENCES tickets(id) ON DELETE CASCADE,
  author_employee_id UUID NOT NULL REFERENCES employees(id),
  body TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE policies (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organizations(id),
  code VARCHAR(64) NOT NULL,
  title VARCHAR(200) NOT NULL,
  category VARCHAR(64),
  content TEXT NOT NULL,
  version VARCHAR(16) NOT NULL DEFAULT '1.0',
  effective_from DATE,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  UNIQUE (organization_id, code, version)
);

CREATE TABLE audit_logs (
  id BIGSERIAL PRIMARY KEY,
  organization_id UUID NOT NULL REFERENCES organizations(id),
  actor_user_id UUID REFERENCES users(id),
  entity_type VARCHAR(64) NOT NULL,
  entity_id UUID,
  action VARCHAR(64) NOT NULL,
  before_data JSONB,
  after_data JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_audit_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX idx_audit_org ON audit_logs(organization_id);

-- Directory view for agents / API
CREATE OR REPLACE VIEW v_employee_directory AS
SELECT
  e.id,
  e.employee_code,
  e.first_name,
  e.last_name,
  e.work_email,
  e.employment_status,
  e.workforce_type,
  d.name AS department,
  j.title AS job_title,
  l.name AS location,
  m.employee_code AS manager_code,
  m.first_name || ' ' || m.last_name AS manager_name
FROM employees e
LEFT JOIN departments d ON d.id = e.department_id
LEFT JOIN job_titles j ON j.id = e.job_title_id
LEFT JOIN locations l ON l.id = e.location_id
LEFT JOIN employees m ON m.id = e.manager_id;
