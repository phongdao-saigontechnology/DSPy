document.addEventListener('DOMContentLoaded', function() {
    const problemInput = document.getElementById('problem-input');
    const solveButton = document.getElementById('solve-button');
    const loadingIndicator = document.getElementById('loading');
    const errorContainer = document.getElementById('error-container');

    // Result containers
    const baseReasoning = document.getElementById('base-reasoning');
    const baseAnswer = document.getElementById('base-answer');
    const baseTime = document.getElementById('base-time');
    const optimizedReasoning = document.getElementById('optimized-reasoning');
    const optimizedAnswer = document.getElementById('optimized-answer');
    const optimizedTime = document.getElementById('optimized-time');

    // Example problems for quick testing
    const exampleProblems = [
        "What is the smallest integer value of c such that the function f(x) = (x^2 + 1)/(x^2 - x + c) has domain of all real numbers?",
        "If |4x+2|=10 and x<0, what is the value of x?",
        "The doctor has told Cal O'Ree that during his ten weeks of working out at the gym, he can expect each week's weight loss to be 1% of his weight at the end of the previous week. His weight at the beginning of the workouts is 244 pounds. How many pounds does he expect to weigh at the end of the ten weeks? Express your answer to the nearest whole number."
    ];

    // Add some example problems
    problemInput.placeholder = "Enter a math problem or try one of our examples...";

    // Set up enter key handler
    problemInput.addEventListener('keydown', function(event) {
        if (event.key === 'Enter') {
            solveProblem();
        }
    });

    // Set up solve button handler
    solveButton.addEventListener('click', solveProblem);

    // Main function to solve the problem
    function solveProblem() {
        const problem = problemInput.value.trim();

        if (!problem) {
            showError("Please enter a math problem");
            return;
        }

        // Clear previous results
        resetResults();

        // Show loading indicator
        loadingIndicator.classList.remove('d-none');
        errorContainer.classList.add('d-none');

        // Make API calls in parallel
        const basePromise = fetchSolution(problem, 'base');
        const optimizedPromise = fetchSolution(problem, 'optimized');

        // Handle both responses
        Promise.all([basePromise, optimizedPromise])
            .then(([baseResult, optimizedResult]) => {
                // Update the UI with results
                displayResults(baseResult, optimizedResult);

                // Typeset math expressions
                if (window.MathJax) {
                    MathJax.typeset();
                }
            })
            .catch(error => {
                showError(error.message || "An error occurred while solving the problem");
            })
            .finally(() => {
                loadingIndicator.classList.add('d-none');
            });
    }

    // Fetch solution from API
    async function fetchSolution(problem, modelType) {
        try {
            const response = await fetch(`/solve/${modelType}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ problem })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `Error from ${modelType} model: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error(`Error fetching ${modelType} solution:`, error);
            throw error;
        }
    }

    // Display results in UI
    function displayResults(baseResult, optimizedResult) {
        // Base model results
        baseReasoning.textContent = baseResult.reasoning;
        baseAnswer.textContent = baseResult.answer;
        baseTime.textContent = baseResult.execution_time;

        // Optimized model results
        optimizedReasoning.textContent = optimizedResult.reasoning;
        optimizedAnswer.textContent = optimizedResult.answer;
        optimizedTime.textContent = optimizedResult.execution_time;

        // Highlight differences in answers if they don't match
        if (baseResult.answer !== optimizedResult.answer) {
            baseAnswer.classList.add('different');
            optimizedAnswer.classList.add('different');
        }
    }

    // Reset all result fields
    function resetResults() {
        baseReasoning.textContent = '';
        baseAnswer.textContent = '';
        baseTime.textContent = '-';
        optimizedReasoning.textContent = '';
        optimizedAnswer.textContent = '';
        optimizedTime.textContent = '-';

        baseAnswer.classList.remove('different');
        optimizedAnswer.classList.remove('different');
    }

    // Show error message
    function showError(message) {
        errorContainer.textContent = message;
        errorContainer.classList.remove('d-none');
        loadingIndicator.classList.add('d-none');
    }

    // Programmatically fill in an example problem
    document.querySelector('.form-text').addEventListener('click', function() {
        const randomIndex = Math.floor(Math.random() * exampleProblems.length);
        problemInput.value = exampleProblems[randomIndex];
    });
});
