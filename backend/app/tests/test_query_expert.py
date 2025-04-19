import os  
import sys  
from app.agents.query_expert import TranslateToSQLTool, ValidateSQLTool, QueryExpertAgent  
from app.utils.llm_factory import get_llm  # 假设有这个函数来获取LLM模型  

# 测试日志输出  
def log_result(title, result):  
    print(f"\n{'='*50}")  
    print(f"{title}:")  
    print(f"{'='*50}")  
    print(result)  
    print(f"\n{'='*50}\n")  

# 1. 测试TranslateToSQLTool  
def test_translate_tool():  
    tool = TranslateToSQLTool()  
    
    # 正常查询测试  
    query1 = "找出账户余额最高的10个用户"  
    result1 = tool._run(query1)  
    log_result("普通查询转换结果", result1)  
    
    # 复杂查询测试  
    query2 = "分析过去一年中，高风险偏好用户的交易金额总和以及平均每笔交易金额"  
    result2 = tool._run(query2)  
    log_result("复杂查询转换结果", result2)  
    
    return True if result1 and result2 else False  

# 2. 测试ValidateSQLTool  
def test_validate_tool():  
    tool = ValidateSQLTool()  
    
    # 有效SQL  
    valid_sql = "SELECT * FROM users WHERE age > 30 LIMIT 10;"  
    valid_result = tool._run(valid_sql)  
    log_result("有效SQL验证结果", valid_result)  
    
    # 包含危险关键字的SQL  
    dangerous_sql = "DROP TABLE users;"  
    dangerous_result = tool._run(dangerous_sql)  
    log_result("危险SQL验证结果", dangerous_result)  
    
    # 非SELECT查询  
    non_select_sql = "UPDATE users SET balance = 1000;"  
    non_select_result = tool._run(non_select_sql)  
    log_result("非SELECT查询验证结果", non_select_result)  
    
    return True  

# 3. 测试完整Agent (改为同步方式)  
def test_agent():  
    try:  
        # 获取LLM模型  
        llm = get_llm()  
        
        # 创建Agent  
        agent_factory = QueryExpertAgent()  
        agent = agent_factory.get_agent(llm)  
        
        # 运行Agent (使用同步run方法而不是arun)  
        query = "找出所有投资风险承受能力为'high'的用户，并按账户余额降序排列"  
        result = agent.run(query)  
        
        log_result("Agent完整运行结果", result)  
        return True  
    except Exception as e:  
        print(f"Agent测试失败: {str(e)}")  
        return False  

# 3.1 备选Agent测试 - 只测试Agent的工具  
def test_agent_tools():  
    try:  
        # 获取LLM模型  
        llm = get_llm()  
        
        # 创建Agent  
        agent_factory = QueryExpertAgent()  
        agent = agent_factory.get_agent(llm)  
        
        # 直接测试Agent中的工具  
        tools = agent.tools  
        
        # 确认工具存在  
        if not tools or len(tools) < 2:  
            print("Agent中没有找到预期的工具")  
            return False  
            
        # 使用第一个工具(TranslateToSQL)  
        query = "找出投资风险承受能力为'high'的用户"  
        sql = tools[0]._run(query)  
        
        # 使用第二个工具(ValidateSQL)  
        validation = tools[1]._run(sql)  
        
        log_result("Agent工具直接运行结果", f"SQL转换结果:\n{sql}\n\n验证结果:\n{validation}")  
        return True  
    except Exception as e:  
        print(f"Agent工具测试失败: {str(e)}")  
        return False  

# 主函数  
def main():  
    print("开始测试QueryExpert组件...")  
    
    # 测试每个组件  
    translate_result = test_translate_tool()  
    validate_result = test_validate_tool()  
    
    # 首先尝试完整Agent测试  
    agent_result = test_agent()  
    
    # 如果完整测试失败，尝试工具测试  
    if not agent_result:  
        print("尝试备选测试方法...")  
        agent_result = test_agent_tools()  
    
    # 汇总结果  
    print("\n测试结果汇总:")  
    print(f"TranslateToSQL工具测试: {'通过✅' if translate_result else '失败❌'}")  
    print(f"ValidateSQL工具测试: {'通过✅' if validate_result else '失败❌'}")  
    print(f"QueryExpertAgent测试: {'通过✅' if agent_result else '失败❌'}")  
    
    # 总体判断  
    if translate_result and validate_result and agent_result:  
        print("\n🎉 所有测试通过! QueryExpert组件正常工作!")  
    else:  
        print("\n❌ 测试未全部通过，请检查失败项。")  

if __name__ == "__main__":  
    # 运行主函数  
    main()  