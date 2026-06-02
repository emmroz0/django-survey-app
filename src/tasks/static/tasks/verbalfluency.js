(function () {
    const app = document.getElementById("verbalfluency-app");
    if (!app) {
        return;
    }

    const trialsDataEl = document.getElementById("trials-data");
    const trials = JSON.parse(trialsDataEl.textContent);

    const startBtn = document.getElementById("start-btn");
    const wordInput = document.getElementById("word-input");
    const addWordBtn = document.getElementById("add-word-btn");
    const wordInputWrap = document.getElementById("word-input-wrap");
    const wordListWrap = document.getElementById("word-list-wrap");
    const wordList = document.getElementById("word-list");
    const trialCategory = document.getElementById("trial-category");
    const trialLetter = document.getElementById("trial-letter");
    const timerValue = document.getElementById("timer-value");
    const resultPanel = document.getElementById("result-panel");
    const trialPanel = document.getElementById("trial-panel");

    let currentTrial = 0;
    let trialResults = [];
    let currentTrialWords = [];
    let timeLeft = 0;
    let timerInterval = null;
    let isRunning = false;

    function startTrial(index) {
        if (index >= trials.length) {
            finishTask();
            return;
        }

        const trial = trials[index];
        currentTrial = index;
        currentTrialWords = [];
        timeLeft = trial.time_limit;

        trialCategory.textContent = trial.category;
        trialLetter.textContent = trial.letter;
        timerValue.textContent = String(timeLeft);

        wordInputWrap.classList.remove("d-none");
        wordListWrap.classList.remove("d-none");
        wordList.innerHTML = "";
        wordInput.value = "";
        wordInput.disabled = false;
        wordInput.focus();
        addWordBtn.disabled = false;

        timerInterval = setInterval(function () {
            timeLeft--;
            timerValue.textContent = String(timeLeft);

            if (timeLeft <= 0) {
                clearInterval(timerInterval);
                endTrial();
            }
        }, 1000);
    }

    function endTrial() {
        wordInput.disabled = true;
        addWordBtn.disabled = true;
        wordInputWrap.classList.add("d-none");

        trialResults.push({
            trial_id: trials[currentTrial].id,
            letter: trials[currentTrial].letter,
            category: trials[currentTrial].category,
            time_limit: trials[currentTrial].time_limit,
            words: currentTrialWords.slice(),
        });

        setTimeout(function () {
            startTrial(currentTrial + 1);
        }, 1500);
    }

    function addWord() {
        if (!isRunning) return;

        const word = wordInput.value.trim().toLowerCase();
        if (!word) return;

        var firstLetter = trials[currentTrial].letter.toLowerCase();
        if (word[0] !== firstLetter) {
            wordInput.classList.add("is-invalid");
            setTimeout(function () {
                wordInput.classList.remove("is-invalid");
            }, 800);
            return;
        }

        var isDuplicate = currentTrialWords.some(function (w) {
            return w.toLowerCase() === word;
        });
        if (isDuplicate) {
            wordInput.classList.add("is-invalid");
            setTimeout(function () {
                wordInput.classList.remove("is-invalid");
            }, 800);
            return;
        }

        currentTrialWords.push(word);
        wordInput.value = "";
        wordInput.focus();

        var li = document.createElement("li");
        li.className = "list-group-item d-flex justify-content-between align-items-center";
        li.innerHTML = '<span>' + word + '</span><span class="badge bg-primary rounded-pill">' + currentTrialWords.length + '</span>';
        wordList.appendChild(li);
    }

    function finishTask() {
        isRunning = false;
        trialPanel.classList.add("d-none");
        startBtn.classList.add("d-none");
        resultPanel.classList.remove("d-none");

        fetch("/tasks/verbalfluency/result/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                trials: trialResults,
            }),
        });
    }

    wordInput.addEventListener("keydown", function (e) {
        if (e.key === "Enter") {
            e.preventDefault();
            addWord();
        }
    });

    addWordBtn.addEventListener("click", function () {
        addWord();
    });

    startBtn.addEventListener("click", function () {
        isRunning = true;
        startBtn.classList.add("d-none");
        startTrial(0);
    });
})();
