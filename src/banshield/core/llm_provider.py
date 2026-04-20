"""LLM provider factory for Azure OpenAI and Google Gemini."""

import os

from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI

load_dotenv()


def get_llm() -> AzureChatOpenAI:
    """Return a LangChain-compatible LLM based on LLM_PROVIDER env var."""
    provider = os.getenv("LLM_PROVIDER", "azure").lower()

    if provider == "azure":
        return AzureChatOpenAI(
            api_key=os.getenv("AZURE_API_KEY"),
            azure_endpoint=os.getenv("AZURE_ENDPOINT"),
            api_version=os.getenv("AZURE_API_VERSION"),
        )

    if provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(
            model="gemini-1.5-pro",
            api_key=os.getenv("GEMINI_API_KEY"),
        )

    raise ValueError(
        f"Invalid LLM_PROVIDER: '{provider}'. Accepted values: 'azure' or 'gemini'."
    )
