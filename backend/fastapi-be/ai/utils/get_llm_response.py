from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_groq import ChatGroq
import os

GROQ_API_KEY = str(os.getenv("GROQ_API_KEY"))

models = [
    "deepseek-r1-distill-llama-70b",
    "llama-3.1-8b-instant"
]

llm = ChatGroq(
    temperature=0.0,
    model=models[0],  
    api_key=GROQ_API_KEY
)

def get_llm_response(prompt: str,system_prompt:str) -> str|None:
    """
    Get a response from the LLM using the provided prompt.
    
    Args:
        prompt (str): The input prompt for the LLM.
        
    Returns:
        str: The response from the LLM.
    """
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY environment variable is not set.")

    try:
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=prompt)
        ]
        
        response = llm.invoke(messages).content.strip()
        return response if response else None
    except Exception as e:
        print(f"Error getting LLM response: {e}")
        return None