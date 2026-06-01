(function () {
    const app = document.getElementById("sart-app");
    if (!app) {
        return;
    }

    const totalTrials = 30;
    const trialDuration = 300;
    const gapDuration = 700;
    const noGoDigit = 3;

    const startBtn = document.getElementById("start-btn");
    const responseBtn = document.getElementById("response-btn");
    const digitDisplay = document.getElementById("digit-display");

    let sequence = [];
    let trials = [];
    let isRunning = false;
    let currentTrial = 0;
    let trialStartTime = 0;
    let isTrialActive = false;
    let hasResponded = false;

    function generateSequence() {
        return Array.from({ length: totalTrials }, () => Math.floor(Math.random() * 10));
    }

    function runTrial(index) {
        if (index >= totalTrials) {
            finishTest();
            return;
        }

        const digit = sequence[index];
        digitDisplay.textContent = String(digit);
        responseBtn.disabled = false;
        currentTrial = index;
        trialStartTime = performance.now();
        isTrialActive = true;
        hasResponded = false;

        setTimeout(() => {
            digitDisplay.textContent = "\u00A0";

            setTimeout(() => {
                isTrialActive = false;
                responseBtn.disabled = true;

                if (!hasResponded) {
                    trials.push({
                        digit: digit,
                        clicked: false,
                        rt_ms: null,
                        correct: digit === noGoDigit,
                    });
                }

                runTrial(index + 1);
            }, gapDuration);
        }, trialDuration);
    }

    function finishTest() {
        responseBtn.disabled = true;
        digitDisplay.textContent = "\u00A0";
        startBtn.disabled = false;
        startBtn.textContent = "Zakończono";
        startBtn.disabled = true;
        isRunning = false;

        const commissionErrors = trials.filter(function (t) {
            return t.digit === noGoDigit && t.clicked;
        }).length;
        const omissionErrors = trials.filter(function (t) {
            return t.digit !== noGoDigit && !t.clicked;
        }).length;
        const reactionTimes = trials
            .filter(function (t) { return t.rt_ms !== null; })
            .map(function (t) { return t.rt_ms; });
        const meanRt = reactionTimes.length > 0
            ? Math.round(reactionTimes.reduce(function (a, b) { return a + b; }, 0) / reactionTimes.length * 10) / 10
            : null;

        fetch("/tasks/sart/result/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                sequence: sequence,
                trials: trials,
                commission_errors: commissionErrors,
                omission_errors: omissionErrors,
                mean_reaction_time: meanRt,
            }),
        });
    }

    responseBtn.addEventListener("click", function () {
        if (!isTrialActive || hasResponded) return;

        hasResponded = true;
        const digit = sequence[currentTrial];
        const rtMs = Math.round(performance.now() - trialStartTime);

        trials.push({
            digit: digit,
            clicked: true,
            rt_ms: rtMs,
            correct: digit !== noGoDigit,
        });
    });

    startBtn.addEventListener("click", function () {
        if (isRunning) return;
        isRunning = true;

        sequence = generateSequence();
        trials = [];
        startBtn.disabled = true;

        runTrial(0);
    });
})();
