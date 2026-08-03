/**
 * Exam Guide India – Admin Panel JS
 * Placeholder for future CRUD interactions.
 * All buttons are non-functional in this architecture phase.
 */

(function () {
    'use strict';

    // ── Placeholder handler for all admin action buttons ───────────────────
    function onAdminAction(action, context) {
        // Will be replaced with real CRUD calls in a later phase
        const labels = {
            edit:      '✏️  Edit: ',
            delete:    '🗑️  Delete: ',
            add:       '➕  Add to: ',
            publish:   '✅  Publish: ',
            unpublish: '⏸️  Unpublish: ',
            reorder:   '↕️  Reorder: ',
        };
        console.info('[Admin] Action queued:', labels[action] || action, context || '');
        showAdminToast(labels[action] + (context || 'item') + ' — CRUD coming soon.', 'info');
    }

    // ── Toast notification ─────────────────────────────────────────────────
    function showAdminToast(message, type) {
        let container = document.getElementById('admin-toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'admin-toast-container';
            Object.assign(container.style, {
                position: 'fixed', bottom: '24px', right: '24px',
                zIndex: '99999', display: 'flex', flexDirection: 'column', gap: '8px',
            });
            document.body.appendChild(container);
        }

        const toast = document.createElement('div');
        const bg = type === 'info'    ? '#f5f3ff'
                 : type === 'success' ? '#f0fdf4'
                 : type === 'danger'  ? '#fff1f2'
                 : '#fffbeb';
        const border = type === 'info'    ? '#c4b5fd'
                     : type === 'success' ? '#bbf7d0'
                     : type === 'danger'  ? '#fecdd3'
                     : '#fed7aa';
        const color  = type === 'info'    ? '#4c1d95'
                     : type === 'success' ? '#15803d'
                     : type === 'danger'  ? '#be123c'
                     : '#92400e';

        Object.assign(toast.style, {
            padding: '10px 16px', borderRadius: '8px', fontSize: '0.78rem',
            fontWeight: '600', fontFamily: 'Poppins, sans-serif',
            background: bg, border: '1.5px solid ' + border, color: color,
            boxShadow: '0 4px 16px rgba(0,0,0,0.1)',
            maxWidth: '340px', lineHeight: '1.5',
            animation: 'adminFadeIn 0.2s ease',
        });
        toast.textContent = message;
        container.appendChild(toast);
        setTimeout(() => toast.remove(), 3500);
    }

    // ── Bind all admin buttons ─────────────────────────────────────────────
    function bindAdminButtons() {
        document.querySelectorAll('[data-admin-action]').forEach(function (el) {
            el.addEventListener('click', function (e) {
                e.preventDefault();
                e.stopPropagation();
                const action  = el.getAttribute('data-admin-action');
                const context = el.getAttribute('data-admin-context') || '';
                onAdminAction(action, context);
            });
        });
    }

    // ── Confirm before delete ──────────────────────────────────────────────
    function bindDeleteConfirm() {
        document.querySelectorAll('[data-admin-action="delete"]').forEach(function (el) {
            el.addEventListener('click', function (e) {
                e.preventDefault();
                e.stopPropagation();
                const context = el.getAttribute('data-admin-context') || 'this item';
                // Placeholder — real delete will show a modal in a later phase
                showAdminToast('🗑️ Delete "' + context + '" — confirmation modal coming soon.', 'danger');
            });
        }, true);
    }

    // ── Inject CSS keyframe for toast animation ────────────────────────────
    function injectAnimations() {
        if (document.getElementById('admin-anim-style')) return;
        const style = document.createElement('style');
        style.id = 'admin-anim-style';
        style.textContent = '@keyframes adminFadeIn { from { opacity:0; transform:translateY(8px); } to { opacity:1; transform:translateY(0); } }';
        document.head.appendChild(style);
    }

    // ── Init ───────────────────────────────────────────────────────────────
    document.addEventListener('DOMContentLoaded', function () {
        injectAnimations();
        bindAdminButtons();
        bindDeleteConfirm();
        console.info('[Admin Panel] Architecture mode active. CRUD handlers are placeholders.');
    });

})();
