import sqlite3
import requests
import logging
import os
from datetime import datetime, date
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'exams.db')

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-IN,en;q=0.9',
}

SCRAPE_TARGETS = {
    'ssc': {
        'url': 'https://ssc.gov.in/notice-board',
        'exams': ['ssc-cgl', 'ssc-chsl', 'ssc-gd', 'ssc-mts'],
        'selector': 'a',
        'keywords': ['notification', 'vacancy', 'result', 'admit', 'schedule'],
    },
    'psc': {
        'url': 'https://psc.wb.gov.in/notices',
        'exams': ['wbcs', 'psc-misc', 'psc-clerkship'],
        'selector': 'a',
        'keywords': ['notification', 'vacancy', 'result', 'advertisement'],
    },
    'railway': {
        'url': 'https://indianrailways.gov.in/railwayboard/view_section.jsp?lang=0&id=0,1,304',
        'exams': ['railway-ntpc-graduate', 'railway-ntpc-ug', 'railway-group-d', 'railway-technician'],
        'selector': 'a',
        'keywords': ['ntpc', 'group d', 'technician', 'rrb', 'recruitment'],
    },
    'police': {
        'url': 'https://wbpolice.gov.in/recruitment.aspx',
        'exams': ['police'],
        'selector': 'a',
        'keywords': ['recruitment', 'notification', 'result', 'constable', 'si'],
    },
}

SEED_NOTIFICATIONS = [
    ('ssc-cgl',       'SSC CGL 2024-25 Tier-II Result Declared',         '2025-05-15', 'https://ssc.gov.in/notice-board'),
    ('ssc-cgl',       'SSC CGL 2025 Notification Released – 14,582 Posts','2025-04-02', 'https://ssc.gov.in/notice-board'),
    ('ssc-chsl',      'SSC CHSL 2025 Tier-I Admit Card Available',        '2025-05-20', 'https://ssc.gov.in/notice-board'),
    ('ssc-chsl',      'SSC CHSL 2025 Notification Out – 3,712 Vacancies', '2025-03-18', 'https://ssc.gov.in/notice-board'),
    ('ssc-gd',        'SSC GD Constable 2025 Final Result Released',      '2025-05-10', 'https://ssc.gov.in/notice-board'),
    ('ssc-gd',        'SSC GD Constable 2026 Notification Expected Soon', '2025-04-25', 'https://ssc.gov.in/notice-board'),
    ('ssc-mts',       'SSC MTS & Havaldar 2025 Notification Released',    '2025-04-15', 'https://ssc.gov.in/notice-board'),
    ('ssc-mts',       'SSC MTS 2025 Application Window Open',             '2025-05-01', 'https://ssc.gov.in/notice-board'),
    ('wbcs',          'WBCS (Exe.) 2025 Preliminary Exam Result Out',     '2025-05-08', 'https://psc.wb.gov.in'),
    ('wbcs',          'WBCS 2025 Mains Exam Date Announced',              '2025-04-20', 'https://psc.wb.gov.in'),
    ('psc-misc',      'WBPSC Miscellaneous 2025 – 1,780 Vacancies',       '2025-04-10', 'https://psc.wb.gov.in'),
    ('psc-misc',      'WBPSC MISC 2025 Prelim Admit Card Download',       '2025-05-18', 'https://psc.wb.gov.in'),
    ('psc-clerkship', 'PSC Clerkship 2025 Recruitment Advertisement',     '2025-03-25', 'https://psc.wb.gov.in'),
    ('psc-clerkship', 'PSC Clerkship 2025 Exam Schedule Published',       '2025-05-05', 'https://psc.wb.gov.in'),
    ('railway-ntpc-graduate','RRB NTPC 2025 Notification – 11,558 Posts', '2025-05-01', 'https://rrbapply.gov.in'),
    ('railway-ntpc-graduate','RRB NTPC Graduate Exam City Intimation',    '2025-05-22', 'https://rrbapply.gov.in'),
    ('railway-ntpc-ug',     'RRB NTPC UG Recruitment 2025 Open',         '2025-05-01', 'https://rrbapply.gov.in'),
    ('railway-ntpc-ug',     'RRB NTPC UG Application Form Last Date',    '2025-06-01', 'https://rrbapply.gov.in'),
    ('railway-group-d',     'RRB Group D 2025 Notification Coming Soon', '2025-04-18', 'https://rrbapply.gov.in'),
    ('railway-group-d',     'Railway Group D 2024 Result Declared',      '2025-03-30', 'https://rrbapply.gov.in'),
    ('railway-technician',  'RRB Technician Grade-1 Signal 2025 Result', '2025-05-14', 'https://rrbapply.gov.in'),
    ('railway-technician',  'RRB Technician 2025 CBT Exam Dates Out',    '2025-04-28', 'https://rrbapply.gov.in'),
    ('police',        'WB Police Constable 2025 Recruitment Notification','2025-04-12', 'https://wbpolice.gov.in'),
    ('police',        'WB Police SI 2025 – 1,043 Vacancies Announced',   '2025-05-09', 'https://wbpolice.gov.in'),
]

SEED_VACANCIES = [
    ('ssc-cgl',       'SSC CGL 2025',              14582, '2025-06-15', 'https://ssc.gov.in', 'https://ssc.gov.in/notice-board'),
    ('ssc-chsl',      'SSC CHSL 2025',              3712, '2025-06-20', 'https://ssc.gov.in', 'https://ssc.gov.in/notice-board'),
    ('ssc-gd',        'SSC GD Constable 2026',     50000, '2025-09-30', 'https://ssc.gov.in', 'https://ssc.gov.in/notice-board'),
    ('ssc-mts',       'SSC MTS & Havaldar 2025',    9583, '2025-07-10', 'https://ssc.gov.in', 'https://ssc.gov.in/notice-board'),
    ('wbcs',          'WBCS (Exe.) 2025',             450, '2025-02-28', 'https://psc.wb.gov.in', 'https://psc.wb.gov.in'),
    ('psc-misc',      'WBPSC Miscellaneous 2025',   1780, '2025-05-31', 'https://psc.wb.gov.in', 'https://psc.wb.gov.in'),
    ('psc-clerkship', 'PSC Clerkship 2025',          600, '2025-06-30', 'https://psc.wb.gov.in', 'https://psc.wb.gov.in'),
    ('railway-ntpc-graduate','RRB NTPC Graduate 2025',11558,'2025-06-01','https://rrbapply.gov.in','https://rrbapply.gov.in'),
    ('railway-ntpc-ug',     'RRB NTPC UG 2025',    8113, '2025-06-01', 'https://rrbapply.gov.in', 'https://rrbapply.gov.in'),
    ('railway-group-d',     'RRB Group D 2025',   32438, '2025-08-31', 'https://rrbapply.gov.in', 'https://rrbapply.gov.in'),
    ('railway-technician',  'RRB Technician 2025',  9144, '2025-07-15', 'https://rrbapply.gov.in', 'https://rrbapply.gov.in'),
    ('police',        'WB Police Constable 2025',   4919, '2025-05-25', 'https://wbpolice.gov.in', 'https://wbpolice.gov.in'),
    ('police',        'WB Police SI (UNARMED) 2025',1043, '2025-06-10', 'https://wbpolice.gov.in', 'https://wbpolice.gov.in'),
]


def get_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        exam_key TEXT NOT NULL,
        title TEXT NOT NULL,
        date TEXT NOT NULL,
        link TEXT,
        source TEXT DEFAULT 'official',
        scraped_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS vacancies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        exam_key TEXT NOT NULL,
        title TEXT NOT NULL,
        post_count INTEGER DEFAULT 0,
        apply_link TEXT,
        last_date TEXT,
        result_link TEXT,
        scraped_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS scrape_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source TEXT,
        status TEXT,
        message TEXT,
        ran_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()

    row = c.execute('SELECT COUNT(*) FROM notifications').fetchone()
    if row[0] == 0:
        seed_db(c)
        conn.commit()
        log.info('Database seeded with initial data.')
    conn.close()


def seed_db(cursor):
    for item in SEED_NOTIFICATIONS:
        cursor.execute(
            'INSERT INTO notifications (exam_key, title, date, link, source) VALUES (?,?,?,?,?)',
            (item[0], item[1], item[2], item[3], 'seed')
        )
    for item in SEED_VACANCIES:
        cursor.execute(
            'INSERT INTO vacancies (exam_key, title, post_count, apply_link, last_date, result_link) VALUES (?,?,?,?,?,?)',
            item
        )


def get_notifications(exam_key, limit=10):
    conn = get_db()
    rows = conn.execute(
        'SELECT * FROM notifications WHERE exam_key=? ORDER BY date DESC, id DESC LIMIT ?',
        (exam_key, limit)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_vacancies(exam_key):
    conn = get_db()
    rows = conn.execute(
        'SELECT * FROM vacancies WHERE exam_key=? ORDER BY scraped_at DESC',
        (exam_key,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_notifications(limit=30):
    conn = get_db()
    rows = conn.execute(
        'SELECT * FROM notifications ORDER BY date DESC, id DESC LIMIT ?', (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def scrape_source(source_key, config):
    conn = get_db()
    c = conn.cursor()
    count = 0
    try:
        resp = requests.get(config['url'], headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'lxml')
        links = soup.find_all('a', href=True)
        today = date.today().isoformat()
        for a in links:
            text = a.get_text(strip=True)
            href = a['href']
            if not text or len(text) < 10:
                continue
            text_lower = text.lower()
            if not any(kw in text_lower for kw in config['keywords']):
                continue
            if not href.startswith('http'):
                from urllib.parse import urljoin
                href = urljoin(config['url'], href)
            exam_key = _classify(text_lower, source_key, config['exams'])
            existing = c.execute(
                'SELECT id FROM notifications WHERE exam_key=? AND title=?',
                (exam_key, text[:200])
            ).fetchone()
            if not existing:
                c.execute(
                    'INSERT INTO notifications (exam_key, title, date, link, source) VALUES (?,?,?,?,?)',
                    (exam_key, text[:200], today, href, 'scrape')
                )
                count += 1
        conn.commit()
        c.execute('INSERT INTO scrape_log (source, status, message) VALUES (?,?,?)',
                  (source_key, 'success', f'Added {count} new notifications'))
        conn.commit()
        log.info(f'Scraped {source_key}: {count} new items')
    except Exception as e:
        log.warning(f'Scrape failed for {source_key}: {e}')
        c.execute('INSERT INTO scrape_log (source, status, message) VALUES (?,?,?)',
                  (source_key, 'error', str(e)[:300]))
        conn.commit()
    finally:
        conn.close()
    return count


def _classify(text, source_key, exams):
    keywords_map = {
        'ssc-cgl':              ['cgl', 'combined graduate'],
        'ssc-chsl':             ['chsl', 'combined higher secondary'],
        'ssc-gd':               ['gd constable', 'gd '],
        'ssc-mts':              ['mts', 'multi tasking'],
        'wbcs':                 ['wbcs'],
        'psc-misc':             ['misc', 'miscellaneous'],
        'psc-clerkship':        ['clerk'],
        'railway-ntpc-graduate':['ntpc graduate', 'ntpc grad'],
        'railway-ntpc-ug':      ['ntpc ug', 'ntpc under'],
        'railway-group-d':      ['group d', 'grp d'],
        'railway-technician':   ['technician'],
        'police':               ['constable', 'si ', 'police'],
    }
    for exam_key in exams:
        kws = keywords_map.get(exam_key, [])
        if any(kw in text for kw in kws):
            return exam_key
    return exams[0]


def run_all_scrapers():
    log.info('Running all scrapers...')
    total = 0
    for key, config in SCRAPE_TARGETS.items():
        total += scrape_source(key, config)
    log.info(f'All scrapers done. Total new: {total}')
    return total


def get_scrape_logs(limit=20):
    conn = get_db()
    rows = conn.execute(
        'SELECT * FROM scrape_log ORDER BY ran_at DESC LIMIT ?', (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
