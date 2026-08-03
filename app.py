import os
import threading
from flask import Flask, render_template, jsonify, request, redirect, url_for
from apscheduler.schedulers.background import BackgroundScheduler
from scraper.scraper import (
    init_db, get_notifications, get_vacancies,
    get_all_notifications, run_all_scrapers, get_scrape_logs
)

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.secret_key = os.environ.get('SESSION_SECRET', os.environ.get('SECRET_KEY', 'examguideindia2026'))

# ── Admin Panel Blueprint ────────────────────────────────────────────────────
from admin_panel import admin_bp
app.register_blueprint(admin_bp)

NOTICE_TEXT = "No active notification as of June 2026. Visit the official website for latest updates."
VACANCY_TEXT = "Official notification yet to be released – visit official website for latest updates."

EXAM_CONFIG = {
    'railway-group-d': {
        'key': 'railway-group-d', 'name': 'Railway Group D',
        'full_name': 'RRB Group D – Level 1 Posts',
        'icon': '⚙️', 'color': '#16a34a', 'light': '#f0fdf4',
        'official_url': 'https://rrbapply.gov.in',
        'apply_link': 'https://rrbapply.gov.in', 'result_link': 'https://rrbapply.gov.in',
        'category': 'railway',
        'overview': 'RRB Group D (Level 1) is one of the largest recruitment drives in India. It fills posts like Track Maintainer Grade-IV, Helper (Electrical/Mechanical/S&T), Hospital Attendant, and other support roles across all Railway zones and production units.',
        'pattern': [
            {'stage': 'CBT (Single Stage)', 'subjects': 'Mathematics | GI & Reasoning | General Science | General Awareness', 'questions': 100, 'marks': 100, 'duration': '90 min', 'negative': '1/3'},
            {'stage': 'Physical Efficiency Test (PET)', 'subjects': 'Male: carry 35 kg for 100m & run 1000m in 4:15 | Female: carry 20 kg for 100m & run 1000m in 5:40', 'questions': '—', 'marks': 'Qualifying', 'duration': '—', 'negative': '—'},
            {'stage': 'Document Verification & Medical', 'subjects': 'Colour vision, hearing & general fitness per Railway Board norms', 'questions': '—', 'marks': 'Qualifying', 'duration': '—', 'negative': '—'},
        ],
        'syllabus': [
            'Mathematics (Number System, BODMAS, Fractions, LCM/HCF, Ratio, Percentages, Mensuration, Time & Work, Time & Distance)',
            'General Intelligence & Reasoning (Analogies, Alphabetical Series, Coding-Decoding, Mathematical Operations, Syllogisms)',
            'General Science (Physics, Chemistry, Life Sciences – Class X CBSE standard)',
            'General Awareness & Current Affairs (Science & Tech, Sports, Culture, Personalities, Indian Railways)',
        ],
        'age_limit': '18–36 years (general category)',
        'age_relaxation': 'OBC (NCL): +3 years | SC/ST: +5 years | PwD: +10 years | Ex-Servicemen: as per rules',
        'qualification': 'Passed Class 10 (Matriculation) or ITI (NCVT) certificate from a recognised institution.',
        'posts': [
            {'post': 'Track Maintainer Grade-IV', 'pay_level': 'Level 1', 'grade_pay': '₹1,800', 'salary': '₹18,000 – ₹56,900/month + HRA + TA'},
            {'post': 'Helper (Electrical / Mechanical / S&T)', 'pay_level': 'Level 1', 'grade_pay': '₹1,800', 'salary': '₹18,000 – ₹56,900/month + HRA'},
            {'post': 'Hospital Attendant', 'pay_level': 'Level 1', 'grade_pay': '₹1,800', 'salary': '₹18,000 – ₹56,900/month'},
        ],
        'selection_process': ['Computer Based Test (CBT)', 'Physical Efficiency Test (PET)', 'Document Verification', 'Medical Examination (Colour Vision, Hearing, etc.)'],
        'app_fee': {'general': '₹500', 'obc': '₹500', 'sc_st': '₹250 (refunded on appearing in CBT)'},
        'notice': NOTICE_TEXT, 'vacancy': VACANCY_TEXT, 'sub_pages': [],
    },
    'police': {
        'key': 'police', 'name': 'WB Police',
        'full_name': 'West Bengal Police – Recruitment Overview',
        'icon': '👮', 'color': '#be123c', 'light': '#fff1f2',
        'official_url': 'https://wbpolice.gov.in',
        'apply_link': 'https://prb.wb.gov.in',
        'result_link': 'https://wbpolice.gov.in/recruitment.aspx',
        'category': 'police',
        'overview': 'The West Bengal Police Recruitment Board (WBPRB) conducts recruitment for various posts in the WB Police force including Sub-Inspector (SI), Constable, Lady Constable, and specialised roles. Kolkata Police has a separate recruitment process. Click the sub-pages below for detailed information on specific posts.',
        'pattern': [
            {'stage': 'Preliminary Written Test (MCQ)', 'subjects': 'GS + Arithmetic + Reasoning + English/Bengali', 'questions': 100, 'marks': 100, 'duration': '60 min', 'negative': '0.25'},
            {'stage': 'Physical Measurement Test (PMT)', 'subjects': 'Height, Chest, Weight – qualifying', 'questions': '—', 'marks': 'Qualifying', 'duration': '—', 'negative': '—'},
            {'stage': 'Physical Efficiency Test (PET)', 'subjects': '1600m run, Long Jump, High Jump', 'questions': '—', 'marks': 'Qualifying', 'duration': '—', 'negative': '—'},
            {'stage': 'Final Written Test (MCQ)', 'subjects': 'GK, Reasoning, Maths, Bengali/English, Computer', 'questions': 85, 'marks': 85, 'duration': '60 min', 'negative': 'No'},
            {'stage': 'Interview (SI posts only)', 'subjects': 'Personality Test', 'questions': '—', 'marks': 15, 'duration': '—', 'negative': '—'},
        ],
        'syllabus': [
            'General Studies: History of India & West Bengal, Geography, Indian Polity & Constitution',
            'Current Affairs & General Knowledge (last 6 months, national & state)',
            'Arithmetic (Class X level): Percentage, Ratio, Time-Speed-Distance, Simple Interest',
            'Reasoning & Mental Ability: Analogy, Series, Blood Relation, Direction Sense',
            'Bengali & English Language: Grammar, Comprehension',
            'Computer Basics & Applications: MS Office, Internet',
        ],
        'age_limit': 'Constable: 18–27 years | SI (UB): 20–27 years (general category)',
        'age_relaxation': 'SC/ST of WB: +5 years | OBC-A/B of WB: +3 years | Ex-Servicemen: as per rules',
        'qualification': 'Constable: Passed Class 10 (Madhyamik) or equivalent | SI (UB): Bachelor\'s degree from a recognised university',
        'posts': [
            {'post': 'Sub-Inspector – Unarmed Branch (UB)', 'pay_level': 'Level 8', 'grade_pay': '₹4,400', 'salary': '₹39,000 – ₹1,00,000/month (approx.)'},
            {'post': 'Constable – Unarmed Branch (UB)', 'pay_level': 'Level 3', 'grade_pay': '₹2,000', 'salary': '₹22,000 – ₹65,000/month (approx.)'},
        ],
        'selection_process': ['Preliminary Written Exam', 'PMT', 'PET', 'Final Written Exam', 'Personality Test (SI only)', 'Medical & Document Verification'],
        'app_fee': {'general': '₹200', 'obc': '₹200', 'sc_st': '₹50 (SC/ST of WB)'},
        'notice': NOTICE_TEXT, 'vacancy': VACANCY_TEXT,
        'sub_pages': [
            {'name': 'WBP Constable', 'url': '/police/wbp-constable/'},
            {'name': 'WBP SI', 'url': '/police/wbp-si/'},
            {'name': 'Kolkata Police', 'url': '/police/kolkata-police/'},
        ],
    },
}

WBP_CONSTABLE = {
    'key': 'wbp-constable', 'name': 'WBP Constable',
    'full_name': 'West Bengal Police Constable Recruitment',
    'icon': '🛡️', 'color': '#be123c', 'light': '#fff1f2',
    'official_url': 'https://wbpolice.gov.in',
    'apply_link': 'https://prb.wb.gov.in',
    'result_link': 'https://wbpolice.gov.in/recruitment.aspx',
    'overview': 'The WBPRB recruits Constables (Unarmed Branch) for the West Bengal Police. This is one of the most popular state-level recruitment exams with thousands of vacancies announced periodically.',
    'pattern': [
        {'stage': 'Preliminary Written Test (MCQ)', 'subjects': 'GK, Arithmetic, Reasoning, English, Bengali', 'questions': 100, 'marks': 100, 'duration': '60 min', 'negative': '0.25'},
        {'stage': 'PMT – Physical Measurement Test', 'subjects': 'Male: 167 cm height, 79/84 cm chest | Female: 160 cm height', 'questions': '—', 'marks': 'Qualifying', 'duration': '—', 'negative': '—'},
        {'stage': 'PET – Physical Efficiency Test', 'subjects': '1600m run: 6:30 min (M) / 4:00 min (F); Long Jump; High Jump', 'questions': '—', 'marks': 'Qualifying', 'duration': '—', 'negative': '—'},
        {'stage': 'Final Written Test (MCQ)', 'subjects': 'GK, Arithmetic, Reasoning, Computer, Bengali/English', 'questions': 85, 'marks': 85, 'duration': '60 min', 'negative': 'No'},
        {'stage': 'Medical Examination', 'subjects': 'Vision, Physical Fitness', 'questions': '—', 'marks': 'Qualifying', 'duration': '—', 'negative': '—'},
    ],
    'syllabus': [
        'General Knowledge: History of India & West Bengal, Geography, Polity, Science & Technology',
        'Current Affairs (last 6 months): National & State Level news',
        'Arithmetic: Percentage, Ratio, Simple Interest, Time-Speed-Distance, Profit & Loss',
        'Reasoning: Analogies, Odd One Out, Series, Blood Relation, Direction Sense',
        'English: Comprehension, Grammar, Fill in the Blanks, Error Detection',
        'Bengali: Grammar, Comprehension, Proverbs, Idioms',
        'Computer Basics: MS Office, Internet, Email',
        'Physical Standards: Male – 167 cm height, 79/84 cm chest; Female – 160 cm height',
    ],
    'age_limit': '18–27 years (general category)',
    'age_relaxation': 'SC/ST of WB: +5 years | OBC-A/B of WB: +3 years | Ex-Servicemen: as per rules',
    'qualification': 'Passed Class 10 (Madhyamik) or equivalent from a recognised Board.',
    'posts': [
        {'post': 'Constable (Unarmed Branch – Male)', 'pay_level': 'Level 3', 'grade_pay': '₹2,000', 'salary': '₹22,000 – ₹65,000/month (approx.) + DA + HRA + Medical Allowance'},
        {'post': 'Lady Constable (Unarmed Branch)', 'pay_level': 'Level 3', 'grade_pay': '₹2,000', 'salary': '₹22,000 – ₹65,000/month (approx.) + DA + HRA + Medical Allowance'},
    ],
    'selection_process': ['Preliminary Written Test', 'Physical Measurement Test (PMT)', 'Physical Efficiency Test (PET)', 'Final Written Test', 'Medical Examination & Document Verification'],
    'app_fee': {'general': '₹200', 'obc': '₹200', 'sc_st': '₹50 (SC/ST of WB)'},
    'notice': 'Official notification yet to be released – visit official website for latest updates.',
    'vacancy': VACANCY_TEXT,
}

KOLKATA_POLICE = {
    'key': 'kolkata-police', 'name': 'Kolkata Police',
    'full_name': 'Kolkata Police Constable & Sergeant Recruitment',
    'icon': '🚔', 'color': '#0369a1', 'light': '#f0f9ff',
    'official_url': 'https://kolkatapolice.gov.in',
    'apply_link': 'https://prb.wb.gov.in',
    'result_link': 'https://kolkatapolice.gov.in',
    'overview': 'Kolkata Police is the law enforcement agency for the Kolkata Metropolitan Area, operating under the West Bengal government. Recruitment for Constable, Lady Constable, and Sergeant positions is conducted by the Kolkata Police Recruitment Board (KPRB).',
    'pattern': [
        {'stage': 'Written Test – MCQ', 'subjects': 'GK, Arithmetic, Reasoning, Bengali/English', 'questions': 100, 'marks': 100, 'duration': '60 min', 'negative': '0.25'},
        {'stage': 'Physical Measurement Test', 'subjects': 'Male: 167 cm height, 79/84 cm chest | Female: 160 cm height', 'questions': '—', 'marks': 'Qualifying', 'duration': '—', 'negative': '—'},
        {'stage': 'Physical Efficiency Test', 'subjects': '1600m run, Long Jump, High Jump', 'questions': '—', 'marks': 'Qualifying', 'duration': '—', 'negative': '—'},
        {'stage': 'Final Written Test – MCQ', 'subjects': 'GK, Arithmetic, Reasoning, Language, Computer', 'questions': 85, 'marks': 85, 'duration': '60 min', 'negative': 'No'},
        {'stage': 'Medical Examination & Document Verification', 'subjects': '—', 'questions': '—', 'marks': 'Qualifying', 'duration': '—', 'negative': '—'},
    ],
    'syllabus': [
        'General Knowledge: History of Kolkata & West Bengal, Indian Polity, Geography, Science',
        'Current Affairs: Local, National and International events (last 6 months)',
        'Arithmetic: Class X level Mathematics',
        'Reasoning & Mental Ability',
        'Bengali & English Language: Grammar, Comprehension',
        'Computer Knowledge: Basic MS Office, Internet, Email',
        'Physical Standards: Male – 167 cm height, 79/84 cm chest; Female – 160 cm height',
    ],
    'age_limit': '18–27 years for Constable; 20–27 years for Sergeant (general category)',
    'age_relaxation': 'SC/ST of WB: +5 years | OBC-A/B of WB: +3 years | Ex-Servicemen: as per rules',
    'qualification': 'Constable / Lady Constable: Passed Class 10 (Madhyamik) or equivalent | Sergeant: Class 10 + additional requirements as per notification',
    'posts': [
        {'post': 'Constable – Kolkata Police (Male)', 'pay_level': 'Level 3', 'grade_pay': '₹2,000', 'salary': '₹22,000 – ₹65,000/month (approx.) + DA + HRA'},
        {'post': 'Lady Constable – Kolkata Police', 'pay_level': 'Level 3', 'grade_pay': '₹2,000', 'salary': '₹22,000 – ₹65,000/month (approx.) + DA + HRA'},
        {'post': 'Sergeant – Kolkata Police', 'pay_level': 'Level 5', 'grade_pay': '₹2,800', 'salary': '₹29,200 – ₹92,300/month (approx.)'},
    ],
    'selection_process': ['Written Test (MCQ)', 'Physical Measurement Test (PMT)', 'Physical Efficiency Test (PET)', 'Final Written Test', 'Medical Examination & Document Verification'],
    'app_fee': {'general': '₹200', 'obc': '₹200', 'sc_st': '₹50 (SC/ST of WB)'},
    'notice': 'Official notification yet to be released – visit official website for latest updates.',
    'vacancy': VACANCY_TEXT,
}

WBSSC_GROUP_C = {
    'key': 'wbssc-group-c', 'name': 'WBSSC Group C',
    'full_name': 'West Bengal School Service Commission – Group C Recruitment',
    'icon': '📋', 'color': '#7c3aed', 'light': '#f5f3ff',
    'official_url': 'https://wbssc.in',
    'apply_link': 'https://wbssc.in',
    'result_link': 'https://wbssc.in',
    'category': 'exam',
    'overview': 'The West Bengal School Service Commission (WBSSC) conducts Group C recruitment for clerical and non-teaching posts in government and government-aided secondary schools across West Bengal. Posts include Upper Division Clerk, Lower Division Clerk, and Laboratory Assistant.',
    'pattern': [
        {'stage': 'Written Test (MCQ)', 'subjects': 'General Studies · English · Bengali · Arithmetic · Reasoning', 'questions': 100, 'marks': 100, 'duration': '90 min', 'negative': '0.25'},
        {'stage': 'Interview / Personality Test', 'subjects': 'Viva-Voce (for select posts)', 'questions': '—', 'marks': 25, 'duration': '—', 'negative': '—'},
    ],
    'syllabus': [
        'General Studies: History of India & West Bengal, Geography, Indian Polity & Constitution, Science & Technology',
        'English: Grammar, Comprehension, Vocabulary, Error Detection',
        'Bengali: Grammar, Composition, Comprehension',
        'Arithmetic: Percentage, Ratio, Profit & Loss, Simple & Compound Interest, Time-Speed-Distance (Class X level)',
        'Reasoning & Mental Ability: Analogies, Series, Coding-Decoding, Direction Sense',
        'Computer Basics: MS Office, Internet, Email fundamentals',
    ],
    'age_limit': '18–40 years (general category)',
    'age_relaxation': 'SC/ST of WB: +5 years | OBC-A/B: +3 years | PwD: +10 years',
    'qualification': "Passed Higher Secondary (10+2) or Bachelor's degree as per post. LDC posts require 10+2; UDC posts may require graduation.",
    'posts': [
        {'post': 'Upper Division Clerk (UDC)', 'pay_level': 'Level 7', 'grade_pay': '₹4,200', 'salary': '₹25,500 – ₹81,100/month'},
        {'post': 'Lower Division Clerk (LDC)', 'pay_level': 'Level 5', 'grade_pay': '₹2,900', 'salary': '₹17,500 – ₹44,200/month'},
        {'post': 'Laboratory Assistant', 'pay_level': 'Level 5', 'grade_pay': '₹2,900', 'salary': '₹17,500 – ₹44,200/month'},
    ],
    'selection_process': ['Written Test (MCQ)', 'Interview / Personality Test (select posts)', 'Document Verification & Background Check'],
    'app_fee': {'general': '₹160', 'obc': '₹120', 'sc_st': '₹60 (SC/ST of WB)'},
    'notice': NOTICE_TEXT, 'vacancy': VACANCY_TEXT, 'sub_pages': [],
}

WBSSC_GROUP_D = {
    'key': 'wbssc-group-d', 'name': 'WBSSC Group D',
    'full_name': 'West Bengal School Service Commission – Group D Recruitment',
    'icon': '🏗️', 'color': '#d97706', 'light': '#fffbeb',
    'official_url': 'https://wbssc.in',
    'apply_link': 'https://wbssc.in',
    'result_link': 'https://wbssc.in',
    'category': 'exam',
    'overview': 'WBSSC Group D recruitment fills support staff and non-teaching positions in government and government-aided schools across West Bengal. Posts include Peon, Night Guard, Sweeper, and other Group D support roles across all districts.',
    'pattern': [
        {'stage': 'Written Test (MCQ)', 'subjects': 'General Studies & Arithmetic (Class VIII level)', 'questions': 75, 'marks': 75, 'duration': '60 min', 'negative': '0.25'},
    ],
    'syllabus': [
        'General Studies (Class VIII level): History, Geography, Science, Current Affairs',
        'Arithmetic: Basic Calculations, Percentages, Simple Interest, Time & Work (Class VIII standard)',
        'Bengali Language: Basic Grammar, Reading Comprehension',
        'General Knowledge: State & National Events',
    ],
    'age_limit': '18–40 years (general category)',
    'age_relaxation': 'SC/ST of WB: +5 years | OBC-A/B: +3 years | PwD: +10 years',
    'qualification': 'Passed Class 8 (Class VIII) or Class 10 (Madhyamik) depending on the post applied for.',
    'posts': [
        {'post': 'Peon / Group D Staff', 'pay_level': 'Level 1', 'grade_pay': '₹1,800', 'salary': '₹18,000 – ₹56,900/month'},
        {'post': 'Night Guard / Watchman', 'pay_level': 'Level 1', 'grade_pay': '₹1,800', 'salary': '₹18,000 – ₹56,900/month'},
    ],
    'selection_process': ['Written Test (MCQ)', 'Document Verification', 'Background Check'],
    'app_fee': {'general': '₹160', 'obc': '₹120', 'sc_st': '₹60 (SC/ST of WB)'},
    'notice': NOTICE_TEXT, 'vacancy': VACANCY_TEXT, 'sub_pages': [],
}

PANCHAYAT = {
    'key': 'panchayat', 'name': 'Panchayat',
    'full_name': 'West Bengal Panchayat & Rural Development Recruitment',
    'icon': '🌿', 'color': '#15803d', 'light': '#f0fdf4',
    'official_url': 'https://wbprd.gov.in',
    'apply_link': 'https://wbprd.gov.in',
    'result_link': 'https://wbprd.gov.in',
    'category': 'exam',
    'overview': 'West Bengal Panchayat and Rural Development Department conducts recruitment for various posts in Gram Panchayats, Panchayat Samitis, and Zilla Parishads across West Bengal. Posts include Sahayak, Nirman Sahayak, Data Entry Operator, and Accounts Clerk.',
    'pattern': [
        {'stage': 'Written Test (MCQ)', 'subjects': 'General Studies · Arithmetic · Reasoning · Bengali/English', 'questions': 100, 'marks': 100, 'duration': '90 min', 'negative': '0.25'},
        {'stage': 'Computer Proficiency Test', 'subjects': 'MS Office, Data Entry (for DEO posts)', 'questions': '—', 'marks': 'Qualifying', 'duration': '30 min', 'negative': '—'},
    ],
    'syllabus': [
        'General Studies: Indian Polity, History, Geography, Science & Technology, Environment',
        'Current Affairs & General Knowledge: State & National level (last 6 months)',
        'Arithmetic: Percentage, Ratio, Profit & Loss, Time & Work, Simple Interest (Class X level)',
        'Reasoning & Mental Ability: Analogy, Series, Coding-Decoding, Blood Relations',
        'Bengali Language: Grammar, Comprehension, Letter Writing',
        'Computer Basics: MS Word, Excel, Internet, Email (for DEO/office posts)',
    ],
    'age_limit': '18–40 years (general category)',
    'age_relaxation': 'SC/ST of WB: +5 years | OBC-A/B of WB: +3 years | PwD: +10 years | Ex-Servicemen: as per WB rules',
    'qualification': "Varies by post: Class 10 for Sahayak; 10+2 for Accounts Clerk; Bachelor's degree for Technical posts. Computer knowledge required for office posts.",
    'posts': [
        {'post': 'Sahayak (Panchayat Level)', 'pay_level': 'Level 3', 'grade_pay': '₹2,000', 'salary': '₹21,700 – ₹69,100/month'},
        {'post': 'Nirman Sahayak', 'pay_level': 'Level 5', 'grade_pay': '₹2,900', 'salary': '₹25,500 – ₹81,100/month'},
        {'post': 'Data Entry Operator (DEO)', 'pay_level': 'Level 4', 'grade_pay': '₹2,400', 'salary': '₹25,500 – ₹81,100/month'},
        {'post': 'Accounts Clerk', 'pay_level': 'Level 5', 'grade_pay': '₹2,900', 'salary': '₹25,500 – ₹81,100/month'},
    ],
    'selection_process': ['Written Test (MCQ)', 'Computer Proficiency Test (for office posts)', 'Document Verification & Background Check'],
    'app_fee': {'general': '₹200', 'obc': '₹150', 'sc_st': '₹50 (SC/ST of WB)'},
    'notice': NOTICE_TEXT, 'vacancy': VACANCY_TEXT, 'sub_pages': [],
}

CATEGORY_CONFIG = {
    'railway': {'name': 'Railway', 'full_name': 'Railway Recruitment Board', 'icon': '🚆', 'color': '#ea580c', 'light': '#fff7ed', 'desc': 'RRB recruitment for various posts in Indian Railways.', 'exams': ['railway-group-d']},
    'police': {'name': 'Police', 'full_name': 'West Bengal Police Recruitment Board', 'icon': '👮', 'color': '#be123c', 'light': '#fff1f2', 'desc': 'WB Police and Kolkata Police recruitment for SI, Constable, and other posts.', 'exams': ['police']},
    'notes': {'name': 'Notes', 'full_name': 'Study Notes & Materials', 'icon': '📚', 'color': '#0d9488', 'light': '#f0fdfa', 'desc': '', 'exams': []},
    'exam': {'name': 'Exams', 'full_name': 'WB Government Exams', 'icon': '📋', 'color': '#6c3fbf', 'light': '#f5f0ff', 'desc': '', 'exams': []},
}

EXAM_SUBJECTS = {
    'wbp-constable': [
        {'icon': '🏛️', 'name': 'General Knowledge', 'desc': 'History · Geography · Polity · Science'},
        {'icon': '📰', 'name': 'Current Affairs', 'desc': 'National & State · Last 6 months'},
        {'icon': '🔢', 'name': 'Arithmetic', 'desc': 'Percentage · Ratio · Time & Distance · Profit & Loss'},
        {'icon': '🧠', 'name': 'Reasoning', 'desc': 'Analogies · Series · Blood Relations · Direction Sense'},
        {'icon': '🇬🇧', 'name': 'English Language', 'desc': 'Grammar · Comprehension · Vocabulary'},
        {'icon': '🔤', 'name': 'Bengali Language', 'desc': 'Grammar · Comprehension · Idioms'},
        {'icon': '💻', 'name': 'Computer Basics', 'desc': 'MS Office · Internet · Email'},
    ],
    'kolkata-police': [
        {'icon': '🏛️', 'name': 'General Knowledge', 'desc': 'History of Kolkata & WB · Polity · Geography'},
        {'icon': '📰', 'name': 'Current Affairs', 'desc': 'Local · National · International events'},
        {'icon': '🔢', 'name': 'Arithmetic', 'desc': 'Class X level Mathematics'},
        {'icon': '🧠', 'name': 'Reasoning & Mental Ability', 'desc': 'Analogies · Series · Direction Sense'},
        {'icon': '🇬🇧', 'name': 'English Language', 'desc': 'Grammar · Comprehension'},
        {'icon': '🔤', 'name': 'Bengali Language', 'desc': 'Grammar · Comprehension'},
        {'icon': '💻', 'name': 'Computer Knowledge', 'desc': 'MS Office · Internet · Email'},
    ],
    'wbssc-group-c': [
        {'icon': '🏛️', 'name': 'General Studies', 'desc': 'History · Geography · Polity · Science & Technology'},
        {'icon': '🇬🇧', 'name': 'English', 'desc': 'Grammar · Comprehension · Error Detection'},
        {'icon': '🔤', 'name': 'Bengali', 'desc': 'Grammar · Composition · Comprehension'},
        {'icon': '🔢', 'name': 'Arithmetic & Numerical Ability', 'desc': 'Percentage · Ratio · Simple Interest · Time & Work'},
        {'icon': '🧠', 'name': 'Reasoning & Mental Ability', 'desc': 'Analogies · Series · Coding-Decoding'},
        {'icon': '💻', 'name': 'Computer Basics', 'desc': 'MS Office · Internet · Email fundamentals'},
    ],
    'wbssc-group-d': [
        {'icon': '🏛️', 'name': 'General Studies', 'desc': 'History · Geography · Science (Class VIII level)'},
        {'icon': '🔢', 'name': 'Basic Arithmetic', 'desc': 'Percentages · Simple Interest · Time & Work'},
        {'icon': '🔤', 'name': 'Bengali Language', 'desc': 'Basic Grammar · Reading Comprehension'},
        {'icon': '📰', 'name': 'General Knowledge', 'desc': 'State & National Events'},
    ],
    'panchayat': [
        {'icon': '🏛️', 'name': 'General Studies', 'desc': 'Indian Polity · History · Geography · Science'},
        {'icon': '📰', 'name': 'Current Affairs & GK', 'desc': 'State & National level · Last 6 months'},
        {'icon': '🔢', 'name': 'Arithmetic', 'desc': 'Percentage · Ratio · Time & Work · Simple Interest'},
        {'icon': '🧠', 'name': 'Reasoning & Mental Ability', 'desc': 'Analogy · Series · Coding-Decoding · Blood Relations'},
        {'icon': '🔤', 'name': 'Bengali Language', 'desc': 'Grammar · Comprehension · Letter Writing'},
        {'icon': '💻', 'name': 'Computer Basics', 'desc': 'MS Word · Excel · Internet · Email'},
    ],
    'railway-group-d': [
        {'icon': '🔬', 'name': 'General Science', 'desc': 'Physics · Chemistry · Life Sciences (Class X level)'},
        {'icon': '🏛️', 'name': 'General Knowledge & CA', 'desc': 'History · Polity · Geography · Railways · Current Affairs'},
        {'icon': '🔢', 'name': 'Mathematics', 'desc': 'Arithmetic · Algebra · Geometry (Class X level)'},
        {'icon': '🧠', 'name': 'General Intelligence & Reasoning', 'desc': 'Analogies · Coding-Decoding · Series · Direction Sense'},
    ],
}

EXAM_BY_SLUG = {
    'wbp-constable': {**WBP_CONSTABLE, 'detail_url': '/police/wbp-constable/', 'dashboard_url': '/exam/wbp-constable/', 'subjects': EXAM_SUBJECTS['wbp-constable']},
    'kolkata-police': {**KOLKATA_POLICE, 'detail_url': '/police/kolkata-police/', 'dashboard_url': '/exam/kolkata-police/', 'subjects': EXAM_SUBJECTS['kolkata-police']},
    'wbssc-group-c': {**WBSSC_GROUP_C, 'detail_url': '/exam/wbssc-group-c/detail/', 'dashboard_url': '/exam/wbssc-group-c/', 'subjects': EXAM_SUBJECTS['wbssc-group-c']},
    'wbssc-group-d': {**WBSSC_GROUP_D, 'detail_url': '/exam/wbssc-group-d/detail/', 'dashboard_url': '/exam/wbssc-group-d/', 'subjects': EXAM_SUBJECTS['wbssc-group-d']},
    'panchayat': {**PANCHAYAT, 'detail_url': '/exam/panchayat/detail/', 'dashboard_url': '/exam/panchayat/', 'subjects': EXAM_SUBJECTS['panchayat']},
    'railway-group-d': {**EXAM_CONFIG['railway-group-d'], 'detail_url': '/railway/group-d/', 'dashboard_url': '/exam/railway-group-d/', 'subjects': EXAM_SUBJECTS['railway-group-d']},
}


@app.route('/exam/<slug>/notes/', strict_slashes=False)
def exam_section_notes(slug):
    exam = EXAM_BY_SLUG.get(slug)
    if not exam:
        return redirect('/#popular-exams')
    return render_template('exam_notes.html', exam=exam)

@app.route('/exam/<slug>/quiz/', strict_slashes=False)
def exam_section_quiz(slug):
    exam = EXAM_BY_SLUG.get(slug)
    if not exam:
        return redirect('/#popular-exams')
    return render_template('exam_quiz.html', exam=exam, mock_test=False)

@app.route('/exam/<slug>/mock-test/', strict_slashes=False)
def exam_section_mock_test(slug):
    exam = EXAM_BY_SLUG.get(slug)
    if not exam:
        return redirect('/#popular-exams')
    return render_template('exam_quiz.html', exam=exam, mock_test=True)

@app.route('/exam/<slug>/current-affairs/', strict_slashes=False)
def exam_section_current_affairs(slug):
    exam = EXAM_BY_SLUG.get(slug)
    if not exam:
        return redirect('/#popular-exams')
    return render_template('exam_current_affairs.html', exam=exam)

@app.route('/exam/<slug>/previous-papers/', strict_slashes=False)
def exam_section_previous_papers(slug):
    exam = EXAM_BY_SLUG.get(slug)
    if not exam:
        return redirect('/#popular-exams')
    return render_template('exam_papers.html', exam=exam)


@app.route('/')
def home():
    return render_template('index.html', notifications=get_all_notifications(limit=6))

@app.route('/about/', strict_slashes=False)
def about():
    return render_template('about.html')

@app.route('/contact/', strict_slashes=False)
def contact():
    return render_template('contact.html')







@app.route('/railway/group-d/', strict_slashes=False)
def railway_group_d():
    return render_template('exam_page.html', exam=EXAM_CONFIG['railway-group-d'], category=CATEGORY_CONFIG['railway'], section_base='/exam/railway-group-d')


@app.route('/police/', strict_slashes=False)
def police():
    return render_template('exam_page.html', exam=EXAM_CONFIG['police'], category=CATEGORY_CONFIG['police'])

@app.route('/police/wbp-constable/', strict_slashes=False)
def wbp_constable():
    return render_template('police_sub.html', exam=WBP_CONSTABLE, section_base='/exam/wbp-constable')


@app.route('/police/kolkata-police/', strict_slashes=False)
def kolkata_police():
    return render_template('police_sub.html', exam=KOLKATA_POLICE, section_base='/exam/kolkata-police')

@app.route('/exam/', strict_slashes=False)
def exam_home():
    return redirect('/#popular-exams')

@app.route('/exam/wbp-constable/', strict_slashes=False)
def exam_wbp_constable_dashboard():
    return render_template('exam_dashboard.html', exam={**WBP_CONSTABLE, 'detail_url': '/police/wbp-constable/'})

@app.route('/exam/kolkata-police/', strict_slashes=False)
def exam_kolkata_police_dashboard():
    return render_template('exam_dashboard.html', exam={**KOLKATA_POLICE, 'detail_url': '/police/kolkata-police/'})

@app.route('/exam/wbssc-group-c/', strict_slashes=False)
def exam_wbssc_group_c_dashboard():
    return render_template('exam_dashboard.html', exam={**WBSSC_GROUP_C, 'detail_url': '/exam/wbssc-group-c/detail/'})

@app.route('/exam/wbssc-group-c/detail/', strict_slashes=False)
def exam_wbssc_group_c_detail():
    return render_template('exam_page.html', exam=WBSSC_GROUP_C, category=CATEGORY_CONFIG['exam'], section_base='/exam/wbssc-group-c')

@app.route('/exam/wbssc-group-d/', strict_slashes=False)
def exam_wbssc_group_d_dashboard():
    return render_template('exam_dashboard.html', exam={**WBSSC_GROUP_D, 'detail_url': '/exam/wbssc-group-d/detail/'})

@app.route('/exam/wbssc-group-d/detail/', strict_slashes=False)
def exam_wbssc_group_d_detail():
    return render_template('exam_page.html', exam=WBSSC_GROUP_D, category=CATEGORY_CONFIG['exam'], section_base='/exam/wbssc-group-d')

@app.route('/exam/panchayat/', strict_slashes=False)
def exam_panchayat_dashboard():
    return render_template('exam_dashboard.html', exam={**PANCHAYAT, 'detail_url': '/exam/panchayat/detail/'})

@app.route('/exam/panchayat/detail/', strict_slashes=False)
def exam_panchayat_detail():
    return render_template('exam_page.html', exam=PANCHAYAT, category=CATEGORY_CONFIG['exam'], section_base='/exam/panchayat')

@app.route('/exam/railway-group-d/', strict_slashes=False)
def exam_railway_group_d_dashboard():
    rg = EXAM_CONFIG['railway-group-d']
    return render_template('exam_dashboard.html', exam={**rg, 'detail_url': '/railway/group-d/'})

@app.route('/notes/', strict_slashes=False)
def notes():
    return render_template('notes.html', category=CATEGORY_CONFIG['notes'])

@app.route('/notes/demo-notes/', strict_slashes=False)
def demo_notes():
    return render_template('demo_notes.html')

@app.route('/quiz/', strict_slashes=False)
def quiz():
    return render_template('quiz.html')

@app.route('/quiz/demo-quiz/', strict_slashes=False)
def demo_quiz():
    return render_template('demo_quiz.html')

@app.route('/search/', strict_slashes=False)
def search():
    q = request.args.get('q', '').strip()
    return render_template('search.html', q=q)

@app.route('/api/search')
def api_search():
    q = request.args.get('q', '').strip().lower()
    if not q or len(q) < 2:
        return jsonify([])

    results = []

    # Search exams
    for key, exam in EXAM_CONFIG.items():
        score = 0
        haystack = ' '.join([
            exam.get('name', ''), exam.get('full_name', ''),
            exam.get('overview', ''), exam.get('qualification', ''),
            exam.get('category', ''),
        ]).lower()
        if q in haystack:
            # Boost if query in name directly
            score = 10 if q in exam.get('name', '').lower() else (
                     8  if q in exam.get('full_name', '').lower() else 4)
            cat = exam.get('category', key)
            if cat == key:
                url = f'/{cat}/'
            else:
                slug = key.replace(cat + '-', '')
                url = f'/{cat}/{slug}/'
            results.append({
                'type': 'exam',
                'icon': exam.get('icon', '📋'),
                'title': exam.get('full_name', exam.get('name', '')),
                'subtitle': f"{exam.get('category', '').upper()} • {exam.get('age_limit', '')}",
                'url': url,
                'color': exam.get('color', '#6c3fbf'),
                'score': score,
            })

    # Search notes topics
    notes_topics = [
        {'title': 'June 2026 Current Affairs',        'subtitle': 'Monthly CA Notes • PDF',        'url': '/notes/demo-notes/', 'icon': '📘'},
        {'title': 'Indian Polity Summary Notes',      'subtitle': 'Constitution • Articles • GK',   'url': '/notes/',            'icon': '🏛️'},
        {'title': 'West Bengal GK Notes',             'subtitle': 'History • Geography • Culture',  'url': '/notes/',            'icon': '🗺️'},
        {'title': 'WB Police Constable Notes',        'subtitle': 'GS • Reasoning • Bengali',      'url': '/notes/demo-notes/', 'icon': '👮'},
        {'title': 'Current Affairs May 2026',         'subtitle': 'Monthly CA Notes • PDF',        'url': '/notes/',            'icon': '📰'},
        {'title': 'Reasoning & Mental Ability Notes', 'subtitle': 'All exams • Shortcuts',         'url': '/notes/',            'icon': '🧠'},
    ]
    for n in notes_topics:
        if q in n['title'].lower() or q in n['subtitle'].lower():
            results.append({
                'type': 'notes', 'icon': n['icon'],
                'title': n['title'], 'subtitle': n['subtitle'],
                'url': n['url'], 'color': '#1d4ed8', 'score': 3,
            })

    # Search quizzes
    quiz_topics = [
        {'title': 'WB Police Constable Quiz',   'subtitle': '5 Questions • GS + Reasoning + Bengali',  'url': '/quiz/'},
        {'title': 'Demo Quiz – 10 Questions',   'subtitle': 'Mixed topics • Detailed answers',         'url': '/quiz/demo-quiz/'},
    ]
    for qt in quiz_topics:
        if q in qt['title'].lower() or q in qt['subtitle'].lower():
            results.append({
                'type': 'quiz', 'icon': '📝',
                'title': qt['title'], 'subtitle': qt['subtitle'],
                'url': qt['url'], 'color': '#7c3aed', 'score': 2,
            })

    results.sort(key=lambda x: -x['score'])
    return jsonify(results[:12])

@app.route('/admin', strict_slashes=False)
def admin():
    return render_template('admin.html', logs=get_scrape_logs(30), notifications=get_all_notifications(50), exam_keys=list(EXAM_CONFIG.keys()))

@app.route('/api/notifications')
def api_notifications():
    exam_key = request.args.get('exam', '')
    limit = min(int(request.args.get('limit', 10)), 50)
    if not exam_key:
        return jsonify({'error': 'exam parameter required'}), 400
    return jsonify(get_notifications(exam_key, limit))

@app.route('/api/vacancies')
def api_vacancies():
    exam_key = request.args.get('exam', '')
    if not exam_key:
        return jsonify({'error': 'exam parameter required'}), 400
    return jsonify(get_vacancies(exam_key))

@app.route('/api/scrape', methods=['POST'])
def api_scrape():
    threading.Thread(target=run_all_scrapers, daemon=True).start()
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
