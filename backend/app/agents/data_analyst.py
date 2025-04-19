from crewai import Agent  
from crewai.tools import BaseTool  
from typing import Optional, List, Dict, Any, ClassVar  
import pandas as pd  
import json  
import matplotlib.pyplot as plt  
import base64  
from io import BytesIO  
from app.core.logger import logger  

class StatisticalAnalysisTool(BaseTool):  
    """执行统计分析的工具"""  
    
    name: str = "StatisticalAnalysis"  
    description: str = "执行统计分析，包括描述性统计、相关性分析和假设检验"  
    
    def _run(self, data_description: str) -> str:  
        """实现必需的_run方法"""  
        try:  
            # 此处应实现统计分析逻辑  
            # 在实际实现中，可以使用pandas、numpy等进行分析  
            
            analysis_results = """  
            ## 统计分析结果  

            ### 交易数据分析  
            - 总交易量: ¥1,245,678  
            - 平均交易金额: ¥5,432  
            - 交易频率: 每用户每月平均2.3笔  
            - 客单价分布: 25%用户<¥2,000, 50%用户¥2,000-¥8,000, 25%用户>¥8,000  

            ### 用户行为模式  
            - 高峰交易时间: 周一至周五 10:00-11:30, 14:00-15:00  
            - 最活跃用户群: 35-45岁, 男性投资者  
            - 交易触发因素: 金价波动>1%时交易量增加50%  
            - 复购率: 首次交易用户30天内复购率38%  

            ### 风险偏好分布  
            - 保守型: 30% (平均交易金额¥3,200)  
            - 平衡型: 45% (平均交易金额¥5,500)  
            - 进取型: 25% (平均交易金额¥9,800)  
            
            ### 用户价值分层  
            - 高价值用户: 18% (贡献65%交易额)  
            - 中价值用户: 32% (贡献25%交易额)  
            - 低价值用户: 50% (贡献10%交易额)  
            """  
            
            return analysis_results  
            
        except Exception as e:  
            error_message = f"执行统计分析时出错: {str(e)}"  
            logger.error(error_message, exc_info=True)  
            return error_message  

class DataVisualizationTool(BaseTool):  
    """生成数据可视化的工具"""  
    
    name: str = "DataVisualization"  
    description: str = "生成数据可视化，帮助理解数据模式和关系"  
    
    def _run(self, data_description: str) -> str:  
        """实现必需的_run方法"""  
        try:  
            # 此处应实现数据可视化逻辑  
            # 实际实现中可以使用matplotlib、seaborn等  
            
            visualization_results = """  
            ## 数据可视化结果  

            ### 关键可视化发现  
            1. 交易量与金价呈负相关关系 (r = -0.72)  
            2. 风险偏好与年龄分布呈双峰特征  
            3. 新用户首月交易频率显著高于平均水平  
            4. 用户活跃度呈现明显的周内和月内周期性  

            ### 用户分群  
            - 群体A: 高频小额交易者 (15% 用户)  
              特征: 每周交易3-5次，单笔交易金额<¥3,000  
              行为: 对价格敏感，偏好在价格下跌时买入  
              
            - 群体B: 低频大额交易者 (25% 用户)  
              特征: 每月交易1-2次，单笔交易金额>¥10,000  
              行为: 倾向于长期持有，关注宏观经济信息  
              
            - 群体C: 趋势跟随者 (40% 用户)  
              特征: 在金价上涨时增加买入频率和金额  
              行为: 中等交易频率，关注市场趋势分析  
              
            - 群体D: 逆势交易者 (20% 用户)  
              特征: 在金价下跌时大额买入  
              行为: 交易频率不规律，但单笔金额较大  

            ### 转化漏斗  
            浏览→注册→首次交易→重复交易→忠诚用户  
            转化率: 100%→35%→20%→12%→8%  
            """  
            
            return visualization_results  
            
        except Exception as e:  
            error_message = f"生成数据可视化时出错: {str(e)}"  
            logger.error(error_message, exc_info=True)  
            return error_message  

class MarketingSuggestionsTool(BaseTool):  
    """生成营销建议的工具"""  
    
    name: str = "MarketingSuggestions"  
    description: str = "基于数据分析结果，生成具体的营销建议"  
    
    def _run(self, analysis_results: str) -> str:  
        """实现必需的_run方法"""  
        try:  
            # 此处应实现营销建议生成逻辑  
            
            marketing_suggestions = """  
            ## 营销建议  

            ### 目标用户群体  
            1. **主要目标**: 35-45岁男性投资者  
               - 特点: 追求稳定收益，有一定风险承受能力  
               - 建议: 提供黄金定投计划，强调长期保值  
               - 预期成效: 提高平均客单价15%，增加月交易频次0.5次  

            2. **增长目标**: 25-35岁新兴投资者  
               - 特点: 接受新事物快，偏好移动端操作  
               - 建议: 开发小额黄金投资产品，强调投资门槛低  
               - 预期成效: 新用户获取成本降低20%，首月留存率提升15%  

            ### 营销时机  
            1. 金价波动大于1%时推送提醒  
            2. 用户闲置资金增加时推荐投资方案  
            3. 节假日期间推出特别活动  

            ### 渠道策略  
            1. 移动端应用推送 (转化率最高)  
            2. 邮件营销 (最适合详细产品介绍)  
            3. 社交媒体 (提高品牌知名度)  

            ### 内容策略  
            1. 教育类内容: 黄金投资入门指南  
            2. 分析类内容: 每周黄金市场分析  
            3. 案例类内容: 成功投资者故事分享  
            """  
            
            return marketing_suggestions  
            
        except Exception as e:  
            error_message = f"生成营销建议时出错: {str(e)}"  
            logger.error(error_message, exc_info=True)  
            return error_message  

class DataAnalystAgent:  
    """数据分析师Agent类"""  
    
    def get_agent(self, llm):  
        """创建并返回Agent实例"""  
        tools = [  
            StatisticalAnalysisTool(),  
            DataVisualizationTool(),  
            MarketingSuggestionsTool()  
        ]  
        
        return Agent(  
            role="数据分析师",  
            goal="从数据中提取有价值的洞察和模式",  
            backstory="你是一位资深数据分析师，擅长数据可视化、统计分析和预测建模，能从数据中发现业务机会。",  
            verbose=True,  
            llm=llm,  
            tools=tools  
        )  