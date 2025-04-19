import os  
import aiohttp  
import json  
import asyncio  
from typing import Dict, Any, List, Optional, AsyncGenerator  
import logging  
from app.core.config import settings  

logger = logging.getLogger(__name__)  

class DeepseekLLM:  
    """Deepseek API集成"""  
    
    def __init__(  
        self,  
        api_key: str = None,  
        api_base: str = None,  
        model: str = "deepseek-chat",  
        temperature: float = 0.7,  
        max_tokens: int = 500,  
    ):  
        self.api_key = api_key or settings.DEEPSEEK_API_KEY  
        self.api_base = api_base or settings.DEEPSEEK_API_BASE  
        self.model = model or settings.LLM_MODEL  
        self.temperature = temperature  
        self.max_tokens = max_tokens  
        
        if not self.api_key:  
            raise ValueError("Deepseek API 密钥未提供")  
    
    async def acompletion(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:  
        """执行异步聊天完成请求"""  
        headers = {  
            "Content-Type": "application/json",  
            "Authorization": f"Bearer {self.api_key}"  
        }  
        
        # 准备请求数据  
        data = {  
            "model": self.model,  
            "messages": messages,  
            "temperature": kwargs.get("temperature", self.temperature),  
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),  
        }  
        
        # 添加其他有效参数  
        for key, value in kwargs.items():  
            if key not in data and key not in ["stream"]:  
                data[key] = value  
        
        url = f"{self.api_base}/chat/completions"  
        
        try:  
            async with aiohttp.ClientSession() as session:  
                async with session.post(url, headers=headers, json=data) as response:  
                    if response.status != 200:  
                        error_text = await response.text()  
                        raise Exception(f"API请求失败: {response.status} - {error_text}")  
                    
                    result = await response.json()  
                    return result  
        except Exception as e:  
            logger.error(f"Deepseek API调用失败: {str(e)}")  
            raise  
    
    async def astream_completion(self, messages: List[Dict[str, str]], **kwargs) -> AsyncGenerator[str, None]:  
        """执行流式聊天完成请求"""  
        headers = {  
            "Content-Type": "application/json",  
            "Authorization": f"Bearer {self.api_key}"  
        }  
        
        # 准备请求数据  
        data = {  
            "model": self.model,  
            "messages": messages,  
            "temperature": kwargs.get("temperature", self.temperature),  
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),  
            "stream": True  
        }  
        
        # 添加其他有效参数  
        for key, value in kwargs.items():  
            if key not in data and key not in ["stream"]:  
                data[key] = value  
        
        url = f"{self.api_base}/chat/completions"  
        
        try:  
            async with aiohttp.ClientSession() as session:  
                async with session.post(url, headers=headers, json=data) as response:  
                    if response.status != 200:  
                        error_text = await response.text()  
                        raise Exception(f"API请求失败: {response.status} - {error_text}")  
                    
                    # 处理流式响应  
                    async for line in response.content:  
                        line = line.decode('utf-8').strip()  
                        if line.startswith('data: '):  
                            line = line[6:].strip()  
                            if line == "[DONE]":  
                                break  
                            try:  
                                chunk = json.loads(line)  
                                delta = chunk.get('choices', [{}])[0].get('delta', {})  
                                content = delta.get('content', '')  
                                if content:  
                                    yield content  
                            except json.JSONDecodeError:  
                                logger.warning(f"无法解析JSON: {line}")  
        except Exception as e:  
            logger.error(f"Deepseek流式API调用失败: {str(e)}")  
            yield f"生成文本时出错: {str(e)}"  

    # CrewAI 接口兼容方法  
    def generate(self, prompt: str) -> str:  
        """同步生成文本（用于CrewAI）"""  
        loop = asyncio.get_event_loop()  
        messages = [{"role": "user", "content": prompt}]  
        response = loop.run_until_complete(self.acompletion(messages))  
        return response['choices'][0]['message']['content']  

def get_llm(  
    provider: str = None,  
    model: str = None,  
    temperature: float = None,  
    max_tokens: int = None  
) -> Any:  
    """创建LLM实例"""  
    
    provider = provider or settings.LLM_PROVIDER  
    model = model or settings.LLM_MODEL  
    temperature = temperature or settings.LLM_TEMPERATURE  
    max_tokens = max_tokens or settings.LLM_MAX_TOKENS  
    
    if provider.lower() == "deepseek":  
        return DeepseekLLM(  
            model=model,  
            temperature=temperature,  
            max_tokens=max_tokens  
        )  
    else:  
        raise ValueError(f"不支持的LLM提供商: {provider}")  