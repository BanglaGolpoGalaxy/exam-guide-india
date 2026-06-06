async function initExamPage(examKey) {
    await Promise.all([
        loadNotifications(examKey),
        loadVacancies(examKey),
    ]);
}

async function loadNotifications(examKey) {
    const container = document.getElementById('notifList');
    if (!container) return;
    try {
        const res = await fetch(`/api/notifications?exam=${encodeURIComponent(examKey)}&limit=15`);
        const data = await res.json();
        if (!data || data.length === 0) {
            container.innerHTML = `<div class="empty-state"><div class="es-icon">📭</div><p>No notifications yet. Check back soon or visit the <a href="#" onclick="document.querySelector('[data-tab=\\'overview\\']').click()">official site</a>.</p></div>`;
            return;
        }
        container.innerHTML = data.map(n => `
            <a href="${n.link || '#'}" target="_blank" rel="noopener" class="notif-row">
                <span class="notif-date-tag">${formatDate(n.date)}</span>
                <span class="notif-row-title">${escHtml(n.title)}</span>
                ${n.link ? '<span class="notif-row-link">↗ View</span>' : ''}
            </a>
        `).join('');
    } catch (e) {
        container.innerHTML = `<div class="empty-state"><div class="es-icon">⚠️</div><p>Could not load notifications. Please try again later.</p></div>`;
    }
}

async function loadVacancies(examKey) {
    const container = document.getElementById('vacancyList');
    if (!container) return;
    try {
        const res = await fetch(`/api/vacancies?exam=${encodeURIComponent(examKey)}`);
        const data = await res.json();
        if (!data || data.length === 0) {
            container.innerHTML = `<div class="empty-state"><div class="es-icon">📋</div><p>No vacancies currently listed. New vacancies are added automatically when announced.</p></div>`;
            return;
        }
        container.innerHTML = data.map(v => `
            <div class="vacancy-card">
                <div>
                    <div class="vc-title">${escHtml(v.title)}</div>
                    <div class="vc-meta">
                        ${v.post_count ? `<span>👥 <strong>${Number(v.post_count).toLocaleString()}</strong> Posts</span>` : ''}
                        ${v.last_date  ? `<span>📅 Last Date: <strong>${formatDate(v.last_date)}</strong></span>` : ''}
                    </div>
                </div>
                <div class="vc-actions">
                    ${v.apply_link  ? `<a href="${v.apply_link}"  target="_blank" rel="noopener" class="btn-apply-sm">📋 Apply</a>` : ''}
                    ${v.result_link ? `<a href="${v.result_link}" target="_blank" rel="noopener" class="btn-result-sm">📊 Result</a>` : ''}
                </div>
            </div>
        `).join('');
    } catch (e) {
        container.innerHTML = `<div class="empty-state"><div class="es-icon">⚠️</div><p>Could not load vacancies. Please try again later.</p></div>`;
    }
}

function formatDate(dateStr) {
    if (!dateStr) return '';
    try {
        const d = new Date(dateStr + 'T00:00:00');
        return d.toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' });
    } catch { return dateStr; }
}

function escHtml(str) {
    if (!str) return '';
    return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}
