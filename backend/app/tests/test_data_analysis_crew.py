import os  
import sys  
import json  
import unittest  
from unittest.mock import MagicMock, patch  
from app.crews.data_analysis_crew import DataAnalysisCrew  
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
        
    def from_url(self, url, decode_responses=True):  
        return self  

# 模拟Crew运行结果  
class MockCrewResult:  
    def __init__(self, result_text):  
        self.raw = result_text  

# 测试函数  
def test_data_analysis_crew():  
    print("开始测试DataAnalysisCrew...")  
    
    # 步骤1: 设置测试环境和模拟对象  
    mock_redis = MockRedisClient()  
    job_id = "test_job_123"  
    test_query = "分析用户投资行为的趋势及相关影响因素"  
    
    # 模拟返回值  
    mock_results = {  
        "sql_translation": "SELECT user_id, investment_amount, investment_date, risk_profile FROM investments WHERE investment_date > '2023-01-01'",  
        "sql_execution": "查询结果: 返回了1000条记录，主要包含用户ID、投资金额、投资日期和风险偏好",  
        "data_preprocessing": "数据已预处理: 处理了缺失值，标准化了日期格式，计算了每用户的平均投资金额",  
        "statistical_analysis": "统计分析结果: 平均投资金额为5000元，风险偏好分布为低风险30%，中风险50%，高风险20%",  
        "visualization": "可视化结果: 生成了投资金额分布图、风险偏好饼图和投资时间趋势图",  
        "marketing_suggestions": "营销建议: 针对高风险偏好用户推出高收益产品，对低风险用户强调安全性"  
    }  
    
    # 步骤2: 测试主要功能  
    try:  
        # 注意: 我们不尝试创建 Crew 或 Task 实例，而是整个执行过程打补丁  
        with patch('app.crews.data_analysis_crew.DataAnalysisCrew._update_progress_sync') as mock_update_progress, \
             patch('app.crews.data_analysis_crew.Crew') as mock_crew_class, \
             patch('app.crews.data_analysis_crew.Task') as mock_task_class, \
             patch('app.crews.data_analysis_crew.get_llm') as mock_get_llm, \
             patch('app.crews.data_analysis_crew.QueryExpertAgent') as mock_query_expert, \
             patch('app.crews.data_analysis_crew.DatabaseExpertAgent') as mock_db_expert, \
             patch('app.crews.data_analysis_crew.DataAnalystAgent') as mock_data_analyst:  
            
            # 设置合适的返回值，避免实际执行 Task 初始化  
            mock_task_instance = MagicMock()  
            mock_task_class.return_value = mock_task_instance  
            
            # 设置 Crew 实例返回最终分析结果  
            mock_crew_instance = MagicMock()  
            final_result = "数据分析完成！\n\n" + "\n\n".join(mock_results.values())  
            mock_crew_instance.kickoff.return_value = MockCrewResult(final_result)  
            mock_crew_class.return_value = mock_crew_instance  
            
            # 设置进度更新成功  
            mock_update_progress.return_value = True  
            
            # 创建 DataAnalysisCrew 实例  
            crew = DataAnalysisCrew(mock_redis, job_id, test_query)  
            
            # 执行分析流程  
            result = crew.execute()  
            
            # 验证结果  
            print("\n测试结果:")  
            print(f"{'='*50}")  
            
            # 1. 检查是否返回了最终结果  
            result_check = isinstance(result, str) and "数据分析完成" in result  
            print(f"返回结果检查: {'通过✅' if result_check else '失败❌'}")  
            if not result_check:  
                print(f"实际结果: {result[:100]}...")  
            
            # 2. 检查是否尝试创建任务  
            tasks_attempted = mock_task_class.call_count > 0  
            print(f"任务创建尝试检查: {'通过✅' if tasks_attempted else '失败❌'}")  
            print(f"任务创建尝试次数: {mock_task_class.call_count}")  
            
            # 3. 检查是否尝试启动 Crew  
            crew_started = mock_crew_instance.kickoff.call_count > 0  
            print(f"Crew 启动检查: {'通过✅' if crew_started else '失败❌'}")  
            
            # 4. 检查是否尝试更新进度  
            progress_updated = mock_update_progress.call_count > 0  
            print(f"进度更新检查: {'通过✅' if progress_updated else '失败❌'}")  
            print(f"进度更新次数: {mock_update_progress.call_count}")  
            
            # 总体结果  
            all_passed = result_check and tasks_attempted and crew_started and progress_updated  
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
    job_id = "test_error_job"  
    test_query = "错误测试查询"  
    
    try:  
        # 直接模拟整个执行过程  
        with patch('app.crews.data_analysis_crew.DataAnalysisCrew._update_progress_sync') as mock_update_progress, \
             patch('app.crews.data_analysis_crew.Crew') as mock_crew_class, \
             patch('app.crews.data_analysis_crew.Task') as mock_task_class, \
             patch('app.crews.data_analysis_crew.get_llm') as mock_get_llm:  
            
            # 设置 Crew 实例抛出异常  
            mock_crew_instance = MagicMock()  
            mock_crew_instance.kickoff.side_effect = Exception("模拟的执行错误")  
            mock_crew_class.return_value = mock_crew_instance  
            
            # 创建 DataAnalysisCrew 实例  
            crew = DataAnalysisCrew(mock_redis, job_id, test_query)  
            
            # 执行，应该捕获异常  
            result = crew.execute()  
            
            # 验证结果  
            error_handled = "错误" in result or "出现错误" in result  
            print(f"错误处理检查: {'通过✅' if error_handled else '失败❌'}")  
            print(f"错误响应: {result[:100]}...")  
            
            # 检查是否调用了错误状态更新  
            error_updated = any(args[1] < 0 for args, _ in mock_update_progress.call_args_list)  
            print(f"错误状态更新调用检查: {'通过✅' if error_updated else '失败❌'}")  
            
            return error_handled and error_updated  
            
    except Exception as e:  
        print(f"错误处理测试失败: {str(e)}")  
        return False  

# 主函数  
def main():  
    print("开始测试DataAnalysisCrew组件...\n")  
    
    # 运行功能测试  
    main_test_result = test_data_analysis_crew()  
    
    # 运行错误处理测试  
    error_test_result = test_error_handling()  
    
    # 汇总结果  
    print("\n测试结果汇总:")  
    print(f"主要功能测试: {'通过✅' if main_test_result else '失败❌'}")  
    print(f"错误处理测试: {'通过✅' if error_test_result else '失败❌'}")  
    
    all_passed = main_test_result and error_test_result  
    if all_passed:  
        print("\n🎉 所有测试通过! DataAnalysisCrew组件工作正常!")  
    else:  
        print("\n❌ 部分测试未通过，请检查失败项。")  
    
    return all_passed  

if __name__ == "__main__":  
    # 运行主函数  
    main()  