from flask import Flask, render_template, request, redirect, url_for, flash
import json
import database as db

app = Flask(__name__)
app.secret_key = 'job_tracker_secret'

JOB_TYPES = ['Full-time', 'Part-time', 'Contract', 'Internship']
STATUSES = ['Applied', 'Screening', 'Interview', 'Offer', 'Rejected', 'Withdrawn']

def to_int(value):
    if value is None or value == '':
        return None
    return int(value)

def skills_to_json(text):
    skills = [s.strip() for s in text.split(',') if s.strip()]
    return json.dumps(skills)

def json_to_skills(value):
    if not value:
        return ''
    if isinstance(value, str):
        value = json.loads(value)
    return ', '.join(value)

def interview_notes_from_db(data):
    if not data:
        return ''
    if isinstance(data, str):
        data = json.loads(data)
    return data.get('notes', '')

def company_form():
    return {
        'company_name': request.form.get('company_name', '').strip(),
        'industry': request.form.get('industry', ''),
        'website': request.form.get('website', ''),
        'city': request.form.get('city', ''),
        'state': request.form.get('state', ''),
        'notes': request.form.get('notes', '')
    }

def job_form():
    return {
        'company_id': to_int(request.form.get('company_id')),
        'job_title': request.form.get('job_title', '').strip(),
        'job_type': request.form.get('job_type') or None,
        'salary_min': to_int(request.form.get('salary_min')),
        'salary_max': to_int(request.form.get('salary_max')),
        'job_url': request.form.get('job_url', ''),
        'date_posted': request.form.get('date_posted') or None,
        'requirements': skills_to_json(request.form.get('requirements', '')),
        'requirements_text': request.form.get('requirements', '')
    }

def application_form():
    notes = request.form.get('interview_notes', '').strip()
    return {
        'job_id': to_int(request.form.get('job_id')),
        'application_date': request.form.get('application_date'),
        'status': request.form.get('status') or 'Applied',
        'resume_version': request.form.get('resume_version', ''),
        'cover_letter_sent': 1 if request.form.get('cover_letter_sent') else 0,
        'interview_data': json.dumps({'notes': notes}) if notes else None,
        'interview_notes': notes
    }

def contact_form():
    return {
        'company_id': to_int(request.form.get('company_id')),
        'contact_name': request.form.get('contact_name', '').strip(),
        'title': request.form.get('title', ''),
        'email': request.form.get('email', ''),
        'phone': request.form.get('phone', ''),
        'linkedin_url': request.form.get('linkedin_url', ''),
        'notes': request.form.get('notes', '')
    }

@app.route('/')
def dashboard():
    return render_template('dashboard.html', stats=db.get_stats())

@app.route('/companies')
def companies():
    return render_template('companies.html', companies=db.get_companies())

@app.route('/companies/add', methods=['GET', 'POST'])
def add_company():
    if request.method == 'POST':
        data = company_form()
        if not data['company_name']:
            flash('Company name is required.')
            return render_template('companies.html', companies=db.get_companies(), company=data, action='Add')
        db.add_company(data)
        return redirect(url_for('companies'))
    return render_template('companies.html', companies=db.get_companies(), company=None, action='Add')

@app.route('/companies/edit/<int:company_id>', methods=['GET', 'POST'])
def edit_company(company_id):
    company = db.get_company(company_id)
    if not company:
        return redirect(url_for('companies'))
    if request.method == 'POST':
        data = company_form()
        if not data['company_name']:
            flash('Company name is required.')
            return render_template('companies.html', companies=db.get_companies(), company=data, action='Edit')
        db.update_company(company_id, data)
        return redirect(url_for('companies'))
    return render_template('companies.html', companies=db.get_companies(), company=company, action='Edit')

@app.route('/companies/delete/<int:company_id>')
def delete_company(company_id):
    db.delete_company(company_id)
    return redirect(url_for('companies'))

@app.route('/jobs')
def jobs():
    return render_template('jobs.html', jobs=db.get_jobs())

@app.route('/jobs/add', methods=['GET', 'POST'])
def add_job():
    company_list = db.get_companies()
    if request.method == 'POST':
        data = job_form()
        if not data['job_title'] or not data['company_id']:
            flash('Job title and company are required.')
            return render_template('jobs.html', jobs=db.get_jobs(), job=data, company_list=company_list, job_types=JOB_TYPES, action='Add')
        db.add_job(data)
        return redirect(url_for('jobs'))
    return render_template('jobs.html', jobs=db.get_jobs(), job=None, company_list=company_list, job_types=JOB_TYPES, action='Add')

@app.route('/jobs/edit/<int:job_id>', methods=['GET', 'POST'])
def edit_job(job_id):
    job = db.get_job(job_id)
    company_list = db.get_companies()
    if not job:
        return redirect(url_for('jobs'))
    if request.method == 'POST':
        data = job_form()
        if not data['job_title'] or not data['company_id']:
            flash('Job title and company are required.')
            return render_template('jobs.html', jobs=db.get_jobs(), job=data, company_list=company_list, job_types=JOB_TYPES, action='Edit')
        db.update_job(job_id, data)
        return redirect(url_for('jobs'))
    job['requirements_text'] = json_to_skills(job.get('requirements'))
    return render_template('jobs.html', jobs=db.get_jobs(), job=job, company_list=company_list, job_types=JOB_TYPES, action='Edit')

@app.route('/jobs/delete/<int:job_id>')
def delete_job(job_id):
    db.delete_job(job_id)
    return redirect(url_for('jobs'))

@app.route('/applications')
def applications():
    return render_template('applications.html', applications=db.get_applications())

@app.route('/applications/add', methods=['GET', 'POST'])
def add_application():
    job_list = db.get_jobs()
    if request.method == 'POST':
        data = application_form()
        if not data['job_id'] or not data['application_date']:
            flash('Job and application date are required.')
            return render_template('applications.html', applications=db.get_applications(), application=data, job_list=job_list, statuses=STATUSES, action='Add')
        db.add_application(data)
        return redirect(url_for('applications'))
    return render_template('applications.html', applications=db.get_applications(), application=None, job_list=job_list, statuses=STATUSES, action='Add')

@app.route('/applications/edit/<int:application_id>', methods=['GET', 'POST'])
def edit_application(application_id):
    application = db.get_application(application_id)
    job_list = db.get_jobs()
    if not application:
        return redirect(url_for('applications'))
    if request.method == 'POST':
        data = application_form()
        if not data['job_id'] or not data['application_date']:
            flash('Job and application date are required.')
            return render_template('applications.html', applications=db.get_applications(), application=data, job_list=job_list, statuses=STATUSES, action='Edit')
        db.update_application(application_id, data)
        return redirect(url_for('applications'))
    application['interview_notes'] = interview_notes_from_db(application.get('interview_data'))
    return render_template('applications.html', applications=db.get_applications(), application=application, job_list=job_list, statuses=STATUSES, action='Edit')

@app.route('/applications/delete/<int:application_id>')
def delete_application(application_id):
    db.delete_one('applications', 'application_id', application_id)
    return redirect(url_for('applications'))

@app.route('/contacts')
def contacts():
    return render_template('contacts.html', contacts=db.get_contacts())

@app.route('/contacts/add', methods=['GET', 'POST'])
def add_contact():
    company_list = db.get_companies()
    if request.method == 'POST':
        data = contact_form()
        if not data['contact_name'] or not data['company_id']:
            flash('Contact name and company are required.')
            return render_template('contacts.html', contacts=db.get_contacts(), contact=data, company_list=company_list, action='Add')
        db.add_contact(data)
        return redirect(url_for('contacts'))
    return render_template('contacts.html', contacts=db.get_contacts(), contact=None, company_list=company_list, action='Add')

@app.route('/contacts/edit/<int:contact_id>', methods=['GET', 'POST'])
def edit_contact(contact_id):
    contact = db.get_contact(contact_id)
    company_list = db.get_companies()
    if not contact:
        return redirect(url_for('contacts'))
    if request.method == 'POST':
        data = contact_form()
        if not data['contact_name'] or not data['company_id']:
            flash('Contact name and company are required.')
            return render_template('contacts.html', contacts=db.get_contacts(), contact=data, company_list=company_list, action='Edit')
        db.update_contact(contact_id, data)
        return redirect(url_for('contacts'))
    return render_template('contacts.html', contacts=db.get_contacts(), contact=contact, company_list=company_list, action='Edit')

@app.route('/contacts/delete/<int:contact_id>')
def delete_contact(contact_id):
    db.delete_one('contacts', 'contact_id', contact_id)
    return redirect(url_for('contacts'))

@app.route('/job-match', methods=['GET', 'POST'])
def job_match():
    results = []
    skills_text = ''
    if request.method == 'POST':
        skills_text = request.form.get('skills', '')
        skills = [s.strip() for s in skills_text.split(',')]
        results = db.match_jobs(skills)
    return render_template('job_match.html', results=results, skills_text=skills_text)

if __name__ == '__main__':
    app.run(debug=True)
