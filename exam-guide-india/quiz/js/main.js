// Simple quiz handler (demo)
const quizData = {
    wbcs1: {
        title: "WBCS Prelims Mock 1",
        questions: [
            { text: "ভারতের সংবিধান কত সালে গৃহীত হয়?", options: ["1947", "1950", "1952", "1949"], correct: 1 },
            { text: "পশ্চিমবঙ্গের রাজধানী?", options: ["কলকাতা", "দার্জিলিং", "হাওড়া", "শিলিগুড়ি"], correct: 0 },
            { text: "কোনটি রাষ্ট্রপতির অভিশংসনের ক্ষমতা রাখে?", options: ["সুপ্রিম কোর্ট", "লোকসভা", "রাজ্যসভা", "সংসদ"], correct: 3 }
        ]
    },
    ssc1: {
        title: "SSC CGL Quiz",
        questions: [
            { text: "Which is the largest planet?", options: ["Earth", "Mars", "Jupiter", "Saturn"], correct: 2 },
            { text: "Who wrote 'Discovery of India'?", options: ["Nehru", "Gandhi", "Tagore", "Ambedkar"], correct: 0 }
        ]
    },
    rrb1: {
        title: "Railway NTPC GK",
        questions: [
            { text: "Indian Railways was established in?", options: ["1853", "1947", "1905", "1860"], correct: 0 }
        ]
    }
};

function startQuiz(quizId) {
    const data = quizData[quizId];
    if (!data) return;
    const container = document.getElementById('quizContainer');
    container.style.display = 'block';
    let html = `<h3>${data.title}</h3>`;
    data.questions.forEach((q, idx) => {
        html += `<div class="question"><p><strong>${idx+1}. ${q.text}</strong></p><div class="options">`;
        q.options.forEach((opt, optIdx) => {
            html += `<label><input type="radio" name="q${idx}" value="${optIdx}"> ${opt}</label><br>`;
        });
        html += `</div></div>`;
    });
    html += `<button onclick="submitQuiz('${quizId}')">Submit Answers</button>`;
    container.innerHTML = html;
}

function submitQuiz(quizId) {
    const data = quizData[quizId];
    let score = 0;
    data.questions.forEach((q, idx) => {
        const selected = document.querySelector(`input[name="q${idx}"]:checked`);
        if (selected && parseInt(selected.value) === q.correct) score++;
    });
    const container = document.getElementById('quizContainer');
    container.innerHTML += `<div class="result-box">Your score: ${score} / ${data.questions.length}</div>`;
}
