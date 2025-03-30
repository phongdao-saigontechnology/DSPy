import argparse
import os

import dspy
import ujson


def setup_argparse():
    """Set up command line arguments."""
    parser = argparse.ArgumentParser(description='Train a math reasoning model using DSPy.')
    parser.add_argument('--model', type=str, default='openai/gpt-4o-mini',
                        help='Model to use for default LM (default: openai/gpt-4o-mini)')
    parser.add_argument('--teacher_model', type=str, default='openai/gpt-4o',
                        help='Model to use as teacher (default: openai/gpt-4o)')
    parser.add_argument('--threads', type=int, default=4,
                        help='Number of threads for parallel processing (default: 4)')
    parser.add_argument('--max_demos', type=int, default=4,
                        help='Maximum number of demos to include in prompt (default: 4)')
    parser.add_argument('--save_path', type=str, default='math_reasoning_model.pkl',
                        help='Path to save the optimized model (default: math_reasoning_model.pkl)')
    parser.add_argument('--eval_only', action='store_true',
                        help='Run evaluation only (no optimization)')
    parser.add_argument('--load_model', type=str, default=None,
                        help='Path to load a previously saved model')

    return parser.parse_args()


def setup_models(args):
    """Configure DSPy to use the specified language models."""
    default_lm = dspy.LM(
            "azure/gpt-4o-mini",
            api_base=os.environ.get("AZURE_OPENAI_ENDPOINT"),
            api_version=os.environ.get("OPENAI_API_VERSION"),
        )
    teacher_lm = dspy.LM(
            "azure/gpt-4o",
            api_base=os.environ.get("AZURE_OPENAI_ENDPOINT"),
            api_version=os.environ.get("OPENAI_API_VERSION"),
        )
    dspy.configure(lm=default_lm)

    return default_lm, teacher_lm


def load_dataset():
    """Load the MATH dataset (algebra subset)."""
    from dspy.datasets import MATH
    dataset = MATH(subset='algebra')
    print(f"Loaded {len(dataset.train)} training examples and {len(dataset.dev)} dev examples")

    # Display a sample example
    example = dataset.train[0]
    print("\nSample training example:")
    print(f"Question: {example.question}")
    print(f"Answer: {example.answer}")

    return dataset


def create_module():
    """Create a ChainOfThought module for math reasoning."""
    module = dspy.ChainOfThought("question -> answer")
    return module


def evaluate_module(module, dataset, args):
    """Evaluate the module on the dev set."""
    print("\nEvaluating module...")
    kwargs = dict(num_threads=args.threads, display_progress=True, display_table=5)
    evaluate = dspy.Evaluate(devset=dataset.dev, metric=dataset.metric, **kwargs)
    result = evaluate(module)
    return result


def optimize_module(module, dataset, args, default_lm, teacher_lm):
    """Optimize the module using MIPROv2."""
    print("\nOptimizing module...")
    kwargs = dict(
        num_threads=args.threads,
        teacher_settings=dict(lm=teacher_lm),
        prompt_model=default_lm
    )
    optimizer = dspy.MIPROv2(metric=dataset.metric, auto="medium", **kwargs)

    compile_kwargs = dict(
        requires_permission_to_run=False,
        max_bootstrapped_demos=args.max_demos,
        max_labeled_demos=args.max_demos
    )
    optimized_module = optimizer.compile(module, trainset=dataset.train, **compile_kwargs)

    return optimized_module


def save_module(module, path):
    """Save the optimized module to disk."""
    print(f"\nSaving module to {path}...")
    module.save(path)
    print(f"Module saved successfully!")


def load_module(path):
    """Load a previously saved module from disk."""
    print(f"\nLoading module from {path}...")
    with open(path, "r") as f:
        state = ujson.loads(f.read())
    optimized_module = dspy.ChainOfThought("question -> answer").load_state(state)
    print(f"Module loaded successfully!")
    return optimized_module


def main():
    args = setup_argparse()
    default_lm, teacher_lm = setup_models(args)
    dataset = load_dataset()

    # Set up MLflow for tracking. This is optional and can be removed if not needed.
    # import mlflow
    #
    # mlflow.set_tracking_uri("http://localhost:5000")
    # mlflow.set_experiment("DSPy")
    if args.load_model:
        # Load pre-existing model
        module = load_module(args.load_model)
    else:
        # Create new module
        module = create_module()
        print("\nTesting unoptimized module on a sample question...")
        example = dataset.train[0]
        result = module(question=example.question)
        print(f"Input: {example.question}")
        print(f"Output: {result}")

    # Evaluate the module
    evaluate_module(module, dataset, args)

    if not args.eval_only and not args.load_model:
        # Optimize the module
        optimized_module = optimize_module(module, dataset, args, default_lm, teacher_lm)

        # Evaluate the optimized module
        print("\nEvaluating optimized module...")
        evaluate_module(optimized_module, dataset, args)

        # Save the optimized module
        save_module(optimized_module, args.save_path)

        print("\nYou can now use the optimized module for inference!")
        print(f"To load it: 'with open('{args.save_path}', 'rb') as f: module = pickle.load(f)'")


if __name__ == "__main__":
    main()
