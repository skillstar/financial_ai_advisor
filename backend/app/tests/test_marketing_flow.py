import os  
import sys  
import json  
import asyncio  
from unittest.mock import MagicMock, patch  
from app.flows.marketing_flow import MarketingFlow  
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

# 模拟MarketingCrew  
class MockMarketingCrew:  
    def __init__(self, redis_client, job_id, data_analysis_result):  
        self.redis_client = redis_client  
        self.job_id = job_id  
        self.data_analysis_result = data_analysis_result  
        self.execution_called = False  
    
    def execute(self):  
        self.execution_called = True  
        # 返回模拟的营销战略结果  
        return """  
        # 营销战略方案  

        ## 用户画像分析  

        1. **主要用户群体**  
           - 稳健型投资者(60%): 35-50岁，追求长期稳定收益  
           - 机会型投资者(25%): 28-40岁，寻求中短期增值机会  
           - 新手投资者(15%): 22-35岁，初次接触黄金投资  

        2. **行为特征**  
           - 投资频率: 稳健型月均1-2次，机会型周均1-2次  
           - 平均投资额: 稳健型¥10,000+，机会型¥5,000+，新手型¥2,000+  
           - 渠道偏好: 稳健型偏好PC端，机会型和新手型偏好移动端  

        ## 营销战略框架  

        1. **差异化内容策略**  
           - 稳健型: 权威市场分析、长期投资组合建议  
           - 机会型: 短期趋势分析、价格突破点预警  
           - 新手型: 基础知识教程、小额定投指南  

        2. **渠道组合**  
           - 线上渠道: 官网博客(40%)、移动APP(35%)、社交媒体(25%)  
           - 线下渠道: 投资讲座(季度)、VIP客户沙龙(月度)  

        ## 创意活动方案  

        1. **黄金大师养成计划**  
           - 为新手设计的8周系列课程  
           - 每完成一个阶段获得相应徽章  
           - 课程毕业可享受投资顾问一对一咨询  

        2. **金市预见者挑战赛**  
           - 为机会型投资者设计的预测比赛  
           - 参与者预测未来一周黄金价格走势  
           - 最准确预测者获得交易手续费减免  

        3. **稳金有道VIP俱乐部**  
           - 针对高净值稳健型客户  
           - 提供行业专家季度宏观分析  
           - 专属投资顾问定制投资组合  
        """  

# 异步测试函数  
async def test_marketing_flow():  
    print("开始测试MarketingFlow...")  
    
    # 设置测试环境  
    mock_redis = MockRedisClient()  
    job_id = "test_marketing_flow_123"  
    data_analysis_result = """  
    数据分析结果:  
    用户投资行为偏好明显分化，需要差异化营销策略。  
    60%用户属于稳健型，25%属于机会型，15%是新手投资者。  
    平台流量主要来源是移动端(65%)和PC端(35%)。  
    """  
    user_id = 1001  
    conversation_id = "conv_market_123"  
    
    # 创建测试用例  
    try:  
        # 替换依赖  
        with patch('app.flows.marketing_flow.RedisMemoryManager') as mock_memory_manager, \
             patch('app.flows.marketing_flow.MarketingCrew') as mock_crew_class:  
            
            # 配置模拟对象  
            mock_memory_mgr = MockMemoryManager(mock_redis)  
            mock_memory_manager.return_value = mock_memory_mgr  
            
            mock_crew = MockMarketingCrew(mock_redis, job_id, data_analysis_result)  
            mock_crew_class.return_value = mock_crew  
            
            # 创建MarketingFlow实例  
            flow = MarketingFlow(mock_redis)  
            
            # 执行flow  
            result = await flow.execute(  
                job_id=job_id,  
                data_analysis_result=data_analysis_result,  
                user_id=user_id,  
                conversation_id=conversation_id  
            )  
            
            # 验证结果  
            print("\n测试结果:")  
            print(f"{'='*50}")  
            
            # 1. 检查是否返回了结果  
            result_check = "营销战略方案" in result and "创意活动方案" in result  
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

# 测试错误处理 - 修复版本  
async def test_error_handling():  
    print("\n开始测试错误处理...")  
    
    # 设置测试环境  
    mock_redis = MockRedisClient()  
    job_id = "test_marketing_error_job"  
    data_analysis_result = "错误的数据分析结果"  
    user_id = 1002  
    
    # 创建一个存储执行状态的字典  
    test_results = {  
        "error_caught": False,  
        "save_job_called": False,  
        "status_correct": False,  
        "progress_correct": False,  
        "error_in_output": False  
    }  
    
    try:  
        # 创建一个模拟的MarketingFlow，重写内部方法并记录调用  
        class TestMarketingFlow(MarketingFlow):  
            async def _run_crew_in_thread(self, crew):  
                # 模拟错误  
                raise Exception("模拟的营销战略制定错误")  
                
            # 重写save_job_data方法以验证它被调用  
            async def execute(self, job_id, data_analysis_result, user_id, conversation_id=None):  
                try:  
                    # 尝试执行原方法  
                    return await super().execute(job_id, data_analysis_result, user_id, conversation_id)  
                except Exception as e:  
                    # 记录错误被捕获  
                    test_results["error_caught"] = True  
                    # 重新抛出异常  
                    raise  
        
        # 替换内存管理器  
        with patch('app.flows.marketing_flow.RedisMemoryManager') as mock_memory_manager:  
            # 创建一个特殊版本的内存管理器，记录save_job_data的调用  
            class TestMemoryManager(MockMemoryManager):  
                async def save_job_data(self, job_id, data):  
                    # 记录方法被调用  
                    test_results["save_job_called"] = True  
                    
                    # 检查数据内容  
                    test_results["status_correct"] = data.get('status') == 'ERROR'  
                    test_results["progress_correct"] = data.get('progress') == -1  
                    test_results["error_in_output"] = "错误" in str(data.get('current_output', ''))  
                    
                    # 保存数据  
                    return await super().save_job_data(job_id, data)  
            
            # 配置模拟对象  
            mock_memory_mgr = TestMemoryManager(mock_redis)  
            mock_memory_manager.return_value = mock_memory_mgr  
            
            # 创建测试Flow实例  
            flow = TestMarketingFlow(mock_redis)  
            
            # 执行flow (应该抛出异常)  
            try:  
                result = await flow.execute(  
                    job_id=job_id,  
                    data_analysis_result=data_analysis_result,  
                    user_id=user_id  
                )  
                print(f"预期抛出异常，但实际返回了: {result}")  
            except Exception as e:  
                # 已经在TestMarketingFlow中记录了异常捕获  
                print(f"捕获到异常: {str(e)}")  
        
        # 验证结果  
        print(f"异常捕获检查: {'通过✅' if test_results['error_caught'] else '失败❌'}")  
        print(f"保存作业数据调用检查: {'通过✅' if test_results['save_job_called'] else '失败❌'}")  
        print(f"作业状态检查: {'通过✅' if test_results['status_correct'] else '失败❌'}")  
        print(f"作业进度检查: {'通过✅' if test_results['progress_correct'] else '失败❌'}")  
        print(f"错误消息检查: {'通过✅' if test_results['error_in_output'] else '失败❌'}")  
        
        # 总体结果  
        all_passed = all(test_results.values())  
        print(f"\n错误处理测试结果: {'通过✅' if all_passed else '失败❌'}")  
        
        return all_passed  
            
    except Exception as e:  
        print(f"错误处理测试失败: {str(e)}")  
        import traceback  
        traceback.print_exc()  
        return False  

# 主函数  
async def main():  
    print("开始测试MarketingFlow组件...\n")  
    
    # 运行功能测试  
    main_test_result = await test_marketing_flow()  
    
    # 运行错误处理测试  
    error_test_result = await test_error_handling()  
    
    # 汇总结果  
    print("\n测试结果汇总:")  
    print(f"主要功能测试: {'通过✅' if main_test_result else '失败❌'}")  
    print(f"错误处理测试: {'通过✅' if error_test_result else '失败❌'}")  
    
    all_passed = main_test_result and error_test_result  
    if all_passed:  
        print("\n🎉 所有测试通过! MarketingFlow组件工作正常!")  
    else:  
        print("\n❌ 部分测试未通过，请检查失败项。")  
    
    return all_passed  

if __name__ == "__main__":  
    # 运行主函数 (异步)  
    asyncio.run(main())  