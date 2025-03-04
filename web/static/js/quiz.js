// Quiz management functionality
const quizState = {
    currentQuestion: 0,
    score: 0,
    questions: [],
    selectedDifficulty: '',
    selectedSubject: '',
    timeLeft: 0,
    timer: null
};

function startQuiz(subject, difficulty) {
    quizState.selectedSubject = subject;
    quizState.selectedDifficulty = difficulty;
    quizState.currentQuestion = 0;
    quizState.score = 0;
    
    // Fetch questions from server
    fetch(`/api/questions?subject=${subject}&difficulty=${difficulty}`)
        .then(response => response.json())
        .then(data => {
            quizState.questions = data;
            displayQuestion();
            startTimer();
        });
}

function displayQuestion() {
    const question = quizState.questions[quizState.currentQuestion];
    document.getElementById('question-text').textContent = question.text;
    
    const optionsContainer = document.getElementById('options-container');
    optionsContainer.innerHTML = '';
    
    ['A', 'B', 'C', 'D'].forEach(option => {
        const button = document.createElement('button');
        button.className = 'option-button btn btn-outline-primary';
        button.textContent = question[`option_${option.toLowerCase()}`];
        button.onclick = () => checkAnswer(option);
        optionsContainer.appendChild(button);
    });
}

function checkAnswer(selectedOption) {
    const question = quizState.questions[quizState.currentQuestion];
    const buttons = document.querySelectorAll('.option-button');
    
    buttons.forEach(button => {
        button.disabled = true;
    });

    if(selectedOption === question.correct_answer) {
        quizState.score++;
        document.querySelector(`button:contains('${selectedOption}')`).classList.add('correct-answer');
    } else {
        document.querySelector(`button:contains('${selectedOption}')`).classList.add('wrong-answer');
        document.querySelector(`button:contains('${question.correct_answer}')`).classList.add('correct-answer');
    }

    setTimeout(() => {
        quizState.currentQuestion++;
        if(quizState.currentQuestion < quizState.questions.length) {
            displayQuestion();
        } else {
            endQuiz();
        }
    }, 1500);
}

function startTimer() {
    quizState.timeLeft = 600; // 10 minutes
    updateTimerDisplay();
    
    quizState.timer = setInterval(() => {
        quizState.timeLeft--;
        updateTimerDisplay();
        
        if(quizState.timeLeft <= 0) {
            endQuiz();
        }
    }, 1000);
}

function updateTimerDisplay() {
    const minutes = Math.floor(quizState.timeLeft / 60);
    const seconds = quizState.timeLeft % 60;
    document.getElementById('timer').textContent = 
        `${minutes}:${seconds.toString().padStart(2, '0')}`;
}

function endQuiz() {
    clearInterval(quizState.timer);
    
    // Calculate rewards based on difficulty
    let reward = 0;
    switch(quizState.selectedDifficulty) {
        case 'easy':
            reward = quizState.score * 5 + (quizState.score === 10 ? 10 : 0);
            break;
        case 'medium':
            reward = quizState.score * 10 + (quizState.score === 10 ? 25 : 0);
            break;
        case 'hard':
            reward = quizState.score * 15 + (quizState.score === 10 ? 50 : 0);
            break;
    }

    // Send results to server
    fetch('/api/quiz-complete', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            score: quizState.score,
            reward: reward,
            subject: quizState.selectedSubject,
            difficulty: quizState.selectedDifficulty
        })
    }).then(() => {
        window.location.href = `/quiz-result?score=${quizState.score}&reward=${reward}`;
    });
}

// Shop functionality
function purchaseItem(itemId, cost) {
    fetch('/api/purchase', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            itemId: itemId,
            cost: cost
        })
    })
    .then(response => response.json())
    .then(data => {
        if(data.success) {
            updateCoins(data.newBalance);
            showToast('Purchase successful!');
        } else {
            showToast('Not enough coins!', 'error');
        }
    });
}

function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast ${type === 'success' ? 'bg-success' : 'bg-danger'} text-white`;
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

function updateCoins(newBalance) {
    document.getElementById('coin-balance').textContent = newBalance;
}
