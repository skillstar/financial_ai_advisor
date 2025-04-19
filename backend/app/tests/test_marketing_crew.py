import os  
import sys  
import json  
from unittest.mock import MagicMock, patch  
from app.crews.marketing_crew import MarketingCrew  
from app.core.logger import logger  
from crewai import Agent  # 导入真实的Agent类进行继承  

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
        
    def from_url(self, url, decode_responses=True):  
        return self  

# 模拟CrewAI的Agent类  
class MockAgent(Agent):  
    """一个继承自真实Agent的模拟类，可以通过验证"""  
    def __init__(self, role="测试角色", goal="测试目标", backstory="测试背景"):  
        super().__init__(  
            role=role,  
            goal=goal,  
            backstory=backstory,  
            verbose=True,  
            # 删掉llm参数，因为我们不需要实际调用  
        )  
        
    def run(self, *args, **kwargs):  
        """覆盖run方法，返回固定结果"""  
        return "模拟的Agent结果"  

# 模拟Crew运行结果  
class MockCrewResult:  
    def __init__(self, result_text):  
        self.raw = result_text  

# 测试函数  
def test_marketing_crew():  
    print("开始测试MarketingCrew...")  
    
    # 步骤1: 设置测试环境和模拟对象  
    mock_redis = MockRedisClient()  
    job_id = "test_marketing_job_123"  
    test_data_analysis = """  
    数据分析结果:  
    1. 用户画像：主要用户为30-45岁的男性，有稳定收入，对黄金投资有兴趣  
    2. 投资行为：平均交易金额为5000元，偏好早晨交易，周一交易频率最高  
    3. 风险承受能力：中等，倾向于长期持有黄金作为资产配置的一部分  
    4. 营销渠道偏好：对电子邮件和App内推送反应最佳，社交媒体效果一般  
    """  
    
    # 模拟返回值  
    mock_results = {  
        "user_profile": "用户画像分析：确定了三个主要客户群体：稳健型投资者(60%)、机会型投资者(25%)和新手投资者(15%)",  
        "marketing_strategy": "营销战略框架：采用分层精准营销，针对不同风险偏好用户制定差异化内容和渠道策略",  
        "campaign_design": "创意活动设计：推出'黄金财富大师'系列活动，包括投资课程、模拟投资比赛和线下沙龙",  
        "copywriting": "营销文案：'稳健投资，闪耀未来 - 开启您的黄金理财之旅'，强调安全性和长期价值"  
    }  
    
    # 步骤2: 测试主要功能  
    try:  
        # 1. 先直接替换Task类，这样我们就不需要担心验证问题  
        with patch('app.crews.marketing_crew.Task') as mock_task_class, \
             patch('app.utils.llm_factory.get_llm') as mock_get_llm, \
             patch('app.crews.marketing_crew.Crew') as mock_crew:  
            
            # 2. 创建模拟Task实例  
            mock_tasks = []  
            for task_name in ["用户画像任务", "营销策略任务", "活动设计任务", "文案创作任务"]:  
                mock_task = MagicMock()  
                mock_task.description = f"{task_name}描述"  
                mock_task.expected_output = f"{task_name}预期输出"  
                mock_tasks.append(mock_task)  
                
            # 3. 配置Task构造函数返回模拟Task实例  
            mock_task_class.side_effect = mock_tasks  
            
            # 4. 创建两个模拟Agent  
            mock_marketing_analyst = MockAgent(  
                role="营销策略分析师",   
                goal="制定营销策略",   
                backstory="营销专家背景"  
            )  
            
            mock_content_creator = MockAgent(  
                role="内容创作师",  
                goal="创作内容",  
                backstory="创意专家背景"  
            )  
            
            # 5. 模拟Agent工厂返回我们的MockAgent  
            with patch('app.crews.marketing_crew.MarketingAnalystAgent.get_agent') as mock_get_marketing_agent, \
                 patch('app.crews.marketing_crew.ContentCreatorAgent.get_agent') as mock_get_content_agent:  
                
                mock_get_marketing_agent.return_value = mock_marketing_analyst  
                mock_get_content_agent.return_value = mock_content_creator  
                
                # 6. 配置Crew返回最终结果  
                final_result = "营销战略与创意内容规划完成！\n\n" + "\n\n".join(mock_results.values())  
                mock_crew_instance = MagicMock()  
                mock_crew_instance.kickoff.return_value = MockCrewResult(final_result)  
                mock_crew.return_value = mock_crew_instance  
                
                # 7. 模拟Redis配置  
                with patch('redis.Redis.from_url') as mock_redis_from_url:  
                    mock_redis_from_url.return_value = mock_redis  
                    
                    # 创建MarketingCrew实例  
                    crew = MarketingCrew(mock_redis, job_id, test_data_analysis)  
                    
                    # 执行营销流程  
                    result = crew.execute()  
                    
                    # 验证结果  
                    print("\n测试结果:")  
                    print(f"{'='*50}")  
                    
                    # 1. 检查是否返回了期望的结果字符串  
                    result_check = "营销战略与创意内容" in result or "黄金财富大师" in result  
                    print(f"返回结果检查: {'通过✅' if result_check else '失败❌'}")  
                    if not result_check:  
                        print(f"实际结果: {result[:100]}...")  
                    
                    # 2. 检查是否正确调用了Crew  
                    crew_called = mock_crew.called  
                    print(f"Crew创建检查: {'通过✅' if crew_called else '失败❌'}")  
                    
                    # 3. 检查是否调用了kickoff方法  
                    kickoff_called = mock_crew_instance.kickoff.called  
                    print(f"Crew执行检查: {'通过✅' if kickoff_called else '失败❌'}")  
                    
                    # 4. 检查进度更新是否被调用  
                    key = f"gold_trading:job:{job_id}"  
                    update_check = key in mock_redis.storage  
                    print(f"进度更新检查: {'通过✅' if update_check else '失败❌'}")  
                    
                    if update_check:  
                        # 显示部分Redis存储内容  
                        job_data = json.loads(mock_redis.storage[key])  
                        print(f"最终作业状态: {job_data.get('status', 'unknown')}")  
                        print(f"最终进度: {job_data.get('progress', 'unknown')}%")  
                    
                    # 总体结果  
                    all_passed = result_check and crew_called and kickoff_called and update_check  
                    print(f"\n总体测试结果: {'通过✅' if all_passed else '失败❌'}")  
                    
                    return all_passed  
            
    except Exception as e:  
        print(f"测试过程中出错: {str(e)}")  
        import traceback  
        traceback.print_exc()  
        return False  

# 测试错误处理  
def test_error_handling():  
    print("\n开始测试错误处理...")  
    
    # 设置测试环境  
    mock_redis = MockRedisClient()  
    job_id = "test_marketing_error_job"  
    test_data = "错误的数据分析结果"  
    
    try:  
        # 1. 替换关键类以避免验证问题  
        with patch('app.crews.marketing_crew.Task') as mock_task_class, \
             patch('app.utils.llm_factory.get_llm') as mock_get_llm, \
             patch('app.crews.marketing_crew.Crew') as mock_crew, \
             patch('redis.Redis.from_url') as mock_redis_from_url:  
            
            # 2. 配置模拟对象  
            mock_task = MagicMock()  
            mock_task_class.return_value = mock_task  
            
            mock_crew_instance = MagicMock()  
            mock_crew_instance.kickoff.side_effect = Exception("模拟的营销策略执行错误")  
            mock_crew.return_value = mock_crew_instance  
            
            mock_redis_from_url.return_value = mock_redis  
            
            # 3. 模拟Agent工厂  
            with patch('app.crews.marketing_crew.MarketingAnalystAgent.get_agent') as mock_get_marketing_agent, \
                 patch('app.crews.marketing_crew.ContentCreatorAgent.get_agent') as mock_get_content_agent:  
                
                mock_get_marketing_agent.return_value = MockAgent()  
                mock_get_content_agent.return_value = MockAgent()  
                
                # 创建MarketingCrew实例  
                crew = MarketingCrew(mock_redis, job_id, test_data)  
                
                # 执行，应该捕获异常  
                result = crew.execute()  
                
                # 验证结果  
                error_handled = "错误" in result or "出现错误" in result  
                print(f"错误处理检查: {'通过✅' if error_handled else '失败❌'}")  
                
                # 检查进度是否被标记为错误(-1)  
                key = f"gold_trading:job:{job_id}"  
                status_updated = False  
                
                if key in mock_redis.storage:  
                    job_data = json.loads(mock_redis.storage[key])  
                    status_updated = job_data.get('status') == "ERROR" and job_data.get('progress', 0) < 0  
                    
                print(f"错误状态更新检查: {'通过✅' if status_updated else '失败❌'}")  
                
                return error_handled and status_updated  
            
    except Exception as e:  
        print(f"错误处理测试失败: {str(e)}")  
        return False  

# 主函数  
def main():  
    print("开始测试MarketingCrew组件...\n")  
    
    # 运行功能测试  
    main_test_result = test_marketing_crew()  
    
    # 运行错误处理测试  
    error_test_result = test_error_handling()  
    
    # 汇总结果  
    print("\n测试结果汇总:")  
    print(f"主要功能测试: {'通过✅' if main_test_result else '失败❌'}")  
    print(f"错误处理测试: {'通过✅' if error_test_result else '失败❌'}")  
    
    all_passed = main_test_result and error_test_result  
    if all_passed:  
        print("\n🎉 所有测试通过! MarketingCrew组件工作正常!")  
    else:  
        print("\n❌ 部分测试未通过，请检查失败项。")  
    
    return all_passed  

if __name__ == "__main__":  
    # 运行主函数  
    main()  