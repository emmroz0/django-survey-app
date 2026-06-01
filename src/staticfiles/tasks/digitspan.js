(function () {
    const app = document.getElementById("digitspan-app");
    if (!app) {
        return;
    }

    const initialSpan = 2
    const digitDelay = 800

    const startBtn = document.getElementById("start-btn");
    const digitCard = document.getElementById("digit-card");
    const answerInput = document.getElementById("answer-input");
    const answerWrap = document.getElementById("answer-wrap");

    let currentSpan = initialSpan;
    let currentSequence = [];
    let started = false;
    let isRunning = false;

    function generateSequence(span) {
        return Array.from({ length: span }, () => Math.floor(Math.random() * 10));
    }


    function showSequence(sequence) {
        let index = 0;
        let showingGap = false;
        const gapDuration = 200;
        digitCard.textContent = "\u00A0";

        const interval = setInterval(() => {
            if (index >= sequence.length) {
                clearInterval(interval);
                digitCard.textContent = "\u00A0";
                answerWrap.classList.remove("d-none");
                answerInput.disabled = false;
                answerInput.value = "";
                answerInput.focus();
                startBtn.disabled = false;
                isRunning = false;
                return;
            }

            if (showingGap) {
                digitCard.textContent = "\u00A0";
                showingGap = false;
                index++;
                return;
            }

            digitCard.textContent = String(sequence[index]);
            showingGap = true;
        }, digitDelay - gapDuration);
    }


    function startRound() {
        answerWrap.classList.add("d-none");
        answerInput.disabled = true;
        startBtn.disabled = true;
        digitCard.classList.remove("d-none");
        digitCard.textContent = "\u00A0";

        isRunning = true;
        currentSequence = generateSequence(currentSpan);
        showSequence(currentSequence);
    }


    function sendResult() {
        const sequence = currentSequence;
        const answer = answerInput.value.trim();

        fetch("/tasks/digitspan/result/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                span: currentSpan,
                sequence: sequence,
                answer: answer,
            }),
        });
    }


    startBtn.addEventListener("click", () => {
        if (isRunning) {
            return;
        }

        if (!started) {
            started = true;
            startBtn.textContent = "Dalej";
            startRound();
            return;
        }

        sendResult();
        currentSpan++;
        startRound();
    });
})();
