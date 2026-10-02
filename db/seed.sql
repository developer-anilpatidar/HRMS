-- ============================================================
-- HRMS dummy seed data (PostgreSQL)
-- Run after schema.sql
-- ============================================================

INSERT INTO organizations (id, code, name, legal_name)
VALUES (
  '11111111-1111-1111-1111-111111111111',
  'NOVA',
  'NovaTech Solutions',
  'NovaTech Solutions Pvt Ltd'
);

INSERT INTO locations (id, organization_id, code, name, city, state) VALUES
(
  '22222222-2222-2222-2222-222222222201',
  '11111111-1111-1111-1111-111111111111',
  'BLR',
  'Bangalore HQ',
  'Bengaluru',
  'Karnataka'
),
(
  '22222222-2222-2222-2222-222222222202',
  '11111111-1111-1111-1111-111111111111',
  'HYD',
  'Hyderabad Office',
  'Hyderabad',
  'Telangana'
),
(
  '22222222-2222-2222-2222-222222222203',
  '11111111-1111-1111-1111-111111111111',
  'PNQ',
  'Pune Office',
  'Pune',
  'Maharashtra'
);

INSERT INTO departments (id, organization_id, parent_id, code, name) VALUES
(
  '33333333-3333-3333-3333-333333333301',
  '11111111-1111-1111-1111-111111111111',
  NULL,
  'ENG',
  'Engineering'
),
(
  '33333333-3333-3333-3333-333333333302',
  '11111111-1111-1111-1111-111111111111',
  '33333333-3333-3333-3333-333333333301',
  'ENG-BE',
  'Backend Engineering'
),
(
  '33333333-3333-3333-3333-333333333303',
  '11111111-1111-1111-1111-111111111111',
  '33333333-3333-3333-3333-333333333301',
  'ENG-FE',
  'Frontend Engineering'
),
(
  '33333333-3333-3333-3333-333333333304',
  '11111111-1111-1111-1111-111111111111',
  NULL,
  'HR',
  'Human Resources'
),
(
  '33333333-3333-3333-3333-333333333305',
  '11111111-1111-1111-1111-111111111111',
  NULL,
  'FIN',
  'Finance'
),
(
  '33333333-3333-3333-3333-333333333306',
  '11111111-1111-1111-1111-111111111111',
  NULL,
  'SALES',
  'Sales'
);

INSERT INTO job_titles (id, organization_id, code, title, grade) VALUES
(
  '44444444-4444-4444-4444-444444444401',
  '11111111-1111-1111-1111-111111111111',
  'CEO',
  'Chief Executive Officer',
  'E1'
),
(
  '44444444-4444-4444-4444-444444444402',
  '11111111-1111-1111-1111-111111111111',
  'ENG-MGR',
  'Engineering Manager',
  'M2'
),
(
  '44444444-4444-4444-4444-444444444403',
  '11111111-1111-1111-1111-111111111111',
  'SSE',
  'Senior Software Engineer',
  'IC4'
),
(
  '44444444-4444-4444-4444-444444444404',
  '11111111-1111-1111-1111-111111111111',
  'SDE',
  'Software Engineer',
  'IC3'
),
(
  '44444444-4444-4444-4444-444444444405',
  '11111111-1111-1111-1111-111111111111',
  'HRBP',
  'HR Business Partner',
  'M1'
),
(
  '44444444-4444-4444-4444-444444444406',
  '11111111-1111-1111-1111-111111111111',
  'HR-EX',
  'HR Executive',
  'IC2'
),
(
  '44444444-4444-4444-4444-444444444407',
  '11111111-1111-1111-1111-111111111111',
  'FIN-MGR',
  'Finance Manager',
  'M1'
),
(
  '44444444-4444-4444-4444-444444444408',
  '11111111-1111-1111-1111-111111111111',
  'AE',
  'Account Executive',
  'IC3'
);

INSERT INTO roles (id, organization_id, code, name) VALUES
(
  '55555555-5555-5555-5555-555555555501',
  '11111111-1111-1111-1111-111111111111',
  'EMPLOYEE',
  'Employee'
),
(
  '55555555-5555-5555-5555-555555555502',
  '11111111-1111-1111-1111-111111111111',
  'MANAGER',
  'Manager'
),
(
  '55555555-5555-5555-5555-555555555503',
  '11111111-1111-1111-1111-111111111111',
  'HR_ADMIN',
  'HR Admin'
);

INSERT INTO permissions (code, description) VALUES
('employee.self.read', 'Read own profile'),
('leave.self.apply', 'Apply own leave'),
('leave.team.approve', 'Approve team leave'),
('employee.team.read', 'Read direct reports'),
('employee.org.read', 'Read all employees'),
('leave.org.manage', 'Manage all leave'),
('ticket.org.manage', 'Manage all tickets'),
('policy.org.manage', 'Manage policies');

INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM roles r
JOIN permissions p ON (
  (r.code = 'EMPLOYEE' AND p.code IN ('employee.self.read', 'leave.self.apply'))
  OR (
    r.code = 'MANAGER'
    AND p.code IN (
      'employee.self.read',
      'leave.self.apply',
      'leave.team.approve',
      'employee.team.read'
    )
  )
  OR (r.code = 'HR_ADMIN')
)
WHERE r.organization_id = '11111111-1111-1111-1111-111111111111';

INSERT INTO leave_types (id, organization_id, code, name, is_paid, annual_quota) VALUES
(
  '66666666-6666-6666-6666-666666666601',
  '11111111-1111-1111-1111-111111111111',
  'AL',
  'Annual Leave',
  TRUE,
  18
),
(
  '66666666-6666-6666-6666-666666666602',
  '11111111-1111-1111-1111-111111111111',
  'SL',
  'Sick Leave',
  TRUE,
  12
),
(
  '66666666-6666-6666-6666-666666666603',
  '11111111-1111-1111-1111-111111111111',
  'CL',
  'Casual Leave',
  TRUE,
  6
),
(
  '66666666-6666-6666-6666-666666666604',
  '11111111-1111-1111-1111-111111111111',
  'UL',
  'Unpaid Leave',
  FALSE,
  NULL
);

INSERT INTO holiday_calendars (id, organization_id, location_id, name, year) VALUES
(
  '77777777-7777-7777-7777-777777777701',
  '11111111-1111-1111-1111-111111111111',
  '22222222-2222-2222-2222-222222222201',
  'India 2026 - BLR',
  2026
);

INSERT INTO holidays (calendar_id, holiday_date, name) VALUES
('77777777-7777-7777-7777-777777777701', '2026-01-26', 'Republic Day'),
('77777777-7777-7777-7777-777777777701', '2026-03-14', 'Holi'),
('77777777-7777-7777-7777-777777777701', '2026-08-15', 'Independence Day'),
('77777777-7777-7777-7777-777777777701', '2026-10-02', 'Gandhi Jayanti'),
('77777777-7777-7777-7777-777777777701', '2026-10-20', 'Diwali');

INSERT INTO users (id, organization_id, email, password_hash) VALUES
(
  '88888888-8888-8888-8888-888888888801',
  '11111111-1111-1111-1111-111111111111',
  'aisha.khan@novatech.example',
  'dev-hash'
),
(
  '88888888-8888-8888-8888-888888888802',
  '11111111-1111-1111-1111-111111111111',
  'rohan.mehta@novatech.example',
  'dev-hash'
),
(
  '88888888-8888-8888-8888-888888888803',
  '11111111-1111-1111-1111-111111111111',
  'neha.verma@novatech.example',
  'dev-hash'
),
(
  '88888888-8888-8888-8888-888888888804',
  '11111111-1111-1111-1111-111111111111',
  'arjun.patel@novatech.example',
  'dev-hash'
),
(
  '88888888-8888-8888-8888-888888888805',
  '11111111-1111-1111-1111-111111111111',
  'priya.nair@novatech.example',
  'dev-hash'
),
(
  '88888888-8888-8888-8888-888888888806',
  '11111111-1111-1111-1111-111111111111',
  'vikram.singh@novatech.example',
  'dev-hash'
),
(
  '88888888-8888-8888-8888-888888888807',
  '11111111-1111-1111-1111-111111111111',
  'sara.ali@novatech.example',
  'dev-hash'
),
(
  '88888888-8888-8888-8888-888888888808',
  '11111111-1111-1111-1111-111111111111',
  'kabir.das@novatech.example',
  'dev-hash'
);

-- Hierarchy: Aisha (CEO) -> Rohan / Priya / Vikram / Kabir
-- Rohan manages Neha & Arjun; Priya manages Sara
INSERT INTO employees (
  id,
  organization_id,
  user_id,
  employee_code,
  first_name,
  last_name,
  work_email,
  phone,
  date_of_birth,
  gender,
  hire_date,
  employment_status,
  workforce_type,
  location_id,
  department_id,
  job_title_id,
  manager_id
) VALUES
(
  '99999999-9999-9999-9999-999999999901',
  '11111111-1111-1111-1111-111111111111',
  '88888888-8888-8888-8888-888888888801',
  'NT-0001',
  'Aisha',
  'Khan',
  'aisha.khan@novatech.example',
  '+91-9000000001',
  '1984-04-12',
  'female',
  '2018-01-15',
  'active',
  'full_time',
  '22222222-2222-2222-2222-222222222201',
  '33333333-3333-3333-3333-333333333301',
  '44444444-4444-4444-4444-444444444401',
  NULL
),
(
  '99999999-9999-9999-9999-999999999902',
  '11111111-1111-1111-1111-111111111111',
  '88888888-8888-8888-8888-888888888802',
  'NT-0002',
  'Rohan',
  'Mehta',
  'rohan.mehta@novatech.example',
  '+91-9000000002',
  '1988-09-03',
  'male',
  '2019-03-01',
  'active',
  'full_time',
  '22222222-2222-2222-2222-222222222201',
  '33333333-3333-3333-3333-333333333302',
  '44444444-4444-4444-4444-444444444402',
  '99999999-9999-9999-9999-999999999901'
),
(
  '99999999-9999-9999-9999-999999999903',
  '11111111-1111-1111-1111-111111111111',
  '88888888-8888-8888-8888-888888888803',
  'NT-0003',
  'Neha',
  'Verma',
  'neha.verma@novatech.example',
  '+91-9000000003',
  '1994-11-21',
  'female',
  '2021-06-14',
  'active',
  'full_time',
  '22222222-2222-2222-2222-222222222201',
  '33333333-3333-3333-3333-333333333302',
  '44444444-4444-4444-4444-444444444403',
  '99999999-9999-9999-9999-999999999902'
),
(
  '99999999-9999-9999-9999-999999999904',
  '11111111-1111-1111-1111-111111111111',
  '88888888-8888-8888-8888-888888888804',
  'NT-0004',
  'Arjun',
  'Patel',
  'arjun.patel@novatech.example',
  '+91-9000000004',
  '1996-02-08',
  'male',
  '2022-08-01',
  'probation',
  'full_time',
  '22222222-2222-2222-2222-222222222202',
  '33333333-3333-3333-3333-333333333303',
  '44444444-4444-4444-4444-444444444404',
  '99999999-9999-9999-9999-999999999902'
),
(
  '99999999-9999-9999-9999-999999999905',
  '11111111-1111-1111-1111-111111111111',
  '88888888-8888-8888-8888-888888888805',
  'NT-0005',
  'Priya',
  'Nair',
  'priya.nair@novatech.example',
  '+91-9000000005',
  '1990-07-19',
  'female',
  '2020-01-10',
  'active',
  'full_time',
  '22222222-2222-2222-2222-222222222201',
  '33333333-3333-3333-3333-333333333304',
  '44444444-4444-4444-4444-444444444405',
  '99999999-9999-9999-9999-999999999901'
),
(
  '99999999-9999-9999-9999-999999999906',
  '11111111-1111-1111-1111-111111111111',
  '88888888-8888-8888-8888-888888888806',
  'NT-0006',
  'Vikram',
  'Singh',
  'vikram.singh@novatech.example',
  '+91-9000000006',
  '1987-12-01',
  'male',
  '2019-11-18',
  'active',
  'full_time',
  '22222222-2222-2222-2222-222222222203',
  '33333333-3333-3333-3333-333333333305',
  '44444444-4444-4444-4444-444444444407',
  '99999999-9999-9999-9999-999999999901'
),
(
  '99999999-9999-9999-9999-999999999907',
  '11111111-1111-1111-1111-111111111111',
  '88888888-8888-8888-8888-888888888807',
  'NT-0007',
  'Sara',
  'Ali',
  'sara.ali@novatech.example',
  '+91-9000000007',
  '1995-05-30',
  'female',
  '2023-02-20',
  'active',
  'full_time',
  '22222222-2222-2222-2222-222222222201',
  '33333333-3333-3333-3333-333333333304',
  '44444444-4444-4444-4444-444444444406',
  '99999999-9999-9999-9999-999999999905'
),
(
  '99999999-9999-9999-9999-999999999908',
  '11111111-1111-1111-1111-111111111111',
  '88888888-8888-8888-8888-888888888808',
  'NT-0008',
  'Kabir',
  'Das',
  'kabir.das@novatech.example',
  '+91-9000000008',
  '1993-10-11',
  'male',
  '2021-09-05',
  'active',
  'full_time',
  '22222222-2222-2222-2222-222222222203',
  '33333333-3333-3333-3333-333333333306',
  '44444444-4444-4444-4444-444444444408',
  '99999999-9999-9999-9999-999999999901'
);

INSERT INTO user_roles (user_id, role_id)
SELECT u.id, r.id
FROM users u
JOIN roles r
  ON r.organization_id = u.organization_id
 AND r.code = 'EMPLOYEE';

INSERT INTO user_roles (user_id, role_id) VALUES
(
  '88888888-8888-8888-8888-888888888802',
  '55555555-5555-5555-5555-555555555502'
),
(
  '88888888-8888-8888-8888-888888888805',
  '55555555-5555-5555-5555-555555555502'
),
(
  '88888888-8888-8888-8888-888888888805',
  '55555555-5555-5555-5555-555555555503'
),
(
  '88888888-8888-8888-8888-888888888807',
  '55555555-5555-5555-5555-555555555503'
);

INSERT INTO employee_assignments (
  employee_id,
  department_id,
  job_title_id,
  manager_id,
  location_id,
  effective_from,
  is_current
)
SELECT
  id,
  department_id,
  job_title_id,
  manager_id,
  location_id,
  hire_date,
  TRUE
FROM employees;

INSERT INTO employee_contacts (
  employee_id,
  contact_type,
  name,
  relationship,
  phone,
  email
) VALUES
(
  '99999999-9999-9999-9999-999999999903',
  'emergency',
  'Ravi Verma',
  'father',
  '+91-9000000103',
  'ravi.verma@example.com'
),
(
  '99999999-9999-9999-9999-999999999904',
  'emergency',
  'Meera Patel',
  'mother',
  '+91-9000000104',
  'meera.patel@example.com'
);

INSERT INTO leave_balances (employee_id, leave_type_id, year, entitled, used, pending)
SELECT
  e.id,
  lt.id,
  2026,
  COALESCE(lt.annual_quota, 0),
  CASE WHEN e.employee_code IN ('NT-0003', 'NT-0004') THEN 2 ELSE 1 END,
  CASE WHEN e.employee_code = 'NT-0003' THEN 1 ELSE 0 END
FROM employees e
CROSS JOIN leave_types lt
WHERE lt.organization_id = '11111111-1111-1111-1111-111111111111'
  AND lt.code IN ('AL', 'SL', 'CL');

INSERT INTO leave_requests (
  id,
  employee_id,
  leave_type_id,
  start_date,
  end_date,
  days,
  reason,
  status,
  approver_id,
  decided_at
) VALUES
(
  'aaaaaaa1-aaaa-aaaa-aaaa-aaaaaaaaaaa1',
  '99999999-9999-9999-9999-999999999903',
  '66666666-6666-6666-6666-666666666601',
  '2026-09-10',
  '2026-09-12',
  3,
  'Family function',
  'approved',
  '99999999-9999-9999-9999-999999999902',
  '2026-09-01 10:00:00+05:30'
),
(
  'aaaaaaa1-aaaa-aaaa-aaaa-aaaaaaaaaaa2',
  '99999999-9999-9999-9999-999999999903',
  '66666666-6666-6666-6666-666666666603',
  '2026-10-06',
  '2026-10-06',
  1,
  'Personal work',
  'pending',
  '99999999-9999-9999-9999-999999999902',
  NULL
),
(
  'aaaaaaa1-aaaa-aaaa-aaaa-aaaaaaaaaaa3',
  '99999999-9999-9999-9999-999999999904',
  '66666666-6666-6666-6666-666666666602',
  '2026-08-18',
  '2026-08-19',
  2,
  'Fever',
  'approved',
  '99999999-9999-9999-9999-999999999902',
  '2026-08-17 09:30:00+05:30'
),
(
  'aaaaaaa1-aaaa-aaaa-aaaa-aaaaaaaaaaa4',
  '99999999-9999-9999-9999-999999999908',
  '66666666-6666-6666-6666-666666666601',
  '2026-07-01',
  '2026-07-05',
  5,
  'Vacation',
  'rejected',
  '99999999-9999-9999-9999-999999999901',
  '2026-06-20 16:00:00+05:30'
);

INSERT INTO leave_approvals (
  leave_request_id,
  actor_employee_id,
  action,
  comments
) VALUES
(
  'aaaaaaa1-aaaa-aaaa-aaaa-aaaaaaaaaaa1',
  '99999999-9999-9999-9999-999999999903',
  'submitted',
  NULL
),
(
  'aaaaaaa1-aaaa-aaaa-aaaa-aaaaaaaaaaa1',
  '99999999-9999-9999-9999-999999999902',
  'approved',
  'Approved'
),
(
  'aaaaaaa1-aaaa-aaaa-aaaa-aaaaaaaaaaa2',
  '99999999-9999-9999-9999-999999999903',
  'submitted',
  NULL
),
(
  'aaaaaaa1-aaaa-aaaa-aaaa-aaaaaaaaaaa3',
  '99999999-9999-9999-9999-999999999904',
  'submitted',
  NULL
),
(
  'aaaaaaa1-aaaa-aaaa-aaaa-aaaaaaaaaaa3',
  '99999999-9999-9999-9999-999999999902',
  'approved',
  'Get well soon'
),
(
  'aaaaaaa1-aaaa-aaaa-aaaa-aaaaaaaaaaa4',
  '99999999-9999-9999-9999-999999999908',
  'submitted',
  NULL
),
(
  'aaaaaaa1-aaaa-aaaa-aaaa-aaaaaaaaaaa4',
  '99999999-9999-9999-9999-999999999901',
  'rejected',
  'Critical quarter end'
);

INSERT INTO attendance_daily (
  employee_id,
  work_date,
  status,
  check_in,
  check_out,
  worked_minutes
) VALUES
(
  '99999999-9999-9999-9999-999999999903',
  '2026-09-29',
  'present',
  '2026-09-29 09:35:00+05:30',
  '2026-09-29 18:40:00+05:30',
  545
),
(
  '99999999-9999-9999-9999-999999999903',
  '2026-09-30',
  'remote',
  '2026-09-30 09:50:00+05:30',
  '2026-09-30 18:10:00+05:30',
  500
),
(
  '99999999-9999-9999-9999-999999999903',
  '2026-10-01',
  'present',
  '2026-10-01 09:28:00+05:30',
  '2026-10-01 19:05:00+05:30',
  577
),
(
  '99999999-9999-9999-9999-999999999904',
  '2026-09-29',
  'present',
  '2026-09-29 10:05:00+05:30',
  '2026-09-29 19:00:00+05:30',
  535
),
(
  '99999999-9999-9999-9999-999999999904',
  '2026-09-30',
  'half_day',
  '2026-09-30 09:40:00+05:30',
  '2026-09-30 13:30:00+05:30',
  230
);

INSERT INTO tickets (
  organization_id,
  ticket_number,
  requester_employee_id,
  assignee_employee_id,
  category,
  subject,
  description,
  status,
  priority
) VALUES
(
  '11111111-1111-1111-1111-111111111111',
  'TKT-1001',
  '99999999-9999-9999-9999-999999999904',
  '99999999-9999-9999-9999-999999999907',
  'payroll',
  'Payslip missing for August',
  'Unable to download Aug 2026 payslip from portal',
  'in_progress',
  'high'
),
(
  '11111111-1111-1111-1111-111111111111',
  'TKT-1002',
  '99999999-9999-9999-9999-999999999903',
  '99999999-9999-9999-9999-999999999905',
  'leave',
  'Leave balance mismatch',
  'Casual leave balance shows 4 but I used only 1',
  'open',
  'medium'
),
(
  '11111111-1111-1111-1111-111111111111',
  'TKT-1003',
  '99999999-9999-9999-9999-999999999908',
  '99999999-9999-9999-9999-999999999907',
  'it_asset',
  'Need laptop charger replacement',
  'Charger not working after travel',
  'resolved',
  'low'
);

INSERT INTO ticket_comments (ticket_id, author_employee_id, body)
SELECT
  t.id,
  '99999999-9999-9999-9999-999999999907',
  'Looking into payroll export job.'
FROM tickets t
WHERE t.ticket_number = 'TKT-1001';

INSERT INTO policies (
  organization_id,
  code,
  title,
  category,
  content,
  version,
  effective_from
) VALUES
(
  '11111111-1111-1111-1111-111111111111',
  'LEAVE-POL',
  'Leave Policy',
  'leave',
  'Employees are entitled to 18 days annual leave, 12 sick leave, and 6 casual leave per calendar year. Leave of more than 3 consecutive days requires manager approval at least 7 days in advance except medical emergencies.',
  '1.0',
  '2026-01-01'
),
(
  '11111111-1111-1111-1111-111111111111',
  'WFH-POL',
  'Remote Work Policy',
  'attendance',
  'Employees may work remotely up to 2 days per week with manager approval. Core hours are 11:00–16:00 IST.',
  '1.0',
  '2026-01-01'
),
(
  '11111111-1111-1111-1111-111111111111',
  'CONDUCT',
  'Code of Conduct',
  'hr',
  'All employees must maintain professional conduct, protect confidential information, and report harassment through HR channels.',
  '1.0',
  '2026-01-01'
);

INSERT INTO audit_logs (
  organization_id,
  actor_user_id,
  entity_type,
  entity_id,
  action,
  after_data
) VALUES
(
  '11111111-1111-1111-1111-111111111111',
  '88888888-8888-8888-8888-888888888802',
  'leave_request',
  'aaaaaaa1-aaaa-aaaa-aaaa-aaaaaaaaaaa1',
  'approved',
  '{"status":"approved","days":3}'::jsonb
);
