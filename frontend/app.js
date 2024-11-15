const API_BASE_URL = 'http://127.0.0.1:8000/api/v1';

let participantId = null;
let questions = [];
let currentQuestionIndex = 0;

// Welcome Page Form Submission
document.getElementById('participant-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    const age = document.getElementById('age').value;
    const education = document.getElementById('education').value;
    const familiarity = document.getElementById('familiarity').value;
    const studied = document.getElementById('studied').checked;

    // Create participant
    const response = await fetch(`${API_BASE_URL}/participants/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            age,
            education,
            hugo_style_familiarity: familiarity,
            studied_french_literature: studied,
        }),
    });
    const data = await response.json();
    participantId = data.id;

    // Fetch questionnaire
    const questionnaireResponse = await fetch(`${API_BASE_URL}/questionnaire`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ participant_id: participantId }),
    });
    const questionnaireData = await questionnaireResponse.json();
    questions = questionnaireData.questions;

    // Update total questions
    document.getElementById('total-questions').textContent = questions.length;

    // Show quiz page
    document.getElementById('welcome-page').style.display = 'none';
    document.getElementById('quiz-page').style.display = 'block';
    loadQuestion();
});

// Load a question
function loadQuestion() {
    const question = questions[currentQuestionIndex];
    document.getElementById('current-question').textContent = currentQuestionIndex + 1;
    document.getElementById('question-category').textContent = `Catégorie : ${question.category}`;
    document.getElementById('left-text').textContent = `Gauche : ${question.left}`;
    document.getElementById('right-text').textContent = `Droite : ${question.right}`;
}

// Next Question Button
document.getElementById('next-btn').addEventListener('click', async () => {
    const choice = document.querySelector('input[name="choice"]:checked').value;

    // Submit answer
    await fetch(`${API_BASE_URL}/answers/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            question_id: currentQuestionIndex + 1,
            choice,
        }),
    });

    // Go to next question or finish
    currentQuestionIndex++;
    if (currentQuestionIndex < questions.length) {
        loadQuestion();
    } else {
        document.getElementById('quiz-page').style.display = 'none';
        document.getElementById('thank-you-page').style.display = 'block';
    }
});
