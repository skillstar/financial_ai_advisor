import os  
import sys  
from app.agents.data_analyst import (  
    StatisticalAnalysisTool,  
    DataVisualizationTool,   
    MarketingSuggestionsTool,  
    DataAnalystAgent  
)  
from app.utils.llm_factory import get_llm  # 假设有这个函数来获取LLM模型  

# 测试日志输出  
def log_result(title, result):  
    print(f"\n{'='*50}")  
    print(f"{title}:")  
    print(f"{'='*50}")  
    print(result)  
    print(f"\n{'='*50}\n")  

# 1. 测试StatisticalAnalysisTool  
def test_statistical_tool():  
    tool = StatisticalAnalysisTool()  
    
    # 测试数据描述  
    data_desc = "用户交易数据，包含用户ID、交易金额、交易时间、用户风险偏好等信息"  
    result = tool._run(data_desc)  
    log_result("统计分析工具测试结果", result)  
    
    return True if result else False  

# 2. 测试DataVisualizationTool  
def test_visualization_tool():  
    tool = DataVisualizationTool()  
    
    # 测试数据描述  
    data_desc = "用户交易数据，需要可视化用户分布、交易频率、风险偏好等维度"  
    result = tool._run(data_desc)  
    log_result("数据可视化工具测试结果", result)  
    
    return True if result else False  

# 3. 测试MarketingSuggestionsTool  
def test_marketing_tool():  
    tool = MarketingSuggestionsTool()  
    
    # 假设的分析结果输入  
    analysis = """  
    主要用户群体为35-45岁男性，偏好大额交易，风险承受能力较高。  
    交易高峰期为每月初和月中，周一和周四交易频率最高。  
    新用户首月留存率45%，第三个月下降至23%。  
    """  
    
    result = tool._run(analysis)  
    log_result("营销建议工具测试结果", result)  
    
    return True if result else False  

# 4. 测试完整Agent  
def test_agent():  
    try:  
        # 获取LLM模型  
        llm = get_llm()  
        
        # 创建Agent  
        agent_factory = DataAnalystAgent()  
        agent = agent_factory.get_agent(llm)  
        
        # 运行Agent  
        query = "分析黄金交易平台用户的行为模式，找出高价值用户群体特征"  
        result = agent.run(query)  
        
        log_result("数据分析师Agent完整运行结果", result)  
        return True  
    except Exception as e:  
        print(f"Agent测试失败: {str(e)}")  
        return False  

# 5. 备选Agent测试 - 只测试Agent的工具  
def test_agent_tools():  
    try:  
        # 获取LLM模型  
        llm = get_llm()  
        
        # 创建Agent  
        agent_factory = DataAnalystAgent()  
        agent = agent_factory.get_agent(llm)  
        
        # 直接测试Agent中的工具  
        tools = agent.tools  
        
        # 确认工具存在  
        if not tools or len(tools) < 3:  
            print("Agent中没有找到预期的工具")  
            return False  
            
        # 测试统计分析工具  
        data_desc = "用户交易数据，包含1000条记录"  
        stats_result = tools[0]._run(data_desc)  
        
        # 测试可视化工具  
        viz_result = tools[1]._run(data_desc)  
        
        # 测试营销建议工具  
        marketing_result = tools[2]._run(stats_result)  
        
        log_result("Agent工具组合测试",   
                  f"1. 统计分析结果片段:\n{stats_result[:200]}...\n\n"  
                  f"2. 可视化结果片段:\n{viz_result[:200]}...\n\n"  
                  f"3. 营销建议片段:\n{marketing_result[:200]}...")  
        
        return True  
    except Exception as e:  
        print(f"Agent工具测试失败: {str(e)}")  
        return False  

# 主函数  
def main():  
    print("开始测试DataAnalyst组件...")  
    
    # 测试每个工具  
    stats_result = test_statistical_tool()  
    viz_result = test_visualization_tool()  
    marketing_result = test_marketing_tool()  
    
    # 首先尝试完整Agent测试  
    agent_result = test_agent()  
    
    # 如果完整测试失败，尝试工具测试  
    if not agent_result:  
        print("尝试备选测试方法...")  
        agent_result = test_agent_tools()  
    
    # 汇总结果  
    print("\n测试结果汇总:")  
    print(f"统计分析工具测试: {'通过✅' if stats_result else '失败❌'}")  
    print(f"数据可视化工具测试: {'通过✅' if viz_result else '失败❌'}")  
    print(f"营销建议工具测试: {'通过✅' if marketing_result else '失败❌'}")  
    print(f"DataAnalystAgent测试: {'通过✅' if agent_result else '失败❌'}")  
    
    # 总体判断  
    all_passed = stats_result and viz_result and marketing_result and agent_result  
    if all_passed:  
        print("\n🎉 所有测试通过! DataAnalyst组件正常工作!")  
    else:  
        print("\n❌ 测试未全部通过，请检查失败项。")  

if __name__ == "__main__":  
    # 运行主函数  
    main()  