let currentLang = 'en';

function setLanguage(lang) {
    document.querySelectorAll('[data-en][data-bn]').forEach(el => {
        el.innerText = lang === 'bn' ? el.getAttribute('data-bn') : el.getAttribute('data-en');
    });
    document.querySelectorAll('input[data-en-placeholder][data-bn-placeholder]').forEach(input => {
        input.placeholder = lang === 'bn' ? input.getAttribute('data-bn-placeholder') : input.getAttribute('data-en-placeholder');
    });
    const btn = document.getElementById('langToggle');
    if (btn) btn.innerHTML = lang === 'bn' ? '🔁 English' : '🔁 বাংলা';
    currentLang = lang;
    localStorage.setItem('lang', lang);
}

document.addEventListener('DOMContentLoaded', () => {
    const saved = localStorage.getItem('lang') || 'en';
    setLanguage(saved);

    const toggleBtn = document.getElementById('langToggle');
    if (toggleBtn) {
        toggleBtn.addEventListener('click', () => setLanguage(currentLang === 'en' ? 'bn' : 'en'));
    }

    const subscribeBtn = document.getElementById('subscribeBtn');
    if (subscribeBtn) {
        subscribeBtn.addEventListener('click', () => {
            const emailInput = document.getElementById('emailInput');
            const email = emailInput ? emailInput.value : '';
            if (!email.trim()) {
                alert(currentLang === 'bn' ? 'দয়া করে আপনার ইমেল দিন।' : 'Please enter your email.');
            } else if (!email.includes('@')) {
                alert(currentLang === 'bn' ? 'সঠিক ইমেল দিন।' : 'Please enter a valid email.');
            } else {
                alert(currentLang === 'bn' ? 'ধন্যবাদ! আপনি সাবস্ক্রাইব করেছেন।' : 'Thank you! You have subscribed.');
                if (emailInput) emailInput.value = '';
            }
        });
    }

    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            const target = document.querySelector(targetId);
            if (target) { e.preventDefault(); target.scrollIntoView({ behavior: 'smooth' }); }
        });
    });

    const hamburger = document.getElementById('hamburger');
    const mainNav = document.getElementById('mainNav');
    if (hamburger && mainNav) {
        hamburger.addEventListener('click', () => {
            mainNav.classList.toggle('open');
            hamburger.textContent = mainNav.classList.contains('open') ? '✕' : '☰';
        });
    }

    const tabs = document.querySelectorAll('.tab-btn');
    tabs.forEach(btn => {
        btn.addEventListener('click', () => {
            tabs.forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            btn.classList.add('active');
            const target = document.getElementById('tab-' + btn.dataset.tab);
            if (target) target.classList.add('active');
        });
    });
});
