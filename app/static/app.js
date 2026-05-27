let currentQuestion = null;

const votingArea = document.getElementById('voting-area');
const resultsArea = document.getElementById('results-area');
const choiceA = document.getElementById('choice-a');
const choiceB = document.getElementById('choice-b');
const textA = document.getElementById('text-a');
const textB = document.getElementById('text-b');
const nextBtn = document.getElementById('next-btn');
const addForm = document.getElementById('add-form');
const addFeedback = document.getElementById('add-feedback');
const subtitle = document.getElementById('subtitle');

function showVotingState(question) {
    currentQuestion = question;
    textA.textContent = question.option_a;
    textB.textContent = question.option_b;
    choiceA.disabled = false;
    choiceB.disabled = false;
    subtitle.textContent = 'Clique sur ton choix !';
    resultsArea.hidden = true;
    votingArea.hidden = false;
}

function showResultsState(question, userChoice) {
    const votesA = parseInt(question.votes_a) || 0;
    const votesB = parseInt(question.votes_b) || 0;
    const total = votesA + votesB;
    const pctA = total > 0 ? Math.round((votesA / total) * 100) : 0;
    const pctB = total > 0 ? Math.round((votesB / total) * 100) : 0;

    document.getElementById('your-choice-text').textContent =
        userChoice === 'A' ? question.option_a : question.option_b;
    document.getElementById('result-text-a').textContent = question.option_a;
    document.getElementById('result-text-b').textContent = question.option_b;
    document.getElementById('result-percent-a').textContent = pctA + '%';
    document.getElementById('result-percent-b').textContent = pctB + '%';
    document.getElementById('vote-count-a').textContent =
        votesA + (votesA <= 1 ? ' vote' : ' votes');
    document.getElementById('vote-count-b').textContent =
        votesB + (votesB <= 1 ? ' vote' : ' votes');

    // Marquer le gagnant
    document.getElementById('result-a').classList.toggle('winner', votesA > votesB);
    document.getElementById('result-b').classList.toggle('winner', votesB > votesA);

    subtitle.textContent = 'Voilà les résultats !!!';
    votingArea.hidden = true;
    resultsArea.hidden = false;

    // Animation des barres
    document.getElementById('bar-fill-a').style.width = '0%';
    document.getElementById('bar-fill-b').style.width = '0%';
    setTimeout(() => {
        document.getElementById('bar-fill-a').style.width = pctA + '%';
        document.getElementById('bar-fill-b').style.width = pctB + '%';
    }, 100);
}

async function loadRandomQuestion() {
    try {
        const res = await fetch('/api/questions/random');
        if (!res.ok) throw new Error('Erreur API');
        const question = await res.json();
        showVotingState(question);
    } catch (err) {
        textA.textContent = 'Erreur de chargement :(';
        textB.textContent = 'Réessaie plus tard';
    }
}

async function vote(choice) {
    if (!currentQuestion) return;
    choiceA.disabled = true;
    choiceB.disabled = true;

    try {
        const res = await fetch(`/api/questions/${currentQuestion.id}/vote`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ choice })
        });
        if (!res.ok) throw new Error('Erreur vote');
        const updated = await res.json();
        showResultsState(updated, choice);
    } catch (err) {
        alert('Erreur lors du vote');
        choiceA.disabled = false;
        choiceB.disabled = false;
    }
}

choiceA.addEventListener('click', () => vote('A'));
choiceB.addEventListener('click', () => vote('B'));
nextBtn.addEventListener('click', loadRandomQuestion);

addForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const a = document.getElementById('new-a').value.trim();
    const b = document.getElementById('new-b').value.trim();

    try {
        const res = await fetch('/api/questions', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ option_a: a, option_b: b })
        });
        if (!res.ok) throw new Error('Erreur ajout');
        addFeedback.textContent = 'Question ajoutée avec succès !';
        addFeedback.className = 'success';
        addForm.reset();
        setTimeout(() => { addFeedback.textContent = ''; }, 3000);
    } catch (err) {
        addFeedback.textContent = 'Erreur lors de l\'ajout';
        addFeedback.className = 'error';
    }
});

loadRandomQuestion();