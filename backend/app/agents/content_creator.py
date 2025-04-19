from crewai import Agent  
from crewai.tools import BaseTool  
from typing import Optional, List, Dict, Any, ClassVar  
from app.core.logger import logger  

class DesignCampaignTool(BaseTool):  
    """设计营销活动的工具"""  
    
    name: str = "DesignCampaign"  
    description: str = "设计引人入胜的营销活动，基于用户画像和营销策略"  
    
    def _run(self, strategy_data: str) -> str:  
        """实现必需的_run方法"""  
        try:  
            # 此处应实现营销活动设计逻辑  
            
            campaign_design = """  
            ## 黄金交易平台创意活动方案  

            ### 活动方案一：「黄金未来家」  
            #### 概念核心  
            将黄金投资与未来规划紧密结合，针对稳健型定投用户  

            #### 活动形式  
            1. 线上黄金定投挑战赛（100天定投，展示不同市场环境下的收益）  
            2. 个人「金色未来计划」制定工具（根据用户目标生成专属投资建议）  
            3. 真实用户故事分享（展示通过定投实现财务目标的案例）  

            #### 预期效果  
            - 提升定投用户活跃度20%  
            - 增加黄金定投计划开通率15%  
            - 强化品牌的专业可靠形象  

            ### 活动方案二：「黄金创富学院」  
            #### 概念核心  
            为新兴数字投资者提供系统化的黄金投资知识，降低认知门槛  

            #### 活动形式  
            1. 系列微课程（每节5分钟，涵盖黄金基础知识）  
            2. 模拟交易竞赛（零风险体验不同交易策略）  
            3. 新手专享福利（首笔交易金额翻倍，最高100元）  

            #### 预期效果  
            - 新用户注册转化率提升25%  
            - 首次交易完成率提升30%  
            - 扩大年轻用户群体占比  

            ### 活动方案三：「金市大师汇」  
            #### 概念核心  
            为高价值专家型用户打造专业交流平台，强化专属服务  

            #### 活动形式  
            1. 季度线下黄金市场展望会（邀请行业专家和资深投资者）  
            2. VIP专属分析师一对一咨询（重点客户专享）  
            3. 「金市先锋」社区（高级用户交流和分析共享平台）  

            #### 预期效果  
            - 高价值用户留存率提升10%  
            - 大额交易频次增加15%  
            - 建立品牌在专业投资者中的地位  
            """  
            
            return campaign_design  
            
        except Exception as e:  
            error_message = f"设计营销活动时出错: {str(e)}"  
            logger.error(error_message, exc_info=True)  
            return error_message  

class CreateMarketingCopyTool(BaseTool):  
    """创作营销文案的工具"""  
    
    name: str = "CreateMarketingCopy"  
    description: str = "创作有吸引力的营销文案，包括标题、正文和行动号召"  
    
    def _run(self, campaign_data: str) -> str:  
        """实现必需的_run方法"""  
        try:  
            # 此处应实现营销文案创作逻辑  
            
            marketing_copy = """  
            ## 黄金交易平台营销文案  

            ### 「黄金未来家」活动文案  

            #### 主标题  
            **「每一枚金币，都是未来的基石」**  

            #### 副标题  
            稳定积累，让梦想有实现的底气  

            #### 正文  
            人生目标千万种，实现方式只有一个：坚持。  

            黄金定投是通往财务自由的稳健之路。无论市场如何波动，历史告诉我们：长期持有黄金，从未让人失望。  

            加入「黄金未来家」100天定投挑战，见证小额积累的神奇力量。  

            - 每日仅需50元起  
            - 专业顾问全程陪伴  
            - 实时图表展示财富增长  

            更有「金色未来计划」定制工具，为您量身打造专属投资路线图。  

            #### 行动号召  
            **现在加入，即享首月零手续费特权 >>**  

            ### 「黄金创富学院」活动文案  

            #### 主标题  
            **「投资黄金，没有你想的那么难」**  

            #### 副标题  
            5分钟入门，开启财富增长新方式  

            #### 正文  
            黄金投资，听起来很遥远？  
            专业术语，让你望而却步？  
            担心风险，不敢迈出第一步？  

            「黄金创富学院」专为投资新手设计，用最简单的语言，教会你黄金投资的核心知识。  

            - 5分钟微课程，碎片时间轻松学  
            - 模拟交易平台，零风险体验真实市场  
            - 新手专享福利，首笔交易金额翻倍  

            投资，应该是每个人的基本技能，而不是少数人的专利。  

            #### 行动号召  
            **扫码报名，领取新手礼包 >>**  

            ### 「金市大师汇」活动文案  

            #### 主标题  
            **「与顶级投资者，共享一个对话空间」**  

            #### 副标题  
            专业的交流，成就卓越的投资  

            #### 正文  
            市场瞬息万变，独到见解弥足珍贵。  

            「金市大师汇」汇聚行业顶尖分析师与资深投资者，深度解析市场走势，分享独家投资策略。  

            - 季度市场展望会，把握宏观趋势  
            - VIP专属分析师服务，为您答疑解惑  
            - 「金市先锋」高级社区，与同侪切磋交流  

            这不仅是一场活动，更是一个持续的思想交流平台。  

            #### 行动号召  
            **限量席位，立即预约 >>**  
            """  
            
            return marketing_copy  
            
        except Exception as e:  
            error_message = f"创作营销文案时出错: {str(e)}"  
            logger.error(error_message, exc_info=True)  
            return error_message  

class ContentCreatorAgent:  
    """首席创意内容创作师Agent类"""  
    
    def get_agent(self, llm):  
        """创建并返回Agent实例"""  
        tools = [  
            DesignCampaignTool(),  
            CreateMarketingCopyTool()  
        ]  
        
        return Agent(  
            role="首席创意内容创作师",  
            goal="根据营销战略，创造吸引人的活动和文案",  
            backstory="你是内容创意大师，擅长将枯燥的数据和策略转化为吸引人的故事和文案，使营销活动更具吸引力。",  
            verbose=True,  
            llm=llm,  
            tools=tools  
        )  