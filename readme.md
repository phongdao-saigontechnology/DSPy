# DSPy

This project implements an example for using DSPy, to solve math problems using large language models (LLMs). The example is based on the Stanford NLP DSPy, which demonstrates how to optimize a model for solving math problems using MIPROv2.

## Prerequisites

Before running the code, you'll need to install the required packages:

```bash
pip install -U dspy
pip install git+https://github.com/hendrycks/math.git
```

For OpenAI integration, you'll need to set your API key:

```bash
export OPENAI_API_KEY=your_api_key_here
```

## Training a Math Reasoning Model

The `train_math_reasoning.py` script allows you to train and optimize a math reasoning model:

```bash
python train_math_reasoning.py --model openai/gpt-4o-mini --teacher_model openai/gpt-4o --threads 4 --max_demos 4 --save_path math_model.json
```

Key arguments:
- `--model`: Model to use for default LM (default: openai/gpt-4o-mini)
- `--teacher_model`: Model to use as teacher (default: openai/gpt-4o)
- `--threads`: Number of threads for parallel processing (default: 4)
- `--max_demos`: Maximum number of demos to include in prompt (default: 4)
- `--save_path`: Path to save the optimized model (default: math_reasoning_model.pkl)
- `--eval_only`: Run evaluation only (no optimization)
- `--load_model`: Path to load a previously saved model

## Solving Math Problems

After training a model, you can use the `solve_math_problem.py` script to solve math problems:

```bash
python solve_math_problem.py --model_path math_model.json --problem "What is the smallest integer value of c such that the function f(x) = (x^2 + 1)/(x^2 - x + c) has domain of all real numbers?" --show_reasoning
```

Key arguments:
- `--model_path`: Path to the saved model (default: math_reasoning_model.pkl)
- `--lm`: LM to use for inference (default: openai/gpt-4o-mini)
- `--problem`: Math problem to solve (required)
- `--show_reasoning`: Show the reasoning steps

## Using Alternative Models

You can swap out OpenAI models for other LLM providers or local models. Refer to the [DSPy documentation](https://github.com/stanfordnlp/dspy) for more information.
