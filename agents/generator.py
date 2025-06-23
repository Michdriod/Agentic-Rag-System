import os
from typing import List, Dict, Any
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from langchain.prompts import PromptTemplate

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL_NAME = os.getenv("GROQ_MODEL_NAME", "mixtral-8x7b-32768")

PROMPT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts")
SYSTEM_PROMPT_PATH = os.path.join(PROMPT_DIR, "system.txt")
USER_PROMPT_PATH = os.path.join(PROMPT_DIR, "user.txt")

def read_prompt(path: str) -> str:
    with open(path, "r") as f:
        return f.read()

SYSTEM_PROMPT = read_prompt(SYSTEM_PROMPT_PATH)
USER_PROMPT_TEMPLATE = read_prompt(USER_PROMPT_PATH)

# Use LangChain PromptTemplate for user prompt
generator_prompt = PromptTemplate(
    input_variables=["descriptions"],
    template=USER_PROMPT_TEMPLATE
)

class Generator:
    def __init__(self):
        # Initialize the LangChain Groq chat model
        self.llm = ChatGroq(
            api_key=GROQ_API_KEY,
            model=GROQ_MODEL_NAME,
            temperature=0.7,
            max_tokens=500
        )

    async def generate_suggestions(self, records: List[Dict[str, Any]]) -> List[str]:
        """Generate natural language suggestions based on retrieved records using LangChain Groq."""
        descriptions = [record['description'] for record in records]
        user_prompt = generator_prompt.format(descriptions=descriptions)
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_prompt)
        ]
        try:
            response = await self.llm.ainvoke(messages)
            content = response.content.strip()
            suggestions = content.split("\n")
            return [s.strip() for s in suggestions if s.strip()]
        except Exception as e:
            return [f"Error generating suggestions: {str(e)}"]
