import mysql.connector
import json

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'job_tracker'
}

def get_db():
    return mysql.connector.connect(**DB_CONFIG)

def get_all(table):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(f'SELECT * FROM {table}')
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_one(table, id_col, id_val):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(f'SELECT * FROM {table} WHERE {id_col} = %s', (id_val,))
    row = cursor.fetchone()
    conn.close()
    return row

def delete_one(table, id_col, id_val):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(f'DELETE FROM {table} WHERE {id_col} = %s', (id_val,))
    conn.commit()
    conn.close()

def delete_company(company_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        DELETE a FROM applications a
        INNER JOIN jobs j ON a.job_id = j.job_id
        WHERE j.company_id = %s
    ''', (company_id,))
    cursor.execute('DELETE FROM jobs WHERE company_id = %s', (company_id,))
    cursor.execute('DELETE FROM contacts WHERE company_id = %s', (company_id,))
    cursor.execute('DELETE FROM companies WHERE company_id = %s', (company_id,))
    conn.commit()
    conn.close()

def delete_job(job_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM applications WHERE job_id = %s', (job_id,))
    cursor.execute('DELETE FROM jobs WHERE job_id = %s', (job_id,))
    conn.commit()
    conn.close()

def get_companies():
    return get_all('companies')

def get_company(company_id):
    return get_one('companies', 'company_id', company_id)

def add_company(data):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO companies (company_name, industry, website, city, state, notes) VALUES (%s, %s, %s, %s, %s, %s)',
        (data['company_name'], data['industry'], data['website'], data['city'], data['state'], data['notes'])
    )
    conn.commit()
    conn.close()

def update_company(company_id, data):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE companies SET company_name=%s, industry=%s, website=%s, city=%s, state=%s, notes=%s WHERE company_id=%s',
        (data['company_name'], data['industry'], data['website'], data['city'], data['state'], data['notes'], company_id)
    )
    conn.commit()
    conn.close()

def get_jobs():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT j.*, c.company_name
        FROM jobs j
        LEFT JOIN companies c ON j.company_id = c.company_id
    ''')
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_job(job_id):
    return get_one('jobs', 'job_id', job_id)

def add_job(data):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        '''INSERT INTO jobs (company_id, job_title, job_type, salary_min, salary_max, job_url, date_posted, requirements)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s)''',
        (data['company_id'], data['job_title'], data['job_type'], data['salary_min'],
         data['salary_max'], data['job_url'], data['date_posted'], data['requirements'])
    )
    conn.commit()
    conn.close()

def update_job(job_id, data):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        '''UPDATE jobs SET company_id=%s, job_title=%s, job_type=%s, salary_min=%s, salary_max=%s,
           job_url=%s, date_posted=%s, requirements=%s WHERE job_id=%s''',
        (data['company_id'], data['job_title'], data['job_type'], data['salary_min'],
         data['salary_max'], data['job_url'], data['date_posted'], data['requirements'], job_id)
    )
    conn.commit()
    conn.close()

def get_applications():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT a.*, j.job_title, c.company_name
        FROM applications a
        LEFT JOIN jobs j ON a.job_id = j.job_id
        LEFT JOIN companies c ON j.company_id = c.company_id
    ''')
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_application(application_id):
    return get_one('applications', 'application_id', application_id)

def add_application(data):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        '''INSERT INTO applications (job_id, application_date, status, resume_version, cover_letter_sent, interview_data)
           VALUES (%s, %s, %s, %s, %s, %s)''',
        (data['job_id'], data['application_date'], data['status'], data['resume_version'],
         data['cover_letter_sent'], data['interview_data'])
    )
    conn.commit()
    conn.close()

def update_application(application_id, data):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        '''UPDATE applications SET job_id=%s, application_date=%s, status=%s, resume_version=%s,
           cover_letter_sent=%s, interview_data=%s WHERE application_id=%s''',
        (data['job_id'], data['application_date'], data['status'], data['resume_version'],
         data['cover_letter_sent'], data['interview_data'], application_id)
    )
    conn.commit()
    conn.close()

def get_contacts():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT ct.*, c.company_name
        FROM contacts ct
        LEFT JOIN companies c ON ct.company_id = c.company_id
    ''')
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_contact(contact_id):
    return get_one('contacts', 'contact_id', contact_id)

def add_contact(data):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        '''INSERT INTO contacts (company_id, contact_name, title, email, phone, linkedin_url, notes)
           VALUES (%s, %s, %s, %s, %s, %s, %s)''',
        (data['company_id'], data['contact_name'], data['title'], data['email'],
         data['phone'], data['linkedin_url'], data['notes'])
    )
    conn.commit()
    conn.close()

def update_contact(contact_id, data):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        '''UPDATE contacts SET company_id=%s, contact_name=%s, title=%s, email=%s, phone=%s,
           linkedin_url=%s, notes=%s WHERE contact_id=%s''',
        (data['company_id'], data['contact_name'], data['title'], data['email'],
         data['phone'], data['linkedin_url'], data['notes'], contact_id)
    )
    conn.commit()
    conn.close()

def get_stats():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT COUNT(*) as count FROM companies')
    companies = cursor.fetchone()['count']
    cursor.execute('SELECT COUNT(*) as count FROM jobs')
    jobs = cursor.fetchone()['count']
    cursor.execute('SELECT COUNT(*) as count FROM applications')
    applications = cursor.fetchone()['count']
    cursor.execute('SELECT COUNT(*) as count FROM contacts')
    contacts = cursor.fetchone()['count']
    cursor.execute('SELECT status, COUNT(*) as count FROM applications GROUP BY status')
    by_status = cursor.fetchall()
    conn.close()
    return {
        'companies': companies,
        'jobs': jobs,
        'applications': applications,
        'contacts': contacts,
        'by_status': by_status
    }

def job_skills(req):
    if not req:
        return []
    if isinstance(req, str):
        req = json.loads(req)
    return [str(s).strip() for s in req if str(s).strip()]

def match_jobs(skills):
    user_skills = {s.strip().lower() for s in skills if s.strip()}
    if not user_skills:
        return []
    results = []
    for job in get_jobs():
        required = job_skills(job.get('requirements'))
        if not required:
            continue
        matched = [s for s in required if s.lower() in user_skills]
        missing = [s for s in required if s.lower() not in user_skills]
        results.append({
            'job': job,
            'percent': round(len(matched) / len(required) * 100),
            'matched': len(matched),
            'total': len(required),
            'missing': missing
        })
    results.sort(key=lambda x: x['percent'], reverse=True)
    return results