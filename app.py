import os
import threading
from flask import Flask, render_template, jsonify, request, redirect, url_for
from apscheduler.schedulers.background import BackgroundScheduler
from scraper.scraper import (
    init_db, get_notifications, get_vacancies,
    get_all_notifications, run_all_scrapers, get_scrape_logs
)

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.secret_key = os.environ.get('SECRET_KEY', 'examguideindia2025')

EXAM_CONFIG = {
    'wbcs': {
        'key': 'wbcs',
        'name': 'WBCS',
        'full_name': 'West Bengal Civil Service',
        'icon': '🏛️',
        'color': '#1d4ed8',
        'light': '#eff6ff',
        'official_url': 'https://psc.wb.gov.in',
        'apply_link': 'https://psc.wb.gov.in/content/wbcs-exam',
        'result_link': 'https://psc.wb.gov.in/content/wbcs-exam',
        'category': 'wbcs',
        'pattern': [
            {'stage': 'Preliminary', 'subjects': 'General Studies (MCQ)', 'questions': 200, 'marks': 200, 'duration': '2.5 hrs', 'negative': '0.25'},
            {'stage': 'Mains', 'subjects': '6 Compulsory + Optional Papers', 'questions': '—', 'marks': 900, 'duration': '3 hrs each', 'negative': 'No'},
            {'stage': 'Interview', 'subjects': 'Personality Test', 'questions': '—', 'marks': 100, 'duration': '—', 'negative': '—'},
        ],
        'syllabus': [
            'English Composition & Language',
            'General Science & Environment',
            'Indian History, Culture & Heritage',
            'Geography of India & West Bengal',
            'Indian Economy & Planning',
            'Indian Polity & Constitution',
            'Current Affairs & General Knowledge',
            'Mathematics & Mental Ability',
            'Bengali / Hindi / Urdu / Nepali / Santhali',
        ],
        'sub_pages': [],
    },
    'psc-misc': {
        'key': 'psc-misc',
        'name': 'PSC MISC',
        'full_name': 'WBPSC Miscellaneous Services',
        'icon': '⚖️',
        'color': '#15803d',
        'light': '#f0fdf4',
        'official_url': 'https://psc.wb.gov.in',
        'apply_link': 'https://psc.wb.gov.in/content/misc-exam',
        'result_link': 'https://psc.wb.gov.in/content/misc-exam',
        'category': 'psc',
        'pattern': [
            {'stage': 'Preliminary', 'subjects': 'General Studies & Arithmetic', 'questions': 200, 'marks': 200, 'duration': '2.5 hrs', 'negative': '0.25'},
            {'stage': 'Mains', 'subjects': 'General Studies & English/Bengali', 'questions': '—', 'marks': 400, 'duration': '3 hrs each', 'negative': 'No'},
            {'stage': 'Interview', 'subjects': 'Viva-Voce', 'questions': '—', 'marks': 50, 'duration': '—', 'negative': '—'},
        ],
        'syllabus': [
            'General Studies (History, Geography, Polity, Science)',
            'Current Affairs & General Knowledge',
            'Arithmetic & Higher Mathematics',
            'English Composition & Language',
            'Bengali Composition & Language',
            'Reasoning & Mental Ability',
        ],
        'sub_pages': [],
    },
    'psc-clerkship': {
        'key': 'psc-clerkship',
        'name': 'PSC Clerkship',
        'full_name': 'WBPSC Clerkship Examination',
        'icon': '📋',
        'color': '#0d9488',
        'light': '#f0fdfa',
        'official_url': 'https://psc.wb.gov.in',
        'apply_link': 'https://psc.wb.gov.in/content/clerkship-exam',
        'result_link': 'https://psc.wb.gov.in/content/clerkship-exam',
        'category': 'psc',
        'pattern': [
            {'stage': 'Written Test', 'subjects': 'General Studies + Arithmetic + Language', 'questions': 100, 'marks': 100, 'duration': '90 min', 'negative': '0.25'},
            {'stage': 'Personality Test', 'subjects': 'Interview', 'questions': '—', 'marks': 10, 'duration': '—', 'negative': '—'},
        ],
        'syllabus': [
            'General Studies (Class X level)',
            'Arithmetic & Numerical Ability',
            'English Language & Comprehension',
            'Bengali / Hindi Language',
            'General Knowledge & Current Affairs',
        ],
        'sub_pages': [],
    },
    'ssc-cgl': {
        'key': 'ssc-cgl',
        'name': 'SSC CGL',
        'full_name': 'Staff Selection Commission – Combined Graduate Level',
        'icon': '🎖️',
        'color': '#7c3aed',
        'light': '#f5f3ff',
        'official_url': 'https://ssc.gov.in',
        'apply_link': 'https://ssc.gov.in/candidate-corner',
        'result_link': 'https://ssc.gov.in/notice-board',
        'category': 'ssc',
        'pattern': [
            {'stage': 'Tier-I (CBE)', 'subjects': 'GI & Reasoning, GK, Quant, English', 'questions': 100, 'marks': 200, 'duration': '60 min', 'negative': '0.50'},
            {'stage': 'Tier-II (CBE)', 'subjects': 'Paper-I (Maths+Reasoning+English), Paper-II/III (optional)', 'questions': 150, 'marks': 300, 'duration': '2 hrs 15 min', 'negative': '1'},
            {'stage': 'Tier-III', 'subjects': 'Descriptive Paper (Hindi/English)', 'questions': '—', 'marks': 100, 'duration': '60 min', 'negative': 'No'},
            {'stage': 'Tier-IV', 'subjects': 'DEST / CPT (Skill Test)', 'questions': '—', 'marks': 'Qualifying', 'duration': '15 min', 'negative': '—'},
        ],
        'syllabus': [
            'General Intelligence & Reasoning (Analogy, Classification, Series, Coding-Decoding)',
            'General Awareness (Current Affairs, Indian History, Geography, Economy)',
            'Quantitative Aptitude (Arithmetic, Algebra, Trigonometry, Geometry, Statistics)',
            'English Comprehension (Reading, Cloze Test, Error Detection, Vocab)',
            'Computer Knowledge (MS Office, Internet Basics)',
            'Statistics (for JSO post – Tier-II Paper-II)',
        ],
        'sub_pages': [],
    },
    'ssc-chsl': {
        'key': 'ssc-chsl',
        'name': 'SSC CHSL',
        'full_name': 'Staff Selection Commission – Combined Higher Secondary Level',
        'icon': '📑',
        'color': '#b45309',
        'light': '#fffbeb',
        'official_url': 'https://ssc.gov.in',
        'apply_link': 'https://ssc.gov.in/candidate-corner',
        'result_link': 'https://ssc.gov.in/notice-board',
        'category': 'ssc',
        'pattern': [
            {'stage': 'Tier-I (CBE)', 'subjects': 'GI & Reasoning, GK, Quant, English', 'questions': 100, 'marks': 200, 'duration': '60 min', 'negative': '0.50'},
            {'stage': 'Tier-II (Descriptive)', 'subjects': 'Essay + Letter Writing (Hindi/English)', 'questions': '—', 'marks': 100, 'duration': '60 min', 'negative': 'No'},
            {'stage': 'Tier-III', 'subjects': 'Skill / Typing Test', 'questions': '—', 'marks': 'Qualifying', 'duration': '15 min', 'negative': '—'},
        ],
        'syllabus': [
            'General Intelligence & Reasoning',
            'English Language (Basic Comprehension, Vocabulary)',
            'Quantitative Aptitude (Arithmetic, Data Interpretation)',
            'General Awareness (Current Events, History, Geography, Science)',
        ],
        'sub_pages': [],
    },
    'ssc-gd': {
        'key': 'ssc-gd',
        'name': 'SSC GD',
        'full_name': 'SSC GD Constable (CAPFs / NIA / SSF)',
        'icon': '🛡️',
        'color': '#dc2626',
        'light': '#fef2f2',
        'official_url': 'https://ssc.gov.in',
        'apply_link': 'https://ssc.gov.in/candidate-corner',
        'result_link': 'https://ssc.gov.in/notice-board',
        'category': 'ssc',
        'pattern': [
            {'stage': 'CBE (Online)', 'subjects': 'GI & Reasoning, GK, Maths, English/Hindi', 'questions': 80, 'marks': 160, 'duration': '60 min', 'negative': '0.50'},
            {'stage': 'PET / PST', 'subjects': 'Physical Efficiency Test & Physical Standard Test', 'questions': '—', 'marks': 'Qualifying', 'duration': '—', 'negative': '—'},
            {'stage': 'Medical Exam', 'subjects': 'Medical Fitness', 'questions': '—', 'marks': 'Qualifying', 'duration': '—', 'negative': '—'},
            {'stage': 'Document Verification', 'subjects': '—', 'questions': '—', 'marks': '—', 'duration': '—', 'negative': '—'},
        ],
        'syllabus': [
            'General Intelligence & Reasoning (Analogies, Spatial Visualization, Patterns)',
            'General Knowledge & General Awareness (Current Events, Indian Polity, History)',
            'Elementary Mathematics (Number Systems, Decimals, Percentages, Mensuration)',
            'English / Hindi Language (Comprehension, Fill in the Blanks, Error Detection)',
            'Physical Standards: Height, Chest, Weight as per CAPFs norms',
        ],
        'sub_pages': [],
    },
    'ssc-mts': {
        'key': 'ssc-mts',
        'name': 'SSC MTS',
        'full_name': 'SSC Multi Tasking Staff & Havaldar',
        'icon': '📝',
        'color': '#0369a1',
        'light': '#f0f9ff',
        'official_url': 'https://ssc.gov.in',
        'apply_link': 'https://ssc.gov.in/candidate-corner',
        'result_link': 'https://ssc.gov.in/notice-board',
        'category': 'ssc',
        'pattern': [
            {'stage': 'Session-I (Paper-I)', 'subjects': 'Numerical & Mathematical Ability, Reasoning & Problem Solving', 'questions': 60, 'marks': 60, 'duration': '45 min', 'negative': '1'},
            {'stage': 'Session-II (Paper-I)', 'subjects': 'General Awareness, English Language & Comprehension', 'questions': 75, 'marks': 75, 'duration': '45 min', 'negative': '1'},
            {'stage': 'Paper-II', 'subjects': 'Descriptive (Short Essay + Letter in Hindi/English)', 'questions': '—', 'marks': 50, 'duration': '45 min', 'negative': 'No'},
        ],
        'syllabus': [
            'Numerical & Mathematical Ability (Class VIII level)',
            'Reasoning & Problem Solving (Pattern Recognition, Logical Thinking)',
            'General Awareness (History, Geography, Polity, Science & Technology)',
            'English Language & Comprehension',
            'Short Essay & Letter Writing (Paper-II)',
        ],
        'sub_pages': [],
    },
    'railway-ntpc-graduate': {
        'key': 'railway-ntpc-graduate',
        'name': 'NTPC Graduate',
        'full_name': 'RRB NTPC – Graduate Posts',
        'icon': '🚆',
        'color': '#ea580c',
        'light': '#fff7ed',
        'official_url': 'https://rrbapply.gov.in',
        'apply_link': 'https://rrbapply.gov.in',
        'result_link': 'https://rrbapply.gov.in',
        'category': 'railway',
        'pattern': [
            {'stage': 'CBT-1', 'subjects': 'Mathematics, General Intelligence & Reasoning, General Awareness', 'questions': 100, 'marks': 100, 'duration': '90 min', 'negative': '1/3'},
            {'stage': 'CBT-2', 'subjects': 'Mathematics, General Intelligence, General Awareness, General Science', 'questions': 120, 'marks': 120, 'duration': '90 min', 'negative': '1/3'},
            {'stage': 'Skill Test / CBAT', 'subjects': 'Role-specific test (e.g., Typing / Aptitude)', 'questions': '—', 'marks': 'Qualifying', 'duration': '—', 'negative': '—'},
            {'stage': 'Document Verification & Medical', 'subjects': '—', 'questions': '—', 'marks': '—', 'duration': '—', 'negative': '—'},
        ],
        'syllabus': [
            'Mathematics (Number System, HCF/LCM, Ratio, Percentage, Time-Speed-Distance, SI/CI, Geometry)',
            'General Intelligence & Reasoning (Analogies, Alphabetical Series, Coding, Puzzles)',
            'General Awareness (Current Affairs, Indian Railways, Science & Technology, History)',
            'General Science (Physics, Chemistry, Life Science – Class X level)',
            'Computer & MS-Office Basics',
        ],
        'sub_pages': [],
    },
    'railway-ntpc-ug': {
        'key': 'railway-ntpc-ug',
        'name': 'NTPC UG',
        'full_name': 'RRB NTPC – Under-Graduate Posts',
        'icon': '🚉',
        'color': '#d97706',
        'light': '#fffbeb',
        'official_url': 'https://rrbapply.gov.in',
        'apply_link': 'https://rrbapply.gov.in',
        'result_link': 'https://rrbapply.gov.in',
        'category': 'railway',
        'pattern': [
            {'stage': 'CBT-1', 'subjects': 'Mathematics, Reasoning, General Awareness', 'questions': 100, 'marks': 100, 'duration': '90 min', 'negative': '1/3'},
            {'stage': 'CBT-2', 'subjects': 'Mathematics, Reasoning, General Awareness, General Science', 'questions': 120, 'marks': 120, 'duration': '90 min', 'negative': '1/3'},
            {'stage': 'Typing Test', 'subjects': 'English 30 WPM / Hindi 25 WPM', 'questions': '—', 'marks': 'Qualifying', 'duration': '10 min', 'negative': '—'},
        ],
        'syllabus': [
            'Mathematics (Arithmetic – Class X level)',
            'General Intelligence & Reasoning',
            'General Awareness & Current Affairs',
            'General Science (Physics, Chemistry, Biology – Class X)',
            'English Language Basics',
        ],
        'sub_pages': [],
    },
    'railway-group-d': {
        'key': 'railway-group-d',
        'name': 'Railway Group D',
        'full_name': 'RRB Group D – Level 1 Posts',
        'icon': '⚙️',
        'color': '#16a34a',
        'light': '#f0fdf4',
        'official_url': 'https://rrbapply.gov.in',
        'apply_link': 'https://rrbapply.gov.in',
        'result_link': 'https://rrbapply.gov.in',
        'category': 'railway',
        'pattern': [
            {'stage': 'CBT', 'subjects': 'Mathematics, GI & Reasoning, General Science, General Awareness', 'questions': 100, 'marks': 100, 'duration': '90 min', 'negative': '1/3'},
            {'stage': 'PET', 'subjects': 'Physical Efficiency Test (Running, Weight Lift)', 'questions': '—', 'marks': 'Qualifying', 'duration': '—', 'negative': '—'},
            {'stage': 'Medical', 'subjects': 'Vision & General Fitness', 'questions': '—', 'marks': 'Qualifying', 'duration': '—', 'negative': '—'},
        ],
        'syllabus': [
            'Mathematics (Number System, BODMAS, Fractions, Decimals, Ratio, Percentages)',
            'General Intelligence & Reasoning (Analogies, Classification, Spatial Reasoning)',
            'General Science (Physics, Chemistry, Life Sciences – Class X CBSE)',
            'General Awareness & Current Affairs (India & International)',
            'Physical: 1000m run in 4 min 15 sec (Male) / 5 min 40 sec (Female); 35 kg weight lift (Male) / 20 kg (Female)',
        ],
        'sub_pages': [],
    },
    'railway-technician': {
        'key': 'railway-technician',
        'name': 'RRB Technician',
        'full_name': 'RRB Technician – Grade-1 Signal & Other Posts',
        'icon': '🔧',
        'color': '#0891b2',
        'light': '#ecfeff',
        'official_url': 'https://rrbapply.gov.in',
        'apply_link': 'https://rrbapply.gov.in',
        'result_link': 'https://rrbapply.gov.in',
        'category': 'railway',
        'pattern': [
            {'stage': 'CBT', 'subjects': 'Mathematics, GI & Reasoning, General Science, General Awareness, Technical Ability', 'questions': 100, 'marks': 100, 'duration': '90 min', 'negative': '1/3'},
            {'stage': 'Document Verification', 'subjects': '—', 'questions': '—', 'marks': '—', 'duration': '—', 'negative': '—'},
            {'stage': 'Medical', 'subjects': 'Medical Fitness (Vision Standards)', 'questions': '—', 'marks': 'Qualifying', 'duration': '—', 'negative': '—'},
        ],
        'syllabus': [
            'Mathematics (Algebra, Geometry, Trigonometry, Statistics)',
            'General Intelligence & Reasoning',
            'General Science (Physics, Chemistry – Class XII level)',
            'General Awareness & Current Affairs',
            'Technical Ability: Relevant to ITI trade / Engineering Diploma (Electrical/Electronics/Mechanical/Signal)',
        ],
        'sub_pages': [],
    },
    'police': {
        'key': 'police',
        'name': 'WB Police',
        'full_name': 'West Bengal Police – SI / Constable Recruitment',
        'icon': '👮',
        'color': '#be123c',
        'light': '#fff1f2',
        'official_url': 'https://wbpolice.gov.in',
        'apply_link': 'https://prb.wb.gov.in',
        'result_link': 'https://wbpolice.gov.in/recruitment.aspx',
        'category': 'police',
        'pattern': [
            {'stage': 'Preliminary Written Test', 'subjects': 'General Studies, Arithmetic, Reasoning, Language', 'questions': 100, 'marks': 100, 'duration': '60 min', 'negative': '0.25'},
            {'stage': 'Physical Measurement Test (PMT)', 'subjects': 'Height, Chest (Constable only)', 'questions': '—', 'marks': 'Qualifying', 'duration': '—', 'negative': '—'},
            {'stage': 'Physical Efficiency Test (PET)', 'subjects': 'Running, Long Jump, High Jump', 'questions': '—', 'marks': 'Qualifying', 'duration': '—', 'negative': '—'},
            {'stage': 'Final Written Test', 'subjects': 'GK, Reasoning, Maths, Bengali/English, Computer', 'questions': 85, 'marks': 85, 'duration': '60 min', 'negative': 'No'},
            {'stage': 'Interview / Personality Test (SI only)', 'subjects': '—', 'questions': '—', 'marks': 15, 'duration': '—', 'negative': '—'},
        ],
        'syllabus': [
            'General Studies (History of India & WB, Geography, Indian Polity)',
            'Current Affairs & General Knowledge',
            'Arithmetic (Class X level – Percentage, Ratio, Time-Speed-Distance)',
            'Reasoning & Mental Ability',
            'Bengali & English Language',
            'Computer Basics & Applications',
            'Physical: 1600m run, Long Jump, High Jump (standards vary by post)',
        ],
        'sub_pages': [],
    },
}

CATEGORY_CONFIG = {
    'wbcs': {
        'name': 'WBCS',
        'full_name': 'West Bengal Civil Service',
        'icon': '🏛️',
        'color': '#1d4ed8',
        'light': '#eff6ff',
        'desc': 'The most prestigious state civil service exam in West Bengal, conducted by the Public Service Commission.',
        'exams': ['wbcs'],
    },
    'psc': {
        'name': 'PSC',
        'full_name': 'West Bengal Public Service Commission',
        'icon': '⚖️',
        'color': '#15803d',
        'light': '#f0fdf4',
        'desc': 'Exams conducted by WBPSC for various Group B and C posts across West Bengal government departments.',
        'exams': ['psc-misc', 'psc-clerkship'],
    },
    'ssc': {
        'name': 'SSC',
        'full_name': 'Staff Selection Commission',
        'icon': '🎖️',
        'color': '#7c3aed',
        'light': '#f5f3ff',
        'desc': 'National-level exams by SSC for recruitment to Group B, C and D posts in Central Government departments.',
        'exams': ['ssc-cgl', 'ssc-chsl', 'ssc-gd', 'ssc-mts'],
    },
    'railway': {
        'name': 'Railway',
        'full_name': 'Railway Recruitment Board',
        'icon': '🚆',
        'color': '#ea580c',
        'light': '#fff7ed',
        'desc': 'RRB recruitment for various posts in Indian Railways – the largest employer in India.',
        'exams': ['railway-ntpc-graduate', 'railway-ntpc-ug', 'railway-group-d', 'railway-technician'],
    },
    'police': {
        'name': 'Police',
        'full_name': 'West Bengal Police Recruitment Board',
        'icon': '👮',
        'color': '#be123c',
        'light': '#fff1f2',
        'desc': 'WB Police recruitment for SI, Constable, and other posts conducted by Police Recruitment Board WB.',
        'exams': ['police'],
    },
    'notes': {
        'name': 'Notes',
        'full_name': 'Study Notes & Materials',
        'icon': '📚',
        'color': '#0d9488',
        'light': '#f0fdfa',
        'desc': '',
        'exams': [],
    },
}


@app.route('/')
def home():
    recent_notifications = get_all_notifications(limit=6)
    return render_template('index.html', notifications=recent_notifications)


@app.route('/wbcs/')
@app.route('/wbcs')
def wbcs():
    return render_template('exam_page.html',
                           exam=EXAM_CONFIG['wbcs'],
                           category=CATEGORY_CONFIG['wbcs'])


@app.route('/psc/')
@app.route('/psc')
def psc():
    cat = CATEGORY_CONFIG['psc']
    exams = [EXAM_CONFIG[k] for k in cat['exams']]
    return render_template('category.html', category=cat, exams=exams)


@app.route('/psc/misc/')
@app.route('/psc/misc')
def psc_misc():
    return render_template('exam_page.html',
                           exam=EXAM_CONFIG['psc-misc'],
                           category=CATEGORY_CONFIG['psc'])


@app.route('/psc/clerkship/')
@app.route('/psc/clerkship')
def psc_clerkship():
    return render_template('exam_page.html',
                           exam=EXAM_CONFIG['psc-clerkship'],
                           category=CATEGORY_CONFIG['psc'])


@app.route('/psc/wbcs/')
@app.route('/psc/wbcs')
def psc_wbcs():
    return redirect(url_for('wbcs'))


@app.route('/ssc/')
@app.route('/ssc')
def ssc():
    cat = CATEGORY_CONFIG['ssc']
    exams = [EXAM_CONFIG[k] for k in cat['exams']]
    return render_template('category.html', category=cat, exams=exams)


@app.route('/ssc/cgl/')
@app.route('/ssc/cgl')
def ssc_cgl():
    return render_template('exam_page.html',
                           exam=EXAM_CONFIG['ssc-cgl'],
                           category=CATEGORY_CONFIG['ssc'])


@app.route('/ssc/chsl/')
@app.route('/ssc/chsl')
def ssc_chsl():
    return render_template('exam_page.html',
                           exam=EXAM_CONFIG['ssc-chsl'],
                           category=CATEGORY_CONFIG['ssc'])


@app.route('/ssc/gd/')
@app.route('/ssc/gd')
def ssc_gd():
    return render_template('exam_page.html',
                           exam=EXAM_CONFIG['ssc-gd'],
                           category=CATEGORY_CONFIG['ssc'])


@app.route('/ssc/mts/')
@app.route('/ssc/mts')
def ssc_mts():
    return render_template('exam_page.html',
                           exam=EXAM_CONFIG['ssc-mts'],
                           category=CATEGORY_CONFIG['ssc'])


@app.route('/railway/')
@app.route('/railway')
def railway():
    cat = CATEGORY_CONFIG['railway']
    exams = [EXAM_CONFIG[k] for k in cat['exams']]
    return render_template('category.html', category=cat, exams=exams)


@app.route('/railway/ntpc-graduate/')
@app.route('/railway/ntpc-graduate')
def railway_ntpc_graduate():
    return render_template('exam_page.html',
                           exam=EXAM_CONFIG['railway-ntpc-graduate'],
                           category=CATEGORY_CONFIG['railway'])


@app.route('/railway/ntpc-ug/')
@app.route('/railway/ntpc-ug')
def railway_ntpc_ug():
    return render_template('exam_page.html',
                           exam=EXAM_CONFIG['railway-ntpc-ug'],
                           category=CATEGORY_CONFIG['railway'])


@app.route('/railway/group-d/')
@app.route('/railway/group-d')
def railway_group_d():
    return render_template('exam_page.html',
                           exam=EXAM_CONFIG['railway-group-d'],
                           category=CATEGORY_CONFIG['railway'])


@app.route('/railway/technician/')
@app.route('/railway/technician')
def railway_technician():
    return render_template('exam_page.html',
                           exam=EXAM_CONFIG['railway-technician'],
                           category=CATEGORY_CONFIG['railway'])


@app.route('/police/')
@app.route('/police')
def police():
    return render_template('exam_page.html',
                           exam=EXAM_CONFIG['police'],
                           category=CATEGORY_CONFIG['police'])


@app.route('/notes/')
@app.route('/notes')
def notes():
    return render_template('notes.html', category=CATEGORY_CONFIG['notes'])


@app.route('/quiz/')
@app.route('/quiz')
def quiz():
    return render_template('quiz.html')


@app.route('/admin')
@app.route('/admin/')
def admin():
    logs = get_scrape_logs(30)
    all_notifs = get_all_notifications(50)
    return render_template('admin.html', logs=logs, notifications=all_notifs,
                           exam_keys=list(EXAM_CONFIG.keys()))


# ── API endpoints ────────────────────────────────────────────────────────────

@app.route('/api/notifications')
def api_notifications():
    exam_key = request.args.get('exam', '')
    limit = min(int(request.args.get('limit', 10)), 50)
    if not exam_key:
        return jsonify({'error': 'exam parameter required'}), 400
    data = get_notifications(exam_key, limit)
    return jsonify(data)


@app.route('/api/vacancies')
def api_vacancies():
    exam_key = request.args.get('exam', '')
    if not exam_key:
        return jsonify({'error': 'exam parameter required'}), 400
    data = get_vacancies(exam_key)
    return jsonify(data)


@app.route('/api/scrape', methods=['POST'])
def api_scrape():
    def run():
        run_all_scrapers()
    t = threading.Thread(target=run, daemon=True)
    t.start()
    return jsonify({'status': 'started', 'message': 'Scraper launched in background.'})


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    init_db()
    scheduler = BackgroundScheduler()
    scheduler.add_job(run_all_scrapers, 'interval', hours=6, id='scraper')
    scheduler.start()
    app.run(host='0.0.0.0', port=5000, debug=False)
