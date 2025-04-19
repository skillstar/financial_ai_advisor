from crewai.tools import BaseTool  
from typing import Optional, Dict, Any, List  
import json  
import re  
from app.core.logger import logger  

class MarketingSuggestionsTool(BaseTool):  
    """生成营销建议的工具"""  
    
    name: str = "MarketingSuggestions"  
    description: str = "基于数据分析结果，生成具体的营销建议"  
    
    def _run(self, analysis_results: str) -> str:  
        """实现必需的_run方法"""  
        try:  
            # 解析分析结果  
            data = self._parse_analysis_results(analysis_results)  
            
            # 生成用户群体分析  
            user_segments = self._analyze_user_segments(data)  
            
            # 确定最佳营销时机  
            marketing_timing = self._determine_marketing_timing(data)  
            
            # 制定渠道策略  
            channel_strategy = self._develop_channel_strategy(data, user_segments)  
            
            # 设计内容策略  
            content_strategy = self._design_content_strategy(data, user_segments)  
            
            # 整合所有策略，生成完整的营销建议  
            marketing_suggestions = self._generate_final_suggestions(  
                user_segments, marketing_timing, channel_strategy, content_strategy  
            )  
            
            return marketing_suggestions  
            
        except Exception as e:  
            error_message = f"生成营销建议时出错: {str(e)}"  
            logger.error(error_message, exc_info=True)  
            return error_message  
    
    def _parse_analysis_results(self, analysis_results: str) -> Dict[str, Any]:  
        """解析分析结果文本"""  
        # 尝试从文本中提取JSON数据  
        try:  
            json_match = re.search(r'```json\n(.*?)\n```', analysis_results, re.DOTALL)  
            if json_match:  
                json_str = json_match.group(1)  
                return json.loads(json_str)  
        except Exception:  
            pass  
        
        # 如果没有找到JSON或解析失败，使用正则表达式提取关键信息  
        data = {}  
        
        # 提取用户分群信息  
        segments_pattern = r'群体([A-D]):\s*([^(]+)\s*\((\d+)%\s*用户\)'  
        segments = re.findall(segments_pattern, analysis_results)  
        
        user_segments = []  
        for segment_id, desc, percentage in segments:  
            user_segments.append({  
                "id": segment_id,  
                "description": desc.strip(),  
                "percentage": int(percentage)  
            })  
        
        data['user_segments'] = user_segments  
        
        # 提取活跃用户群信息  
        active_group_pattern = r'最活跃用户群:\s*([^,]+)'  
        active_group_match = re.search(active_group_pattern, analysis_results)  
        if active_group_match:  
            data['active_group'] = active_group_match.group(1).strip()  
        
        # 提取风险偏好信息  
        risk_pattern = r'(保守型|平衡型|进取型):\s*(\d+)%\s*\(平均交易金额¥([\d,]+)\)'  
        risk_profiles = re.findall(risk_pattern, analysis_results)  
        
        risk_data = []  
        for risk_type, percentage, amount in risk_profiles:  
            risk_data.append({  
                "type": risk_type,  
                "percentage": int(percentage),  
                "amount": amount.replace(',', '')  
            })  
        
        data['risk_profiles'] = risk_data  
        
        # 提取用户价值分层信息  
        value_pattern = r'(高|中|低)价值用户:\s*(\d+)%\s*\(贡献(\d+)%交易额\)'  
        value_tiers = re.findall(value_pattern, analysis_results)  
        
        value_data = []  
        for tier, user_pct, amount_pct in value_tiers:  
            value_data.append({  
                "tier": tier,  
                "user_percentage": int(user_pct),  
                "amount_percentage": int(amount_pct)  
            })  
        
        data['value_tiers'] = value_data  
        
        return data  
    
    def _analyze_user_segments(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:  
        """分析用户群体，确定目标用户群"""  
        # 如果有用户分群数据，分析每个群体的价值  
        if 'user_segments' in data and data['user_segments']:  
            segments = data['user_segments']  
            # 按照特定逻辑排序分群（这里简单使用ID）  
            sorted_segments = sorted(segments, key=lambda x: x['id'])  
            return sorted_segments  
        
        # 如果有用户价值分层数据，使用它来确定目标  
        elif 'value_tiers' in data and data['value_tiers']:  
            targets = []  
            
            # 处理高价值用户  
            high_value = next((tier for tier in data['value_tiers'] if tier['tier'] == '高'), None)  
            if high_value:  
                targets.append({  
                    "id": "A",  
                    "name": "主要目标",  
                    "description": "35-45岁男性投资者",  
                    "characteristics": "追求稳定收益，有一定风险承受能力",  
                    "recommendation": "提供黄金定投计划，强调长期保值",  
                    "expected_results": "提高平均客单价15%，增加月交易频次0.5次"  
                })  
            
            # 添加增长目标  
            targets.append({  
                "id": "B",  
                "name": "增长目标",  
                "description": "25-35岁新兴投资者",  
                "characteristics": "接受新事物快，偏好移动端操作",  
                "recommendation": "开发小额黄金投资产品，强调投资门槛低",  
                "expected_results": "新用户获取成本降低20%，首月留存率提升15%"  
            })  
            
            return targets  
        
        # 如果没有足够数据，提供默认目标群体  
        else:  
            return [  
                {  
                    "id": "A",  
                    "name": "主要目标",  
                    "description": "35-45岁男性投资者",  
                    "characteristics": "追求稳定收益，有一定风险承受能力",  
                    "recommendation": "提供黄金定投计划，强调长期保值",  
                    "expected_results": "提高平均客单价15%，增加月交易频次0.5次"  
                },  
                {  
                    "id": "B",  
                    "name": "增长目标",  
                    "description": "25-35岁新兴投资者",  
                    "characteristics": "接受新事物快，偏好移动端操作",  
                    "recommendation": "开发小额黄金投资产品，强调投资门槛低",  
                    "expected_results": "新用户获取成本降低20%，首月留存率提升15%"  
                }  
            ]  
    
    def _determine_marketing_timing(self, data: Dict[str, Any]) -> List[Dict[str, str]]:  
        """确定最佳营销时机"""  
        # 基于分析结果确定营销时机  
        timings = [  
            {  
                "trigger": "金价波动大于1%",  
                "action": "推送提醒",  
                "rationale": "数据显示金价波动与交易量呈负相关，用户倾向在价格变动时做决策"  
            },  
            {  
                "trigger": "用户闲置资金增加",  
                "action": "推荐投资方案",  
                "rationale": "及时引导用户将闲置资金转化为投资，提高平台资金利用率"  
            },  
            {  
                "trigger": "节假日期间",  
                "action": "推出特别活动",  
                "rationale": "节假日用户有更多时间关注投资，且存在季节性消费习惯"  
            }  
        ]  
        
        # 如果有活跃时间数据，添加特定时段营销建议  
        if 'active_hours' in data:  
            timings.append({  
                "trigger": "日内高峰交易时段",  
                "action": "加强实时市场分析推送",  
                "rationale": "在用户最活跃的时段提供决策支持，提高转化率"  
            })  
        
        return timings  
    
    def _develop_channel_strategy(self, data: Dict[str, Any], user_segments: List[Dict[str, Any]]) -> List[Dict[str, str]]:  
        """制定渠道策略"""  
        # 基本渠道策略  
        channels = [  
            {  
                "channel": "移动端应用推送",  
                "advantage": "转化率最高",  
                "target_segments": "所有用户群体",  
                "content_type": "交易提醒、价格波动提醒"  
            },  
            {  
                "channel": "邮件营销",  
                "advantage": "最适合详细产品介绍",  
                "target_segments": "高价值用户、低频大额交易者",  
                "content_type": "市场分析报告、投资组合建议"  
            },  
            {  
                "channel": "社交媒体",  
                "advantage": "提高品牌知名度",  
                "target_segments": "潜在用户、年轻投资者",  
                "content_type": "教育内容、品牌故事、市场趋势"  
            }  
        ]  
        
        # 根据用户分群调整渠道策略  
        if len(user_segments) > 2:  
            # 针对频繁交易者的渠道  
            channels.append({  
                "channel": "即时通讯工具",  
                "advantage": "快速触达活跃用户",  
                "target_segments": "高频交易者",  
                "content_type": "实时市场动态、闪购优惠"  
            })  
        
        return channels  
    
    def _design_content_strategy(self, data: Dict[str, Any], user_segments: List[Dict[str, Any]]) -> List[Dict[str, str]]:  
        """设计内容策略"""  
        # 基本内容策略  
        contents = [  
            {  
                "type": "教育类内容",  
                "title": "黄金投资入门指南",  
                "target": "新用户、初级投资者",  
                "objective": "降低入门门槛，提升品牌权威性"  
            },  
            {  
                "type": "分析类内容",  
                "title": "每周黄金市场分析",  
                "target": "活跃投资者、高价值客户",  
                "objective": "提供决策支持，增强用户粘性"  
            },  
            {  
                "type": "案例类内容",  
                "title": "成功投资者故事分享",  
                "target": "所有用户",  
                "objective": "建立信任，鼓励用户效仿成功案例"  
            }  
        ]  
        
        # 根据用户群体特征增强内容策略  
        if any('风险' in str(segment) for segment in user_segments):  
            contents.append({  
                "type": "工具类内容",  
                "title": "个人风险承受能力评估工具",  
                "target": "新用户、风险意识较强用户",  
                "objective": "帮助用户了解自己的风险偏好，引导合适产品"  
            })  
        
        return contents  
    
    def _generate_final_suggestions(  
        self,   
        user_segments: List[Dict[str, Any]],   
        marketing_timing: List[Dict[str, str]],   
        channel_strategy: List[Dict[str, str]],   
        content_strategy: List[Dict[str, str]]  
    ) -> str:  
        """整合所有策略，生成完整的营销建议"""  
        # 格式化目标用户群体  
        user_segments_text = "### 目标用户群体\n"  
        for i, segment in enumerate(user_segments[:2]):  # 只展示前两个主要目标  
            if 'name' in segment:  
                user_segments_text += f"{i+1}. **{segment['name']}**: {segment.get('description', '')}\n"  
            else:  
                user_segments_text += f"{i+1}. **目标{i+1}**: {segment.get('description', '')}\n"  
                
            if 'characteristics' in segment:  
                user_segments_text += f"   - 特点: {segment['characteristics']}\n"  
            
            if 'recommendation' in segment:  
                user_segments_text += f"   - 建议: {segment['recommendation']}\n"  
            
            if 'expected_results' in segment:  
                user_segments_text += f"   - 预期成效: {segment['expected_results']}\n"  
            
            user_segments_text += "\n"  
        
        # 格式化营销时机  
        timing_text = "### 营销时机\n"  
        for i, timing in enumerate(marketing_timing):  
            timing_text += f"{i+1}. {timing['trigger']}时{timing['action']}\n"  
        
        # 格式化渠道策略  
        channel_text = "### 渠道策略\n"  
        for i, channel in enumerate(channel_strategy):  
            channel_text += f"{i+1}. {channel['channel']} ({channel['advantage']})\n"  
        
        # 格式化内容策略  
        content_text = "### 内容策略\n"  
        for i, content in enumerate(content_strategy):  
            content_text += f"{i+1}. {content['type']}: {content['title']}\n"  
        
        # 整合所有策略  
        final_suggestions = f"""  
        ## 营销建议  

        {user_segments_text}  
        {timing_text}  
        {channel_text}  
        {content_text}  
        """  
        
        return final_suggestions  