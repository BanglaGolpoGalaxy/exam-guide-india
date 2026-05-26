// ভাষা টগল ফাংশন
let currentLang = 'en'; // 'en' অথবা 'bn'

function setLanguage(lang) {
    // সব এলিমেন্ট যাদের data-en ও data-bn আছে
    document.querySelectorAll('[data-en][data-bn]').forEach(el => {
        if (lang === 'bn') {
            el.innerText = el.getAttribute('data-bn');
        } else {
            el.innerText = el.getAttribute('data-en');
        }
    });
    
    // প্লেসহোল্ডার আপডেট (যেমন ইনপুট ফিল্ড)
    document.querySelectorAll('input[data-en-placeholder][data-bn-placeholder]').forEach(input => {
        if (lang === 'bn') {
            input.placeholder = input.getAttribute('data-bn-placeholder');
        } else {
            input.placeholder = input.getAttribute('data-en-placeholder');
        }
    });
    
    // টগল বাটনের টেক্সট পরিবর্তন
    const toggleBtn = document.getElementById('langToggle');
    if (toggleBtn) {
        toggleBtn.innerHTML = (lang === 'bn') ? '🔁 English' : '🔁 বাংলা';
    }
    
    currentLang = lang;
}

// ইভেন্ট লিসেনার – ডোম লোড হলে
document.addEventListener('DOMContentLoaded', () => {
    const toggleBtn = document.getElementById('langToggle');
    if (toggleBtn) {
        toggleBtn.addEventListener('click', () => {
            if (currentLang === 'en') {
                setLanguage('bn');
            } else {
                setLanguage('en');
            }
        });
    }
    
    // সাবস্ক্রাইব বাটনের জন্য অ্যালার্ট (ডেমো)
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
});

// ডিফল্ট ভাষা ইংরেজি সেট (যেহেতু HTML-এ data-en দেখানো আছে)
setLanguage('en');
