import argparse
import json

import dspy


def setup_argparse():
    """Set up command line arguments."""
    parser = argparse.ArgumentParser(description='Solve math problems using a trained DSPy model.')
    parser.add_argument('--model_path', type=str, default='math_reasoning_model.pkl',
                        help='Path to the saved model (default: math_reasoning_model.pkl)')
    parser.add_argument('--lm', type=str, default='openai/gpt-4o-mini',
                        help='LM to use for inference (default: openai/gpt-4o-mini)')
    parser.add_argument('--problem', type=str, required=True,
                        help='Math problem to solve')
    parser.add_argument('--show_reasoning', action='store_true',
                        help='Show the reasoning steps')

    return parser.parse_args()


def load_model(path):
    """Load a saved model from disk."""
    try:
        with open(path, 'rb') as f:
            module = json.load(f)
        return module
    except Exception as e:
        print(f"Error loading model: {e}")
        return None


def main():
    args = setup_argparse()

    # Configure DSPy with the specified LM
    lm = dspy.LM(args.lm, max_tokens=2000)
    dspy.configure(lm=lm)

    # Load the model
    module = load_model(args.model_path)
    if not module:
        return

    # Solve the problem
    result = module(question=args.problem)

    # Display the results
    print("\n=== Math Problem Solver ===")
    print(f"\nProblem: {args.problem}")

    if args.show_reasoning:
        print("\nReasoning:")
        print(result.reasoning)

    print("\nAnswer:")
    print(result.answer)


if __name__ == "__main__":
    main()
