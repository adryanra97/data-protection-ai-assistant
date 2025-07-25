"""
QA Engine - Multi-Agent Legal Question Answering System

This module implements the core question-answering engine that orchestrates
multiple agents to provide comprehensive legal answers.

Author: Adryan R A
"""

import logging
import json
from typing import Dict, List, Optional, Any, Tuple
from langchain.memory import ConversationBufferMemory
from langchain_openai import AzureChatOpenAI
from langchain.schema import BaseMessage, HumanMessage, SystemMessage

from .tools import ToolManager
from ..core.config import settings

logger = logging.getLogger(__name__)


class QAEngineError(Exception):
    """Custom exception for QA engine errors."""
    pass


class QAEngine:
    """
    Multi-agent question answering engine for legal queries.
    
    This class orchestrates multiple agents including tool selection,
    document retrieval, web search, and response synthesis to provide
    comprehensive answers to legal questions.
    """
    
    def __init__(self, tool_manager: ToolManager):
        """
        Initialize the QA engine.
        
        Args:
            tool_manager (ToolManager): Configured tool manager instance
        """
        self.tool_manager = tool_manager
        self.tools = tool_manager.get_tools()
        
        # Initialize Azure OpenAI LLM
        try:
            self.llm = AzureChatOpenAI(
                openai_api_key=settings.OPENAI_CHAT_API_KEY,
                azure_endpoint=settings.CHAT_OPENAI_API_BASE,
                openai_api_version="2024-12-01-preview",
                azure_deployment=settings.CHAT_MODEL_NAME,
                temperature=0.1,  # Low temperature for consistent legal advice
                max_tokens=2000,
                request_timeout=60
            )
        except Exception as e:
            logger.error(f"Failed to initialize Azure OpenAI: {e}")
            raise QAEngineError(f"LLM initialization failed: {e}")
        
        # Initialize conversation memory
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            max_token_limit=4000
        )
        
        # Query attempt tracking to prevent infinite loops
        self.attempt_counter = {}
        self.max_attempts = 3
        
        # System prompts
        self.tool_selector_prompt = self._create_tool_selector_prompt()
        self.legal_expert_prompt = self._create_legal_expert_prompt()
        self.relevance_checker_prompt = self._create_relevance_checker_prompt()
    
    def answer(self, query: str, context: Optional[str] = None) -> str:
        """
        Generate a comprehensive answer to a legal question.
        
        Args:
            query (str): User's legal question
            context (Optional[str]): Additional context or uploaded document content
            
        Returns:
            str: Comprehensive legal answer
        """
        try:
            logger.info(f"Processing query: {query[:100]}...")
            
            # Track query attempts
            attempt_count = self.attempt_counter.get(query, 0)
            
            # Step 1: Select relevant tools
            selected_tools = self._select_tools(query)
            logger.debug(f"Selected tools: {selected_tools}")
            
            # Step 2: Retrieve information from selected tools
            retrieved_content = self._retrieve_information(query, selected_tools)
            
            # Step 3: Handle case when no relevant content is found
            if not retrieved_content:
                return self._handle_no_content(query, attempt_count)
            
            # Step 4: Check relevance for web search results
            if list(retrieved_content.keys()) == ["tavily"]:
                if not self._check_relevance(query, retrieved_content["tavily"]):
                    return self._handle_no_content(query, attempt_count)
            
            # Step 5: Generate final answer
            final_answer = self._synthesize_answer(query, retrieved_content, context)
            
            # Step 6: Update conversation memory
            self._update_memory(query, final_answer)
            
            # Reset attempt counter on success
            self.attempt_counter[query] = 0
            
            return final_answer
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return f"I apologize, but I encountered an error while processing your question: {str(e)}"
    
    def _select_tools(self, query: str) -> List[str]:
        """
        Select the most relevant tools for the given query.
        
        Args:
            query (str): User's question
            
        Returns:
            List[str]: List of selected tool names
        """
        try:
            messages = [
                SystemMessage(content=self.tool_selector_prompt),
                HumanMessage(content=f"User question: {query}")
            ]
            
            response = self.llm(messages)
            
            # Parse the response to extract tool names
            try:
                # Expect response in format like: ['gdpr', 'pdp'] or ['tavily']
                selected = eval(response.content.strip())
                if isinstance(selected, list):
                    # Validate tool names
                    valid_tools = [tool for tool in selected if tool in self.tools]
                    if valid_tools:
                        return valid_tools
            except:
                pass
            
            # Fallback: use keyword matching
            return self._fallback_tool_selection(query)
            
        except Exception as e:
            logger.error(f"Tool selection failed: {e}")
            return self._fallback_tool_selection(query)
    
    def _fallback_tool_selection(self, query: str) -> List[str]:
        """
        Fallback tool selection based on keyword matching.
        
        Args:
            query (str): User's question
            
        Returns:
            List[str]: List of selected tool names
        """
        query_lower = query.lower()
        selected_tools = []
        
        # GDPR-related keywords
        if any(keyword in query_lower for keyword in 
               ['gdpr', 'general data protection', 'european', 'eu data']):
            selected_tools.append('gdpr')
        
        # UU PDP-related keywords
        if any(keyword in query_lower for keyword in 
               ['uu pdp', 'indonesia', 'indonesian data protection', 'undang-undang']):
            selected_tools.append('pdp')
        
        # Company policy keywords
        if any(keyword in query_lower for keyword in 
               ['company', 'internal', 'organizational', 'corporate policy']):
            selected_tools.append('company')
        
        # If no specific tools selected, use all document tools
        if not selected_tools:
            selected_tools = ['gdpr', 'pdp', 'company']
        
        # Add web search as fallback
        if len(selected_tools) == 0 or 'recent' in query_lower or 'latest' in query_lower:
            selected_tools.append('tavily')
        
        return selected_tools
    
    def _retrieve_information(self, query: str, tool_names: List[str]) -> Dict[str, str]:
        """
        Retrieve information using selected tools.
        
        Args:
            query (str): User's question
            tool_names (List[str]): Names of tools to use
            
        Returns:
            Dict[str, str]: Retrieved content from each tool
        """
        retrieved_content = {}
        
        for tool_name in tool_names:
            try:
                tool = self.tools.get(tool_name)
                if tool:
                    result = tool.func(query)
                    if result and result.strip():
                        retrieved_content[tool_name] = result
                        logger.debug(f"Retrieved content from {tool_name}: {len(result)} chars")
                else:
                    logger.warning(f"Tool {tool_name} not found")
            except Exception as e:
                logger.error(f"Error retrieving from {tool_name}: {e}")
        
        # If no content retrieved and tavily not tried, try web search
        if not retrieved_content and 'tavily' not in tool_names:
            try:
                tavily_tool = self.tools.get('tavily')
                if tavily_tool:
                    result = tavily_tool.func(query)
                    if result and result.strip():
                        retrieved_content['tavily'] = result
            except Exception as e:
                logger.error(f"Fallback tavily search failed: {e}")
        
        return retrieved_content
    
    def _check_relevance(self, query: str, content: str) -> bool:
        """
        Check if web search content is relevant to the query.
        
        Args:
            query (str): Original query
            content (str): Content to check
            
        Returns:
            bool: True if content is relevant
        """
        try:
            messages = [
                SystemMessage(content=self.relevance_checker_prompt),
                HumanMessage(content=f"Query: {query}\n\nContent:\n{content[:1000]}")
            ]
            
            response = self.llm(messages)
            return 'relevant' in response.content.lower()
            
        except Exception as e:
            logger.error(f"Relevance check failed: {e}")
            return True  # Assume relevant if check fails
    
    def _synthesize_answer(self, query: str, content: Dict[str, str], 
                          context: Optional[str] = None) -> str:
        """
        Synthesize a comprehensive answer from retrieved content.
        
        Args:
            query (str): Original query
            content (Dict[str, str]): Retrieved content from tools
            context (Optional[str]): Additional context
            
        Returns:
            str: Synthesized answer
        """
        try:
            # Prepare source content
            source_content = "\n\n".join([
                f"--- {source.upper()} SOURCE ---\n{text}"
                for source, text in content.items()
            ])
            
            # Add context if provided
            if context:
                source_content = f"--- USER PROVIDED CONTEXT ---\n{context}\n\n{source_content}"
            
            # Get conversation history
            history_messages = self.memory.chat_memory.messages[-6:]  # Last 3 exchanges
            
            # Create synthesis prompt
            messages = history_messages + [
                SystemMessage(content=self.legal_expert_prompt),
                HumanMessage(content=f"Question: {query}\n\nSource Information:\n{source_content}")
            ]
            
            response = self.llm(messages)
            return response.content
            
        except Exception as e:
            logger.error(f"Answer synthesis failed: {e}")
            return "I apologize, but I encountered an error while synthesizing the answer."
    
    def _handle_no_content(self, query: str, attempt_count: int) -> str:
        """
        Handle cases where no relevant content is found.
        
        Args:
            query (str): Original query
            attempt_count (int): Number of previous attempts
            
        Returns:
            str: Response for no content scenarios
        """
        if attempt_count < self.max_attempts:
            self.attempt_counter[query] = attempt_count + 1
            return ("I couldn't find specific information about your question in our legal documents. "
                   "Could you please provide more specific details or rephrase your question?")
        
        # Reset counter and provide general response
        self.attempt_counter[query] = 0
        try:
            messages = [
                SystemMessage(content="You are a legal expert. Provide general guidance based on your knowledge."),
                HumanMessage(content=f"Please provide general guidance on: {query}")
            ]
            response = self.llm(messages)
            return f"Note: This response is based on general legal knowledge, not specific documents.\n\n{response.content}"
        except:
            return ("I apologize, but I couldn't find specific information about your question "
                   "in our available legal documents. Please consider consulting with a legal expert "
                   "for detailed advice on this matter.")
    
    def _update_memory(self, query: str, answer: str) -> None:
        """Update conversation memory with the latest exchange."""
        try:
            self.memory.chat_memory.add_user_message(query)
            self.memory.chat_memory.add_ai_message(answer)
        except Exception as e:
            logger.error(f"Failed to update memory: {e}")
    
    def reset_memory(self) -> None:
        """Reset conversation memory."""
        try:
            self.memory.chat_memory.messages.clear()
            self.attempt_counter.clear()
            logger.info("Conversation memory reset")
        except Exception as e:
            logger.error(f"Failed to reset memory: {e}")
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """
        Get conversation history in a formatted way.
        
        Returns:
            List[Dict[str, str]]: List of conversation exchanges
        """
        history = []
        messages = self.memory.chat_memory.messages
        
        for i in range(0, len(messages), 2):
            if i + 1 < len(messages):
                history.append({
                    "question": messages[i].content,
                    "answer": messages[i + 1].content
                })
        
        return history
    
    def _create_tool_selector_prompt(self) -> str:
        """Create system prompt for tool selection."""
        return """You are a tool selector for a legal AI assistant. Your job is to select the most relevant tools for answering legal questions.

Available tools:
- 'gdpr': For questions about GDPR (General Data Protection Regulation), European data protection law
- 'pdp': For questions about UU PDP (Indonesian Personal Data Protection Law)
- 'company': For questions about internal company policies and procedures
- 'tavily': For web search when information is not available in documents, or for recent legal developments

Instructions:
1. Analyze the user's question
2. Select 1-3 most relevant tools
3. Respond with a Python list format, e.g., ['gdpr'] or ['gdpr', 'pdp'] or ['tavily']
4. Prefer document tools over web search when possible
5. Use web search for recent developments or when specific information might not be in documents

Examples:
- "What are GDPR data subject rights?" → ['gdpr']
- "Indonesian data protection penalties" → ['pdp']
- "Company email retention policy" → ['company']
- "Recent GDPR court cases" → ['tavily']
- "Data protection requirements for EU and Indonesia" → ['gdpr', 'pdp']"""
    
    def _create_legal_expert_prompt(self) -> str:
        """Create system prompt for legal expert synthesis."""
        return """You are an expert legal advisor specializing in data protection and privacy law. Your role is to provide accurate, comprehensive, and practical legal guidance.

Guidelines:
1. **Accuracy**: Base your answers strictly on the provided source information
2. **Clarity**: Explain complex legal concepts in clear, understandable terms
3. **Comprehensiveness**: Address all aspects of the question when possible
4. **Practical**: Provide actionable guidance when appropriate
5. **Citations**: Reference specific regulations, articles, or sections when mentioned in sources
6. **Disclaimers**: Remind users to consult legal professionals for specific cases

Structure your response as follows:
1. **Direct Answer**: Start with a clear answer to the question
2. **Legal Basis**: Explain the relevant legal framework
3. **Practical Implications**: Discuss real-world applications
4. **Recommendations**: Provide actionable next steps when appropriate
5. **Important Notes**: Add any crucial caveats or disclaimers

Always maintain a professional, helpful tone while ensuring legal accuracy."""
    
    def _create_relevance_checker_prompt(self) -> str:
        """Create system prompt for relevance checking."""
        return """You are a relevance evaluator. Your job is to determine if web search content is relevant to a legal question about data protection.

Respond with either "relevant" or "not relevant" based on whether the content:
1. Directly addresses the legal question
2. Provides useful information about data protection, privacy, or related legal topics
3. Contains current legal information or developments
4. Offers practical guidance related to the question

Be strict in your evaluation - only mark content as relevant if it genuinely helps answer the question."""
