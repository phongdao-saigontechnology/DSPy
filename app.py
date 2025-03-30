import os
from typing import Optional

import dspy
import ujson
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

load_dotenv()

app = FastAPI(title="Math Reasoning Comparison")

# Set up templates and static files
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize global variables for models
base_module = None
optimized_module = None
default_lm = None


class MathProblem(BaseModel):
    problem: str


class MathResponse(BaseModel):
    reasoning: str
    answer: str
    execution_time: float


def load_models(model_path: Optional[str] = None):
    """Load the models for comparison."""

    # Set up the LM
    default_lm = dspy.LM(
        'azure/gpt-4o-mini',
        max_tokens=2000,
        api_base=os.environ.get("AZURE_OPENAI_ENDPOINT"),
        api_version=os.environ.get("OPENAI_API_VERSION"),
    )
    dspy.configure(lm=default_lm)



@app.on_event("startup")
async def startup_event():
    """Initialize models on startup."""
    # Default path, can be overridden by environment variable
    model_path = os.environ.get("OPTIMIZED_MODEL_PATH", "math_model.json")
    load_models(model_path)


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Render the main page."""
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "has_optimized_model": optimized_module is not None}
    )


@app.post("/solve/base", response_model=MathResponse)
async def solve_with_base(problem: MathProblem):
    """Solve math problem with the base model."""
    import time
    base_module = dspy.ChainOfThought("question -> answer")

    if not base_module:
        raise HTTPException(status_code=500, detail="Base model not initialized")

    start_time = time.time()
    result = base_module(question=problem.problem)
    end_time = time.time()

    return {
        "reasoning": result.reasoning,
        "answer": result.answer,
        "execution_time": round(end_time - start_time, 2)
    }


@app.post("/solve/optimized", response_model=MathResponse)
async def solve_with_optimized(problem: MathProblem):
    """Solve math problem with the optimized model."""
    import time
    model_path = os.environ.get("OPTIMIZED_MODEL_PATH", "math_model.json")

    try:
        with open(model_path, "r") as f:
            state = ujson.loads(f.read())
        optimized_module = dspy.ChainOfThought("question -> answer")
        optimized_module.load_state(state)
        print(f"Loaded optimized module from {model_path}")
    except Exception as e:
        print(f"Error loading optimized model: {e}")
        optimized_module = None
    start_time = time.time()
    result = optimized_module(question=problem.problem)
    end_time = time.time()

    return {
        "reasoning": result.reasoning,
        "answer": result.answer,
        "execution_time": round(end_time - start_time, 2),
    }


@app.get("/status")
async def get_status():
    """Get the status of the models."""
    return {
        "base_model_loaded": base_module is not None,
        "optimized_model_loaded": optimized_module is not None
    }


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
