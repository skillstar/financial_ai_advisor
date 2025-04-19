import logging  
import sys  
import os  
import colorama  
from colorama import Fore, Style, Back  

# 确保只初始化一次  
_LOGGING_INITIALIZED = False  

class ColoredFormatter(logging.Formatter):  
    """自定义带颜色的日志格式化器"""  
    COLORS = {  
        logging.DEBUG: Fore.BLUE,     # 蓝色  
        logging.INFO: Fore.GREEN,     # 绿色  
        logging.WARNING: Fore.YELLOW, # 黄色  
        logging.ERROR: Fore.RED,      # 红色  
        logging.CRITICAL: Fore.MAGENTA # 紫红色  
    }  

    def format(self, record):  
        # 获取日志级别对应的颜色  
        color = self.COLORS.get(record.levelno, Fore.WHITE)  
        
        # 自定义格式   
        log_format = (  
            f"{Fore.WHITE}%(asctime)s{Style.RESET_ALL} - "  
            f"{Fore.CYAN}%(name)s{Style.RESET_ALL} - "  
            f"{color}%(levelname)s{Style.RESET_ALL} - "  
            f"{color}%(message)s{Style.RESET_ALL}"  
        )  
        
        formatter = logging.Formatter(log_format, datefmt='%Y-%m-%d %H:%M:%S')  
        return formatter.format(record)  

def setup_logging(level=None):  
    global _LOGGING_INITIALIZED  
    
    # 如果已经初始化，直接返回  
    if _LOGGING_INITIALIZED:  
        return  

    # 初始化 colorama  
    colorama.init(autoreset=True)  

    # 从环境变量获取日志级别，默认为 INFO  
    log_level = level or os.environ.get('LOG_LEVEL', 'INFO').upper()  
    
    # 转换日志级别  
    numeric_level = getattr(logging, log_level, logging.INFO)  

    # 创建格式化程序  
    formatter = ColoredFormatter()  

    # 创建控制台处理器  
    console_handler = logging.StreamHandler(sys.stdout)  
    console_handler.setLevel(numeric_level)  
    console_handler.setFormatter(formatter)  

    # 获取根日志记录器  
    root_logger = logging.getLogger()  
    root_logger.setLevel(numeric_level)  

    # 清除之前的处理器  
    root_logger.handlers.clear()  
    root_logger.addHandler(console_handler)  

    # 调整特定模块的日志级别  
    noise_loggers = [  
        'sqlalchemy.engine', 'huggingface', 'transformers',   
        'httpx', 'httpcore', 'uvicorn', 'fastapi',   
        'numexpr', 'urllib3', 'charset_normalizer'  
    ]  
    
    for logger_name in noise_loggers:  
        logging.getLogger(logger_name).setLevel(logging.WARNING)  

    # 标记已初始化  
    _LOGGING_INITIALIZED = True  

    # 彩色输出日志初始化信息  
    print(f"{Fore.GREEN}🌈 彩色日志系统初始化完成。{Fore.YELLOW}当前日志级别: {log_level}{Style.RESET_ALL}")  

# 在应用启动时调用  
setup_logging()  

# 额外的日志级别控制函数  
def set_log_level(level: str):  
    """  
    动态设置全局日志级别  
    
    Args:  
        level (str): 日志级别，如 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'  
    """  
    numeric_level = getattr(logging, level.upper(), logging.INFO)  
    logging.getLogger().setLevel(numeric_level)  
    print(f"{Fore.GREEN}🔄 日志级别已更新为: {level.upper()}{Style.RESET_ALL}")  

# 创建默认logger  
logger = logging.getLogger("gold_trading")  