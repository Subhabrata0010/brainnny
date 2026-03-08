"""
LLM service - Placeholder for future model integration.
Currently NOT used - system only stores and retrieves memory.
"""

import logging

logger = logging.getLogger(__name__)


class LLMService:
    """
    Placeholder LLM service for future integration.
    
    In the current MVP, the system does NOT generate AI responses.
    It only stores conversations and retrieves context.
    
    Future implementation will support:
    - Claude (Anthropic)
    - OpenAI GPT
    - Google Gemini
    - Local models
    """
    
    @staticmethod
    def call_model(model_name: str, prompt: str) -> str:
        """
        Placeholder for future LLM integration.
        
        Args:
            model_name: Model identifier (claude, openai, gemini, local)
            prompt: Input prompt
        
        Returns:
            Model response (currently not implemented)
        
        Raises:
            NotImplementedError: This feature is not yet available
        """
        raise NotImplementedError(
            "LLM response generation is not implemented in MVP. "
            "The system currently only stores and retrieves memory context. "
            "Use the retrieved context with your own LLM integration."
        )
    
    @staticmethod
    def future_adapter_interface():
        """
        Future adapter interface design.
        
        Will support:
        - call_model(model_name, prompt) -> response
        - stream_model(model_name, prompt) -> generator
        - embed_text(model_name, text) -> embedding
        """
        pass


# Future model adapters (not implemented):
# class ClaudeAdapter:
#     pass
#
# class OpenAIAdapter:
#     pass
#
# class GeminiAdapter:
#     pass
#
# class LocalModelAdapter:
#     pass

        """
        Call the specified LLM model with a prompt.
        
        Args:
            model_name: Model identifier (claude, openai, gemini)
            prompt: Input prompt
        
        Returns:
            Model response as string
        """
        if model_name == "claude":
            return LLMService._call_claude(prompt)
        elif model_name == "openai":
            return LLMService._call_openai(prompt)
        elif model_name == "gemini":
            return LLMService._call_gemini(prompt)
        else:
            raise ValueError(f"Unsupported model: {model_name}")
    
    @staticmethod
    def _call_claude(prompt: str) -> str:
        """Call Anthropic Claude API."""
        try:
            import anthropic
            
            client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
            
            message = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return message.content[0].text
        
        except Exception as e:
            logger.error(f"Claude API error: {e}")
            raise
    
    @staticmethod
    def _call_openai(prompt: str) -> str:
        """Call OpenAI API."""
        try:
            import openai
            
            client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
            
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}]
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
    
    @staticmethod
    def _call_gemini(prompt: str) -> str:
        """Call Google Gemini API."""
        try:
            import google.generativeai as genai
            
            genai.configure(api_key=settings.GOOGLE_API_KEY)
            model = genai.GenerativeModel('gemini-pro')
            
            response = model.generate_content(prompt)
            return response.text
        
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise
    
    @staticmethod
    def extract_conversation_data(message: str, model: str = "claude") -> ExtractionResult:
        """
        Extract structured data from conversation using LLM.
        
        Args:
            message: Conversation message
            model: LLM model to use
        
        Returns:
            ExtractionResult with nodes, summary, and metadata
        """
        extraction_prompt = f"""
Analyze this conversation message and extract structured information.
Return ONLY a valid JSON object with this exact structure:

{{
  "session_title": "Brief title for this conversation (max 10 words)",
  "summary": "Concise summary of the conversation (2-3 sentences)",
  "overall_importance": 0.7,
  "nodes": [
    {{
      "node_type": "topic|idea|decision|constraint|promise|summary",
      "content": "The actual content extracted",
      "importance_score": 0.8
    }}
  ]
}}

Extract nodes for:
- topic: Main subjects discussed
- idea: New concepts or suggestions
- decision: Decisions made
- constraint: Limitations or requirements mentioned
- promise: Commitments or promises
- summary: Key takeaways

Conversation:
{message}

Return ONLY the JSON object, no other text.
"""
        
        try:
            response = LLMService.call_model(model, extraction_prompt)
            
            # Parse JSON response
            # Remove markdown code blocks if present
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            
            data = json.loads(response)
            
            # Convert to Pydantic models
            nodes = [ExtractedNode(**node) for node in data.get("nodes", [])]
            
            return ExtractionResult(
                nodes=nodes,
                session_title=data.get("session_title", "Conversation"),
                summary=data.get("summary", message[:200]),
                overall_importance=data.get("overall_importance", 0.5)
            )
        
        except Exception as e:
            logger.error(f"Extraction failed: {e}")
            # Return fallback extraction
            return ExtractionResult(
                nodes=[ExtractedNode(
                    node_type="summary",
                    content=message[:500],
                    importance_score=0.5
                )],
                session_title="Conversation",
                summary=message[:200],
                overall_importance=0.5
            )