import asyncio  
import argparse  
from app.utils.llm_factory import get_llm  
from app.agents.query_expert import QueryExpertAgent, TranslateToSQLTool  
from app.agents.database_expert import DatabaseExpertAgent, ExecuteSQLTool  
from app.agents.data_analyst import DataAnalystAgent  
from crewai import Crew, Task, Process  

async def agent_playground(agent_type, query):  
    """交互式Agent测试环境"""  
    llm = get_llm()  
    
    if agent_type == "query":  
        agent = QueryExpertAgent().get_agent(llm)  
    elif agent_type == "database":  
        agent = DatabaseExpertAgent().get_agent(llm)  
    elif agent_type == "analyst":  
        agent = DataAnalystAgent().get_agent(llm)  
    else:  
        print(f"未知Agent类型: {agent_type}")  
        return  
        
    result = await agent.arun(query)  
    print(f"\n结果:\n{result}")  

async def tool_playground(tool_name, input_text):  
    """交互式Tool测试环境"""  
    if tool_name == "sql":  
        tool = ExecuteSQLTool()  
        result = tool._run(input_text)  
    elif tool_name == "translate":  
        tool = TranslateToSQLTool()  
        result = tool._run(input_text)  
    else:  
        print(f"未知工具: {tool_name}")  
        return  
        
    print(f"\n结果:\n{result}")  

def mini_crew_playground(query):  
    """最小化Crew测试环境 - 只有两个Agent和两个Task"""  
    llm = get_llm()  
    query_agent = QueryExpertAgent().get_agent(llm)  
    db_agent = DatabaseExpertAgent().get_agent(llm)  
    
    sql_translation_task = Task(  
        description=f"将业务问题转化为SQL查询\n\n用户问题: {query}",  
        expected_output="优化的SQL查询语句",  
        agent=query_agent,  
    )  
    
    sql_execution_task = Task(  
        description="执行SQL查询并获取结果",  
        expected_output="格式化的查询结果",  
        agent=db_agent,  
        context=[sql_translation_task],  
    )  
    
    crew = Crew(  
        agents=[query_agent, db_agent],  
        tasks=[sql_translation_task, sql_execution_task],  
        process=Process.sequential,  
        verbose=True,  
    )  
    
    result = crew.kickoff()  
    print(f"\n最终结果:\n{result.raw}")  

# 命令行接口  
if __name__ == "__main__":  
    parser = argparse.ArgumentParser(description="CrewAI调试工具")  
    subparsers = parser.add_subparsers(dest="command", help="选择测试模式")  
    
    # Agent测试  
    agent_parser = subparsers.add_parser("agent", help="测试单个Agent")  
    agent_parser.add_argument("type", choices=["query", "database", "analyst"], help="Agent类型")  
    agent_parser.add_argument("query", help="测试查询")  
    
    # Tool测试  
    tool_parser = subparsers.add_parser("tool", help="测试单个工具")  
    tool_parser.add_argument("name", choices=["sql", "translate"], help="工具名称")  
    tool_parser.add_argument("input", help="工具输入")  
    
    # Mini Crew测试  
    crew_parser = subparsers.add_parser("crew", help="测试最小化Crew")  
    crew_parser.add_argument("query", help="测试查询")  
    
    args = parser.parse_args()  
    
    if args.command == "agent":  
        asyncio.run(agent_playground(args.type, args.query))  
    elif args.command == "tool":  
        asyncio.run(tool_playground(args.name, args.input))  
    elif args.command == "crew":  
        mini_crew_playground(args.query)  
    else:  
        parser.print_help()  