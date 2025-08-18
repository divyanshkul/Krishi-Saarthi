import os
import time
import base64
import requests
from typing import Optional, Dict, Any
from openai import OpenAI
from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class VLMTool:
    
    def __init__(self):
        self.base_url = settings.gpu_server_base_url
        self.health_endpoint = settings.gpu_health_endpoint
        self.generate_endpoint = settings.vllm_generate_endpoint
        self.timeout = settings.gpu_timeout_seconds
        self.openai_client = OpenAI(api_key=settings.openai_api_key)
    
    async def check_health(self) -> Dict[str, Any]:
        logger.info("======== VLM Health Check ========")
        logger.info(f"Checking GPU server health at: {self.base_url}")
        
        try:
            start_time = time.time()
            
            response = requests.get(
                f"{self.base_url}{self.health_endpoint}",
                timeout=10
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            logger.info(f"Health check response time: {response_time:.2f}s")
            
            if response.status_code == 200:
                health_data = response.json()
                logger.info(f"GPU Server Status: {health_data.get('status', 'unknown')}")
                logger.info(f"CUDA Available: {health_data.get('cuda', {}).get('available', False)}")
                logger.info(f"VLLM Service: {health_data.get('services', {}).get('vllm', 'unknown')}")
                
                return {
                    "success": True,
                    "status": health_data.get("status", "unknown"),
                    "cuda_available": health_data.get("cuda", {}).get("available", False),
                    "vllm_status": health_data.get("services", {}).get("vllm", "unknown"),
                    "response_time": response_time,
                    "data": health_data
                }
            else:
                logger.error(f"Health check failed with status: {response.status_code}")
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "response_time": response_time
                }
        
        except requests.exceptions.Timeout:
            logger.error("Health check timed out")
            return {
                "success": False,
                "error": "Health check timeout"
            }
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _analyze_with_gpt4_vision(self, image_path: str, question: str) -> Dict[str, Any]:
        logger.info("======== GPT-4 Vision Fallback ========")
        logger.info(f"Using GPT-4 Vision fallback for image: {image_path}")
        
        try:
            start_time = time.time()
            
            # Encode image to base64
            with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Agricultural-focused system prompt
            agricultural_prompt = f"""You are an agricultural advisor. Analyze the image and answer: "{question}"

            Provide a brief response (2-3 sentences) with:
            - What you observe in the plant
            - Basic recommendation if any issues are visible

            Keep the advice practical but concise."""

            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system", 
                        "content": agricultural_prompt
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": question
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            analysis_response = response.choices[0].message.content
            
            logger.info(f"GPT-4 Vision response time: {response_time:.2f}s")
            logger.info(f"GPT-4 Vision analysis: {analysis_response[:100]}...")
            logger.info("========================================")
            logger.info(f"FINAL GPT-4 VISION OUTPUT:\n{analysis_response}")
            logger.info("========================================")
            
            return {
                "success": True,
                "response": analysis_response,
                "question": question,
                "image_path": image_path,
                "response_time": response_time,
                "fallback_used": True,
                "fallback_method": "gpt-4-vision"
            }
            
        except Exception as e:
            logger.error(f"GPT-4 Vision fallback failed: {str(e)}")
            return {
                "success": False,
                "error": f"GPT-4 Vision fallback failed: {str(e)}",
                "fallback_used": True,
                "fallback_method": "gpt-4-vision"
            }
    
    async def analyze_image(self, image_path: str, question: str) -> Dict[str, Any]:
        logger.info("======== VLM Image Analysis ========")
        logger.info(f"Analyzing image: {image_path}")
        logger.info(f"Question: {question}")
        
        try:
            if not os.path.exists(image_path):
                logger.error(f"Image file not found: {image_path}")
                return {
                    "success": False,
                    "error": f"Image file not found: {image_path}"
                }
            
            start_time = time.time()
            
            # Prepare multipart form data
            with open(image_path, 'rb') as image_file:
                files = {
                    'image': (os.path.basename(image_path), image_file, 'image/jpeg')
                }
                data = {
                    'question': question
                }
                
                logger.info(f"Sending request to: {self.base_url}{self.generate_endpoint}")
                logger.info(f"Timeout set to: {self.timeout}s")
                
                response = requests.post(
                    f"{self.base_url}{self.generate_endpoint}",
                    files=files,
                    data=data,
                    timeout=self.timeout
                )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            logger.info(f"VLLM response time: {response_time:.2f}s")
            logger.info(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Analysis successful: {result.get('success', False)}")
                
                if result.get('success'):
                    analysis_response = result.get('response', '')
                    logger.info(f"Analysis result: {analysis_response[:100]}...")
                    
                    return {
                        "success": True,
                        "response": analysis_response,
                        "question": question,
                        "image_path": image_path,
                        "response_time": response_time,
                        "fallback_used": False,
                        "primary_method": "vllm",
                        "raw_data": result
                    }
                else:
                    error_msg = result.get('error', 'Unknown error from VLLM')
                    logger.error(f"VLLM analysis failed: {error_msg}")
                    logger.info("Attempting GPT-4 Vision fallback...")
                    
                    # Try GPT-4 Vision fallback
                    fallback_result = await self._analyze_with_gpt4_vision(image_path, question)
                    fallback_result["vllm_error"] = error_msg
                    return fallback_result
            else:
                logger.error(f"Request failed with status: {response.status_code}")
                try:
                    error_data = response.json()
                    error_msg = error_data.get('detail', f'HTTP {response.status_code}')
                except:
                    error_msg = f'HTTP {response.status_code}'
                
                logger.info("Attempting GPT-4 Vision fallback...")
                
                # Try GPT-4 Vision fallback
                fallback_result = await self._analyze_with_gpt4_vision(image_path, question)
                fallback_result["vllm_error"] = error_msg
                return fallback_result
        
        except requests.exceptions.Timeout:
            logger.error(f"VLLM request timed out after {self.timeout}s")
            logger.info("Attempting GPT-4 Vision fallback...")
            
            # Try GPT-4 Vision fallback
            fallback_result = await self._analyze_with_gpt4_vision(image_path, question)
            fallback_result["vllm_error"] = f"Request timeout ({self.timeout}s)"
            return fallback_result
            
        except Exception as e:
            logger.error(f"VLLM analysis failed: {str(e)}")
            logger.info("Attempting GPT-4 Vision fallback...")
            
            # Try GPT-4 Vision fallback
            fallback_result = await self._analyze_with_gpt4_vision(image_path, question)
            fallback_result["vllm_error"] = str(e)
            return fallback_result
    
    async def test_connection(self) -> Dict[str, Any]:
        logger.info("======== Testing VLM Connection ========")
        
        # First check health
        health_result = await self.check_health()
        
        if not health_result.get("success"):
            return {
                "success": False,
                "test": "connection",
                "error": "Health check failed",
                "health_result": health_result
            }
        
        if not health_result.get("cuda_available"):
            return {
                "success": False,
                "test": "connection",
                "error": "CUDA not available on GPU server",
                "health_result": health_result
            }
        
        if health_result.get("vllm_status") != "loaded":
            return {
                "success": False,
                "test": "connection",
                "error": f"VLLM status: {health_result.get('vllm_status')}",
                "health_result": health_result
            }
        
        return {
            "success": True,
            "test": "connection",
            "message": "GPU server ready for image analysis",
            "health_result": health_result
        }