import os
from typing import List, Dict, Any
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL_NAME = os.getenv("GROQ_MODEL_NAME")

# Optimized prompts for your use case
SUGGESTION_SYSTEM_PROMPT = """You are a financial insights assistant. Your job is to convert transaction analysis data into clear, actionable suggestions.

Rules:
1. Generate exactly 3 distinct suggestions
2. Each suggestion should be practical and actionable
3. Make suggestions relevant to personal finance management
4. Keep each suggestion to 1-2 sentences
5. Focus on helping users improve their financial habits"""

QUERY_SYSTEM_PROMPT = """You are a financial advisor AI. You analyze transaction data and provide comprehensive, helpful answers.

Rules:
1. Provide one clear, comprehensive answer
2. Base your response on the provided context
3. If the context doesn't fully address the question, say so
4. Give practical, actionable advice when appropriate
5. Be conversational but professional"""

class Generator:
    def __init__(self):
        self.name = "generator"
        try:
            self.llm = ChatGroq(
                api_key=GROQ_API_KEY,
                model=GROQ_MODEL_NAME,
                temperature=0.7,
                max_tokens=500
            )
            print("Generator initialized successfully")
        except Exception as e:
            print(f"Error initializing Generator: {e}")
            raise

    async def generate_suggestions(self, records: List[Dict[str, Any]]) -> List[Dict]:
        """Generate 3 actionable suggestions based on retrieved records."""
        if not records:
            return [
                {"suggestion": "Track your daily expenses to understand spending patterns", "confidence": 0.5},
                {"suggestion": "Set up a monthly budget to better manage your finances", "confidence": 0.5},
                {"suggestion": "Review your transactions weekly to identify savings opportunities", "confidence": 0.5}
            ]
        
        try:
            # Prepare context from records
            context_items = []
            for i, record in enumerate(records[:3], 1):
                desc = record.get('description', record.get('suggestion', ''))
                confidence = record.get('confidence', 0.0)
                context_items.append(f"{i}. {desc} (confidence: {confidence:.2f})")
            
            context = "\n".join(context_items)
            
            user_prompt = f"""Based on these transaction insights, generate exactly 3 practical financial suggestions:

{context}

Format your response as exactly 3 numbered suggestions, each on a new line:
1. [First suggestion]
2. [Second suggestion] 
3. [Third suggestion]"""

            messages = [
                SystemMessage(content=SUGGESTION_SYSTEM_PROMPT),
                HumanMessage(content=user_prompt)
            ]
            
            response = await self.llm.ainvoke(messages)
            content = response.content.strip()
            
            # Parse the numbered suggestions
            suggestions = []
            lines = content.split('\n')
            
            for line in lines:
                line = line.strip()
                if line and (line.startswith(('1.', '2.', '3.')) or line.startswith(('1)', '2)', '3)'))):
                    # Remove the number and period/parenthesis
                    suggestion_text = line[2:].strip() if line[1] in '.):' else line[3:].strip()
                    if suggestion_text:
                        suggestions.append(suggestion_text)
            
            # Ensure we have exactly 3 suggestions
            while len(suggestions) < 3:
                suggestions.append("Consider reviewing your spending patterns for improvement opportunities")
            
            # Format with confidence scores
            result = []
            for i, suggestion in enumerate(suggestions[:3]):
                confidence = records[i].get('confidence', 0.8) if i < len(records) else 0.5
                result.append({
                    "suggestion": suggestion,
                    "confidence": confidence
                })
            
            return result
            
        except Exception as e:
            print(f"Error generating suggestions: {e}")
            return [
                {"suggestion": f"Error generating suggestions: {str(e)}", "confidence": 0.0},
                {"suggestion": "Please try your request again", "confidence": 0.0},
                {"suggestion": "Contact support if the issue persists", "confidence": 0.0}
            ]

    async def generate_answer(self, records: List[Dict[str, Any]], query: str) -> str:
        """Generate a comprehensive answer based on retrieved context."""
        if not records:
            return "I don't have enough transaction data to answer your question. Please ensure your database contains relevant financial insights."
        
        try:
            # Prepare context from records
            context_items = []
            for record in records:
                desc = record.get('description', '')
                confidence = record.get('confidence', 0.0)
                if desc:
                    context_items.append(f"• {desc} (relevance: {confidence:.2f})")
            
            context = "\n".join(context_items)
            
            user_prompt = f"""User Question: {query}

Relevant Transaction Insights:
{context}

Please provide a comprehensive answer based on this financial data. If the context doesn't fully address the question, mention what information might be missing."""

            messages = [
                SystemMessage(content=QUERY_SYSTEM_PROMPT),
                HumanMessage(content=user_prompt)
            ]
            
            response = await self.llm.ainvoke(messages)
            return response.content.strip()
            
        except Exception as e:
            print(f"Error generating answer: {e}")
            return f"I encountered an error while analyzing your question: {str(e)}. Please try rephrasing your question or check if your database contains relevant transaction data."





# import os
# from typing import List, Dict, Any
# from dotenv import load_dotenv
# from langchain_groq import ChatGroq
# from langchain_core.messages import SystemMessage, HumanMessage
# from langchain.prompts import PromptTemplate

# load_dotenv()

# GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# GROQ_MODEL_NAME = os.getenv("GROQ_MODEL_NAME", "llama-3.1-8b-instant")

# PROMPT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts")
# SUGGESTION_SYSTEM_PROMPT_PATH = os.path.join(PROMPT_DIR, "suggestions_system.txt")
# SUGGESTION_USER_PROMPT_PATH = os.path.join(PROMPT_DIR, "suggestions_user.txt")
# QUERY_SYSTEM_PROMPT_PATH = os.path.join(PROMPT_DIR, "query_system.txt")
# QUERY_USER_PROMPT_PATH = os.path.join(PROMPT_DIR, "query_user.txt")

# def read_prompt(path: str) -> str:
#     with open(path, "r") as f:
#         return f.read()

# SUGGESTION_SYSTEM_PROMPT = read_prompt(SUGGESTION_SYSTEM_PROMPT_PATH)
# SUGGESTION_USER_PROMPT_TEMPLATE = read_prompt(SUGGESTION_USER_PROMPT_PATH)
# QUERY_SYSTEM_PROMPT = read_prompt(QUERY_SYSTEM_PROMPT_PATH)
# QUERY_USER_PROMPT_TEMPLATE = read_prompt(QUERY_USER_PROMPT_PATH)


# # Use LangChain PromptTemplate for user prompt
# suggestions_prompt = PromptTemplate(
#     input_variables=["descriptions"],
#     template=SUGGESTION_USER_PROMPT_TEMPLATE
# )

# query_prompt = PromptTemplate(
#     input_variables=["descriptions"],
#     template=QUERY_USER_PROMPT_TEMPLATE
# )

# class Generator:
#     def __init__(self):
#         self.name = "generator"
#         # Initialize the LangChain Groq chat model
#         self.llm = ChatGroq(
#             api_key=GROQ_API_KEY,
#             model=GROQ_MODEL_NAME,
#             temperature=0.7,
#             max_tokens=500
#         )

#     async def generate_suggestions(self, records: List[Dict[str, Any]]) -> List[dict]:
#         """Generate natural language suggestions based on retrieved records using LangChain Groq."""
#         descriptions = [record.get('suggestion', record.get('description', '')) for record in records]
#         user_prompt = suggestions_prompt.format(descriptions=descriptions)
#         messages = [
#             SystemMessage(content=SUGGESTION_SYSTEM_PROMPT),
#             HumanMessage(content=user_prompt)
#         ]
#         try:
#             response = await self.llm.ainvoke(messages)
#             content = response.content.strip()
#             suggestions = [s.strip() for s in content.split("\n") if s.strip()]
#             # Attach confidence if available from input records
#             return [
#                 {
#                     "suggestion": s,
#                     "confidence": records[i]["confidence"] if i < len(records) and "confidence" in records[i] else None
#                 }
#                 for i, s in enumerate(suggestions)
#             ]
#         except Exception as e:
#             return [{"suggestion": f"Error generating suggestions: {str(e)}", "confidence": None}]

#     async def generate_answer(self, records: List[Dict[str, Any]], query: str) -> str:
#         """Generate a synthesized answer using the LLM and the top retrieved records as context."""
#         descriptions = [record['description'] for record in records]
#         user_prompt = query_prompt.format(descriptions=descriptions)
#         messages = [
#             SystemMessage(content=QUERY_SYSTEM_PROMPT),
#             HumanMessage(content=f"User question: {query}\n\nContext:\n" + user_prompt)
#         ]
#         try:
#             response = await self.llm.ainvoke(messages)
#             return response.content.strip()
#         except Exception as e:
#             return f"Error generating answer: {str(e)}"


# import os
# from typing import List, Dict, Any
# from dotenv import load_dotenv
# from langchain_groq import ChatGroq
# from langchain_core.messages import SystemMessage, HumanMessage
# from langchain.prompts import PromptTemplate
# import logging

# load_dotenv()

# GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# GROQ_MODEL_NAME = os.getenv("GROQ_MODEL_NAME")

# def read_prompt(path: str) -> str:
#     """Read prompt from file, log a warning and return empty string if file doesn't exist."""
#     try:
#         if os.path.exists(path):
#             with open(path, "r") as f:
#                 return f.read()
#         else:
#             logging.warning(f"Prompt file not found: {path}, returning empty string")
#             return ""
#     except Exception as e:
#         logging.error(f"Error reading prompt file {path}: {e}, returning empty string")
#         return ""

# # Try to read prompts from files, fallback to defaults
# PROMPT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts")
# SUGGESTION_SYSTEM_PROMPT_PATH = os.path.join(PROMPT_DIR, "suggestions_system.txt")
# SUGGESTION_USER_PROMPT_PATH = os.path.join(PROMPT_DIR, "suggestions_user.txt")
# QUERY_SYSTEM_PROMPT_PATH = os.path.join(PROMPT_DIR, "query_system.txt")
# QUERY_USER_PROMPT_PATH = os.path.join(PROMPT_DIR, "query_user.txt")

# SUGGESTION_SYSTEM_PROMPT = read_prompt(SUGGESTION_SYSTEM_PROMPT_PATH)
# SUGGESTION_USER_PROMPT_TEMPLATE = read_prompt(SUGGESTION_USER_PROMPT_PATH)
# QUERY_SYSTEM_PROMPT = read_prompt(QUERY_SYSTEM_PROMPT_PATH)
# QUERY_USER_PROMPT_TEMPLATE = read_prompt(QUERY_USER_PROMPT_PATH)

# # Create LangChain PromptTemplates
# suggestions_prompt = PromptTemplate(
#     input_variables=["descriptions"],
#     template=SUGGESTION_USER_PROMPT_TEMPLATE
# )

# query_prompt = PromptTemplate(
#     input_variables=["descriptions"],
#     template=QUERY_USER_PROMPT_TEMPLATE
# )

# class Generator:
#     def __init__(self):
#         self.name = "generator"
#         # Initialize the LangChain Groq chat model
#         try:
#             self.llm = ChatGroq(
#                 api_key=GROQ_API_KEY,
#                 model=GROQ_MODEL_NAME,
#                 temperature=0.7,
#                 max_tokens=500
#             )
#             print("Generator initialized successfully")
#         except Exception as e:
#             print(f"Error initializing Generator: {e}")
#             raise

#     async def generate_suggestions(self, records: List[Dict[str, Any]]) -> List[dict]:
#         """Generate natural language suggestions based on retrieved records using LangChain Groq."""
#         if not records:
#             return [{"suggestion": "No relevant data found for suggestions.", "confidence": 0.0}]
        
#         try:
#             # Extract descriptions from records
#             descriptions = []
#             for record in records:
#                 desc = record.get('suggestion', record.get('description', ''))
#                 if desc:
#                     descriptions.append(desc)
            
#             if not descriptions:
#                 return [{"suggestion": "No valid descriptions found.", "confidence": 0.0}]
            
#             # Format descriptions as numbered list
#             formatted_descriptions = "\n".join([f"{i+1}. {desc}" for i, desc in enumerate(descriptions)])
#             user_prompt = suggestions_prompt.format(descriptions=formatted_descriptions)
            
#             messages = [
#                 SystemMessage(content=SUGGESTION_SYSTEM_PROMPT),
#                 HumanMessage(content=user_prompt)
#             ]
            
#             response = await self.llm.ainvoke(messages)
#             content = response.content.strip()
            
#             # Parse suggestions from response
#             suggestions = [s.strip() for s in content.split("\n") if s.strip()]
            
#             # Ensure we have at least one suggestion
#             if not suggestions:
#                 suggestions = ["Unable to generate specific suggestions from the provided data."]
            
#             # Attach confidence if available from input records
#             result = []
#             for i, suggestion in enumerate(suggestions):
#                 confidence = records[i].get("confidence") if i < len(records) else 0.5
#                 result.append({
#                     "suggestion": suggestion,
#                     "confidence": confidence
#                 })
            
#             return result
            
#         except Exception as e:
#             print(f"Error generating suggestions: {e}")
#             return [{"suggestion": f"Error generating suggestions: {str(e)}", "confidence": 0.0}]

#     async def generate_answer(self, records: List[Dict[str, Any]], query: str) -> str:
#         """Generate a synthesized answer using the LLM and the top retrieved records as context."""
#         if not records:
#             return "I don't have enough context to answer your question. Please try rephrasing or asking about different topics."
        
#         try:
#             # Extract descriptions from records
#             descriptions = []
#             for record in records:
#                 desc = record.get('description', record.get('suggestion', ''))
#                 if desc:
#                     descriptions.append(desc)
            
#             if not descriptions:
#                 return "No relevant information found to answer your question."
            
#             # Format descriptions
#             formatted_descriptions = "\n".join([f"- {desc}" for desc in descriptions])
#             context_prompt = query_prompt.format(descriptions=formatted_descriptions)
            
#             messages = [
#                 SystemMessage(content=QUERY_SYSTEM_PROMPT),
#                 HumanMessage(content=f"User question: {query}\n\n{context_prompt}")
#             ]
            
#             response = await self.llm.ainvoke(messages)
#             return response.content.strip()
            
#         except Exception as e:
#             print(f"Error generating answer: {e}")
#             return f"I encountered an error while processing your question: {str(e)}"