import os  
import sys  
import json  
import asyncio  
from unittest.mock import MagicMock, patch  
from app.flows.data_analysis_flow import DataAnalysisFlow  
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
        
    async def append_message(self, conversation_id, role, content):  
        if conversation_id not in self.conversation_history:  
            self.conversation_history[conversation_id] = []  
        self.conversation_history[conversation_id].append({  
            "role": role,  
            "content": content  
        })  
        return True  
    
    async def save_job_data(self, job_id, data):  
        self.job_data[job_id] = data  
        return True  
    
    async def update_job_progress(self, job_id, progress, output):  
        if job_id not in self.job_data:  
            self.job_data[job_id] = {}  
        self.job_data[job_id].update({  
            "progress": progress,  
            "current_output": output,  
            "status": "ERROR" if progress < 0 else ("COMPLETED" if progress >= 100 else "RUNNING")  
        })  
        return True  

# 模拟DataAnalysisCrew  
class MockDataAnalysisCrew:  
    def __init__(self, redis_client, job_id, query, history=""):  
        self.redis_client = redis_client  
        self.job_id = job_id  
        self.query = query  
        self.history = history  
        self.execution_called = False  
    
    def execute(self):  
        self.execution_called = True  
        # 返回模拟的分析结果  
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

# 异步测试函数  
async def test_data_analysis_flow():  
    print("开始测试DataAnalysisFlow...")  
    
    # 设置测试环境  
    mock_redis = MockRedisClient()  
    job_id = "test_flow_job_123"  
    test_query = "分析用户投资行为模式并提供营销建议"  
    user_id = 1001  
    conversation_id = "conv_test_123"  
    
    # 创建测试用例  
    try:  
        # 替换依赖  
        with patch('app.flows.data_analysis_flow.RedisMemoryManager') as mock_memory_manager, \
             patch('app.flows.data_analysis_flow.DataAnalysisCrew') as mock_crew_class:  
            
            # 配置模拟对象  
            mock_memory_mgr = MockMemoryManager(mock_redis)  
            mock_memory_manager.return_value = mock_memory_mgr  
            
            mock_crew = MockDataAnalysisCrew(mock_redis, job_id, test_query)  
            mock_crew_class.return_value = mock_crew  
            
            # 创建DataAnalysisFlow实例  
            flow = DataAnalysisFlow(mock_redis)  
            
            # 执行flow  
            result = await flow.execute(  
                job_id=job_id,  
                query=test_query,  
                user_id=user_id,  
                conversation_id=conversation_id,  
                history="之前讨论了用户数据分析的重要性"  
            )  
            
            # 验证结果  
            print("\n测试结果:")  
            print(f"{'='*50}")  
            
            # 1. 检查是否返回了结果  
            result_check = "数据分析结果" in result and "营销建议" in result  
            print(f"返回结果检查: {'通过✅' if result_check else '失败❌'}")  
            if not result_check:  
                print(f"实际结果: {result[:100]}...")  
            
            # 2. 检查是否调用了Crew的execute方法  
            crew_executed = mock_crew.execution_called  
            print(f"Crew执行检查: {'通过✅' if crew_executed else '失败❌'}")  
            
            # 3. 检查对话历史是否被保存  
            history_saved = conversation_id in mock_memory_mgr.conversation_history  
            print(f"对话历史保存检查: {'通过✅' if history_saved else '失败❌'}")  
            
            if history_saved:  
                history = mock_memory_mgr.conversation_history[conversation_id]  
                last_message = history[-1] if history else None  
                print(f"保存的最后一条消息角色: {last_message['role'] if last_message else 'None'}")  
            
            # 总体结果  
            all_passed = result_check and crew_executed and history_saved  
            print(f"\n总体测试结果: {'通过✅' if all_passed else '失败❌'}")  
            
            return all_passed  
            
    except Exception as e:  
        print(f"测试过程中出错: {str(e)}")  
        import traceback  
        traceback.print_exc()  
        return False  

# 测试错误处理  
async def test_error_handling():  
    print("\n开始测试错误处理...")  
    
    # 设置测试环境  
    mock_redis = MockRedisClient()  
    job_id = "test_flow_error_job"  
    test_query = "错误测试查询"  
    user_id = 1002  
    
    try:  
        # 修复：直接替换_run_crew_in_thread方法，使其抛出异常  
        with patch('app.flows.data_analysis_flow.RedisMemoryManager') as mock_memory_manager, \
             patch('app.flows.data_analysis_flow.DataAnalysisFlow._run_crew_in_thread') as mock_run_in_thread:  
            
            # 配置模拟对象  
            mock_memory_mgr = MockMemoryManager(mock_redis)  
            mock_memory_manager.return_value = mock_memory_mgr  
            
            # 设置 _run_crew_in_thread 方法抛出异常  
            test_error = Exception("模拟的数据分析错误")  
            mock_run_in_thread.side_effect = test_error  
            
            # 创建DataAnalysisFlow实例  
            flow = DataAnalysisFlow(mock_redis)  
            
            # 执行flow (应该抛出异常)  
            error_caught = False  
            try:  
                result = await flow.execute(  
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
            error_check = error_caught  
            print(f"异常捕获检查: {'通过✅' if error_check else '失败❌'}")  
            
            # 检查save_job_data是否被调用  
            save_called = mock_memory_mgr.job_data.get(job_id) is not None  
            print(f"保存作业数据调用检查: {'通过✅' if save_called else '失败❌'}")  
            
            if save_called:  
                job_data = mock_memory_mgr.job_data.get(job_id, {})  
                status_correct = job_data.get('status') == 'ERROR'  
                progress_correct = job_data.get('progress') == -1  
                error_in_output = "错误" in str(job_data.get('current_output', ''))  
                
                print(f"作业状态检查: {'通过✅' if status_correct else '失败❌'}")  
                print(f"作业进度检查: {'通过✅' if progress_correct else '失败❌'}")  
                print(f"错误消息检查: {'通过✅' if error_in_output else '失败❌'}")  
                
                all_checks = status_correct and progress_correct and error_in_output  
            else:  
                all_checks = False  
            
            return error_check and all_checks  
            
    except Exception as e:  
        print(f"错误处理测试失败: {str(e)}")  
        import traceback  
        traceback.print_exc()  
        return False  

# 主函数  
async def main():  
    print("开始测试DataAnalysisFlow组件...\n")  
    
    # 运行功能测试  
    main_test_result = await test_data_analysis_flow()  
    
    # 运行错误处理测试  
    error_test_result = await test_error_handling()  
    
    # 汇总结果  
    print("\n测试结果汇总:")  
    print(f"主要功能测试: {'通过✅' if main_test_result else '失败❌'}")  
    print(f"错误处理测试: {'通过✅' if error_test_result else '失败❌'}")  
    
    all_passed = main_test_result and error_test_result  
    if all_passed:  
        print("\n🎉 所有测试通过! DataAnalysisFlow组件工作正常!")  
    else:  
        print("\n❌ 部分测试未通过，请检查失败项。")  
    
    return all_passed  

if __name__ == "__main__":  
    # 运行主函数 (异步)  
    asyncio.run(main())  