from crewai import Agent  
import inspect  

# 创建简单Agent  
agent = Agent(  
    role="测试员",  
    goal="测试Agent执行方法",  
    backstory="我是测试Agent执行方法的测试员"  
)  

# 打印所有公共方法  
print("Agent公共方法:")  
for method_name in dir(agent):  
    if not method_name.startswith('_'):  
        method = getattr(agent, method_name)  
        if callable(method):  
            # 获取方法签名  
            sig = inspect.signature(method)  
            params = list(sig.parameters.keys())  
            print(f"- {method_name}{sig}")  

# 检查是否有task相关方法  
task_methods = [m for m in dir(agent) if 'task' in m.lower() and callable(getattr(agent, m))]  
if task_methods:  
    print("\nTask相关方法:")  
    for m in task_methods:  
        print(f"- {m}")  