from typing import Type, TypeVar
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.language_models import BaseChatModel
from langchain_core.runnables import Runnable


load_dotenv()

T = TypeVar("T", bound=BaseModel)


def create_llm(
    model: str,
    temperature: float,
    response_model: Type[T] | None = None,
) -> BaseChatModel | Runnable:
    """
    Create an LLM instance based on the model name.

    Args:
        model: The provider and name of the model (e.g., "openai/gpt-4o", "google/gemini-2.0-flash")
        temperature: The temperature setting for the model
        response_model: Optional Pydantic model for structured output

    Returns:
        An instance of BaseChatModel configured for the specified model
    """
    llm: BaseChatModel
    if model.startswith(("openai/")):
        model = model.replace("openai/", "")
        llm = ChatOpenAI(
            temperature=temperature,
            model=model,
        )
    elif model.startswith("anthropic/"):
        model = model.replace("anthropic/", "")
        llm = ChatAnthropic(
            temperature=temperature,
            model_name=model,
            timeout=None,
            stop=None,
        )
    elif model.startswith("google/"):
        model = model.replace("google/", "")
        llm = ChatGoogleGenerativeAI(
            model=model,
            temperature=temperature,
        )
    else:
        raise ValueError(
            f"Unsupported model: {model}. Make sure you added prefix for provider (openai/, anthropic/, google/)"
        )

    if response_model:
        return llm.with_structured_output(response_model)

    return llm
