import asyncio  
import logging  
import re  
from typing import Dict, Any, Optional, List, Union  
from uuid import uuid4  

from app.flows.data_analysis_flow import DataAnalysisFlow  
from app.flows.marketing_flow import MarketingFlow  
from app.utils.memory_manager import RedisMemoryManager  
from app.utils.llm_factory import get_llm, DeepseekLLM  
from app.core.logger import logger  

class FlowManager:  
    """流程管理器 - 协调不同Flow的执行"""  
    
    def __init__(self, redis_client):  
        self.redis_client = redis_client  
        self.memory_manager = RedisMemoryManager(redis_client)  
        self.data_analysis_flow = DataAnalysisFlow(redis_client)  
        self.marketing_flow = MarketingFlow(redis_client)  
        self.llm = DeepseekLLM()  # 初始化用于智能分流的LLM  
    
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
        """使用LLM智能分析用户查询意图，确定最合适的流程类型"""  
        prompt = f"""请分析以下用户查询，并确定最适合的处理流程类型。  

    用户查询: "{query}"  

    可选的流程类型:  
    1. "data_analysis" - 仅执行数据分析，适用于只需查询数据、生成报表等基础需求  
    2. "marketing" - 仅执行营销策略制定，适用于已有数据分析结果，只需要营销建议的情况  
    3. "complete" - 先执行数据分析再执行营销策略制定，适用于需要从数据发掘洞察并据此制定营销策略的综合性需求  

    请分析查询的深层意图与复杂度，仅回复一个流程类型的字符串，不要有任何其他内容: "data_analysis" 或 "marketing" 或 "complete"。"""  

        messages = [{"role": "user", "content": prompt}]  
        try:  
            response = await self.llm.acompletion(messages)  
            content = response['choices'][0]['message']['content'].strip()  
            
            # 增强的预处理逻辑 - 移除引号和额外文本  
            # 1. 检查是否包含流程类型关键词  
            if "complete" in content.lower():  
                flow_type = "complete"  
            elif "marketing" in content.lower():  
                flow_type = "marketing"  
            elif "data_analysis" in content.lower() or "data analysis" in content.lower():  
                flow_type = "data_analysis"  
            else:  
                # 2. 尝试提取引号中的内容  
                match = re.search(r'"([^"]*)"', content)  
                if match:  
                    extracted = match.group(1).lower()  
                    if extracted in ["data_analysis", "marketing", "complete"]:  
                        flow_type = extracted  
                    else:  
                        logger.warning(f"从引号中提取的流程类型无效: {extracted}，使用默认值")  
                        flow_type = "complete"  # 使用complete作为默认，因为它是最全面的流程  
                else:  
                    logger.warning(f"无法从LLM返回中提取有效流程类型: {content}，使用默认值")  
                    flow_type = "complete"  # 默认使用complete流程  
            
            # 记录更详细的日志  
            logger.info(f"LLM原始返回: '{content}' -> 解析后流程类型: '{flow_type}'")  
            logger.info(f"智能分流结果 - 查询: '{query}' -> 流程类型: '{flow_type}'")  
            return flow_type  
            
        except Exception as e:  
            logger.error(f"智能分流失败: {str(e)}", exc_info=True)  
            # 对于包含营销相关词汇的查询，默认使用complete流程  
            if any(word in query.lower() for word in ["营销", "策略", "方案", "推广", "campaign", "marketing"]):  
                return "complete"  
            return "data_analysis"  # 其他情况使用默认流程类型  
    
    async def execute_flow(  
        self,  
        flow_type: str,  
        job_id: str,  
        query: str,  
        user_id: int,  
        conversation_id: Optional[str] = None  
    ) -> str:  
        """执行指定的Flow"""  
        try:  
            # 智能分流决策 - 根据查询内容动态确定最合适的流程类型  
            if flow_type == "data_analysis" or flow_type == "auto":  
                # 只在必要时使用智能分流  
                smart_flow_type = await self._smart_flow_classification(query)  
                if smart_flow_type != flow_type:  
                    logger.info(f"智能分流: 将流程从 '{flow_type}' 升级为 '{smart_flow_type}'")  
                    flow_type = smart_flow_type  
            
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
                "current_output": f"准备执行{flow_type}流程",  
                "status": "STARTED"  
            })  
            
            # 根据流程类型选择不同的处理方式  
            if flow_type == "data_analysis":  
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
                    error_message = f"数据分析执行失败: {str(e)}"  
                    logger.error(error_message, exc_info=True)  
                    
                    # 更新作业状态  
                    await self.memory_manager.save_job_data(job_id, {  
                        "progress": -1,  
                        "current_output": error_message,  
                        "status": "ERROR"  
                    })  
                    
                    # 构建友好的错误响应  
                    result = (  
                        f"## 数据分析执行出错\n\n"  
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
                
            elif flow_type == "marketing":  
                try:  
                    # 首先获取或生成数据分析结果  
                    try:  
                        data_analysis_result = await self._get_data_analysis_result(query, history_text)  
                    except Exception as da_error:  
                        logger.error(f"营销流程中的数据分析步骤失败: {str(da_error)}", exc_info=True)  
                        # 使用备用数据分析结果  
                        data_analysis_result = self._get_fallback_analysis_result()  
                        
                        # 更新作业进度，告知用户我们使用了备用数据  
                        await self.memory_manager.update_job_progress(  
                            job_id,  
                            25,  
                            f"数据分析过程中出现问题，使用备用数据继续...\n\n{data_analysis_result}"  
                        )  
                    
                    # 执行营销战略流程  
                    result = await self.marketing_flow.execute(  
                        job_id=job_id,  
                        data_analysis_result=data_analysis_result,  
                        user_id=user_id,  
                        conversation_id=conversation_id  
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
                    # 特定于营销流程的错误处理  
                    error_message = f"营销策略执行失败: {str(e)}"  
                    logger.error(error_message, exc_info=True)  
                    
                    # 更新作业状态  
                    await self.memory_manager.save_job_data(job_id, {  
                        "progress": -1,  
                        "current_output": error_message,  
                        "status": "ERROR"  
                    })  
                    
                    # 构建友好的错误响应  
                    result = (  
                        f"## 营销策略执行出错\n\n"  
                        f"{error_message}\n\n"  
                        f"请尝试提供更明确的需求或联系系统管理员。"  
                    )  
                    
                    # 保存对话历史（如果需要）  
                    if conversation_id:  
                        await self.memory_manager.append_message(  
                            conversation_id,  
                            "assistant",  
                            result  
                        )  
                    
                    return result  
                
            elif flow_type == "complete":  
                try:  
                    # 完整流程第一步：数据分析  
                    try:  
                        # 执行数据分析流程  
                        data_analysis_result = await self.data_analysis_flow.execute(  
                            job_id=job_id,  
                            query=query,  
                            user_id=user_id,  
                            history=history_text  
                        )  
                        
                        # 处理CrewOutput对象并检查错误  
                        data_analysis_result = self._process_crew_output(data_analysis_result)  
                        
                        # 更新进度  
                        await self.memory_manager.update_job_progress(  
                            job_id,   
                            50,  
                            f"数据分析完成，开始营销战略制定...\n\n{data_analysis_result}"  
                        )  
                    except Exception as da_error:  
                        # 数据分析失败，但尝试继续进行营销部分  
                        logger.error(f"完整流程中的数据分析步骤失败: {str(da_error)}", exc_info=True)  
                        
                        # 使用备用数据分析结果  
                        data_analysis_result = self._get_fallback_analysis_result()  
                        
                        # 更新作业进度，告知用户我们使用了备用数据  
                        await self.memory_manager.update_job_progress(  
                            job_id,  
                            25,  
                            f"数据分析过程中出现问题，使用备用数据继续...\n\n{data_analysis_result}"  
                        )  
                    
                    # 完整流程第二步：营销战略  
                    try:  
                        # 执行营销战略流程  
                        marketing_result = await self.marketing_flow.execute(  
                            job_id=job_id,  
                            data_analysis_result=data_analysis_result,  
                            user_id=user_id  
                        )  
                        
                        # 处理CrewOutput对象并检查错误   
                        marketing_result = self._process_crew_output(marketing_result)  
                        
                        # 组合完整结果  
                        result = f"# 黄金交易平台完整分析\n\n## 第一部分：数据分析\n\n{data_analysis_result}\n\n## 第二部分：营销战略\n\n{marketing_result}"  
                        
                    except Exception as marketing_error:  
                        # 营销部分失败但数据分析成功  
                        logger.error(f"完整流程中的营销战略步骤失败: {str(marketing_error)}", exc_info=True)  
                        
                        # 构建部分成功的结果  
                        result = (  
                            f"# 黄金交易平台分析（部分完成）\n\n"  
                            f"## 第一部分：数据分析\n\n{data_analysis_result}\n\n"  
                            f"## 第二部分：营销战略\n\n"  
                            f"**营销战略生成失败**：{str(marketing_error)}\n\n"  
                            f"请尝试单独执行营销战略流程或联系系统管理员。"  
                        )  
                        
                        # 更新作业状态为部分完成  
                        await self.memory_manager.save_job_data(job_id, {  
                            "progress": 75,  
                            "current_output": result,  
                            "status": "PARTIAL_COMPLETE"  
                        })  
                    
                    # 无论营销部分成功与否，都更新最终结果  
                    await self.memory_manager.update_job_progress(job_id, 100, result)  
                    
                    # 保存对话历史（如果需要）  
                    if conversation_id:  
                        await self.memory_manager.append_message(  
                            conversation_id,  
                            "assistant",  
                            result  
                        )  
                    
                    return result  
                    
                except Exception as e:  
                    # 完整流程中的总体错误处理  
                    error_message = f"完整分析流程执行失败: {str(e)}"  
                    logger.error(error_message, exc_info=True)  
                    
                    # 更新作业状态  
                    await self.memory_manager.save_job_data(job_id, {  
                        "progress": -1,  
                        "current_output": error_message,  
                        "status": "ERROR"  
                    })  
                    
                    # 构建友好的错误响应  
                    result = (  
                        f"## 完整分析流程执行出错\n\n"  
                        f"{error_message}\n\n"  
                        f"请尝试拆分为单独的数据分析和营销需求，或联系系统管理员。"  
                    )  
                    
                    # 保存对话历史（如果需要）  
                    if conversation_id:  
                        await self.memory_manager.append_message(  
                            conversation_id,  
                            "assistant",  
                            result  
                        )  
                    
                    return result  
                
            else:  
                # 使用Deepseek直接处理普通查询  
                try:  
                    result = await self._process_with_llm(query, history_text, flow_type)  
                    await self.memory_manager.update_job_progress(job_id, 100, result)  
                    
                    # 如果有会话ID，保存对话历史  
                    if conversation_id:  
                        await self.memory_manager.append_message(  
                            conversation_id,  
                            "assistant",  
                            result  
                        )  
                        
                    return result  
                    
                except Exception as e:  
                    # LLM处理错误  
                    error_message = f"LLM处理查询失败: {str(e)}"  
                    logger.error(error_message, exc_info=True)  
                    
                    # 更新作业状态  
                    await self.memory_manager.save_job_data(job_id, {  
                        "progress": -1,  
                        "current_output": error_message,  
                        "status": "ERROR"  
                    })  
                    
                    # 构建友好的错误响应  
                    result = (  
                        f"## 处理查询时出错\n\n"  
                        f"{error_message}\n\n"  
                        f"请尝试重新表述您的问题或联系系统管理员。"  
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
            logger.error(f"Flow执行错误: {str(e)}", exc_info=True)  
            
            # 更新作业状态  
            await self.memory_manager.save_job_data(job_id, {  
                "progress": -1,  
                "current_output": f"错误: {str(e)}",  
                "status": "ERROR"  
            })  
            
            # 构建友好的错误响应  
            result = (  
                f"## 执行出错\n\n"  
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
    
    async def _get_data_analysis_result(self, query: str, history: str) -> str:  
        """获取数据分析结果，用于营销流程"""  
        try:  
            # 创建临时作业ID  
            temp_job_id = f"temp_{str(uuid4())}"  
            
            # 执行数据分析流程  
            result = await self.data_analysis_flow.execute(  
                job_id=temp_job_id,  
                query=query,  
                user_id=0,  # 临时用户ID  
                history=history  
            )  
            
            # 处理CrewOutput对象并检查错误  
            result = self._process_crew_output(result)  
            
            return result  
        except Exception as e:  
            logger.error(f"获取数据分析结果失败: {str(e)}")  
            # 向上抛出异常，让调用者处理  
            raise  
    
    def _get_fallback_analysis_result(self) -> str:  
        """提供备用的数据分析结果，用于数据分析失败的情况"""  
        return """  
        ## 数据分析简要结果 (备用数据)  

        ### 用户分析  
        - 高价值用户群体: 45-60岁男性，高频交易者  
        - 稳定用户群体: 35-45岁，定期小额交易  
        - 新兴用户群体: 25-35岁，科技偏好高，移动端操作  

        ### 交易行为  
        - 交易高峰: 工作日10:00-15:00  
        - 客单价: 平均¥5,500  
        - 频次: 每用户每月2.3次  
        
        ### 风险偏好分布  
        - 保守型: 30% (平均交易金额¥3,200)  
        - 平衡型: 45% (平均交易金额¥5,500)  
        - 进取型: 25% (平均交易金额¥9,800)  
        
        ### 用户价值分层  
        - 高价值用户: 18% (贡献65%交易额)  
        - 中价值用户: 32% (贡献25%交易额)  
        - 低价值用户: 50% (贡献10%交易额)  
        
        > 注意：这是备用数据，由于原始数据分析失败而提供。  
        """  
    
    async def _process_with_llm(self, query: str, history: str, flow_type: str) -> str:  
        """使用Deepseek直接处理查询"""  
        llm = DeepseekLLM()  
        
        prompt = self._build_prompt(flow_type, query, history)  
        
        messages = [{"role": "user", "content": prompt}]  
        response = await llm.acompletion(messages)  
        
        return response['choices'][0]['message']['content']  
    
    def _build_prompt(self, flow_type: str, query: str, history: str = "") -> str:  
        """构建提示词"""  
        base_prompt = (  
            "你是一个专业的黄金交易分析助手，帮助用户分析数据和制定营销策略。\n\n"  
            f"用户历史对话:\n{history}\n\n"  
            f"用户当前问题: {query}\n\n"  
        )  
        
        if flow_type == "data_analysis":  
            prompt = base_prompt + (  
                "请你扮演数据分析专家，使用以下数据表进行分析:\n"  
                "- users: 保存用户的基本信息和财务状况\n"  
                "- transactions: 记录用户的每笔交易（买入和卖出黄金）\n"  
                "- products: 存储黄金产品信息\n"  
                "- user_profiles: 记录用户的投资风险偏好和偏好类型\n\n"  
                "请首先分析用户可能需要的SQL查询，然后提供详细的数据分析结果，包括统计分析、可视化解读和初步的营销建议。"  
            )  
        elif flow_type == "marketing":  
            prompt = base_prompt + (  
                "请你扮演营销策略专家，为黄金交易平台制定精准的营销战略:\n"  
                "1. 分析用户画像，确定目标客群\n"  
                "2. 制定营销战略框架，包括渠道选择和时间安排\n"  
                "3. 设计有吸引力的营销活动\n"  
                "4. 编写营销文案\n\n"  
                "请考虑用户的投资风险偏好、交易行为和市场趋势，提供完整的营销方案。"  
            )  
        elif flow_type == "complete":  
            prompt = base_prompt + (  
                "请你综合发挥数据分析师和营销专家的能力，为黄金交易平台提供全面分析:\n"  
                "1. 首先进行数据分析，了解用户行为和交易模式\n"  
                "2. 基于分析结果，识别高价值客户群体\n"  
                "3. 制定针对性的营销策略\n"  
                "4. 设计创意活动和文案\n\n"  
                "请提供既有数据支持又有具体执行计划的完整解决方案。"  
            )  
        else:  
            prompt = base_prompt + "请回答用户的问题，提供专业的黄金交易相关建议。"  
        
        return prompt  
    
    async def get_job_progress(self, job_id: str) -> int:  
        """获取作业的当前进度"""  
        return await self.memory_manager.get_job_progress(job_id)  
    
    async def get_job_current_output(self, job_id: str) -> str:  
        """获取作业的当前输出文本"""  
        return await self.memory_manager.get_job_current_output(job_id)  