"""
Tool Creation and Management

This module provides tools for document retrieval and web search
used by the multi-agent system.

Author: Adryan R A
"""

import logging
import requests
from typing import Dict, List, Optional, Any
from langchain.tools import Tool

from ..core.config import settings

logger = logging.getLogger(__name__)


class ToolError(Exception):
    """Custom exception for tool-related errors."""
    pass


class ToolManager:
    """
    Manager class for creating and managing agent tools.
    
    This class provides various tools for document retrieval from different
    legal document stores and web search capabilities.
    """
    
    def __init__(self, stores: Dict[str, Any], search_config: Optional[Dict] = None):
        """
        Initialize the tool manager.
        
        Args:
            stores (Dict[str, Any]): Dictionary of document stores
            search_config (Optional[Dict]): Search configuration parameters
        """
        self.stores = stores
        self.search_config = search_config or {
            "k": settings.SEARCH_K,
            "score_threshold": settings.SEARCH_SCORE_THRESHOLD
        }
        self.tools = self._create_tools()
    
    def _create_tools(self) -> Dict[str, Tool]:
        """
        Create all available tools for the agents.
        
        Returns:
            Dict[str, Tool]: Dictionary of available tools
        """
        tools = {}
        
        # Document retrieval tools
        if 'gdpr' in self.stores:
            tools['gdpr'] = self._create_gdpr_tool()
        
        if 'pdp' in self.stores:
            tools['pdp'] = self._create_pdp_tool()
        
        if 'company' in self.stores:
            tools['company'] = self._create_company_tool()
        
        # Web search tool
        tools['tavily'] = self._create_tavily_tool()
        
        logger.info(f"Created {len(tools)} tools: {list(tools.keys())}")
        return tools
    
    def _create_gdpr_tool(self) -> Tool:
        """Create GDPR document retrieval tool."""
        return Tool(
            name="AskGDPR",
            description=(
                "Retrieve relevant information from GDPR (General Data Protection Regulation) documents. "
                "Use this tool for questions about European data protection law, GDPR compliance, "
                "data subject rights, processing lawfulness, and GDPR-specific requirements."
            ),
            func=lambda query: self._retrieve_documents('gdpr', query)
        )
    
    def _create_pdp_tool(self) -> Tool:
        """Create UU PDP (Indonesian Personal Data Protection Law) retrieval tool."""
        return Tool(
            name="AskPDP", 
            description=(
                "Retrieve relevant information from UU PDP (Undang-Undang Perlindungan Data Pribadi) documents. "
                "Use this tool for questions about Indonesian personal data protection law, "
                "local compliance requirements, and Indonesia-specific data protection regulations."
            ),
            func=lambda query: self._retrieve_documents('pdp', query)
        )
    
    def _create_company_tool(self) -> Tool:
        """Create company policy retrieval tool."""
        return Tool(
            name="AskCompany",
            description=(
                "Retrieve relevant information from internal company data protection policies and procedures. "
                "Use this tool for questions about company-specific privacy policies, internal procedures, "
                "data handling guidelines, and organizational data protection measures."
            ),
            func=lambda query: self._retrieve_documents('company', query)
        )
    
    def _create_tavily_tool(self) -> Tool:
        """Create Tavily web search tool."""
        return Tool(
            name="AskTavily",
            description=(
                "Search the web for recent legal information and developments in data protection law. "
                "Use this as a fallback when internal documents don't contain sufficient information, "
                "or when looking for recent legal updates, case law, or external expert opinions."
            ),
            func=self._tavily_search
        )
    
    def _retrieve_documents(self, store_name: str, query: str) -> Optional[str]:
        """
        Retrieve relevant documents from a specific store.
        
        Args:
            store_name (str): Name of the document store
            query (str): Search query
            
        Returns:
            Optional[str]: Retrieved document chunks joined as text, or None if no results
        """
        try:
            store = self.stores.get(store_name)
            if not store:
                logger.error(f"Store {store_name} not found")
                return None
            
            # Perform similarity search
            retriever = store.as_retriever(search_kwargs=self.search_config)
            documents = retriever.get_relevant_documents(query)
            
            if not documents:
                logger.debug(f"No documents found for query in {store_name}: {query}")
                return None
            
            # Extract and join content
            content_chunks = []
            for doc in documents:
                content = doc.page_content.strip()
                if content:
                    # Add metadata context if available
                    metadata = doc.metadata
                    source_info = ""
                    if metadata.get('filename'):
                        source_info = f"[Source: {metadata['filename']}] "
                    content_chunks.append(source_info + content)
            
            result = "\n\n".join(content_chunks)
            logger.debug(f"Retrieved {len(documents)} documents from {store_name}")
            return result if result.strip() else None
            
        except Exception as e:
            logger.error(f"Error retrieving documents from {store_name}: {e}")
            return None
    
    def _tavily_search(self, query: str) -> str:
        """
        Perform web search using Tavily API.
        
        Args:
            query (str): Search query
            
        Returns:
            str: Search results or error message
        """
        try:
            headers = {
                "Authorization": f"Bearer {settings.TAVILY_API_KEY}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "query": query,
                "search_depth": "advanced",
                "max_results": 3,
                "include_domains": [],
                "exclude_domains": [],
                "include_answer": True
            }
            
            response = requests.post(
                settings.TAVILY_API_URL,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                
                if not results:
                    return "No relevant web search results found."
                
                # Format results
                formatted_results = []
                for result in results:
                    title = result.get("title", "Unknown Title")
                    content = result.get("content", "No content available")
                    url = result.get("url", "")
                    
                    formatted_result = f"**{title}**\n{content}"
                    if url:
                        formatted_result += f"\n[Source: {url}]"
                    
                    formatted_results.append(formatted_result)
                
                return "\n\n".join(formatted_results)
            
            else:
                logger.error(f"Tavily API error: {response.status_code} - {response.text}")
                return f"Web search failed with status {response.status_code}"
                
        except requests.exceptions.Timeout:
            logger.error("Tavily API request timed out")
            return "Web search timed out. Please try again."
        
        except Exception as e:
            logger.error(f"Tavily search error: {e}")
            return f"Web search error: {str(e)}"
    
    def get_tools(self) -> Dict[str, Tool]:
        """
        Get all available tools.
        
        Returns:
            Dict[str, Tool]: Dictionary of tools
        """
        return self.tools.copy()
    
    def get_tool(self, tool_name: str) -> Optional[Tool]:
        """
        Get a specific tool by name.
        
        Args:
            tool_name (str): Name of the tool
            
        Returns:
            Optional[Tool]: Tool instance or None if not found
        """
        return self.tools.get(tool_name)
    
    def test_tool(self, tool_name: str, test_query: str = "test") -> Dict[str, Any]:
        """
        Test a specific tool with a query.
        
        Args:
            tool_name (str): Name of the tool to test
            test_query (str): Query to test with
            
        Returns:
            Dict[str, Any]: Test results
        """
        tool = self.get_tool(tool_name)
        if not tool:
            return {"success": False, "error": f"Tool {tool_name} not found"}
        
        try:
            result = tool.func(test_query)
            return {
                "success": True,
                "tool_name": tool_name,
                "query": test_query,
                "result_length": len(result) if result else 0,
                "has_result": bool(result)
            }
        except Exception as e:
            return {
                "success": False,
                "tool_name": tool_name,
                "error": str(e)
            }
