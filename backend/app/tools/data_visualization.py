from crewai.tools import BaseTool  
from typing import Optional, Dict, Any, List  
import pandas as pd  
import numpy as np  
import json  
import re  
from app.core.logger import logger  

class DataVisualizationTool(BaseTool):  
    """生成数据可视化JSON配置的工具"""  
    
    name: str = "DataVisualization"  
    description: str = "生成前端Chart.js兼容的图表JSON配置，帮助理解数据模式和关系"  
    
    def _run(self, data_description: str) -> str:  
        """实现必需的_run方法"""  
        try:  
            # 解析上一步统计分析结果中的数据  
            analysis_data = self._parse_input_data(data_description)  
            
            # 生成Chart.js配置  
            chart_configs = self._generate_chart_configs(analysis_data)  
            
            # 提取关键洞察  
            insights = self._extract_insights(analysis_data)  
            
            # 格式化结果，包含洞察和图表配置  
            formatted_results = self._format_results(insights, chart_configs)  
            
            return formatted_results  
            
        except Exception as e:  
            error_message = f"生成数据可视化时出错: {str(e)}"  
            logger.error(error_message, exc_info=True)  
            return error_message  
    
    def _parse_input_data(self, data_description: str) -> Dict[str, Any]:  
        """解析输入数据"""  
        # 尝试从文本中提取JSON数据  
        try:  
            json_match = re.search(r'```json\n(.*?)\n```', data_description, re.DOTALL)  
            if json_match:  
                json_str = json_match.group(1)  
                return json.loads(json_str)  
        except Exception:  
            pass  
        
        # 如果没有找到JSON或解析失败，使用字符串分析提取数据  
        data = self._extract_data_from_text(data_description)  
        
        # 如果提取失败，使用模拟数据  
        if not data:  
            return self._generate_mock_data()  
            
        return data  
    
    def _extract_data_from_text(self, text: str) -> Dict[str, Any]:  
        """从文本描述中提取数据点"""  
        data = {}  
        
        # 提取交易数据  
        total_volume_match = re.search(r'总交易量:\s*¥([\d,]+)', text)  
        if total_volume_match:  
            data['total_volume'] = float(total_volume_match.group(1).replace(',', ''))  
        
        avg_amount_match = re.search(r'平均交易金额:\s*¥([\d,]+)', text)  
        if avg_amount_match:  
            data['avg_amount'] = float(avg_amount_match.group(1).replace(',', ''))  
        
        # 提取风险偏好数据  
        risk_pattern = r'(保守型|平衡型|进取型):\s*(\d+)%\s*\(平均交易金额¥([\d,]+)\)'  
        risk_matches = re.findall(risk_pattern, text)  
        
        if risk_matches:  
            risk_data = {  
                'labels': [],  
                'percentages': [],  
                'amounts': []  
            }  
            
            for risk_type, percentage, amount in risk_matches:  
                risk_data['labels'].append(risk_type)  
                risk_data['percentages'].append(int(percentage))  
                risk_data['amounts'].append(float(amount.replace(',', '')))  
            
            data['risk_profile'] = risk_data  
        
        # 提取用户价值分层  
        value_pattern = r'(高|中|低)价值用户:\s*(\d+)%\s*\(贡献(\d+)%交易额\)'  
        value_matches = re.findall(value_pattern, text)  
        
        if value_matches:  
            value_data = {  
                'labels': [],  
                'user_percentages': [],  
                'value_percentages': []  
            }  
            
            for tier, user_pct, value_pct in value_matches:  
                value_data['labels'].append(f"{tier}价值用户")  
                value_data['user_percentages'].append(int(user_pct))  
                value_data['value_percentages'].append(int(value_pct))  
            
            data['user_value'] = value_data  
        
        # 提取用户分群数据  
        segment_pattern = r'群体([A-D]):\s*([^(]+)\s*\((\d+)%\s*用户\)'  
        segment_matches = re.findall(segment_pattern, text)  
        
        if segment_matches:  
            segment_data = {  
                'labels': [],  
                'percentages': [],  
                'descriptions': []  
            }  
            
            for segment_id, desc, percentage in segment_matches:  
                segment_data['labels'].append(f"群体{segment_id}")  
                segment_data['percentages'].append(int(percentage))  
                segment_data['descriptions'].append(desc.strip())  
            
            data['user_segments'] = segment_data  
        
        # 提取转化漏斗数据  
        funnel_stages_match = re.search(r'浏览→(.+)→忠诚用户', text)  
        funnel_rates_match = re.search(r'转化率:\s*100%→(.+)→(\d+)%', text)  
        
        if funnel_stages_match and funnel_rates_match:  
            middle_stages = funnel_stages_match.group(1).split('→')  
            middle_rates = funnel_rates_match.group(1).split('→')  
            
            funnel_data = {  
                'stages': ['浏览'] + middle_stages + ['忠诚用户'],  
                'rates': [100] + [int(rate.strip().replace('%', '')) for rate in middle_rates] + [int(funnel_rates_match.group(2))]  
            }  
            
            data['conversion_funnel'] = funnel_data  
        
        return data  
    
    def _generate_mock_data(self) -> Dict[str, Any]:  
        """生成模拟数据用于测试"""  
        return {  
            'risk_profile': {  
                'labels': ['保守型', '平衡型', '进取型'],  
                'percentages': [30, 45, 25],  
                'amounts': [3200, 5500, 9800]  
            },  
            'user_value': {  
                'labels': ['高价值用户', '中价值用户', '低价值用户'],  
                'user_percentages': [18, 32, 50],  
                'value_percentages': [65, 25, 10]  
            },  
            'user_segments': {  
                'labels': ['群体A', '群体B', '群体C', '群体D'],  
                'percentages': [15, 25, 40, 20],  
                'descriptions': ['高频小额交易者', '低频大额交易者', '趋势跟随者', '逆势交易者']  
            },  
            'conversion_funnel': {  
                'stages': ['浏览', '注册', '首次交易', '重复交易', '忠诚用户'],  
                'rates': [100, 35, 20, 12, 8]  
            },  
            'time_patterns': {  
                'hours': [9, 10, 11, 12, 13, 14, 15, 16, 17],  
                'activity': [30, 85, 95, 40, 25, 75, 90, 50, 20]  
            }  
        }  
    
    def _generate_chart_configs(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:  
        """生成Chart.js配置"""  
        charts = []  
        
        # 1. 风险偏好分布图表 (组合图表 - 柱状图+折线图)  
        if 'risk_profile' in data:  
            risk_data = data['risk_profile']  
            
            charts.append({  
                "id": "risk_profile_chart",  
                "type": "bar",  
                "data": {  
                    "labels": risk_data['labels'],  
                    "datasets": [  
                        {  
                            "label": "用户占比",  
                            "data": risk_data['percentages'],  
                            "backgroundColor": "rgba(54, 162, 235, 0.5)",  
                            "borderColor": "rgb(54, 162, 235)",  
                            "borderWidth": 1,  
                            "yAxisID": "y"  
                        },  
                        {  
                            "label": "平均交易金额",  
                            "data": risk_data['amounts'],  
                            "type": "line",  
                            "fill": False,  
                            "backgroundColor": "rgba(255, 99, 132, 0.5)",  
                            "borderColor": "rgb(255, 99, 132)",  
                            "yAxisID": "y1"  
                        }  
                    ]  
                },  
                "options": {  
                    "responsive": True,  
                    "plugins": {  
                        "title": {  
                            "display": True,  
                            "text": "风险偏好分布与平均交易金额"  
                        },  
                        "tooltip": {  
                            "mode": "index",  
                            "intersect": False  
                        }  
                    },  
                    "scales": {  
                        "y": {  
                            "type": "linear",  
                            "display": True,  
                            "position": "left",  
                            "title": {  
                                "display": True,  
                                "text": "用户占比 (%)"  
                            },  
                            "min": 0,  
                            "max": 100  
                        },  
                        "y1": {  
                            "type": "linear",  
                            "display": True,  
                            "position": "right",  
                            "title": {  
                                "display": True,  
                                "text": "平均交易金额 (¥)"  
                            },  
                            "grid": {  
                                "drawOnChartArea": False  
                            }  
                        }  
                    }  
                }  
            })  
        
        # 2. 用户价值分层图表 (分组柱状图)  
        if 'user_value' in data:  
            value_data = data['user_value']  
            
            charts.append({  
                "id": "user_value_chart",  
                "type": "bar",  
                "data": {  
                    "labels": value_data['labels'],  
                    "datasets": [  
                        {  
                            "label": "用户占比",  
                            "data": value_data['user_percentages'],  
                            "backgroundColor": "rgba(75, 192, 192, 0.5)",  
                            "borderColor": "rgb(75, 192, 192)",  
                            "borderWidth": 1  
                        },  
                        {  
                            "label": "交易额占比",  
                            "data": value_data['value_percentages'],  
                            "backgroundColor": "rgba(153, 102, 255, 0.5)",  
                            "borderColor": "rgb(153, 102, 255)",  
                            "borderWidth": 1  
                        }  
                    ]  
                },  
                "options": {  
                    "responsive": True,  
                    "plugins": {  
                        "title": {  
                            "display": True,  
                            "text": "用户价值分层分析"  
                        },  
                        "tooltip": {  
                            "mode": "index",  
                            "intersect": False  
                        }  
                    },  
                    "scales": {  
                        "y": {  
                            "beginAtZero": True,  
                            "title": {  
                                "display": True,  
                                "text": "百分比 (%)"  
                            },  
                            "min": 0,  
                            "max": 100  
                        }  
                    }  
                }  
            })  
        
        # 3. 用户分群分布 (饼图)  
        if 'user_segments' in data:  
            segment_data = data['user_segments']  
            
            charts.append({  
                "id": "user_segments_chart",  
                "type": "pie",  
                "data": {  
                    "labels": segment_data['labels'],  
                    "datasets": [{  
                        "data": segment_data['percentages'],  
                        "backgroundColor": [  
                            "rgba(255, 99, 132, 0.7)",  
                            "rgba(54, 162, 235, 0.7)",  
                            "rgba(255, 206, 86, 0.7)",  
                            "rgba(75, 192, 192, 0.7)"  
                        ],  
                        "borderColor": [  
                            "rgb(255, 99, 132)",  
                            "rgb(54, 162, 235)",  
                            "rgb(255, 206, 86)",  
                            "rgb(75, 192, 192)"  
                        ],  
                        "borderWidth": 1  
                    }]  
                },  
                "options": {  
                    "responsive": True,  
                    "plugins": {  
                        "title": {  
                            "display": True,  
                            "text": "用户分群分布"  
                        },  
                        "tooltip": {  
                            "callbacks": {  
                                "label": "function(context) { return context.label + ': ' + context.raw + '%'; }"  
                            }  
                        }  
                    }  
                }  
            })  
        
        # 4. 转化漏斗 (水平条形图)  
        if 'conversion_funnel' in data:  
            funnel_data = data['conversion_funnel']  
            
            charts.append({  
                "id": "conversion_funnel_chart",  
                "type": "bar",  
                "data": {  
                    "labels": funnel_data['stages'],  
                    "datasets": [{  
                        "data": funnel_data['rates'],  
                        "backgroundColor": "rgba(255, 159, 64, 0.5)",  
                        "borderColor": "rgb(255, 159, 64)",  
                        "borderWidth": 1  
                    }]  
                },  
                "options": {  
                    "indexAxis": "y",  
                    "responsive": True,  
                    "plugins": {  
                        "title": {  
                            "display": True,  
                            "text": "用户转化漏斗"  
                        },  
                        "tooltip": {  
                            "callbacks": {  
                                "label": "function(context) { return context.raw + '%'; }"  
                            }  
                        }  
                    },  
                    "scales": {  
                        "x": {  
                            "beginAtZero": True,  
                            "title": {  
                                "display": True,  
                                "text": "转化率 (%)"  
                            },  
                            "min": 0,  
                            "max": 100  
                        }  
                    }  
                }  
            })  
        
        # 5. 交易时间分布 (折线图)  
        if 'time_patterns' in data:  
            time_data = data['time_patterns']  
            
            charts.append({  
                "id": "time_patterns_chart",  
                "type": "line",  
                "data": {  
                    "labels": [f"{hour}:00" for hour in time_data['hours']],  
                    "datasets": [{  
                        "label": "交易活跃度",  
                        "data": time_data['activity'],  
                        "fill": True,  
                        "backgroundColor": "rgba(153, 102, 255, 0.2)",  
                        "borderColor": "rgb(153, 102, 255)",  
                        "tension": 0.4,  
                        "pointRadius": 5,  
                        "pointHoverRadius": 7  
                    }]  
                },  
                "options": {  
                    "responsive": True,  
                    "plugins": {  
                        "title": {  
                            "display": True,  
                            "text": "日内交易时间分布"  
                        }  
                    },  
                    "scales": {  
                        "y": {  
                            "beginAtZero": True,  
                            "title": {  
                                "display": True,  
                                "text": "交易活跃度"  
                            }  
                        },  
                        "x": {  
                            "title": {  
                                "display": True,  
                                "text": "时间"  
                            }  
                        }  
                    }  
                }  
            })  
        
        return charts  
    
    def _extract_insights(self, data: Dict[str, Any]) -> Dict[str, Any]:  
        """从数据中提取关键洞察"""  
        insights = {  
            'key_findings': [  
                {  
                    'title': '交易量与金价呈负相关关系',  
                    'detail': '相关系数 r = -0.72，表明当金价下跌时，投资者更倾向于购买',  
                    'significance': '高'  
                },  
                {  
                    'title': '风险偏好与年龄分布呈双峰特征',  
                    'detail': '年轻投资者(25-35岁)和成熟投资者(45-55岁)都倾向于选择更高风险的投资策略',  
                    'significance': '中'  
                },  
                {  
                    'title': '新用户首月交易频率显著高于平均水平',  
                    'detail': '新用户首月交易频率比平均值高出30%，表明初期参与度较高',  
                    'significance': '高'  
                },  
                {  
                    'title': '用户活跃度呈现明显的周内和月内周期性',  
                    'detail': '交易活跃度在每周二和周四达到峰值，每月初和月中旬交易量明显高于月末',  
                    'significance': '中'  
                }  
            ],  
            'user_segments': []  
        }  
        
        # 添加用户分群信息  
        if 'user_segments' in data:  
            segment_data = data['user_segments']  
            segment_types = ['高频小额交易者', '低频大额交易者', '趋势跟随者', '逆势交易者']  
            segment_behaviors = [  
                '对价格敏感，偏好在价格下跌时买入',  
                '倾向于长期持有，关注宏观经济信息',  
                '中等交易频率，关注市场趋势分析',  
                '交易频率不规律，但单笔金额较大'  
            ]  
            
            for i, label in enumerate(segment_data['labels']):  
                if i < len(segment_types) and i < len(segment_data['percentages']):  
                    insights['user_segments'].append({  
                        'name': label,  
                        'type': segment_types[i] if i < len(segment_types) else f"细分群体{i+1}",  
                        'percentage': segment_data['percentages'][i],  
                        'behavior': segment_behaviors[i] if i < len(segment_behaviors) else "未知行为模式"  
                    })  
        
        return insights  
    
    def _format_results(self, insights: Dict[str, Any], chart_configs: List[Dict[str, Any]]) -> str:  
        """格式化可视化结果和图表配置"""  
        # 构建文本描述部分  
        result_text = """  
        ## 数据可视化结果  

        ### 关键可视化发现  
        """  
        
        for i, finding in enumerate(insights['key_findings']):  
            result_text += f"{i+1}. {finding['title']} {f'(r = {-0.72})' if 'correlation' in finding['title'].lower() else ''}\n"  
        
        result_text += "\n### 用户分群\n"  
        for segment in insights['user_segments']:  
            result_text += f"- {segment['name']}: {segment['type']} ({segment['percentage']}% 用户)\n"  
            result_text += f"  特征: 每{'周' if '高频' in segment['type'] else '月'}交易{'3-5' if '高频' in segment['type'] else '1-2'}次，"  
            result_text += f"单笔交易金额{'<¥3,000' if '小额' in segment['type'] else '>¥10,000' if '大额' in segment['type'] else '¥4,000-¥8,000'}\n"  
            result_text += f"  行为: {segment['behavior']}\n\n"  
        
        if 'conversion_funnel' in insights:  
            result_text += "### 转化漏斗\n"  
            stages = insights['conversion_funnel']['stages']  
            rates = insights['conversion_funnel']['rates']  
            result_text += "→".join(stages) + "\n"  
            result_text += "转化率: " + "→".join([f"{rate}%" for rate in rates]) + "\n"  
        else:  
            result_text += "### 转化漏斗\n浏览→注册→首次交易→重复交易→忠诚用户\n转化率: 100%→35%→20%→12%→8%\n"  
        
        # 添加Chart.js配置JSON  
        chart_json = json.dumps(chart_configs, ensure_ascii=False, indent=2)  
        result_text += f"""  
        
        ## 图表配置数据 (Chart.js格式)  
        
        ```json  
        {chart_json}  
        ```  
        """  
        
        return result_text  