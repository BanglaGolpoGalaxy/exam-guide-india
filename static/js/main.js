let currentLang = 'en';

const TRANSLATIONS = {
    en: {
        langBtn: '🔁 বাংলা',
        subscribeSuccess: '✅ Thank you! You\'ve subscribed successfully.',
        subscribeInvalid: 'Please enter a valid email address.',
    },
    bn: {
        langBtn: '🔁 English',
        subscribeSuccess: '✅ ধন্যবাদ! আপনি সফলভাবে সাবস্ক্রাইব করেছেন।',
        subscribeInvalid: 'সঠিক ইমেল ঠিকানা দিন।',
    }
};

function setLanguage(lang) {
    document.querySelectorAll('[data-en][data-bn]').forEach(el => {
        el.innerText = lang === 'bn' ? el.getAttribute('data-bn') : el.getAttribute('data-en');
    });
    document.querySelectorAll('input[data-en-placeholder][data-bn-placeholder]').forEach(input => {
        input.placeholder = lang === 'bn' ? input.getAttribute('data-bn-placeholder') : input.getAttribute('data-en-placeholder');
    });
    const btn = document.getElementById('langToggle');
    if (btn) btn.innerHTML = TRANSLATIONS[lang].langBtn;
    currentLang = lang;
    localStorage.setItem('lang', lang);
}

function handleSubscribe(e) {
    e.preventDefault();
    const emailInput = document.getElementById('emailInput');
    const msgEl = document.getElementById('subscribeMsg');
    if (!emailInput) return;
    const email = emailInput.value.trim();
    if (!email || !email.includes('@') || !email.includes('.')) {
        if (msgEl) {
            msgEl.style.display = 'block';
            msgEl.style.color = '#f87171';
            msgEl.innerText = TRANSLATIONS[currentLang].subscribeInvalid;
        } else {
            alert(TRANSLATIONS[currentLang].subscribeInvalid);
        }
        return;
    }
    if (msgEl) {
        msgEl.style.display = 'block';
        msgEl.style.color = '#86efac';
        msgEl.innerText = TRANSLATIONS[currentLang].subscribeSuccess;
    }
    emailInput.value = '';
    setTimeout(() => { if (msgEl) msgEl.style.display = 'none'; }, 4000);
}

document.addEventListener('DOMContentLoaded', () => {
    const saved = localStorage.getItem('lang') || 'en';
    setLanguage(saved);

    const toggleBtn = document.getElementById('langToggle');
    if (toggleBtn) {
        toggleBtn.addEventListener('click', () => setLanguage(currentLang === 'en' ? 'bn' : 'en'));
    }

    // Hamburger
    const hamburger = document.getElementById('hamburger');
    const mainNav = document.getElementById('mainNav');
    if (hamburger && mainNav) {
        hamburger.addEventListener('click', () => {
            mainNav.classList.toggle('open');
            hamburger.textContent = mainNav.classList.contains('open') ? '✕' : '☰';
        });
        document.addEventListener('click', (e) => {
            if (!hamburger.contains(e.target) && !mainNav.contains(e.target)) {
                mainNav.classList.remove('open');
                hamburger.textContent = '☰';
            }
        });
    }

    // Tabs
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const tabGroup = btn.closest('.container') || document;
            tabGroup.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            tabGroup.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            btn.classList.add('active');
            const target = document.getElementById('tab-' + btn.dataset.tab);
            if (target) target.classList.add('active');
        });
    });

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            const target = document.querySelector(targetId);
            if (target) { e.preventDefault(); target.scrollIntoView({ behavior: 'smooth', block: 'start' }); }
        });
    });

    // Mobile dropdown toggle
    document.querySelectorAll('.dropdown-trigger').forEach(trigger => {
        trigger.addEventListener('click', (e) => {
            if (window.innerWidth <= 768) {
                e.stopPropagation();
                const menu = trigger.closest('.nav-dropdown')?.querySelector('.dropdown-menu');
                if (menu) menu.style.display = menu.style.display === 'block' ? 'none' : 'block';
            }
        });
    });

    // Active nav link highlight
    const path = window.location.pathname;
    document.querySelectorAll('.nav-link[href]').forEach(link => {
        if (link.getAttribute('href') === path || (path !== '/' && path.startsWith(link.getAttribute('href')) && link.getAttribute('href') !== '/')) {
            link.classList.add('active');
        }
    });
});
