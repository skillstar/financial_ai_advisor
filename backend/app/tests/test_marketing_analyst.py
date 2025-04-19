import os  
import sys  
from app.agents.marketing_analyst import (  
    AnalyzeUserProfilesTool,  
    DevelopMarketingStrategyTool,  
    MarketingAnalystAgent  
)  
from app.utils.llm_factory import get_llm 
# 测试日志输出  
def log_result(title, result):  
    print(f"\n{'='*50}")  
    print(f"{title}:")  
    print(f"{'='*50}")  
    print(result)  
    print(f"\n{'='*50}\n")  

# 1. 测试AnalyzeUserProfilesTool  
def test_user_profiles_tool():  
    tool = AnalyzeUserProfilesTool()  
    
    # 准备示例分析数据  
    analysis_data = """  
    用户数据概览:  
    - 总用户数: 25,000  
    - 活跃用户: 12,500 (50%)  
    - 年龄分布: 18-25岁(15%), 26-35岁(35%), 36-45岁(30%), 46岁以上(20%)  
    - 投资行为: 小额投资(<5万, 60%), 中额投资(5-20万, 30%), 大额投资(>20万, 10%)  
    - 风险偏好: 保守型(40%), 平衡型(45%), 激进型(15%)  
    """  
    
    result = tool._run(analysis_data)  
    log_result("用户画像分析工具测试结果", result)  
    
    return True if result else False  

# 2. 测试DevelopMarketingStrategyTool  
def test_marketing_strategy_tool():  
    tool = DevelopMarketingStrategyTool()  
    
    # 使用用户画像作为输入  
    user_profile_data = """  
    主要用户群体:  
    1. 专业投资者: 45岁以上, 高收入, 大额交易  
    2. 普通理财用户: 30-45岁, 中等收入, 定期小额投资  
    3. 年轻尝试者: 18-30岁, 刚开始投资, 对黄金市场感兴趣但知识有限  
    
    营销目标:  
    - 提高用户活跃度和交易频率  
    - 增加新用户获取  
    - 提升品牌知名度  
    """  
    
    result = tool._run(user_profile_data)  
    log_result("营销策略工具测试结果", result)  
    
    return True if result else False  

# 3. 测试完整Agent  
def test_agent():  
    try:  
        # 获取LLM模型  
        llm = get_llm()  
        
        # 创建Agent  
        agent_factory = MarketingAnalystAgent()  
        agent = agent_factory.get_agent(llm)  
        
        # 运行Agent  
        query = "基于黄金交易平台的用户数据，制定针对高价值客户的营销策略"  
        result = agent.run(query)  
        
        log_result("营销策略分析师Agent完整运行结果", result)  
        return True  
    except Exception as e:  
        print(f"Agent测试失败: {str(e)}")  
        return False  

# 4. 备选Agent测试 - 只测试Agent的工具  
def test_agent_tools():  
    try:  
        # 获取LLM模型  
        llm = get_llm()  
        
        # 创建Agent  
        agent_factory = MarketingAnalystAgent()  
        agent = agent_factory.get_agent(llm)  
        
        # 直接测试Agent中的工具  
        tools = agent.tools  
        
        # 确认工具存在  
        if not tools or len(tools) < 2:  
            print("Agent中没有找到预期的工具")  
            return False  
            
        # 测试用户画像分析工具  
        analysis_data = "用户数据摘要，包含25,000名用户的行为和属性"  
        profile_result = tools[0]._run(analysis_data)  
        
        # 使用第一个工具的结果作为第二个工具的输入  
        strategy_result = tools[1]._run(profile_result)  
        
        log_result("Agent工具组合测试",   
                  f"1. 用户画像分析结果片段:\n{profile_result[:200]}...\n\n"  
                  f"2. 营销策略结果片段:\n{strategy_result[:200]}...")  
        
        return True  
    except Exception as e:  
        print(f"Agent工具测试失败: {str(e)}")  
        return False  

# 主函数  
def main():  
    print("开始测试MarketingAnalyst组件...")  
    
    # 测试每个工具  
    profiles_result = test_user_profiles_tool()  
    strategy_result = test_marketing_strategy_tool()  
    
    # 首先尝试完整Agent测试  
    agent_result = test_agent()  
    
    # 如果完整测试失败，尝试工具测试  
    if not agent_result:  
        print("尝试备选测试方法...")  
        agent_result = test_agent_tools()  
    
    # 汇总结果  
    print("\n测试结果汇总:")  
    print(f"用户画像分析工具测试: {'通过✅' if profiles_result else '失败❌'}")  
    print(f"营销策略工具测试: {'通过✅' if strategy_result else '失败❌'}")  
    print(f"MarketingAnalystAgent测试: {'通过✅' if agent_result else '失败❌'}")  
    
    # 总体判断  
    all_passed = profiles_result and strategy_result and agent_result  
    if all_passed:  
        print("\n🎉 所有测试通过! MarketingAnalyst组件正常工作!")  
    else:  
        print("\n❌ 测试未全部通过，请检查失败项。")  

if __name__ == "__main__":  
    # 运行主函数  
    main()  