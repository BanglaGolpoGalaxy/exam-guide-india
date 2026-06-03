const QUIZ_DATA = {
    wbcs1: {
        name: 'WBCS Prelims Mock',
        questions: [
            { q: 'Which river is known as the "Sorrow of Bengal"?', opts: ['Damodar', 'Hooghly', 'Teesta', 'Mahananda'], ans: 0 },
            { q: 'The capital of West Bengal is?', opts: ['Howrah', 'Kolkata', 'Durgapur', 'Asansol'], ans: 1 },
            { q: 'Who was the first Chief Minister of West Bengal?', opts: ['Bidhan Chandra Roy', 'Prafulla Ghosh', 'Siddharth Shankar Ray', 'Jyoti Basu'], ans: 1 },
            { q: 'The Sundarbans is a UNESCO World Heritage Site known for?', opts: ['Mountains', 'Mangrove forests & Royal Bengal Tiger', 'Deserts', 'Coral Reefs'], ans: 1 },
            { q: 'In which year was WBCS Exam first conducted?', opts: ['1947', '1950', '1956', '1951'], ans: 2 },
        ]
    },
    ssc_cgl1: {
        name: 'SSC CGL Tier-I Mock',
        questions: [
            { q: 'If 15% of A = 20% of B, then A:B =?', opts: ['4:3', '3:4', '17:16', '16:17'], ans: 0 },
            { q: 'Find the odd one out: 2, 5, 10, 17, 26, 37, 50, 64', opts: ['26', '37', '50', '64'], ans: 3 },
            { q: 'SSC stands for?', opts: ['Staff Selection Commission', 'State Service Commission', 'Secondary School Certificate', 'None'], ans: 0 },
            { q: 'The synonym of "Benevolent" is?', opts: ['Cruel', 'Kind', 'Angry', 'Greedy'], ans: 1 },
            { q: 'Which article of the Indian Constitution abolishes untouchability?', opts: ['Article 14', 'Article 15', 'Article 17', 'Article 21'], ans: 2 },
        ]
    },
    rrb_ntpc1: {
        name: 'RRB NTPC Mock',
        questions: [
            { q: 'Indian Railways was nationalised in which year?', opts: ['1947', '1950', '1951', '1953'], ans: 3 },
            { q: 'The fastest train in India is?', opts: ['Rajdhani Express', 'Vande Bharat Express', 'Shatabdi Express', 'Gatimaan Express'], ans: 1 },
            { q: 'What is 25% of 480?', opts: ['100', '110', '120', '130'], ans: 2 },
            { q: 'Which is the longest railway platform in India?', opts: ['Gorakhpur', 'Howrah', 'Prayagraj', 'Mumbai CST'], ans: 0 },
            { q: 'RRB stands for?', opts: ['Railway Recruitment Bureau', 'Railway Recruitment Board', 'Railway Registration Board', 'None'], ans: 1 },
        ]
    },
    psc_misc1: {
        name: 'PSC MISC Mock',
        questions: [
            { q: 'WBPSC stands for?', opts: ['West Bengal Primary School Commission', 'West Bengal Public Service Commission', 'West Bengal Police Service Commission', 'None'], ans: 1 },
            { q: 'The official language of West Bengal is?', opts: ['Hindi', 'English', 'Bengali', 'Both B and C'], ans: 3 },
            { q: 'Find the missing number: 2, 6, 12, 20, 30, __', opts: ['40', '42', '44', '48'], ans: 1 },
            { q: 'Who wrote "Gitanjali"?', opts: ['Bankimchandra', 'Rabindranath Tagore', 'Sharat Chandra', 'Sarat Chandra'], ans: 1 },
            { q: 'The Durand Cup is associated with which sport?', opts: ['Cricket', 'Hockey', 'Football', 'Badminton'], ans: 2 },
        ]
    },
    police1: {
        name: 'WB Police Mock',
        questions: [
            { q: 'PRB WB stands for?', opts: ['Police Registration Board WB', 'Police Recruitment Board WB', 'Police Regulation Body WB', 'None'], ans: 1 },
            { q: 'The minimum height for male candidates in WB Police Constable is?', opts: ['160 cm', '165 cm', '167 cm', '170 cm'], ans: 2 },
            { q: 'What is the capital of India?', opts: ['Mumbai', 'Kolkata', 'New Delhi', 'Chennai'], ans: 2 },
            { q: 'Which article grants the right to equality?', opts: ['Article 12', 'Article 14', 'Article 19', 'Article 21'], ans: 1 },
            { q: 'Find: 144 ÷ 12 × 3 + 5 – 2 =?', opts: ['37', '38', '39', '40'], ans: 0 },
        ]
    },
    ssc_gd1: {
        name: 'SSC GD Mock',
        questions: [
            { q: 'CRPF stands for?', opts: ['Central Reserve Police Force', 'Central Regular Police Force', 'Central Regional Police Force', 'None'], ans: 0 },
            { q: 'Which is the largest paramilitary force in the world?', opts: ['BSF', 'CRPF', 'CISF', 'SSB'], ans: 1 },
            { q: 'What is 12² + 5²?', opts: ['144', '169', '196', '225'], ans: 1 },
            { q: 'India got independence in?', opts: ['1945', '1946', '1947', '1948'], ans: 2 },
            { q: 'The antonym of "Courageous" is?', opts: ['Bold', 'Brave', 'Cowardly', 'Strong'], ans: 2 },
        ]
    },
};

let currentQuiz = null;
let currentQ = 0;
let score = 0;
let answered = false;

function startQuiz(id) {
    currentQuiz = QUIZ_DATA[id];
    if (!currentQuiz) return;
    currentQ = 0;
    score = 0;
    answered = false;
    document.getElementById('quizSelectionView').style.display = 'none';
    const container = document.getElementById('quizContainer');
    container.style.display = 'block';
    renderQuestion();
}

function renderQuestion() {
    if (!currentQuiz) return;
    const container = document.getElementById('quizContainer');
    if (currentQ >= currentQuiz.questions.length) {
        renderScore();
        return;
    }
    answered = false;
    const q = currentQuiz.questions[currentQ];
    const total = currentQuiz.questions.length;
    container.innerHTML = `
        <div class="quiz-q-num">Question ${currentQ + 1} of ${total} &nbsp;|&nbsp; ${currentQuiz.name} &nbsp;|&nbsp; Score: ${score}/${currentQ}</div>
        <div class="quiz-question">${q.q}</div>
        <div class="quiz-options">
            ${q.opts.map((opt, i) => `
                <button class="quiz-option" onclick="selectOption(${i})">${opt}</button>
            `).join('')}
        </div>
        <div class="quiz-nav">
            <button class="btn-back-home" onclick="exitQuiz()">✕ Exit Quiz</button>
            <button class="btn-apply-big" id="nextBtn" onclick="nextQuestion()" disabled>Next →</button>
        </div>
    `;
}

function selectOption(selectedIndex) {
    if (answered) return;
    answered = true;
    const q = currentQuiz.questions[currentQ];
    const options = document.querySelectorAll('.quiz-option');
    options.forEach((btn, i) => {
        btn.disabled = true;
        if (i === q.ans) btn.classList.add('correct');
        else if (i === selectedIndex) btn.classList.add('wrong');
    });
    if (selectedIndex === q.ans) score++;
    document.getElementById('nextBtn').disabled = false;
}

function nextQuestion() {
    currentQ++;
    renderQuestion();
}

function renderScore() {
    const container = document.getElementById('quizContainer');
    const total = currentQuiz.questions.length;
    const pct = Math.round((score / total) * 100);
    let msg = pct >= 80 ? '🌟 Excellent!' : pct >= 60 ? '👍 Good Job!' : pct >= 40 ? '📚 Keep Practicing!' : '💪 Don\'t Give Up!';
    container.innerHTML = `
        <div class="quiz-score">
            <div style="font-size:3rem; margin-bottom:12px;">${pct >= 60 ? '🏆' : '📚'}</div>
            <h2>${msg}</h2>
            <p>You scored <strong>${score} out of ${total}</strong> (${pct}%)</p>
            <div style="display:flex; gap:12px; justify-content:center; flex-wrap:wrap;">
                <button class="btn-apply-big" onclick="startQuiz('${Object.keys(QUIZ_DATA).find(k => QUIZ_DATA[k] === currentQuiz)}')">🔄 Retry Quiz</button>
                <button class="btn-back-home" onclick="exitQuiz()">← Choose Another</button>
            </div>
        </div>
    `;
}

function exitQuiz() {
    document.getElementById('quizSelectionView').style.display = 'block';
    document.getElementById('quizContainer').style.display = 'none';
    currentQuiz = null;
}
