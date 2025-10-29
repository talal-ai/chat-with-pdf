"""Enhanced RAG engine with structured, consultant-grade responses."""
from typing import Tuple, List, Dict, Any
import re
import json
import logging
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate
from langchain.schema import Document
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate as CoreChatPromptTemplate

from app.core.config import settings
from app.services.llm_service import llm_service
from app.services.vector_store import vector_store
from app.schemas.qa_response import QAResponse, MultiQueryResponse
from app.core.markdown_renderer import render_markdown, render_simple_markdown
from app.core.json_parser import robust_parser


class RAGEnginePro:
    """Enhanced RAG engine with structured, consultant-grade responses."""
    
    def __init__(self, *, max_sources: int = 5):
        self.max_sources = max_sources
        self._llm = None
        self._retriever = None
        self._initialized = False
        
        # Memory control settings
        self.memory_enabled = True
        self.memory_window_size = 5  # Number of message pairs to keep
        
        # Performance optimization
        self.use_multi_query = False  # Disable multi-query for faster responses
        self.max_retrieval_docs = 8  # Reduced from potential higher numbers
        
        # Initialize memory
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            output_key="answer",
            return_messages=False,
        )
        
        # JSON parser for structured output
        self.json_parser = JsonOutputParser(pydantic_object=QAResponse)
        
        # Multi-query expansion prompt
        self.multi_query_prompt = CoreChatPromptTemplate.from_messages([
            ("system", "You are an expert at generating search queries for AAOIFI Sharia Standards. Generate diverse queries that would find rules, conditions, definitions, exceptions, and requirements."),
            ("human", "Generate 4 alternative search queries for finding information about: {question}\n\nEach query should focus on a different aspect:\n1. Rules and requirements\n2. Conditions and exceptions\n3. Definitions and terminology\n4. Implementation procedures\n\nReturn as JSON with 'queries' array.")
        ])
        
        # Tone-specific system prompts
        self.tone_prompts = {
            "conversational": """You are a friendly, knowledgeable expert on AAOIFI Sharia Standards. Respond naturally like ChatGPT - warm, engaging, and conversational.

CRITICAL: Put your ENTIRE response in the "answer" field combining paragraphs and bullet points naturally.

STYLE:
- Start with a natural paragraph introduction (use \\n\\n for spacing)
- Use bullet points when listing items, requirements, or key points
- Be friendly and approachable while remaining professional
- Explain concepts clearly with examples when helpful
- Use "you" and "your" to connect with the user
- Add context and background to help understanding
- Cite pages naturally within sentences: "According to the standards (page X)..."
- Feel free to use analogies or real-world examples
- Mix paragraphs and bullets naturally based on content
- End with thoughtful follow-up questions (in the follow_up_questions array)

FORMAT:
Paragraph → Bullet points (when listing) → Closing paragraph. Adapt based on question type.""",
            
            "concise": """You are a direct, efficient expert on AAOIFI Sharia Standards. Provide SHORT, to-the-point answers with brief paragraphs and bullets.

CRITICAL: Put your ENTIRE response in the "answer" field. Use paragraphs and bullets efficiently.

STYLE:
- Start with a brief paragraph (1-2 sentences)
- Use bullet points for listing key points or requirements
- Cite pages briefly: "(p. X)"
- Maximum 2-3 bullets if needed
- End with a brief concluding sentence if necessary
- Be direct and efficient

FORMAT:
Brief intro paragraph → Bullets (if listing items) → Done. Keep it tight and focused.""",
            
            "detailed": """You are a thorough expert on AAOIFI Sharia Standards. Provide COMPREHENSIVE, in-depth explanations with clear structure.

CRITICAL: Put your ENTIRE response in the "answer" field. Use full markdown formatting.

STYLE:
- Start with a comprehensive paragraph introduction
- Use headers (###) to organize major sections
- Use bullet points extensively for clarity and organization
- Cover all aspects of the topic systematically
- Include background, context, and implications
- Provide examples and scenarios
- Explain nuances and edge cases
- Cite all relevant pages with full context
- Add implementation guidance
- Include comprehensive follow-up questions (in follow_up_questions array)

FORMAT:
Intro paragraph → ### Section Headers → Bullet points → Examples → Summary. Most structured tone.""",
            
            "professional": """You are a senior consultant on AAOIFI Sharia Standards. Respond in a FORMAL, business-grade manner with paragraphs and bullets.

CRITICAL: Put your ENTIRE response in the "answer" field combining formal paragraphs and bullet points.

STYLE:
- Begin with a formal paragraph introduction
- Use bullet points for listing requirements, conditions, or key points
- Write in formal, professional language with clear spacing (use \\n\\n)
- Be precise and authoritative
- Focus on practical application and compliance
- Include actionable recommendations
- Cite sources formally within text: "As stated on [Page X]..."
- Conclude with a formal summary paragraph
- End with strategic follow-up questions (in follow_up_questions array)

FORMAT:
Formal intro paragraph → Bullet points (for requirements/lists) → Summary paragraph. Business professional style.""",
            
            "simple": """You are a patient teacher explaining AAOIFI Sharia Standards in SIMPLE terms using easy-to-read paragraphs and bullets.

CRITICAL: Put your ENTIRE response in the "answer" field. Use simple paragraphs and bullets.

STYLE:
- Start with a simple, friendly paragraph explaining the basics
- Use bullet points to break down complex ideas into simple steps
- Avoid jargon; define technical terms simply
- Use everyday analogies and examples
- Be encouraging and clear
- Cite pages simply: "The book says on page X..."
- Keep bullets short and easy to understand
- End with a friendly closing paragraph
- Check understanding with follow-up questions (in follow_up_questions array)

FORMAT:
Simple intro → Bullet points (for steps/lists) → Friendly conclusion. Like explaining to a friend."""
        }
        
        # Default prompt (will be replaced based on tone)
        self.structured_prompt = None
    
    def _ensure_initialized(self):
        """Lazily initialize LLM and retriever on first use."""
        if self._initialized:
            return
        
        self._initialized = True
        self._llm = llm_service.get_llm()
        self._retriever = vector_store.as_retriever(
            search_kwargs={"k": int(getattr(settings, "top_k_retrieval", 10))}
        )
        
        # Create the structured chain (requires llm and retriever)
        def get_context_and_history(question: str) -> dict:
            # Get context from retriever
            docs = self._retriever.invoke(question)
            context_text = "\n\n".join([
                f"[Page {doc.metadata.get('page', 'unknown')}]: {doc.page_content[:800]}"
                for doc in docs[:5]
            ])
            
            # Get chat history
            chat_history = self.memory.chat_memory.messages[-2:] if self.memory.chat_memory.messages else []
            
            return {
                "context": context_text,
                "question": question,
                "chat_history": chat_history
            }
        
        self.structured_chain = (
            get_context_and_history
            | self.structured_prompt
            | self._llm
            | self.json_parser
        )
        
        # Fallback chain for when structured parsing fails
        self.fallback_chain = ConversationalRetrievalChain.from_llm(
            llm=self._llm,
            retriever=self._retriever,
            memory=self.memory,
            return_source_documents=True,
            verbose=False,
        )
    
    @property
    def llm(self):
        """Get LLM instance, initializing if needed."""
        self._ensure_initialized()
        return self._llm
    
    @property
    def retriever(self):
        """Get retriever instance, initializing if needed."""
        self._ensure_initialized()
        return self._retriever
    
    def _deduplicate_sources(self, docs: List[Document]) -> List[Document]:
        """Remove duplicate sources using (source,page,chunk_id/content-hash), keep order; cap to max_sources."""
        seen: set = set()
        unique_docs: List[Document] = []
        for doc in docs:
            meta = doc.metadata or {}
            page = str(meta.get("page", "unknown"))
            source = str(meta.get("source", meta.get("file_path", "unknown")))
            # Prefer a stable chunk id if available, else hash a robust slice
            chunk_id = str(meta.get("id") or meta.get("chunk_id") or "")
            if not chunk_id:
                content_key = re.sub(r"\s+", " ", doc.page_content.strip())[:256].lower()
                chunk_id = str(hash((page, content_key)))
            sig = f"{source}::{page}::{chunk_id}"
            if sig in seen:
                continue
            seen.add(sig)
            unique_docs.append(doc)
            if len(unique_docs) >= self.max_sources:
                break
        return unique_docs
    
    def _add_scores_to_docs(self, docs_with_scores: List[tuple]) -> List[Document]:
        """Convert (Document, score) tuples to Documents with score in metadata."""
        result = []
        for doc, score in docs_with_scores:
            # Add score to metadata
            if not hasattr(doc, 'metadata') or doc.metadata is None:
                doc.metadata = {}
            doc.metadata['relevance_score'] = float(score)
            result.append(doc)
        return result

    def _multi_query_retrieval(self, question: str) -> List[Document]:
        """Use multi-query expansion to improve retrieval quality."""
        try:
            # Generate alternative queries
            multi_query_chain = self.multi_query_prompt | self.llm | JsonOutputParser(pydantic_object=MultiQueryResponse)
            response = multi_query_chain.invoke({"question": question})
            
            # Check if response is valid and extract queries
            queries = []
            if hasattr(response, 'queries'):
                queries = response.queries
            elif isinstance(response, dict) and 'queries' in response:
                queries = response['queries']
            else:
                raise ValueError("Invalid response format from multi-query")
            
            # Ensure queries is a list of strings
            if not isinstance(queries, list):
                raise ValueError("Queries must be a list")
            
            # Retrieve documents for each query
            all_docs = []
            for query in queries:
                # Ensure query is a string
                if isinstance(query, dict):
                    # If query is a dict, try to extract the text
                    query_str = query.get('query') or query.get('text') or str(query)
                elif not isinstance(query, str):
                    query_str = str(query)
                else:
                    query_str = query
                
                # Retrieve documents with the string query
                docs = self.retriever.invoke(query_str)
                all_docs.extend(docs)
            
            # Deduplicate and return top results
            unique_docs = self._deduplicate_sources(all_docs)
            return unique_docs[:self.max_sources]
            
        except Exception as e:
            logging.warning(f"Multi-query retrieval failed: {e}")
            # Fallback to single query
            return self.retriever.invoke(question)


    def _is_greeting(self, question: str) -> bool:
        """Check if the question is a simple greeting."""
        # Normalize question
        q_lower = question.lower().strip().rstrip('!?.,')
        
        # Common greetings
        greetings = {
            'hi', 'hello', 'hey', 'greetings', 'good morning', 'good afternoon',
            'good evening', 'good day', 'howdy', 'hiya', 'yo', 'sup', "what's up",
            'whats up', 'how are you', 'how do you do', 'salaam', 'salam',
            'assalamu alaikum', 'peace be upon you'
        }
        
        # Check if question matches any greeting
        if q_lower in greetings:
            return True
        
        # Check if question is very short and contains greeting words
        if len(q_lower.split()) <= 4:
            for greeting in greetings:
                if greeting in q_lower:
                    return True
        
        return False


    def _handle_greeting(self, question: str) -> Tuple[str, List[Document], List[str]]:
        """Handle greeting messages with a friendly, brief response."""
        greeting_response = """Hello! 👋 Welcome to the AAOIFI Standards Chatbot.

I'm here to help you with questions about AAOIFI Sharia Standards for Islamic financial institutions. I can assist you with:

• Understanding Islamic banking principles
• Explaining Sharia compliance requirements
• Clarifying specific standards and guidelines
• Interpreting rules for financial contracts

Feel free to ask me anything about AAOIFI Standards! How can I assist you today?"""

        follow_ups = [
            "What are the key principles of Islamic banking?",
            "Explain the requirements for Sharia compliance",
            "What are the different types of Islamic financial contracts?",
            "Tell me about Murabaha transactions"
        ]
        
        return (greeting_response, [], follow_ups)


    def answer_question(self, question: str, tone: str = "conversational") -> Tuple[str, List[Document], List[str]]:
        """Answer a question using enhanced RAG with tone-adaptive responses.
        
        Args:
            question: User's question
            tone: Response tone (conversational, concise, detailed, professional, simple)
        
        Returns:
            Tuple of (answer text, source documents, follow-up questions)
        """
        try:
            # Check if this is a simple greeting
            if self._is_greeting(question):
                return self._handle_greeting(question)
            
            # Create tone-specific prompt
            tone_system_prompt = self.tone_prompts.get(tone, self.tone_prompts["conversational"])
            
            self.structured_prompt = CoreChatPromptTemplate.from_messages([
                ("system", tone_system_prompt + "\n\n{format_instructions}"),
                ("human", """Context from AAOIFI Sharia Standards:
{context}

Question: {question}

Previous conversation:
{chat_history}

Provide a response in the requested style:""")
            ])
            
            # Get context and sources - use single query for speed
            if self.use_multi_query:
                sources = self._multi_query_retrieval(question)
            else:
                # Single query retrieval - much faster
                sources = self.retriever.invoke(question)
            
            sources = self._deduplicate_sources(sources)
            
            # Create context text - reduce chunk size for faster processing
            context_text = "\n\n".join([
                f"[Page {doc.metadata.get('page', 'unknown')}]: {doc.page_content[:600]}"
                for doc in sources[:4]  # Reduced from 5 to 4 for speed
            ])
            
            # Get chat history respecting memory settings
            chat_history = self._get_chat_history()
            
            # Try structured response
            try:
                # Create the prompt input
                prompt_input = {
                    "context": context_text,
                    "question": question,
                    "chat_history": chat_history,
                    "format_instructions": self.json_parser.get_format_instructions()
                }
                
                # Get structured response
                response = self.structured_prompt.invoke(prompt_input)
                llm_response = self.llm.invoke(response)
                
                # Use robust parser with fallback
                llm_text = llm_response.content if hasattr(llm_response, 'content') else str(llm_response)
                parsed_response = robust_parser.parse_with_fallback(llm_text)
                
                # Log confidence score for monitoring
                logging.info(f"Response parsed with confidence: {parsed_response.confidence_score}")
                
                if parsed_response:
                    # Render with bold keywords and structured format
                    answer = render_markdown(parsed_response, extra_terms={"enforceability", "guarantee", "pledge"})
                    follow_ups = parsed_response.follow_up_questions if parsed_response.follow_up_questions else []
                    
                    # Trim memory after successful response
                    self._trim_memory()
                    
                    return answer, sources, follow_ups
                else:
                    raise ValueError("Parser returned None (should not happen with fallback)")
                    
            except Exception as structured_error:
                logging.warning(f"Structured response failed: {structured_error}")
                # Fall through to simple fallback
                
        except Exception as e:
            logging.exception("Error in structured response setup")
            
        # Simple fallback - direct LLM call without memory
        try:
            logging.info("Using simple fallback without memory")
            
            # Create a simple prompt without memory
            simple_prompt = CoreChatPromptTemplate.from_messages([
                ("system", f"""You are an expert on AAOIFI Sharia Standards. Answer the question based on the context provided.

{self.tone_prompts.get(tone, self.tone_prompts['conversational'])}

Provide a direct answer in paragraph form with page citations."""),
                ("human", """Context from AAOIFI Sharia Standards:
{context}

Question: {question}

Answer the question based on the context above.""")
            ])
            
            # Get the response
            prompt_result = simple_prompt.invoke({
                "context": context_text,
                "question": question
            })
            
            llm_response = self.llm.invoke(prompt_result)
            answer_text = llm_response.content if hasattr(llm_response, 'content') else str(llm_response)
            
            # Apply bold keywords
            answer = render_simple_markdown(answer_text, [str(doc.metadata.get("page", "unknown")) for doc in sources[:3]], 
                                          extra_terms={"enforceability", "guarantee", "pledge"})
            
            # Generate basic follow-up questions for fallback
            fallback_follow_ups = [
                "Could you provide more details on this topic?",
                "How does this relate to other AAOIFI standards?"
            ]
            
            # Trim memory after fallback response
            self._trim_memory()
            
            return answer, sources, fallback_follow_ups
            
        except Exception as fallback_error:
            logging.exception("Fallback also failed")
            return (
                "I couldn't find specific information about that in the AAOIFI standards. "
                "Try narrowing the question or specify the standard/section.",
                [],
                ["What specific aspect of AAOIFI standards are you interested in?"]
            )

    def _enforce_single_page_citation(self, text: str) -> str:
        """Keep only the first [Page X] occurrence for each X; remove subsequent duplicates."""
        pattern = re.compile(r"\[Page\s+([\d.]+)\]")
        seen_pages: set = set()
        out: List[str] = []
        last_end = 0
        for m in pattern.finditer(text):
            out.append(text[last_end:m.start()])
            page = m.group(1)
            if page not in seen_pages:
                out.append(m.group(0))  # keep first
                seen_pages.add(page)
            # else: drop duplicate citation
            last_end = m.end()
        out.append(text[last_end:])
        return "".join(out)

    def clear_memory(self):
        """Clear conversation history."""
        try:
            self.memory.clear()
        except Exception:
            self.memory = ConversationBufferMemory(
                memory_key="chat_history", output_key="answer", return_messages=False
            )
    
    def set_memory_enabled(self, enabled: bool):
        """Enable or disable conversation memory."""
        self.memory_enabled = enabled
        if not enabled:
            self.clear_memory()
    
    def set_memory_window_size(self, size: int):
        """Set the number of message pairs to keep in memory.
        
        Args:
            size: Number of Q&A pairs to retain (2, 5, 10, or 20)
        """
        if size not in [2, 5, 10, 20]:
            raise ValueError("Memory window size must be 2, 5, 10, or 20")
        self.memory_window_size = size
        self._trim_memory()
    
    def _trim_memory(self):
        """Trim memory to keep only the last N message pairs."""
        if not self.memory_enabled or not self.memory.chat_memory.messages:
            return
        
        # Each Q&A pair = 2 messages (user + assistant)
        max_messages = self.memory_window_size * 2
        messages = self.memory.chat_memory.messages
        
        if len(messages) > max_messages:
            # Keep only the last N pairs
            self.memory.chat_memory.messages = messages[-max_messages:]
    
    def _get_chat_history(self) -> List:
        """Get chat history respecting memory settings."""
        if not self.memory_enabled:
            return []
        
        messages = self.memory.chat_memory.messages
        if not messages:
            return []
        
        # Return last N pairs based on window size
        max_messages = self.memory_window_size * 2
        return messages[-max_messages:] if len(messages) > max_messages else messages
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get current memory statistics.
        
        Returns:
            Dict with memory status, window size, and message count
        """
        message_count = len(self.memory.chat_memory.messages) if self.memory.chat_memory.messages else 0
        return {
            "enabled": self.memory_enabled,
            "window_size": self.memory_window_size,
            "current_messages": message_count,
            "conversation_pairs": message_count // 2,
            "at_capacity": message_count >= (self.memory_window_size * 2)
        }


# Enhanced engine instance
rag_engine_pro = RAGEnginePro()
