let currentLang = 'en';

function setLanguage(lang) {
    document.querySelectorAll('[data-en][data-bn]').forEach(el => {
        if (lang === 'bn') {
            el.innerText = el.getAttribute('data-bn');
        } else {
            el.innerText = el.getAttribute('data-en');
        }
    });
    document.querySelectorAll('input[data-en-placeholder][data-bn-placeholder]').forEach(input => {
        if (lang === 'bn') {
            input.placeholder = input.getAttribute('data-bn-placeholder');
        } else {
            input.placeholder = input.getAttribute('data-en-placeholder');
        }
    });
    const toggleBtn = document.getElementById('langToggle');
    if (toggleBtn) {
        toggleBtn.innerHTML = (lang === 'bn') ? '🔁 English' : '🔁 বাংলা';
    }
    currentLang = lang;
}

document.addEventListener('DOMContentLoaded', () => {
    const toggleBtn = document.getElementById('langToggle');
    if (toggleBtn) {
        toggleBtn.addEventListener('click', () => {
            setLanguage(currentLang === 'en' ? 'bn' : 'en');
        });
    }
    
    // সাবস্ক্রাইব বাটন
    const subscribeBtn = document.getElementById('subscribeBtn');
    if (subscribeBtn) {
        subscribeBtn.addEventListener('click', () => {
            const emailInput = document.getElementById('emailInput');
            const email = emailInput ? emailInput.value : '';
            if (email.trim() === '') {
                alert(currentLang === 'bn' ? 'দয়া করে আপনার ইমেল দিন।' : 'Please enter your email.');
            } else {
                alert(currentLang === 'bn' ? 'ধন্যবাদ! আপনি সাবস্ক্রাইব করেছেন।' : 'Thank you! You have subscribed.');
                emailInput.value = '';
            }
        });
    }
    
    // Smooth scroll for anchor links (Exams, About Us, Contact)
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                e.preventDefault();
                targetElement.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });
});

setLanguage('en');
