"""
Admin Panel Routes
Mirrors every public page route but renders admin templates with edit controls.
"""
import os
from flask import render_template, redirect, url_for, session, request, flash, abort
from admin_panel import admin_bp
from admin_panel.decorators import admin_required

# ── Credentials (set ADMIN_PASSWORD env var in production) ──────────────────
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')


# ─────────────────────────────────────────────────────────────────────────────
# AUTH
# ─────────────────────────────────────────────────────────────────────────────

@admin_bp.route('/login', methods=['GET', 'POST'])
def admin_login():
    if session.get('is_admin'):
        return redirect(url_for('admin.admin_home'))
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['is_admin'] = True
            session.permanent = False
            return redirect(url_for('admin.admin_home'))
        error = 'Invalid credentials. Please try again.'
    return render_template('admin/login.html', error=error)


@admin_bp.route('/logout')
def admin_logout():
    session.pop('is_admin', None)
    return redirect(url_for('admin.admin_login'))


# ─────────────────────────────────────────────────────────────────────────────
# HOME
# ─────────────────────────────────────────────────────────────────────────────

@admin_bp.route('/')
@admin_required
def admin_home():
    return render_template('admin/home.html')


# ─────────────────────────────────────────────────────────────────────────────
# EXAM DASHBOARD  (mirrors /exam/<slug>/)
# ─────────────────────────────────────────────────────────────────────────────

@admin_bp.route('/exam/<slug>/')
@admin_required
def admin_exam_dashboard(slug):
    from app import EXAM_BY_SLUG
    exam = EXAM_BY_SLUG.get(slug)
    if not exam:
        abort(404)
    return render_template('admin/exam_dashboard.html', exam=exam, slug=slug)


# ─────────────────────────────────────────────────────────────────────────────
# EXAM SECTIONS
# ─────────────────────────────────────────────────────────────────────────────

@admin_bp.route('/exam/<slug>/notes/')
@admin_required
def admin_exam_notes(slug):
    from app import EXAM_BY_SLUG
    exam = EXAM_BY_SLUG.get(slug)
    if not exam:
        abort(404)
    return render_template('admin/exam_notes.html', exam=exam, slug=slug)


@admin_bp.route('/exam/<slug>/quiz/')
@admin_required
def admin_exam_quiz(slug):
    from app import EXAM_BY_SLUG
    exam = EXAM_BY_SLUG.get(slug)
    if not exam:
        abort(404)
    return render_template('admin/exam_quiz.html', exam=exam, slug=slug, mock_test=False)


@admin_bp.route('/exam/<slug>/mock-test/')
@admin_required
def admin_exam_mock_test(slug):
    from app import EXAM_BY_SLUG
    exam = EXAM_BY_SLUG.get(slug)
    if not exam:
        abort(404)
    return render_template('admin/exam_quiz.html', exam=exam, slug=slug, mock_test=True)


@admin_bp.route('/exam/<slug>/current-affairs/')
@admin_required
def admin_exam_current_affairs(slug):
    from app import EXAM_BY_SLUG
    exam = EXAM_BY_SLUG.get(slug)
    if not exam:
        abort(404)
    return render_template('admin/exam_current_affairs.html', exam=exam, slug=slug)


@admin_bp.route('/exam/<slug>/previous-papers/')
@admin_required
def admin_exam_papers(slug):
    from app import EXAM_BY_SLUG
    exam = EXAM_BY_SLUG.get(slug)
    if not exam:
        abort(404)
    return render_template('admin/exam_papers.html', exam=exam, slug=slug)


# ─────────────────────────────────────────────────────────────────────────────
# EXAM DETAIL / SYLLABUS PAGE  (mirrors /exam/<slug>/detail/ and police/railway sub-pages)
# ─────────────────────────────────────────────────────────────────────────────

@admin_bp.route('/exam/<slug>/detail/')
@admin_required
def admin_exam_detail(slug):
    from app import EXAM_BY_SLUG, EXAM_CONFIG, CATEGORY_CONFIG
    exam = EXAM_BY_SLUG.get(slug)
    if not exam:
        # fall back to EXAM_CONFIG (railway-group-d, police sub-exams)
        exam = EXAM_CONFIG.get(slug)
    if not exam:
        abort(404)
    category_key = exam.get('category', 'police')
    category = CATEGORY_CONFIG.get(category_key, {})
    return render_template('admin/exam_page.html', exam=exam, category=category, slug=slug)


# Police detail pages
@admin_bp.route('/police/wbp-constable/')
@admin_required
def admin_police_wbp_constable():
    from app import WBP_CONSTABLE, CATEGORY_CONFIG
    exam = {**WBP_CONSTABLE, 'detail_url': '/police/wbp-constable/', 'dashboard_url': '/exam/wbp-constable/'}
    category = CATEGORY_CONFIG.get('police', {})
    return render_template('admin/exam_page.html', exam=exam, category=category, slug='wbp-constable')


@admin_bp.route('/police/kolkata-police/')
@admin_required
def admin_police_kolkata():
    from app import KOLKATA_POLICE, CATEGORY_CONFIG
    exam = {**KOLKATA_POLICE, 'detail_url': '/police/kolkata-police/', 'dashboard_url': '/exam/kolkata-police/'}
    category = CATEGORY_CONFIG.get('police', {})
    return render_template('admin/exam_page.html', exam=exam, category=category, slug='kolkata-police')


@admin_bp.route('/railway/group-d/')
@admin_required
def admin_railway_group_d():
    from app import EXAM_CONFIG, CATEGORY_CONFIG
    exam = EXAM_CONFIG.get('railway-group-d', {})
    category = CATEGORY_CONFIG.get('railway', {})
    return render_template('admin/exam_page.html', exam=exam, category=category, slug='railway-group-d')


# ─────────────────────────────────────────────────────────────────────────────
# NOTES & QUIZ LISTING PAGES
# ─────────────────────────────────────────────────────────────────────────────

@admin_bp.route('/notes/')
@admin_required
def admin_notes():
    return render_template('admin/notes.html')


@admin_bp.route('/quiz/')
@admin_required
def admin_quiz():
    return render_template('admin/quiz.html')
