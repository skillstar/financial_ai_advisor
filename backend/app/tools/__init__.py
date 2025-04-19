# tools/__init__.py 的更新部分  
from .translate_to_sql import TranslateToSQLTool  
from .validate_sql import ValidateSQLTool  
from .analyze_user_profiles import AnalyzeUserProfilesTool  
from .develop_marketing_strategy import DevelopMarketingStrategyTool  
from .execute_sql import ExecuteSQLTool  
from .preprocess_data import PreprocessDataTool  
from .design_campaign import DesignCampaignTool  
from .create_marketing_copy import CreateMarketingCopyTool  
# 添加data_analyst使用的工具  
from .statistical_analysis import StatisticalAnalysisTool  
from .data_visualization import DataVisualizationTool  
from .marketing_suggestions import MarketingSuggestionsTool  
from .chart_generation import ChartGenerationTool  

__all__ = [  
    'TranslateToSQLTool',   
    'ValidateSQLTool',  
    'AnalyzeUserProfilesTool',  
    'DevelopMarketingStrategyTool',  
    'ExecuteSQLTool',  
    'PreprocessDataTool',  
    'DesignCampaignTool',  
    'CreateMarketingCopyTool',  
    # 添加data_analyst使用的工具  
    'StatisticalAnalysisTool',  
    'DataVisualizationTool',  
    'MarketingSuggestionsTool',  
    'ChartGenerationTool'  
]  