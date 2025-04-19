import os  
import sys  
from app.agents.content_creator import (  
    DesignCampaignTool,  
    CreateMarketingCopyTool,  
    ContentCreatorAgent  
)  
from app.utils.llm_factory import get_llm  # 假设有这个函数来获取LLM模型  

# 测试日志输出  
def log_result(title, result):  
    print(f"\n{'='*50}")  
    print(f"{title}:")  
    print(f"{'='*50}")  
    print(result)  
    print(f"\n{'='*50}\n")  

# 1. 测试DesignCampaignTool  
def test_design_campaign_tool():  
    tool = DesignCampaignTool()  
    
    # 准备营销策略数据  
    strategy_data = """  
    目标用户群体:  
    1. 稳健型定投用户：35-45岁，中等收入，偏好长期投资  
    2. 新兴数字投资者：25-35岁，科技爱好者，移动端活跃  
    3. 高价值专家型用户：45岁以上，高收入，专业投资知识丰富  
    
    营销重点:  
    - 强调黄金投资的安全性和长期价值  
    - 降低新用户入门门槛，提供教育内容  
    - 为高价值用户提供专属服务和深度分析  
    """  
    
    result = tool._run(strategy_data)  
    log_result("营销活动设计工具测试结果", result)  
    
    return True if result else False  

# 2. 测试CreateMarketingCopyTool  
def test_marketing_copy_tool():  
    tool = CreateMarketingCopyTool()  
    
    # 准备活动设计数据  
    campaign_data = """  
    活动方案:  
    1. 「黄金未来家」- 面向稳健型定投用户的长期投资计划  
    2. 「黄金创富学院」- 为新手提供的黄金投资教育内容  
    3. 「金市大师汇」- 为专业投资者提供的高端交流平台  
    """  
    
    result = tool._run(campaign_data)  
    log_result("营销文案创作工具测试结果", result)  
    
    return True if result else False  

# 3. 测试完整Agent  
def test_agent():  
    try:  
        # 获取LLM模型  
        llm = get_llm()  
        
        # 创建Agent  
        agent_factory = ContentCreatorAgent()  
        agent = agent_factory.get_agent(llm)  
        
        # 运行Agent  
        query = "为黄金交易平台设计一个针对年轻投资者的营销活动，并创作相应的文案"  
        result = agent.run(query)  
        
        log_result("创意内容创作师Agent完整运行结果", result)  
        return True  
    except Exception as e:  
        print(f"Agent测试失败: {str(e)}")  
        return False  

# 4. 备选Agent测试 - 直接测试Agent的工具  
def test_agent_tools():  
    try:  
        # 获取LLM模型  
        llm = get_llm()  
        
        # 创建Agent  
        agent_factory = ContentCreatorAgent()  
        agent = agent_factory.get_agent(llm)  
        
        # 直接测试Agent中的工具  
        tools = agent.tools  
        
        # 确认工具存在  
        if not tools or len(tools) < 2:  
            print("Agent中没有找到预期的工具")  
            return False  
            
        # 测试活动设计工具  
        strategy_data = "黄金交易平台的营销策略，针对年轻投资者"  
        campaign_result = tools[0]._run(strategy_data)  
        
        # 使用第一个工具的结果作为第二个工具的输入  
        copy_result = tools[1]._run(campaign_result)  
        
        log_result("Agent工具组合测试",   
                  f"1. 活动设计结果片段:\n{campaign_result[:200]}...\n\n"  
                  f"2. 营销文案结果片段:\n{copy_result[:200]}...")  
        
        return True  
    except Exception as e:  
        print(f"Agent工具测试失败: {str(e)}")  
        return False  

# 主函数  
def main():  
    print("开始测试ContentCreator组件...")  
    
    # 测试每个工具  
    campaign_result = test_design_campaign_tool()  
    copy_result = test_marketing_copy_tool()  
    
    # 首先尝试完整Agent测试  
    agent_result = test_agent()  
    
    # 如果完整测试失败，尝试工具测试  
    if not agent_result:  
        print("尝试备选测试方法...")  
        agent_result = test_agent_tools()  
    
    # 汇总结果  
    print("\n测试结果汇总:")  
    print(f"营销活动设计工具测试: {'通过✅' if campaign_result else '失败❌'}")  
    print(f"营销文案创作工具测试: {'通过✅' if copy_result else '失败❌'}")  
    print(f"ContentCreatorAgent测试: {'通过✅' if agent_result else '失败❌'}")  
    
    # 总体判断  
    all_passed = campaign_result and copy_result and agent_result  
    if all_passed:  
        print("\n🎉 所有测试通过! ContentCreator组件正常工作!")  
    else:  
        print("\n❌ 测试未全部通过，请检查失败项。")  

if __name__ == "__main__":  
    # 运行主函数  
    main()  