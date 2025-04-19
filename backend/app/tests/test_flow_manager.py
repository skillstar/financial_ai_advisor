import os  
import sys  
import json  
import asyncio  
from unittest.mock import MagicMock, patch  
from app.flows.flow_manager import FlowManager  
from app.core.logger import logger  

# 模拟Redis客户端  
class MockRedisClient:  
    def __init__(self):  
        self.storage = {}  
        
    def set(self, key, value, ex=None):  
        self.storage[key] = value  
        return True  
        
    def get(self, key):  
        return self.storage.get(key)  
        
    def delete(self, key):  
        if key in self.storage:  
            del self.storage[key]  
            return 1  
        return 0  

# 模拟RedisMemoryManager  
class MockMemoryManager:  
    def __init__(self, redis_client):  
        self.redis_client = redis_client  
        self.conversation_history = {}  
        self.job_data = {}  
        self.history_called = False  
        self.save_job_called = False  
        self.update_progress_called = False  
        self.append_message_called = False  
        
    async def get_conversation_history(self, conversation_id):  
        self.history_called = True  
        return [  
            {"role": "user", "content": "你好，我需要一些黄金投资的建议。"},  
            {"role": "assistant", "content": "我可以帮您分析黄金投资数据和策略。请问您想了解哪方面的信息？"},  
            {"role": "user", "content": "我想了解用户的投资行为。"}  
        ] if conversation_id in self.conversation_history else []  
    
    async def save_job_data(self, job_id, data):  
        self.save_job_called = True  
        self.job_data[job_id] = data  
        return True  
    
    async def update_job_progress(self, job_id, progress, output):  
        self.update_progress_called = True  
        if job_id not in self.job_data:  
            self.job_data[job_id] = {}  
        self.job_data[job_id].update({  
            "progress": progress,  
            "current_output": output,  
            "status": "ERROR" if progress < 0 else ("COMPLETED" if progress >= 100 else "RUNNING")  
        })  
        return True  
        
    async def append_message(self, conversation_id, role, content):  
        self.append_message_called = True  
        if conversation_id not in self.conversation_history:  
            self.conversation_history[conversation_id] = []  
        self.conversation_history[conversation_id].append({  
            "role": role,  
            "content": content  
        })  
        return True  
    
    async def get_job_progress(self, job_id):  
        return self.job_data.get(job_id, {}).get("progress", 0)  
    
    async def get_job_current_output(self, job_id):  
        return self.job_data.get(job_id, {}).get("current_output", "")  

# 模拟DataAnalysisFlow  
class MockDataAnalysisFlow:  
    def __init__(self, redis_client):  
        self.redis_client = redis_client  
        self.execution_called = False  
        self.last_query = None  
        
    async def execute(self, job_id, query, user_id, conversation_id=None, history=""):  
        self.execution_called = True  
        self.last_query = query  
        # 返回模拟的数据分析结果  
        return """  
        # 数据分析结果  

        ## 用户投资行为分析  
        
        1. **投资金额分布**  
           - 平均投资金额: ¥5,428  
           - 中位数投资金额: ¥3,200  
           - 最常见投资范围: ¥1,000-¥5,000 (占比62%)  
        
        2. **投资频率**  
           - 每月平均交易次数: 2.3次  
           - 高频用户群体(>5次/月): 18%  
           - 低频用户群体(<1次/月): 35%  
        
        3. **风险偏好分析**  
           - 低风险偏好: 45%  
           - 中风险偏好: 38%   
           - 高风险偏好: 17%  
        
        ## 营销建议  
        
        1. 针对低频高额投资用户，开发定期提醒服务  
        2. 为高风险偏好用户提供专业市场分析工具  
        3. 针对新用户设计渐进式投资教育计划  
        """  

# 模拟MarketingFlow  
class MockMarketingFlow:  
    def __init__(self, redis_client):  
        self.redis_client = redis_client  
        self.execution_called = False  
        self.last_data_analysis = None  
    
    async def execute(self, job_id, data_analysis_result, user_id, conversation_id=None):  
        self.execution_called = True  
        self.last_data_analysis = data_analysis_result  
        # 返回模拟的营销战略结果  
        return """  
        # 营销战略方案  

        ## 用户画像分析  

        1. **主要用户群体**  
           - 稳健型投资者(60%): 35-50岁，追求长期稳定收益  
           - 机会型投资者(25%): 28-40岁，寻求中短期增值机会  
           - 新手投资者(15%): 22-35岁，初次接触黄金投资  

        ## 营销战略框架  

        1. **差异化内容策略**  
           - 稳健型: 权威市场分析、长期投资组合建议  
           - 机会型: 短期趋势分析、价格突破点预警  
           - 新手型: 基础知识教程、小额定投指南  

        ## 创意活动方案  

        1. **黄金大师养成计划**  
           - 为新手设计的8周系列课程  
           - 每完成一个阶段获得相应徽章  
        
        2. **金市预见者挑战赛**  
           - 为机会型投资者设计的预测比赛  
           - 参与者预测未来一周黄金价格走势  
        """  

# 模拟DeepseekLLM  
class MockDeepseekLLM:  
    async def acompletion(self, messages):  
        # 简单地返回一个模拟的回复  
        query = messages[0]["content"] if messages else ""  
        return {  
            "choices": [  
                {  
                    "message": {  
                        "content": f"这是对'{query[:30]}...'的回复：\n\n黄金是一种重要的投资资产，可以用于对冲通货膨胀和市场风险。建议您考虑多元化投资策略，不要将所有资金都投入黄金。"  
                    }  
                }  
            ]  
        }  

# 异步测试函数  
async def test_data_analysis_flow():  
    print("开始测试FlowManager的数据分析流程...")  
    
    # 设置测试环境  
    mock_redis = MockRedisClient()  
    job_id = "test_manager_data_job"  
    test_query = "分析用户投资行为模式并提供营销建议"  
    user_id = 1001  
    conversation_id = "conv_test_123"  
    
    # 创建测试用例  
    try:  
        # 替换依赖  
        with patch('app.flows.flow_manager.RedisMemoryManager') as mock_memory_manager, \
             patch('app.flows.flow_manager.DataAnalysisFlow') as mock_data_flow, \
             patch('app.flows.flow_manager.MarketingFlow') as mock_marketing_flow, \
             patch('app.flows.flow_manager.DeepseekLLM') as mock_llm:  
            
            # 配置模拟对象  
            mock_memory_mgr = MockMemoryManager(mock_redis)  
            mock_memory_manager.return_value = mock_memory_mgr  
            
            mock_data = MockDataAnalysisFlow(mock_redis)  
            mock_data_flow.return_value = mock_data  
            
            mock_marketing = MockMarketingFlow(mock_redis)  
            mock_marketing_flow.return_value = mock_marketing  
            
            mock_llm.return_value = MockDeepseekLLM()  
            
            # 创建FlowManager实例  
            manager = FlowManager(mock_redis)  
            
            # 执行数据分析流程  
            result = await manager.execute_flow(  
                flow_type="data_analysis",  
                job_id=job_id,  
                query=test_query,  
                user_id=user_id,  
                conversation_id=conversation_id  
            )  
            
            # 验证结果  
            print("\n数据分析流程测试结果:")  
            print(f"{'='*50}")  
            
            # 1. 检查是否返回了结果  
            result_check = "数据分析结果" in result and "投资行为分析" in result  
            print(f"返回结果检查: {'通过✅' if result_check else '失败❌'}")  
            if not result_check:  
                print(f"实际结果: {result[:100]}...")  
            
            # 2. 检查是否调用了数据分析Flow的execute方法  
            flow_executed = mock_data.execution_called  
            print(f"数据分析Flow执行检查: {'通过✅' if flow_executed else '失败❌'}")  
            
            # 3. 检查作业数据是否被保存  
            job_saved = mock_memory_mgr.save_job_called  
            print(f"作业数据保存检查: {'通过✅' if job_saved else '失败❌'}")  
            
            # 总体结果  
            data_analysis_passed = result_check and flow_executed and job_saved  
            print(f"\n数据分析流程测试结果: {'通过✅' if data_analysis_passed else '失败❌'}")  
            
            return data_analysis_passed  
            
    except Exception as e:  
        print(f"测试过程中出错: {str(e)}")  
        import traceback  
        traceback.print_exc()  
        return False  

# 测试营销流程  
async def test_marketing_flow():  
    print("\n开始测试FlowManager的营销流程...")  
    
    # 设置测试环境  
    mock_redis = MockRedisClient()  
    job_id = "test_manager_marketing_job"  
    test_query = "设计黄金投资产品的营销策略"  
    user_id = 1002  
    conversation_id = "conv_test_456"  
    
    # 创建测试用例  
    try:  
        # 替换依赖  
        with patch('app.flows.flow_manager.RedisMemoryManager') as mock_memory_manager, \
             patch('app.flows.flow_manager.DataAnalysisFlow') as mock_data_flow, \
             patch('app.flows.flow_manager.MarketingFlow') as mock_marketing_flow, \
             patch('app.flows.flow_manager.DeepseekLLM') as mock_llm:  
            
            # 配置模拟对象  
            mock_memory_mgr = MockMemoryManager(mock_redis)  
            mock_memory_manager.return_value = mock_memory_mgr  
            
            mock_data = MockDataAnalysisFlow(mock_redis)  
            mock_data_flow.return_value = mock_data  
            
            mock_marketing = MockMarketingFlow(mock_redis)  
            mock_marketing_flow.return_value = mock_marketing  
            
            mock_llm.return_value = MockDeepseekLLM()  
            
            # 创建FlowManager实例  
            manager = FlowManager(mock_redis)  
            
            # 执行营销流程  
            result = await manager.execute_flow(  
                flow_type="marketing",  
                job_id=job_id,  
                query=test_query,  
                user_id=user_id,  
                conversation_id=conversation_id  
            )  
            
            # 验证结果  
            print("\n营销流程测试结果:")  
            print(f"{'='*50}")  
            
            # 1. 检查是否返回了结果  
            result_check = "营销战略方案" in result and "创意活动方案" in result  
            print(f"返回结果检查: {'通过✅' if result_check else '失败❌'}")  
            if not result_check:  
                print(f"实际结果: {result[:100]}...")  
            
            # 2. 检查是否调用了数据分析Flow的execute方法(用于获取数据分析结果)  
            data_flow_executed = mock_data.execution_called  
            print(f"数据分析执行检查: {'通过✅' if data_flow_executed else '失败❌'}")  
            
            # 3. 检查是否调用了营销Flow的execute方法  
            marketing_flow_executed = mock_marketing.execution_called  
            print(f"营销Flow执行检查: {'通过✅' if marketing_flow_executed else '失败❌'}")  
            
            # 4. 检查是否将数据分析结果传递给了营销Flow  
            data_passed = mock_marketing.last_data_analysis is not None  
            print(f"数据分析结果传递检查: {'通过✅' if data_passed else '失败❌'}")  
            
            # 总体结果  
            marketing_passed = result_check and data_flow_executed and marketing_flow_executed and data_passed  
            print(f"\n营销流程测试结果: {'通过✅' if marketing_passed else '失败❌'}")  
            
            return marketing_passed  
            
    except Exception as e:  
        print(f"测试过程中出错: {str(e)}")  
        import traceback  
        traceback.print_exc()  
        return False  

# 测试完整流程  
async def test_complete_flow():  
    print("\n开始测试FlowManager的完整流程...")  
    
    # 设置测试环境  
    mock_redis = MockRedisClient()  
    job_id = "test_manager_complete_job"  
    test_query = "为我的黄金交易平台做全面分析和营销规划"  
    user_id = 1003  
    conversation_id = "conv_test_789"  
    
    # 创建测试用例  
    try:  
        # 替换依赖  
        with patch('app.flows.flow_manager.RedisMemoryManager') as mock_memory_manager, \
             patch('app.flows.flow_manager.DataAnalysisFlow') as mock_data_flow, \
             patch('app.flows.flow_manager.MarketingFlow') as mock_marketing_flow, \
             patch('app.flows.flow_manager.DeepseekLLM') as mock_llm:  
            
            # 配置模拟对象  
            mock_memory_mgr = MockMemoryManager(mock_redis)  
            mock_memory_manager.return_value = mock_memory_mgr  
            
            mock_data = MockDataAnalysisFlow(mock_redis)  
            mock_data_flow.return_value = mock_data  
            
            mock_marketing = MockMarketingFlow(mock_redis)  
            mock_marketing_flow.return_value = mock_marketing  
            
            mock_llm.return_value = MockDeepseekLLM()  
            
            # 创建FlowManager实例  
            manager = FlowManager(mock_redis)  
            
            # 执行完整流程  
            result = await manager.execute_flow(  
                flow_type="complete",  
                job_id=job_id,  
                query=test_query,  
                user_id=user_id,  
                conversation_id=conversation_id  
            )  
            
            # 验证结果  
            print("\n完整流程测试结果:")  
            print(f"{'='*50}")  
            
            # 1. 检查是否返回了结果，结果应包含数据分析和营销两部分  
            data_in_result = "数据分析" in result and "投资行为分析" in result  
            marketing_in_result = "营销战略" in result and "创意活动方案" in result  
            result_check = data_in_result and marketing_in_result  
            
            print(f"返回结果检查: {'通过✅' if result_check else '失败❌'}")  
            if not result_check:  
                print(f"实际结果片段: {result[:150]}...")  
            
            # 2. 检查是否调用了数据分析Flow的execute方法  
            data_flow_executed = mock_data.execution_called  
            print(f"数据分析执行检查: {'通过✅' if data_flow_executed else '失败❌'}")  
            
            # 3. 检查是否调用了营销Flow的execute方法  
            marketing_flow_executed = mock_marketing.execution_called  
            print(f"营销Flow执行检查: {'通过✅' if marketing_flow_executed else '失败❌'}")  
            
            # 4. 检查是否更新了作业进度  
            progress_updated = mock_memory_mgr.update_progress_called  
            print(f"进度更新检查: {'通过✅' if progress_updated else '失败❌'}")  
            
            # 5. 检查是否保存了完整结果到对话历史  
            if conversation_id:  
                message_saved = mock_memory_mgr.append_message_called  
                print(f"对话历史保存检查: {'通过✅' if message_saved else '失败❌'}")  
            else:  
                message_saved = True  
            
            # 总体结果  
            complete_passed = result_check and data_flow_executed and marketing_flow_executed and progress_updated and message_saved  
            print(f"\n完整流程测试结果: {'通过✅' if complete_passed else '失败❌'}")  
            
            return complete_passed  
            
    except Exception as e:  
        print(f"测试过程中出错: {str(e)}")  
        import traceback  
        traceback.print_exc()  
        return False  

# 测试常规LLM查询  
async def test_llm_flow():  
    print("\n开始测试FlowManager的常规LLM查询...")  
    
    # 设置测试环境  
    mock_redis = MockRedisClient()  
    job_id = "test_manager_llm_job"  
    test_query = "黄金价格会上涨吗？"  
    user_id = 1004  
    conversation_id = "conv_test_abc"  
    
    # 创建测试用例  
    try:  
        # 替换依赖  
        with patch('app.flows.flow_manager.RedisMemoryManager') as mock_memory_manager, \
             patch('app.flows.flow_manager.DeepseekLLM') as mock_llm_class, \
             patch('app.flows.flow_manager.DataAnalysisFlow') as mock_data_flow, \
             patch('app.flows.flow_manager.MarketingFlow') as mock_marketing_flow:  
            
            # 配置模拟对象  
            mock_memory_mgr = MockMemoryManager(mock_redis)  
            mock_memory_manager.return_value = mock_memory_mgr  
            
            mock_llm = MockDeepseekLLM()  
            mock_llm_class.return_value = mock_llm  
            
            mock_data = MockDataAnalysisFlow(mock_redis)  
            mock_data_flow.return_value = mock_data  
            
            mock_marketing = MockMarketingFlow(mock_redis)  
            mock_marketing_flow.return_value = mock_marketing  
            
            # 创建FlowManager实例  
            manager = FlowManager(mock_redis)  
            
            # 执行常规LLM查询  
            result = await manager.execute_flow(  
                flow_type="general",  
                job_id=job_id,  
                query=test_query,  
                user_id=user_id,  
                conversation_id=conversation_id  
            )  
            
            # 验证结果  
            print("\nLLM查询测试结果:")  
            print(f"{'='*50}")  
            
            # 1. 检查是否返回了结果  
            result_check = "黄金" in result and "投资" in result  
            print(f"返回结果检查: {'通过✅' if result_check else '失败❌'}")  
            if not result_check:  
                print(f"实际结果: {result[:100]}...")  
            
            # 2. 检查是否没有调用特定的Flow  
            data_not_executed = not mock_data.execution_called  
            marketing_not_executed = not mock_marketing.execution_called  
            flow_check = data_not_executed and marketing_not_executed  
            
            print(f"Flow未执行检查: {'通过✅' if flow_check else '失败❌'}")  
            
            # 3. 检查是否更新了作业进度  
            progress_updated = mock_memory_mgr.update_progress_called  
            print(f"进度更新检查: {'通过✅' if progress_updated else '失败❌'}")  
            
            # 4. 检查是否保存了结果到对话历史  
            if conversation_id:  
                message_saved = mock_memory_mgr.append_message_called  
                print(f"对话历史保存检查: {'通过✅' if message_saved else '失败❌'}")  
            else:  
                message_saved = True  
            
            # 总体结果  
            llm_passed = result_check and flow_check and progress_updated and message_saved  
            print(f"\nLLM查询测试结果: {'通过✅' if llm_passed else '失败❌'}")  
            
            return llm_passed  
            
    except Exception as e:  
        print(f"测试过程中出错: {str(e)}")  
        import traceback  
        traceback.print_exc()  
        return False  

# 测试错误处理  
async def test_error_handling():  
    print("\n开始测试FlowManager的错误处理...")  
    
    # 设置测试环境  
    mock_redis = MockRedisClient()  
    job_id = "test_manager_error_job"  
    test_query = "错误测试查询"  
    user_id = 1005  
    
    # 创建测试用例  
    try:  
        # 替换依赖并注入错误  
        with patch('app.flows.flow_manager.RedisMemoryManager') as mock_memory_manager, \
             patch('app.flows.flow_manager.DataAnalysisFlow') as mock_data_flow, \
             patch('app.flows.flow_manager.MarketingFlow') as mock_marketing_flow:  
            
            # 配置模拟对象  
            mock_memory_mgr = MockMemoryManager(mock_redis)  
            mock_memory_manager.return_value = mock_memory_mgr  
            
            # 创建一个模拟的DataAnalysisFlow，会抛出异常  
            mock_data = MagicMock()  
            mock_data.execute.side_effect = Exception("模拟的数据分析错误")  
            mock_data_flow.return_value = mock_data  
            
            mock_marketing = MockMarketingFlow(mock_redis)  
            mock_marketing_flow.return_value = mock_marketing  
            
            # 创建FlowManager实例  
            manager = FlowManager(mock_redis)  
            
            # 执行查询(应该抛出异常)  
            error_caught = False  
            try:  
                result = await manager.execute_flow(  
                    flow_type="data_analysis",  
                    job_id=job_id,  
                    query=test_query,  
                    user_id=user_id  
                )  
                print(f"预期抛出异常，但实际返回了: {result}")  
            except Exception as e:  
                error_caught = True  
                error_message = str(e)  
                print(f"捕获到异常: {error_message}")  
            
            # 验证结果  
            print("\n错误处理测试结果:")  
            print(f"{'='*50}")  
            
            # 1. 检查是否捕获了异常  
            print(f"异常捕获检查: {'通过✅' if error_caught else '失败❌'}")  
            
            # 2. 检查是否将作业标记为错误  
            job_error_marked = job_id in mock_memory_mgr.job_data and \
                              mock_memory_mgr.job_data[job_id].get('status') == 'ERROR'  
                              
            print(f"作业错误状态检查: {'通过✅' if job_error_marked else '失败❌'}")  
            
            if job_error_marked:  
                error_progress = mock_memory_mgr.job_data[job_id].get('progress', 0) < 0  
                print(f"错误进度检查: {'通过✅' if error_progress else '失败❌'}")  
                
                error_output = "错误" in str(mock_memory_mgr.job_data[job_id].get('current_output', ''))  
                print(f"错误输出检查: {'通过✅' if error_output else '失败❌'}")  
                
                all_error_checks = error_progress and error_output  
            else:  
                all_error_checks = False  
            
            # 总体结果  
            error_passed = error_caught and job_error_marked and all_error_checks  
            print(f"\n错误处理测试结果: {'通过✅' if error_passed else '失败❌'}")  
            
            return error_passed  
            
    except Exception as e:  
        print(f"错误处理测试失败: {str(e)}")  
        import traceback  
        traceback.print_exc()  
        return False  

# 主函数  
async def main():  
    print("开始测试FlowManager组件...\n")  
    
    # 运行所有测试  
    data_analysis_result = await test_data_analysis_flow()  
    marketing_result = await test_marketing_flow()  
    complete_result = await test_complete_flow()  
    llm_result = await test_llm_flow()  
    error_result = await test_error_handling()  
    
    # 汇总结果  
    print("\n\n测试结果汇总:")  
    print(f"{'='*50}")  
    print(f"数据分析流程测试: {'通过✅' if data_analysis_result else '失败❌'}")  
    print(f"营销流程测试: {'通过✅' if marketing_result else '失败❌'}")  
    print(f"完整流程测试: {'通过✅' if complete_result else '失败❌'}")  
    print(f"LLM查询测试: {'通过✅' if llm_result else '失败❌'}")  
    print(f"错误处理测试: {'通过✅' if error_result else '失败❌'}")  
    
    all_passed = data_analysis_result and marketing_result and complete_result and llm_result and error_result  
    if all_passed:  
        print("\n🎉 所有测试通过! FlowManager组件工作正常!")  
    else:  
        print("\n❌ 部分测试未通过，请检查失败项。")  
    
    return all_passed  

if __name__ == "__main__":  
    # 运行主函数 (异步)  
    asyncio.run(main())  