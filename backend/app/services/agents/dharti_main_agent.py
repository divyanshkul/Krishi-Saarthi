import time
from typing import Dict, List, Optional, Any
from openai import OpenAI
from app.core.config import settings
from app.utils.logger import get_logger
from app.services.tools.vlm_tool import VLMTool
from app.schemas.chat import ResponseContent

logger = get_logger(__name__)


class MainAgent:
    """
    DHARTI - Decision Hub for Agentic Routing & Task Integration
    
    The intelligent orchestrator that analyzes farmer queries and routes them
    to appropriate agricultural tools for comprehensive task integration.
    
    DHARTI (धरती = Earth/Land) nurtures farmer queries like earth nurtures crops.
    """
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.openai_api_key)
        self.vlm_tool = VLMTool()
        
        # Intent keywords for classification (fallback mechanism)
        self.intent_keywords = {
            "VISUAL_ANALYSIS": [
                "disease", "pest", "spots", "leaves", "color", "damage", "infection", 
                "brown", "yellow", "black", "white", "holes", "wilting", "rotten",
                "what is this", "identify", "diagnose", "problem with", "issue with"
            ],
            "FARMING_ADVICE": [
                "how to", "when to", "best practice", "should I", "technique",
                "planting", "sowing", "harvesting", "cultivation", "growing",
                "fertilizer", "irrigation", "spacing", "timing"
            ],
            "MARKET_INFO": [
                "price", "mandi", "sell", "market", "rate", "cost", "value",
                "when to sell", "market price", "selling time", "profit"
            ],
            "GOVT_SCHEME": [
                "subsidy", "loan", "scheme", "government", "help", "assistance",
                "support", "pm kisan", "insurance", "benefit", "yojana"
            ]
        }
    
    async def process_query(self, 
                           translation_result: Dict[str, Any], 
                           image_path: Optional[str] = None) -> ResponseContent:
        """
        Main entry point for processing farmer queries through DHARTI
        """
        start_time = time.time()
        logger.info("======== DHARTI (Main Agent) Processing ========")
        
        try:
            # Extract translated text and context
            translated_text = translation_result.get("translation", "")
            agricultural_terms = translation_result.get("agricultural_terms", [])
            confidence = translation_result.get("confidence", "Unknown")
            
            logger.info(f"🌍 DHARTI (Main Agent): Processing query: '{translated_text[:60]}...'")
            logger.info(f"🌍 DHARTI (Main Agent): Agricultural terms: {agricultural_terms}")
            logger.info(f"🌍 DHARTI (Main Agent): Translation confidence: {confidence}")
            logger.info(f"🌍 DHARTI (Main Agent): Image provided: {image_path is not None}")
            
            # Step 1: Analyze intent
            intent_analysis = await self._analyze_intent(
                translated_text, 
                agricultural_terms,
                image_path is not None
            )
            
            # Step 2: Select and execute tools
            response = await self._execute_tools(
                intent_analysis, 
                translated_text, 
                image_path
            )
            
            # Step 3: Format final response
            final_response = self._format_response(response, intent_analysis)
            
            end_time = time.time()
            total_time = end_time - start_time
            
            logger.info(f"🎯 DHARTI (Main Agent): Processing completed in {total_time:.2f}s")
            logger.info("======== DHARTI (Main Agent) Processing Complete ========")
            
            return final_response
            
        except Exception as e:
            logger.error(f"❌ DHARTI (Main Agent): Processing failed - {str(e)}")
            # Fallback to basic response
            return ResponseContent(
                text=f"I encountered an issue processing your query, but I can see you're asking about: {translated_text[:100]}. Please try rephrasing your question or contact support."
            )
    
    async def _analyze_intent(self, 
                            text: str, 
                            agricultural_terms: List[str],
                            has_image: bool) -> Dict[str, Any]:
        """
        Analyze the intent of the farmer's query using GPT-4o-mini
        """
        logger.info("🧠 DHARTI (Main Agent): Analyzing query intent...")
        
        try:
            start_time = time.time()
            
            # Create intent analysis prompt
            intent_prompt = f"""You are an agricultural AI assistant. Analyze this farmer's query to determine what they need.

Query: "{text}"
Agricultural terms found: {agricultural_terms}
Image provided: {has_image}

Analyze the query and respond with a JSON object:
{{
    "primary_intent": "VISUAL_ANALYSIS|FARMING_ADVICE|MARKET_INFO|GOVT_SCHEME",
    "needs_visual_analysis": true/false,
    "confidence": 0.0-1.0,
    "reasoning": "Brief explanation",
    "keywords_found": ["list", "of", "relevant", "keywords"]
}}

Intent Guidelines:
- VISUAL_ANALYSIS: Disease/pest identification, visual problems, image analysis needed
- FARMING_ADVICE: General farming practices, how-to questions, cultivation guidance  
- MARKET_INFO: Prices, selling advice, market trends
- GOVT_SCHEME: Government schemes, subsidies, financial assistance

If image is provided AND visual keywords detected, prioritize VISUAL_ANALYSIS."""

            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert agricultural intent classifier. Always respond with valid JSON."},
                    {"role": "user", "content": intent_prompt}
                ],
                max_tokens=300,
                temperature=0.1
            )
            
            end_time = time.time()
            
            # Parse JSON response
            content = response.choices[0].message.content.strip()
            intent_result = self._parse_intent_json(content)
            
            logger.info(f"🎯 DHARTI (Main Agent): Intent Analysis ({end_time - start_time:.2f}s):")
            logger.info(f"   Primary Intent: {intent_result.get('primary_intent', 'UNKNOWN')}")
            logger.info(f"   Needs Visual: {intent_result.get('needs_visual_analysis', False)}")
            logger.info(f"   Confidence: {intent_result.get('confidence', 0.0)}")
            logger.info(f"   Reasoning: {intent_result.get('reasoning', 'N/A')}")
            
            return intent_result
            
        except Exception as e:
            logger.error(f"DHARTI (Main Agent): Intent analysis failed - {str(e)}")
            # Fallback intent analysis
            return self._fallback_intent_analysis(text, has_image)
    
    def _parse_intent_json(self, content: str) -> Dict[str, Any]:
        """Parse JSON response from intent analysis"""
        try:
            import json
            
            # Clean up response
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            return json.loads(content)
            
        except Exception as e:
            logger.warning(f"DHARTI (Main Agent): JSON parsing failed - {e}")
            return {
                "primary_intent": "FARMING_ADVICE",
                "needs_visual_analysis": False,
                "confidence": 0.3,
                "reasoning": "JSON parsing failed, using fallback",
                "keywords_found": []
            }
    
    def _fallback_intent_analysis(self, text: str, has_image: bool) -> Dict[str, Any]:
        """Simple keyword-based fallback intent analysis"""
        logger.info("🔄 DHARTI (Main Agent): Using fallback intent analysis...")
        
        text_lower = text.lower()
        intent_scores = {}
        
        # Score each intent category
        for intent, keywords in self.intent_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                intent_scores[intent] = score
        
        # Determine primary intent
        if has_image and any(keyword in text_lower for keyword in self.intent_keywords["VISUAL_ANALYSIS"]):
            primary_intent = "VISUAL_ANALYSIS"
            needs_visual = True
        elif intent_scores:
            primary_intent = max(intent_scores, key=intent_scores.get)
            needs_visual = primary_intent == "VISUAL_ANALYSIS" and has_image
        else:
            primary_intent = "FARMING_ADVICE"
            needs_visual = has_image
        
        return {
            "primary_intent": primary_intent,
            "needs_visual_analysis": needs_visual,
            "confidence": 0.6 if intent_scores else 0.3,
            "reasoning": "Keyword-based fallback analysis",
            "keywords_found": [k for k in self.intent_keywords[primary_intent] if k in text_lower]
        }
    
    async def _execute_tools(self, 
                           intent_analysis: Dict[str, Any], 
                           query: str, 
                           image_path: Optional[str]) -> Dict[str, Any]:
        """
        Execute appropriate tools based on intent analysis
        """
        primary_intent = intent_analysis.get("primary_intent", "FARMING_ADVICE")
        needs_visual = intent_analysis.get("needs_visual_analysis", False)
        
        logger.info(f"🔧 DHARTI (Main Agent): Executing tools for intent: {primary_intent}")
        
        results = {}
        
        try:
            # Execute VLM tool if visual analysis is needed
            if needs_visual and image_path:
                logger.info("🌍 DHARTI (Main Agent): Executing VLM tool...")
                vlm_result = await self.vlm_tool.analyze_image(image_path, query)
                results["vlm"] = vlm_result
                logger.info(f"🌍 DHARTI (Main Agent): VLM tool completed: {vlm_result.get('success', False)}")
            
            # For now, other tools return mock responses
            # TODO: Implement actual tools in later phases
            
            if primary_intent == "FARMING_ADVICE":
                results["kcc"] = {
                    "success": True,
                    "response": f"Based on your query about farming, here's some general advice: Consider proper irrigation, soil testing, and following seasonal planting guidelines for your region.",
                    "source": "kcc_mock"
                }
            
            elif primary_intent == "MARKET_INFO":
                results["market"] = {
                    "success": True,
                    "response": "Current market prices are favorable. Consider checking local mandi rates before selling. Timing your sales during peak demand periods can maximize profits.",
                    "source": "market_mock"
                }
            
            elif primary_intent == "GOVT_SCHEME":
                results["govt_scheme"] = {
                    "success": True,
                    "response": "You may be eligible for PM-KISAN scheme and crop insurance. Visit your nearest CSC or agriculture office with Aadhaar and land documents for enrollment.",
                    "source": "govt_scheme_mock"
                }
            
            return results
            
        except Exception as e:
            logger.error(f"DHARTI (Main Agent): Tool execution failed - {str(e)}")
            return {
                "error": {
                    "success": False,
                    "response": f"I encountered an issue analyzing your query: {str(e)}",
                    "source": "error_fallback"
                }
            }
    
    def _format_response(self, 
                        tool_results: Dict[str, Any], 
                        intent_analysis: Dict[str, Any]) -> ResponseContent:
        """
        Format the final response for the farmer
        """
        logger.info("📝 DHARTI (Main Agent): Formatting final response...")
        
        try:
            # Combine responses from different tools
            response_parts = []
            
            # Process VLM results (priority - most specific)
            if "vlm" in tool_results and tool_results["vlm"].get("success"):
                vlm_response = tool_results["vlm"]["response"]
                response_parts.append(vlm_response)
                logger.info("🌍 DHARTI (Main Agent): Added VLM analysis to response")
            
            # Process other tool results
            for tool_name, result in tool_results.items():
                if tool_name != "vlm" and result.get("success"):
                    response_parts.append(result["response"])
                    logger.info(f"🌍 DHARTI (Main Agent): Added {tool_name} response")
            
            # Create final combined response
            if response_parts:
                final_text = " ".join(response_parts)
            else:
                final_text = "I understand your agricultural query. For the best assistance, please provide more specific details about your farming concern."
            
            # TODO: Add video/website URLs based on intent
            response_content = ResponseContent(text=final_text)
            
            logger.info(f"🌍 DHARTI (Main Agent): Final response length: {len(final_text)} characters")
            return response_content
            
        except Exception as e:
            logger.error(f"DHARTI (Main Agent): Response formatting failed - {str(e)}")
            return ResponseContent(
                text="I encountered an issue formatting the response. Please try again or contact support."
            )