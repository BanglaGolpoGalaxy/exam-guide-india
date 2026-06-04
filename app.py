import os
import threading
from flask import Flask, render_template, jsonify, request, redirect, url_for
from apscheduler.schedulers.background import BackgroundScheduler
from scraper.scraper import (
    init_db, get_notifications, get_vacancies,
    get_all_notifications, run_all_scrapers, get_scrape_logs
)

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.secret_key = os.environ.get('SECRET_KEY', 'examguideindia2026')

NOTICE_TEXT = "No active notification as of June 2026. Visit the official website for latest updates."
VACANCY_TEXT = "Official notification yet to be released – visit official website for latest updates."

EXAM_CONFIG = {
    'wbcs': {
        'key': 'wbcs', 'name': 'WBCS',
        'full_name': 'West Bengal Civil Service (Executive) Examination',
        'icon': '🏛️', 'color': '#1d4ed8', 'light': '#eff6ff',
        'official_url': 'https://psc.wb.gov.in',
        'apply_link': 'https://psc.wb.gov.in/content/wbcs-exam',
        'result_link': 'https://psc.wb.gov.in/content/wbcs-exam',
        'category': 'wbcs',
        'overview': 'WBCS (West Bengal Civil Service) is the most prestigious state-level civil service examination conducted by the West Bengal Public Service Commission (WBPSC). It recruits for Group A, B, C and D services under the Government of West Bengal, including IAS-equivalent positions at the state level. Successful candidates serve as SDOs, BDOs, Executive Magistrates, and other senior officials.',
        'pattern': [
            {'stage': 'Preliminary (MCQ)', 'subjects': 'General Studies', 'questions': 200, 'marks': 200, 'duration': '2.5 hrs', 'negative': '0.25'},
            {'stage': 'Mains (Descriptive)', 'subjects': '6 Compulsory + Optional Papers', 'questions': '—', 'marks': 900, 'duration': '3 hrs each', 'negative': 'No'},
            {'stage': 'Personality Test', 'subjects': 'Viva-Voce / Interview', 'questions': '—', 'marks': 100, 'duration': '—', 'negative': '—'},
        ],
        'syllabus': [
            'English Composition & Language Skills',
            'General Science & Environment',
            'Indian History, Culture & Heritage',
            'Geography of India & West Bengal',
            'Indian Economy, Planning & Development',
            'Indian Polity & Constitution',
            'Current Affairs & General Knowledge',
            'Mathematics & Mental Ability (Class X level)',
            'Bengali / Hindi / Urdu / Nepali / Santhali (Optional Language Paper)',
        ],
        'age_limit': '21–36 years (as of 1 January of the exam year)',
        'age_relaxation': 'SC/ST: +5 years | OBC-A/B: +3 years | PwD: +10 years | Ex-Servicemen: as per WB govt rules',
        'qualification': "Bachelor's degree in any stream from a recognised university for Group A/B posts. 10+2 for Group C; Class 10 for Group D.",
        'posts': [
            {'post': 'WBCS (Executive) – Group A', 'pay_level': 'Level 14', 'grade_pay': '₹8,700', 'salary': '₹56,100 – ₹1,44,300/month'},
            {'post': 'WBCS (Executive) – Group B', 'pay_level': 'Level 12', 'grade_pay': '₹5,400', 'salary': '₹41,100 – ₹1,00,800/month'},
            {'post': 'Sub-Inspector of Schools (Group C)', 'pay_level': 'Level 9', 'grade_pay': '₹4,600', 'salary': '₹32,300 – ₹82,900/month'},
        ],
        'selection_process': ['Preliminary Written Test (MCQ – 200 marks)', 'Main Written Examination (Descriptive – 900 marks)', 'Personality Test / Interview (100 marks)', 'Final Merit List & Document Verification'],
        'app_fee': {'general': '₹210', 'obc': '₹210', 'sc_st': '₹60 (SC/ST of WB only)'},
        'notice': NOTICE_TEXT, 'vacancy': VACANCY_TEXT, 'sub_pages': [],
    },
    'psc-misc': {
        'key': 'psc-misc', 'name': 'PSC MISC',
        'full_name': 'WBPSC Miscellaneous Services Examination',
        'icon': '⚖️', 'color': '#15803d', 'light': '#f0fdf4',
        'official_url': 'https://psc.wb.gov.in',
        'apply_link': 'https://psc.wb.gov.in/content/misc-exam',
        'result_link': 'https://psc.wb.gov.in/content/misc-exam',
        'category': 'psc',
        'overview': 'The WBPSC Miscellaneous Services Examination recruits candidates to Group B and C posts across various West Bengal government departments including Revenue, Finance, Agriculture, Health, and Co-operative sectors. It is a combined exam for multiple services and is highly competitive.',
        'pattern': [
            {'stage': 'Preliminary (MCQ)', 'subjects': 'General Studies & Arithmetic', 'questions': 200, 'marks': 200, 'duration': '2.5 hrs', 'negative': '0.25'},
            {'stage': 'Mains Paper I', 'subjects': 'General Studies & English', 'questions': '—', 'marks': 200, 'duration': '3 hrs', 'negative': 'No'},
            {'stage': 'Mains Paper II', 'subjects': 'Bengali / Hindi / Urdu', 'questions': '—', 'marks': 100, 'duration': '2 hrs', 'negative': 'No'},
            {'stage': 'Interview / Personality Test', 'subjects': 'Viva-Voce', 'questions': '—', 'marks': 50, 'duration': '—', 'negative': '—'},
        ],
        'syllabus': [
            'General Studies: History, Geography, Indian Polity, Science & Technology, Environment',
            'Current Affairs & General Knowledge (national & state level)',
            'Arithmetic: Percentage, Ratio, Profit-Loss, Time-Speed-Distance, Simple & Compound Interest',
            'English Composition: Essay, Précis, Letter, Comprehension',
            'Bengali / Hindi / Urdu Language & Composition',
            'Reasoning & Mental Ability',
        ],
        'age_limit': '18–36 years (general category)',
        'age_relaxation': 'SC/ST: +5 years | OBC-A/B: +3 years | PwD: +10 years',
        'qualification': "Bachelor's degree from a recognised university. Some posts require specific discipline (Commerce, Science). Check official notification for post-wise eligibility.",
        'posts': [
            {'post': 'Block Development Officer (BDO)', 'pay_level': 'Level 12', 'grade_pay': '₹5,400', 'salary': '₹41,100 – ₹1,00,800/month'},
            {'post': 'Inspector, Co-operative Societies', 'pay_level': 'Level 9', 'grade_pay': '₹4,600', 'salary': '₹32,300 – ₹82,900/month'},
            {'post': 'Auditor (Group C)', 'pay_level': 'Level 7', 'grade_pay': '₹4,200', 'salary': '₹25,500 – ₹81,100/month'},
        ],
        'selection_process': ['Preliminary Written Test', 'Main Written Examination (2 papers)', 'Personality Test / Interview (for select posts)', 'Document Verification'],
        'app_fee': {'general': '₹160', 'obc': '₹160', 'sc_st': '₹60 (SC/ST of WB)'},
        'notice': NOTICE_TEXT, 'vacancy': VACANCY_TEXT, 'sub_pages': [],
    },
    'psc-clerkship': {
        'key': 'psc-clerkship', 'name': 'PSC Clerkship',
        'full_name': 'WBPSC Clerkship Examination',
        'icon': '📋', 'color': '#0d9488', 'light': '#f0fdfa',
        'official_url': 'https://psc.wb.gov.in',
        'apply_link': 'https://psc.wb.gov.in/content/clerkship-exam',
        'result_link': 'https://psc.wb.gov.in/content/clerkship-exam',
        'category': 'psc',
        'overview': 'The WBPSC Clerkship Examination fills Lower Division Clerk (LDC) and similar Group C positions across West Bengal state departments. It is one of the most accessible government job exams in WB with minimum 10+2 qualification required.',
        'pattern': [
            {'stage': 'Written Test – Paper I (MCQ)', 'subjects': 'General Studies + Arithmetic', 'questions': 85, 'marks': 85, 'duration': '60 min', 'negative': '0.25'},
            {'stage': 'Written Test – Paper II (MCQ)', 'subjects': 'Bengali / Hindi / Urdu / Nepali / Santhali', 'questions': 15, 'marks': 15, 'duration': '30 min', 'negative': '0.25'},
            {'stage': 'Personality Test (select posts)', 'subjects': 'Viva-Voce', 'questions': '—', 'marks': 10, 'duration': '—', 'negative': '—'},
        ],
        'syllabus': [
            'General Studies (Class X level): History, Geography, Polity, Science, Environment',
            'Arithmetic & Numerical Ability (Class X level)',
            'English Language & Basic Comprehension',
            'Bengali / Hindi / Urdu Language & Grammar',
            'General Knowledge & Current Affairs',
        ],
        'age_limit': '18–40 years (general category)',
        'age_relaxation': 'SC/ST: +5 years | OBC: +3 years | PwD: +10 years',
        'qualification': 'Passed Higher Secondary (10+2) or equivalent from a recognised Board.',
        'posts': [
            {'post': 'Lower Division Clerk (LDC)', 'pay_level': 'Level 5', 'grade_pay': '₹2,900', 'salary': '₹17,500 – ₹44,200/month'},
            {'post': 'Office Assistant (Statewide)', 'pay_level': 'Level 5', 'grade_pay': '₹2,900', 'salary': '₹17,500 – ₹44,200/month'},
        ],
        'selection_process': ['Written Test (Paper I – GS & Arithmetic)', 'Written Test (Paper II – Language)', 'Personality Test (for certain posts)', 'Document Verification & Medical'],
        'app_fee': {'general': '₹160', 'obc': '₹160', 'sc_st': '₹60 (SC/ST of WB)'},
        'notice': NOTICE_TEXT, 'vacancy': VACANCY_TEXT, 'sub_pages': [],
    },
    'ssc-cgl': {
        'key': 'ssc-cgl', 'name': 'SSC CGL',
        'full_name': 'SSC Combined Graduate Level Examination',
        'icon': '🎖️', 'color': '#7c3aed', 'light': '#f5f3ff',
        'official_url': 'https://ssc.gov.in',
        'apply_link': 'https://ssc.gov.in/candidate-corner',
        'result_link': 'https://ssc.gov.in/notice-board',
        'category': 'ssc',
        'overview': 'SSC CGL is the most coveted national-level exam by the Staff Selection Commission for Group B and C posts across central government ministries. Top posts include Income Tax Inspector, Auditor, JSO, and Assistant Section Officer in MEA.',
        'pattern': [
            {'stage': 'Tier-I (CBE)', 'subjects': 'GI & Reasoning | GK & GA | Quantitative Aptitude | English', 'questions': 100, 'marks': 200, 'duration': '60 min', 'negative': '0.50'},
            {'stage': 'Tier-II Session-I (CBE)', 'subjects': 'Mathematical Abilities + Reasoning + English + GK', 'questions': 150, 'marks': 330, 'duration': '2 hrs 15 min', 'negative': '1'},
            {'stage': 'Tier-II Session-II (Optional)', 'subjects': 'Statistics (JSO) / Finance & Economics (AAO)', 'questions': 100, 'marks': 200, 'duration': '2 hrs', 'negative': '1'},
            {'stage': 'Tier-III (Descriptive)', 'subjects': 'Essay + Letter/Application in Hindi or English', 'questions': '—', 'marks': 100, 'duration': '60 min', 'negative': 'No'},
            {'stage': 'Tier-IV (Skill Test)', 'subjects': 'DEST / CPT – role specific', 'questions': '—', 'marks': 'Qualifying', 'duration': '15 min', 'negative': '—'},
        ],
        'syllabus': [
            'General Intelligence & Reasoning (Analogy, Classification, Coding-Decoding, Series, Matrix, Word Formation)',
            'General Awareness (Current Affairs, Static GK, History, Geography, Economy, Polity, Science)',
            'Quantitative Aptitude (Arithmetic, Algebra, Trigonometry, Geometry, Statistics, Data Interpretation)',
            'English Comprehension (Reading, Cloze Test, Error Spotting, Sentence Improvement, Para Jumbles)',
            'Statistics (JSO post): Probability, Sampling Theory, Analysis & Interpretation of Data',
            'Finance & Economics (AAO post): Fundamental Principles of Finance & Accountancy',
        ],
        'age_limit': '18–32 years (varies by post: 18–27 for some, 20–30 for others; see official notification)',
        'age_relaxation': 'OBC: +3 years | SC/ST: +5 years | PwD: +10–15 years | Ex-Servicemen: as per rules',
        'qualification': "Bachelor's degree in any stream from a recognised university. Some posts require specific degrees (B.Com for Auditor/Accountant, B.Sc(Stats) for JSO).",
        'posts': [
            {'post': 'Assistant Section Officer (MEA/CBI)', 'pay_level': 'Level 7', 'grade_pay': '₹4,600', 'salary': '₹44,900 – ₹1,42,400/month'},
            {'post': 'Income Tax Inspector (CBDT)', 'pay_level': 'Level 7', 'grade_pay': '₹4,600', 'salary': '₹44,900 – ₹1,42,400/month'},
            {'post': 'Auditor / Accountant (C&AG, CGDA)', 'pay_level': 'Level 5', 'grade_pay': '₹2,800', 'salary': '₹29,200 – ₹92,300/month'},
            {'post': 'Junior Statistical Officer (JSO)', 'pay_level': 'Level 6', 'grade_pay': '₹4,200', 'salary': '₹35,400 – ₹1,12,400/month'},
        ],
        'selection_process': ['Tier-I CBE (screening stage)', 'Tier-II CBE (merit stage, Session I & II)', 'Tier-III Descriptive Paper', 'Tier-IV Skill / Typing Test (role specific)', 'Document Verification & Medical Examination'],
        'app_fee': {'general': '₹100', 'obc': '₹100', 'sc_st': 'Nil (Women candidates also exempt)'},
        'notice': NOTICE_TEXT, 'vacancy': VACANCY_TEXT, 'sub_pages': [],
    },
    'ssc-chsl': {
        'key': 'ssc-chsl', 'name': 'SSC CHSL',
        'full_name': 'SSC Combined Higher Secondary Level Examination',
        'icon': '📑', 'color': '#b45309', 'light': '#fffbeb',
        'official_url': 'https://ssc.gov.in',
        'apply_link': 'https://ssc.gov.in/candidate-corner',
        'result_link': 'https://ssc.gov.in/notice-board',
        'category': 'ssc',
        'overview': 'SSC CHSL recruits Lower Division Clerks (LDC), Junior Secretariat Assistants (JSA), Postal/Sorting Assistants (PA/SA), and Data Entry Operators (DEO) in central government organisations. Minimum qualification is 10+2.',
        'pattern': [
            {'stage': 'Tier-I (CBE)', 'subjects': 'GI & Reasoning | GK & GA | Quantitative Aptitude | English', 'questions': 100, 'marks': 200, 'duration': '60 min', 'negative': '0.50'},
            {'stage': 'Tier-II Session-I (Descriptive)', 'subjects': 'Essay (200–250 words) + Letter/Application (150–200 words) in Hindi or English', 'questions': '—', 'marks': 100, 'duration': '60 min', 'negative': 'No'},
            {'stage': 'Tier-II Session-II (Skill/Typing)', 'subjects': 'Typing Test: English 35 WPM / Hindi 30 WPM, or DEST for DEO posts', 'questions': '—', 'marks': 'Qualifying', 'duration': '15 min', 'negative': '—'},
        ],
        'syllabus': [
            'General Intelligence & Reasoning (Analogy, Odd One Out, Series, Coding-Decoding)',
            'English Language (Comprehension, Vocabulary, Error Spotting, Fill in the Blanks)',
            'Quantitative Aptitude (Arithmetic – Class X level: Ratio, Percentage, SI/CI, DI)',
            'General Awareness (Current Events, Indian History, Geography, Economy, Science)',
        ],
        'age_limit': '18–27 years (general category)',
        'age_relaxation': 'OBC: +3 years | SC/ST: +5 years | PwD: +10 years | Ex-Servicemen: as per rules',
        'qualification': 'Passed Higher Secondary (10+2) or equivalent from a recognised Board.',
        'posts': [
            {'post': 'Lower Division Clerk (LDC) / JSA', 'pay_level': 'Level 2', 'grade_pay': '₹1,900', 'salary': '₹19,900 – ₹63,200/month'},
            {'post': 'Postal Assistant / Sorting Assistant', 'pay_level': 'Level 4', 'grade_pay': '₹2,400', 'salary': '₹25,500 – ₹81,100/month'},
            {'post': 'Data Entry Operator (DEO)', 'pay_level': 'Level 4–5', 'grade_pay': '₹2,400–₹2,800', 'salary': '₹25,500 – ₹92,300/month'},
        ],
        'selection_process': ['Tier-I CBE (screening)', 'Tier-II Session-I: Descriptive Paper', 'Tier-II Session-II: Skill Test / Typing Test', 'Document Verification & Medical'],
        'app_fee': {'general': '₹100', 'obc': '₹100', 'sc_st': 'Nil (Women candidates also exempt)'},
        'notice': NOTICE_TEXT, 'vacancy': VACANCY_TEXT, 'sub_pages': [],
    },
    'ssc-gd': {
        'key': 'ssc-gd', 'name': 'SSC GD',
        'full_name': 'SSC GD Constable (CAPFs / NIA / SSF / Rifleman Assam Rifles)',
        'icon': '🛡️', 'color': '#dc2626', 'light': '#fef2f2',
        'official_url': 'https://ssc.gov.in',
        'apply_link': 'https://ssc.gov.in/candidate-corner',
        'result_link': 'https://ssc.gov.in/notice-board',
        'category': 'ssc',
        'overview': 'SSC GD Constable exam recruits General Duty Constables for Central Armed Police Forces: BSF, CRPF, CISF, SSB, ITBP, NIA, SSF and Rifleman in Assam Rifles. One of the largest recruitment drives in India by vacancy count.',
        'pattern': [
            {'stage': 'CBE (Computer Based)', 'subjects': 'GI & Reasoning | GK & GA | Elementary Maths | English/Hindi', 'questions': 80, 'marks': 160, 'duration': '60 min', 'negative': '0.50'},
            {'stage': 'Physical Efficiency Test (PET)', 'subjects': '5km run 24 min (M) / 1.6km 8.5 min (F); Long & High Jump', 'questions': '—', 'marks': 'Qualifying', 'duration': '—', 'negative': '—'},
            {'stage': 'Physical Standard Test (PST)', 'subjects': 'Height, Chest (males), Weight', 'questions': '—', 'marks': 'Qualifying', 'duration': '—', 'negative': '—'},
            {'stage': 'Medical Examination', 'subjects': 'General Health & Vision', 'questions': '—', 'marks': 'Qualifying', 'duration': '—', 'negative': '—'},
        ],
        'syllabus': [
            'General Intelligence & Reasoning (Analogies, Spatial Visualisation, Observation, Discrimination, Arithmetic Reasoning)',
            'General Knowledge & Awareness (Current Events, India & World, Sports, History, Culture, Geography, Science)',
            'Elementary Mathematics (Number Systems, Decimals, Fractions, Percentages, Ratio, Mensuration, Averages)',
            'English / Hindi Language (Comprehension, Fill in Blanks, Error Detection, Vocabulary)',
        ],
        'age_limit': '18–23 years (general category)',
        'age_relaxation': 'OBC: +3 years | SC/ST: +5 years | Ex-Servicemen: as per rules',
        'qualification': 'Passed Class 10 (Matriculation) or equivalent from a recognised Board.',
        'posts': [
            {'post': 'Constable (GD) – BSF/CRPF/CISF/SSB/ITBP', 'pay_level': 'Level 3', 'grade_pay': '₹2,000', 'salary': '₹21,700 – ₹69,100/month + uniform & risk allowances'},
            {'post': 'Rifleman – Assam Rifles', 'pay_level': 'Level 3', 'grade_pay': '₹2,000', 'salary': '₹21,700 – ₹69,100/month + military allowances'},
        ],
        'selection_process': ['Computer Based Examination (CBE)', 'Physical Efficiency Test (PET)', 'Physical Standard Test (PST)', 'Medical Examination', 'Document Verification & Final Merit'],
        'app_fee': {'general': '₹100', 'obc': '₹100', 'sc_st': 'Nil (Women candidates also exempt)'},
        'notice': NOTICE_TEXT, 'vacancy': VACANCY_TEXT, 'sub_pages': [],
    },
    'ssc-mts': {
        'key': 'ssc-mts', 'name': 'SSC MTS',
        'full_name': 'SSC Multi Tasking Staff & Havaldar Examination',
        'icon': '📝', 'color': '#0369a1', 'light': '#f0f9ff',
        'official_url': 'https://ssc.gov.in',
        'apply_link': 'https://ssc.gov.in/candidate-corner',
        'result_link': 'https://ssc.gov.in/notice-board',
        'category': 'ssc',
        'overview': "SSC MTS recruits Multi Tasking Staff (Non-Technical) and Havaldar in CBIC & CBN for Group C, Non-Gazetted, Non-Ministerial posts in central government offices nationwide. Class 10 pass is the minimum qualification.",
        'pattern': [
            {'stage': 'Session-I (Paper-I)', 'subjects': 'Numerical & Mathematical Ability | Reasoning & Problem Solving', 'questions': 60, 'marks': 60, 'duration': '45 min', 'negative': '1'},
            {'stage': 'Session-II (Paper-I)', 'subjects': 'General Awareness | English Language & Comprehension', 'questions': 75, 'marks': 75, 'duration': '45 min', 'negative': '1'},
            {'stage': 'Paper-II (Descriptive)', 'subjects': 'Short Essay + Letter/Application in Hindi / English / any 8th Schedule language', 'questions': '—', 'marks': 50, 'duration': '45 min', 'negative': 'No'},
        ],
        'syllabus': [
            'Numerical & Mathematical Ability (Number System, BODMAS, Fractions, Decimals – Class VIII level)',
            'Reasoning & Problem Solving (Pattern Recognition, Logical Thinking, Non-Verbal Reasoning)',
            'General Awareness (History, Geography, Polity, Economy, Science & Technology)',
            'English Language & Comprehension (Basic Grammar, Vocabulary, Comprehension)',
            'Short Essay & Letter Writing (Paper-II – qualifying nature)',
        ],
        'age_limit': '18–25 years for MTS; 18–27 years for Havaldar posts',
        'age_relaxation': 'OBC: +3 years | SC/ST: +5 years | PwD: +10 years | Ex-Servicemen: as per rules',
        'qualification': 'Passed Class 10 (Matriculation) or equivalent from a recognised Board.',
        'posts': [
            {'post': 'Multi Tasking Staff (MTS) – Non-Technical', 'pay_level': 'Level 1', 'grade_pay': '₹1,800', 'salary': '₹18,000 – ₹56,900/month'},
            {'post': 'Havaldar – CBIC / CBN', 'pay_level': 'Level 1', 'grade_pay': '₹1,800', 'salary': '₹18,000 – ₹56,900/month + uniform allowance'},
        ],
        'selection_process': ['Session-I & Session-II CBE (merit basis)', 'Paper-II Descriptive (qualifying)', 'Document Verification & Medical'],
        'app_fee': {'general': '₹100', 'obc': '₹100', 'sc_st': 'Nil (Women candidates also exempt)'},
        'notice': NOTICE_TEXT, 'vacancy': VACANCY_TEXT, 'sub_pages': [],
    },
    'railway-ntpc-graduate': {
        'key': 'railway-ntpc-graduate', 'name': 'NTPC Graduate',
        'full_name': 'RRB NTPC – Graduate Level Posts',
        'icon': '🚆', 'color': '#ea580c', 'light': '#fff7ed',
        'official_url': 'https://rrbapply.gov.in',
        'apply_link': 'https://rrbapply.gov.in', 'result_link': 'https://rrbapply.gov.in',
        'category': 'railway',
        'overview': 'RRB NTPC Graduate Level exam recruits for Station Master, Goods Guard, Senior Commercial cum Ticket Clerk, Junior Clerk cum Typist, Accounts Clerk cum Typist, and Junior Time Keeper in Indian Railways. These are Level 2 to Level 6 posts.',
        'pattern': [
            {'stage': 'CBT-1 (Preliminary)', 'subjects': 'Mathematics | General Intelligence & Reasoning | General Awareness', 'questions': 100, 'marks': 100, 'duration': '90 min', 'negative': '1/3'},
            {'stage': 'CBT-2 (Mains)', 'subjects': 'Mathematics | General Intelligence & Reasoning | General Awareness | General Science', 'questions': 120, 'marks': 120, 'duration': '90 min', 'negative': '1/3'},
            {'stage': 'Typing / CBAT', 'subjects': 'Typing Test (English 30 WPM / Hindi 25 WPM) or Computer-Based Aptitude Test for Traffic/SM posts', 'questions': '—', 'marks': 'Qualifying', 'duration': '—', 'negative': '—'},
        ],
        'syllabus': [
            'Mathematics (Number System, HCF/LCM, Decimals, SI/CI, Percentages, Ratio, Time & Work, Time & Distance, DI)',
            'General Intelligence & Reasoning (Analogies, Series, Coding-Decoding, Mathematical Operations, Puzzles)',
            'General Awareness (Current Events, Indian Railways, Books & Authors, Sports, Art & Culture, History)',
            'General Science (Physics, Chemistry, Life Sciences – Class X level)',
            'Computer Literacy & MS Office Basics (for typing test posts)',
        ],
        'age_limit': '18–33 years (varies by post; see official notification)',
        'age_relaxation': 'OBC (NCL): +3 years | SC/ST: +5 years | PwD: +10 years | Ex-Servicemen: as per rules',
        'qualification': "Bachelor's degree in any stream from a recognised university.",
        'posts': [
            {'post': 'Station Master', 'pay_level': 'Level 6', 'grade_pay': '₹4,200', 'salary': '₹35,400 – ₹1,12,400/month'},
            {'post': 'Goods Guard', 'pay_level': 'Level 5', 'grade_pay': '₹2,800', 'salary': '₹29,200 – ₹92,300/month'},
            {'post': 'Senior Commercial cum Ticket Clerk', 'pay_level': 'Level 5', 'grade_pay': '₹2,800', 'salary': '₹29,200 – ₹92,300/month'},
            {'post': 'Junior Clerk cum Typist', 'pay_level': 'Level 2', 'grade_pay': '₹1,900', 'salary': '₹19,900 – ₹63,200/month'},
        ],
        'selection_process': ['CBT-1 (Preliminary Screening)', 'CBT-2 (Main Examination)', 'Typing Skill Test / CBAT', 'Document Verification', 'Medical Examination'],
        'app_fee': {'general': '₹500', 'obc': '₹500', 'sc_st': '₹250 (refunded on appearing in CBT-1)'},
        'notice': NOTICE_TEXT, 'vacancy': VACANCY_TEXT, 'sub_pages': [],
    },
    'railway-ntpc-ug': {
        'key': 'railway-ntpc-ug', 'name': 'NTPC UG',
        'full_name': 'RRB NTPC – Under-Graduate Level Posts',
        'icon': '🚉', 'color': '#d97706', 'light': '#fffbeb',
        'official_url': 'https://rrbapply.gov.in',
        'apply_link': 'https://rrbapply.gov.in', 'result_link': 'https://rrbapply.gov.in',
        'category': 'railway',
        'overview': 'RRB NTPC Under-Graduate level exam fills posts like Commercial cum Ticket Clerk, Traffic Assistant, Junior Clerk cum Typist, and Accounts Clerk cum Typist in Indian Railways. Minimum 10+2 qualification is required.',
        'pattern': [
            {'stage': 'CBT-1 (Preliminary)', 'subjects': 'Mathematics | General Intelligence & Reasoning | General Awareness', 'questions': 100, 'marks': 100, 'duration': '90 min', 'negative': '1/3'},
            {'stage': 'CBT-2 (Mains)', 'subjects': 'Mathematics | General Intelligence & Reasoning | General Awareness | General Science', 'questions': 120, 'marks': 120, 'duration': '90 min', 'negative': '1/3'},
            {'stage': 'Typing Test', 'subjects': 'English 30 WPM / Hindi 25 WPM on computer', 'questions': '—', 'marks': 'Qualifying', 'duration': '10 min', 'negative': '—'},
        ],
        'syllabus': [
            'Mathematics (Arithmetic – Class X level: Number System, BODMAS, Ratio, Profit-Loss, Time & Work)',
            'General Intelligence & Reasoning (Analogies, Series Completion, Coding-Decoding, Odd One Out)',
            'General Awareness & Current Affairs (Railway events, National/International news)',
            'General Science (Physics, Chemistry, Biology – Class X CBSE level)',
            'English Language Basics (Comprehension, Vocabulary)',
        ],
        'age_limit': '18–33 years (varies by post; see official notification)',
        'age_relaxation': 'OBC (NCL): +3 years | SC/ST: +5 years | PwD: +10 years | Ex-Servicemen: as per rules',
        'qualification': 'Passed Higher Secondary (10+2) or equivalent from a recognised Board.',
        'posts': [
            {'post': 'Commercial cum Ticket Clerk', 'pay_level': 'Level 3', 'grade_pay': '₹2,000', 'salary': '₹21,700 – ₹69,100/month'},
            {'post': 'Traffic Assistant', 'pay_level': 'Level 2', 'grade_pay': '₹1,900', 'salary': '₹19,900 – ₹63,200/month'},
            {'post': 'Junior Clerk cum Typist (UG Level)', 'pay_level': 'Level 2', 'grade_pay': '₹1,900', 'salary': '₹19,900 – ₹63,200/month'},
        ],
        'selection_process': ['CBT-1 (Preliminary Screening)', 'CBT-2 (Main Examination)', 'Typing Test (for Clerk posts)', 'Document Verification', 'Medical Examination'],
        'app_fee': {'general': '₹500', 'obc': '₹500', 'sc_st': '₹250 (refunded on appearing in CBT-1)'},
        'notice': NOTICE_TEXT, 'vacancy': VACANCY_TEXT, 'sub_pages': [],
    },
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
    'railway-technician': {
        'key': 'railway-technician', 'name': 'RRB Technician',
        'full_name': 'RRB Technician – Grade-1 Signal & Other Trades',
        'icon': '🔧', 'color': '#0891b2', 'light': '#ecfeff',
        'official_url': 'https://rrbapply.gov.in',
        'apply_link': 'https://rrbapply.gov.in', 'result_link': 'https://rrbapply.gov.in',
        'category': 'railway',
        'overview': 'RRB Technician exam recruits Technicians in Electrical, Mechanical, Signal & Telecommunication, Bridge, Carriage & Wagon, and other trades. Grade-1 Signal posts require specialised engineering knowledge at ITI/Diploma level.',
        'pattern': [
            {'stage': 'CBT (Single Stage)', 'subjects': 'Mathematics | GI & Reasoning | General Science | General Awareness | Technical Ability', 'questions': 100, 'marks': 100, 'duration': '90 min', 'negative': '1/3'},
            {'stage': 'Document Verification & Medical', 'subjects': 'Trade-related fitness and vision standards', 'questions': '—', 'marks': 'Qualifying', 'duration': '—', 'negative': '—'},
        ],
        'syllabus': [
            'Mathematics (Algebra, Geometry, Trigonometry, Statistics – Class XII level)',
            'General Intelligence & Reasoning',
            'General Science (Physics, Chemistry – Class XII level)',
            'General Awareness & Current Affairs',
            'Technical Ability: Trade-specific – Electrical/Electronics/Signal/Mechanical/Bridge based on ITI trade or Diploma',
        ],
        'age_limit': '18–36 years (Technician Grade-3); up to 33 years for Grade-1 Signal',
        'age_relaxation': 'OBC (NCL): +3 years | SC/ST: +5 years | PwD: +10 years',
        'qualification': 'ITI (NCVT/SCVT) in the relevant trade OR Diploma in Engineering in relevant branch. Class 10 pass compulsory.',
        'posts': [
            {'post': 'Technician Grade-1 (Signal)', 'pay_level': 'Level 5', 'grade_pay': '₹2,800', 'salary': '₹29,200 – ₹92,300/month'},
            {'post': 'Technician Grade-3 (Electrical / Mechanical)', 'pay_level': 'Level 2', 'grade_pay': '₹1,900', 'salary': '₹19,900 – ₹63,200/month'},
        ],
        'selection_process': ['Computer Based Test (CBT)', 'Document Verification', 'Medical Examination (Vision Standards – Cp-1 to Cp-3 depending on post)'],
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

WBP_SI = {
    'key': 'wbp-si', 'name': 'WBP SI',
    'full_name': 'West Bengal Police Sub-Inspector (Unarmed Branch) Recruitment',
    'icon': '⭐', 'color': '#1d4ed8', 'light': '#eff6ff',
    'official_url': 'https://wbpolice.gov.in',
    'apply_link': 'https://prb.wb.gov.in',
    'result_link': 'https://wbpolice.gov.in/recruitment.aspx',
    'overview': "WBP SI (Unarmed Branch) recruits Sub-Inspectors responsible for law enforcement at the local police station level, managing FIRs, investigations, and supervising Constables. It is a Group B post under the West Bengal Police.",
    'pattern': [
        {'stage': 'Preliminary Written Test (MCQ)', 'subjects': 'GK, Arithmetic, Reasoning, English, Bengali', 'questions': 100, 'marks': 100, 'duration': '60 min', 'negative': '0.25'},
        {'stage': 'PMT – Physical Measurement Test', 'subjects': 'Male: 172 cm height, 80/85 cm chest | Female: 163 cm height', 'questions': '—', 'marks': 'Qualifying', 'duration': '—', 'negative': '—'},
        {'stage': 'PET – Physical Efficiency Test', 'subjects': '1600m run: 5:45 min (M) / 4:30 min (F); Long Jump; High Jump', 'questions': '—', 'marks': 'Qualifying', 'duration': '—', 'negative': '—'},
        {'stage': 'Final Written Test (MCQ)', 'subjects': 'GK, Reasoning, Maths, Bengali/English, Computer', 'questions': 85, 'marks': 85, 'duration': '60 min', 'negative': 'No'},
        {'stage': 'Personality Test / Interview', 'subjects': 'Viva-Voce', 'questions': '—', 'marks': 15, 'duration': '—', 'negative': '—'},
        {'stage': 'Medical Examination', 'subjects': 'Vision, Physical Fitness', 'questions': '—', 'marks': 'Qualifying', 'duration': '—', 'negative': '—'},
    ],
    'syllabus': [
        'General Knowledge: Indian History, Freedom Movement, Indian Polity & Constitution, Geography of India & WB',
        'Current Affairs (national & state, last 6 months)',
        'Arithmetic: Number System, Ratio, Percentage, SI/CI, Time & Work, Mensuration',
        'Reasoning & Mental Ability: Analogy, Classification, Series, Coding-Decoding, Blood Relation',
        'English Language: Comprehension, Vocabulary, Grammar, Error Spotting',
        'Bengali Language: Composition, Grammar, Literature, Comprehension',
        'Computer Basics: Windows, MS Office, Internet Browsing, Email',
    ],
    'age_limit': '20–27 years (general category)',
    'age_relaxation': 'SC/ST of WB: +5 years | OBC-A/B of WB: +3 years | Ex-Servicemen: as per rules',
    'qualification': "Bachelor's degree from a recognised university (any stream).",
    'posts': [
        {'post': 'Sub-Inspector – Unarmed Branch (Male)', 'pay_level': 'Level 8', 'grade_pay': '₹4,400', 'salary': '₹39,000 – ₹1,00,000/month (approx.) + DA + HRA + Medical Allowance'},
        {'post': 'Sub-Inspector – Unarmed Branch (Female)', 'pay_level': 'Level 8', 'grade_pay': '₹4,400', 'salary': '₹39,000 – ₹1,00,000/month (approx.) + DA + HRA + Medical Allowance'},
    ],
    'selection_process': ['Preliminary Written Test', 'PMT', 'PET', 'Final Written Test', 'Personality Test / Interview', 'Medical Examination & Document Verification'],
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

CATEGORY_CONFIG = {
    'wbcs': {'name': 'WBCS', 'full_name': 'West Bengal Civil Service', 'icon': '🏛️', 'color': '#1d4ed8', 'light': '#eff6ff', 'desc': 'The most prestigious state civil service exam in West Bengal, conducted by WBPSC.', 'exams': ['wbcs']},
    'psc': {'name': 'PSC', 'full_name': 'West Bengal Public Service Commission', 'icon': '⚖️', 'color': '#15803d', 'light': '#f0fdf4', 'desc': 'Exams for various Group B and C posts across West Bengal government departments.', 'exams': ['psc-misc', 'psc-clerkship']},
    'ssc': {'name': 'SSC', 'full_name': 'Staff Selection Commission', 'icon': '🎖️', 'color': '#7c3aed', 'light': '#f5f3ff', 'desc': 'National-level exams for Group B, C and D posts in Central Government departments.', 'exams': ['ssc-cgl', 'ssc-chsl', 'ssc-gd', 'ssc-mts']},
    'railway': {'name': 'Railway', 'full_name': 'Railway Recruitment Board', 'icon': '🚆', 'color': '#ea580c', 'light': '#fff7ed', 'desc': 'RRB recruitment for various posts in Indian Railways – one of the largest employers in India.', 'exams': ['railway-ntpc-graduate', 'railway-ntpc-ug', 'railway-group-d', 'railway-technician']},
    'police': {'name': 'Police', 'full_name': 'West Bengal Police Recruitment Board', 'icon': '👮', 'color': '#be123c', 'light': '#fff1f2', 'desc': 'WB Police and Kolkata Police recruitment for SI, Constable, and other posts.', 'exams': ['police']},
    'notes': {'name': 'Notes', 'full_name': 'Study Notes & Materials', 'icon': '📚', 'color': '#0d9488', 'light': '#f0fdfa', 'desc': '', 'exams': []},
}


@app.route('/')
def home():
    return render_template('index.html', notifications=get_all_notifications(limit=6))

@app.route('/about/', strict_slashes=False)
def about():
    return render_template('about.html')

@app.route('/contact/', strict_slashes=False)
def contact():
    return render_template('contact.html')

@app.route('/wbcs/', strict_slashes=False)
def wbcs():
    return render_template('exam_page.html', exam=EXAM_CONFIG['wbcs'], category=CATEGORY_CONFIG['wbcs'])

@app.route('/psc/', strict_slashes=False)
def psc():
    cat = CATEGORY_CONFIG['psc']
    return render_template('category.html', category=cat, exams=[EXAM_CONFIG[k] for k in cat['exams']])

@app.route('/psc/misc/', strict_slashes=False)
def psc_misc():
    return render_template('exam_page.html', exam=EXAM_CONFIG['psc-misc'], category=CATEGORY_CONFIG['psc'])

@app.route('/psc/clerkship/', strict_slashes=False)
def psc_clerkship():
    return render_template('exam_page.html', exam=EXAM_CONFIG['psc-clerkship'], category=CATEGORY_CONFIG['psc'])

@app.route('/ssc/', strict_slashes=False)
def ssc():
    cat = CATEGORY_CONFIG['ssc']
    return render_template('category.html', category=cat, exams=[EXAM_CONFIG[k] for k in cat['exams']])

@app.route('/ssc/cgl/', strict_slashes=False)
def ssc_cgl():
    return render_template('exam_page.html', exam=EXAM_CONFIG['ssc-cgl'], category=CATEGORY_CONFIG['ssc'])

@app.route('/ssc/chsl/', strict_slashes=False)
def ssc_chsl():
    return render_template('exam_page.html', exam=EXAM_CONFIG['ssc-chsl'], category=CATEGORY_CONFIG['ssc'])

@app.route('/ssc/gd/', strict_slashes=False)
def ssc_gd():
    return render_template('exam_page.html', exam=EXAM_CONFIG['ssc-gd'], category=CATEGORY_CONFIG['ssc'])

@app.route('/ssc/mts/', strict_slashes=False)
def ssc_mts():
    return render_template('exam_page.html', exam=EXAM_CONFIG['ssc-mts'], category=CATEGORY_CONFIG['ssc'])

@app.route('/railway/', strict_slashes=False)
def railway():
    cat = CATEGORY_CONFIG['railway']
    return render_template('category.html', category=cat, exams=[EXAM_CONFIG[k] for k in cat['exams']])

@app.route('/railway/ntpc-graduate/', strict_slashes=False)
def railway_ntpc_graduate():
    return render_template('exam_page.html', exam=EXAM_CONFIG['railway-ntpc-graduate'], category=CATEGORY_CONFIG['railway'])

@app.route('/railway/ntpc-ug/', strict_slashes=False)
def railway_ntpc_ug():
    return render_template('exam_page.html', exam=EXAM_CONFIG['railway-ntpc-ug'], category=CATEGORY_CONFIG['railway'])

@app.route('/railway/group-d/', strict_slashes=False)
def railway_group_d():
    return render_template('exam_page.html', exam=EXAM_CONFIG['railway-group-d'], category=CATEGORY_CONFIG['railway'])

@app.route('/railway/technician/', strict_slashes=False)
def railway_technician():
    return render_template('exam_page.html', exam=EXAM_CONFIG['railway-technician'], category=CATEGORY_CONFIG['railway'])

@app.route('/police/', strict_slashes=False)
def police():
    return render_template('exam_page.html', exam=EXAM_CONFIG['police'], category=CATEGORY_CONFIG['police'])

@app.route('/police/wbp-constable/', strict_slashes=False)
def wbp_constable():
    return render_template('police_sub.html', exam=WBP_CONSTABLE)

@app.route('/police/wbp-si/', strict_slashes=False)
def wbp_si():
    return render_template('police_sub.html', exam=WBP_SI)

@app.route('/police/kolkata-police/', strict_slashes=False)
def kolkata_police():
    return render_template('police_sub.html', exam=KOLKATA_POLICE)

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
