import asyncio  
import logging  
import re  
from typing import Dict, Any, Optional, List, Union  
from uuid import uuid4  

from app.flows.data_analysis_flow import DataAnalysisFlow  
# 第一轮测试暂时注释掉营销流程导入  
# from app.flows.marketing_flow import MarketingFlow  
from app.utils.memory_manager import RedisMemoryManager  
from app.utils.llm_factory import get_llm, DeepseekLLM  
from app.core.logger import logger  

class FlowManager:  
    """流程管理器 - 第一轮测试版本 (仅SQL翻译)"""  
    
    def __init__(self, redis_client):  
        self.redis_client = redis_client  
        self.memory_manager = RedisMemoryManager(redis_client)  
        self.data_analysis_flow = DataAnalysisFlow(redis_client)  
        # 第一轮测试暂时注释掉营销流程  
        # self.marketing_flow = MarketingFlow(redis_client)  
        self.llm = DeepseekLLM()  
    
    def _process_crew_output(self, result) -> str:  
        """处理CrewOutput对象转换为字符串，并检查错误"""  
        # 如果是错误字典，提取错误信息  
        if isinstance(result, dict) and "error" in result:  
            error_msg = result.get("message", str(result.get("error")))  
            raise Exception(error_msg)  
            
        # 处理CrewOutput对象  
        if hasattr(result, 'raw'):  
            result_str = result.raw  
        elif not isinstance(result, str):  
            result_str = str(result)  
        else:  
            result_str = result  
            
        # 增强错误检测  
        if self._is_error_result(result_str):  
            error_msg = self._extract_error_message(result_str)  
            # 记录更详细的错误信息  
            logger.error(f"检测到工具执行错误: {error_msg}")  
            logger.debug(f"完整错误信息: {result_str[:500]}")  
            raise Exception(error_msg)  
            
        return result_str  
    
    def _is_error_result(self, result: str) -> bool:  
        """检查结果是否包含错误信息"""  
        error_indicators = [  
            "错误:", "出错:", "执行出错:", "执行统计分析时出错", "生成数据可视化时出错",  
            "NameError:", "TypeError:", "AttributeError:", "ValueError:",  
            "unsupported operand", "not defined", "NoneType", "object has no attribute"  
        ]  
        
        if not isinstance(result, str):  
            return False  
            
        return any(indicator in result for indicator in error_indicators)  
    
    def _extract_error_message(self, result: str) -> str:  
        """从错误结果中提取错误信息"""  
        # 使用正则表达式查找常见错误模式  
        patterns = [  
            r"错误:\s*(.*?)(?:\n|$)",  
            r"出错:\s*(.*?)(?:\n|$)",  
            r"执行出错:\s*(.*?)(?:\n|$)",  
            r"执行统计分析时出错:\s*(.*?)(?:\n|$)",  
            r"生成数据可视化时出错:\s*(.*?)(?:\n|$)",  
            r"NameError:\s*(.*?)(?:\n|$)",  
            r"TypeError:\s*(.*?)(?:\n|$)",  
            r"ValueError:\s*(.*?)(?:\n|$)"  
        ]  
        
        for pattern in patterns:  
            match = re.search(pattern, result)  
            if match:  
                return match.group(1).strip()  
        
        # 如果没有匹配任何模式，返回前100个字符作为错误消息  
        return result[:100] + "..." if len(result) > 100 else result  
    
    async def _smart_flow_classification(self, query: str) -> str:  
        """第一轮测试版本 - 始终返回data_analysis"""  
        logger.info(f"[测试模式] 智能分流已禁用，固定返回'data_analysis'")  
        return "data_analysis"  # 第一轮测试总是返回data_analysis  
    
    async def execute_flow(  
        self,  
        flow_type: str,  
        job_id: str,  
        query: str,  
        user_id: int,  
        conversation_id: Optional[str] = None  
    ) -> str:  
        """执行指定的Flow - 第一轮测试版本 (仅SQL翻译)"""  
        try:  
            # 第一轮测试版本始终使用data_analysis流程  
            flow_type = "data_analysis"  
            logger.info(f"[测试模式] 强制使用data_analysis流程")  
            
            # 如果有会话ID，获取会话历史  
            history_text = ""  
            if conversation_id:  
                history = await self.memory_manager.get_conversation_history(conversation_id)  
                if history:  
                    # 提取历史消息并格式化  
                    formatted_history = []  
                    for msg in history:  
                        formatted_history.append(f"{msg['role']}: {msg['content']}")  
                    
                    # 将格式化的历史添加到输入数据  
                    history_text = "\n".join(formatted_history)  
            
            # 记录作业开始  
            await self.memory_manager.save_job_data(job_id, {  
                "progress": 0,   
                "current_output": f"准备执行第一轮测试 (仅SQL翻译)",  
                "status": "STARTED"  
            })  
            
            # 执行数据分析流程  
            try:  
                # 执行数据分析流程  
                result = await self.data_analysis_flow.execute(  
                    job_id=job_id,  
                    query=query,  
                    user_id=user_id,  
                    conversation_id=conversation_id,  
                    history=history_text  
                )  
                # 处理CrewOutput对象并检查错误  
                result = self._process_crew_output(result)  
                
                # 保存对话历史（如果需要）  
                if conversation_id:  
                    await self.memory_manager.append_message(  
                        conversation_id,  
                        "assistant",  
                        result  
                    )  
                
                return result  
                
            except Exception as e:  
                # 特定于数据分析流程的错误处理  
                error_message = f"SQL翻译测试执行失败: {str(e)}"  
                logger.error(error_message, exc_info=True)  
                
                # 更新作业状态  
                await self.memory_manager.save_job_data(job_id, {  
                    "progress": -1,  
                    "current_output": error_message,  
                    "status": "ERROR"  
                })  
                
                # 构建友好的错误响应  
                result = (  
                    f"## SQL翻译测试执行出错\n\n"  
                    f"{error_message}\n\n"  
                    f"请尝试提供更明确的查询或联系系统管理员。"  
                )  
                
                # 保存对话历史（如果需要）  
                if conversation_id:  
                    await self.memory_manager.append_message(  
                        conversation_id,  
                        "assistant",  
                        result  
                    )  
                
                return result  
            
        except Exception as e:  
            # 流程整体错误处理  
            logger.error(f"测试执行错误: {str(e)}", exc_info=True)  
            
            # 更新作业状态  
            await self.memory_manager.save_job_data(job_id, {  
                "progress": -1,  
                "current_output": f"错误: {str(e)}",  
                "status": "ERROR"  
            })  
            
            # 构建友好的错误响应  
            result = (  
                f"## 测试执行出错\n\n"  
                f"执行过程中遇到未处理的问题: {str(e)}\n\n"  
                f"请尝试更明确的查询或联系系统管理员。"  
            )  
            
            # 保存对话历史（如果需要）  
            if conversation_id:  
                await self.memory_manager.append_message(  
                    conversation_id,  
                    "assistant",  
                    result  
                )  
            
            return result  
    
    # 保留这些方法供测试完成后恢复  
    async def _get_data_analysis_result(self, query: str, history: str) -> str:  
        """[测试模式] 此方法在第一轮测试中不使用"""  
        logger.warning("[测试模式] 尝试调用了不应在第一轮测试中使用的方法")  
        return "测试模式: 此方法在第一轮测试中不可用"  
    
    def _get_fallback_analysis_result(self) -> str:  
        """[测试模式] 此方法在第一轮测试中不使用"""  
        logger.warning("[测试模式] 尝试调用了不应在第一轮测试中使用的方法")  
        return "测试模式: 此方法在第一轮测试中不可用"  
    
    async def _process_with_llm(self, query: str, history: str, flow_type: str) -> str:  
        """[测试模式] 此方法在第一轮测试中不使用"""  
        logger.warning("[测试模式] 尝试调用了不应在第一轮测试中使用的方法")  
        return "测试模式: 此方法在第一轮测试中不可用"  
    
    def _build_prompt(self, flow_type: str, query: str, history: str = "") -> str:  
        """[测试模式] 此方法在第一轮测试中不使用"""  
        logger.warning("[测试模式] 尝试调用了不应在第一轮测试中使用的方法")  
        return "测试模式: 此方法在第一轮测试中不可用"  
    
    async def get_job_progress(self, job_id: str) -> int:  
        """获取作业的当前进度"""  
        return await self.memory_manager.get_job_progress(job_id)  
    
    async def get_job_current_output(self, job_id: str) -> str:  
        """获取作业的当前输出文本"""  
        return await self.memory_manager.get_job_current_output(job_id)  