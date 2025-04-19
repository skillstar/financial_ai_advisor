from crewai.tools import BaseTool  
from typing import Dict, List, Any, Optional  
import json  
import re  
from app.core.logger import logger  

class ChartGenerationTool(BaseTool):  
    """生成Chart.js兼容的图表JSON数据"""  
    
    name: str = "GenerateChartData"  
    description: str = "将分析结果转换为前端Chart.js可以直接使用的JSON数据格式"  
    
    def _run(self, analysis_text: str) -> str:  
        """  
        根据分析文本内容生成Chart.js格式的图表数据  
        
        参数:  
            analysis_text (str): 包含分析结果的文本数据  
            
        返回:  
            str: JSON字符串，包含多个图表配置  
        """  
        try:  
            # 解析文本，提取可视化的数据点  
            extracted_data = self._extract_data_from_text(analysis_text)  
            
            # 决定每组数据适合的图表类型  
            charts_config = self._generate_charts_config(extracted_data)  
            
            # 转换为JSON字符串  
            charts_json = json.dumps(charts_config, ensure_ascii=False, indent=2)  
            
            # 包装为Markdown格式返回  
            result = f"""  
            ## 图表数据 (Chart.js格式)  
            
            以下JSON数据可直接用于前端Chart.js渲染:  
            
            ```json  
            {charts_json}  
            ```  
            
            ### 图表概览  
            
            已生成 {len(charts_config)} 个图表:  
            {self._generate_charts_summary(charts_config)}  
            """  
            
            return result  
            
        except Exception as e:  
            error_message = f"生成图表数据时出错: {str(e)}"  
            logger.error(error_message, exc_info=True)  
            return error_message  
    
    def _extract_data_from_text(self, text: str) -> Dict[str, Any]:  
        """从文本中提取数据点"""  
        extracted_data = {  
            "user_segments": self._extract_user_segments(text),  
            "transaction_metrics": self._extract_transaction_metrics(text),  
            "risk_distribution": self._extract_risk_distribution(text),  
            "user_value_tiers": self._extract_user_value_tiers(text),  
            "conversion_funnel": self._extract_conversion_funnel(text),  
            "time_patterns": self._extract_time_patterns(text)  
        }  
        
        return extracted_data  
    
    def _extract_user_segments(self, text: str) -> Dict[str, Any]:  
        """提取用户分群数据"""  
        # 使用正则表达式查找用户分群部分  
        pattern = r"群体([A-D]):\s*([^(]+)\s*\((\d+)%\s*用户\)"  
        matches = re.findall(pattern, text)  
        
        segments = {}  
        if matches:  
            labels = []  
            percentages = []  
            descriptions = []  
            
            for match in matches:  
                segment_id, desc, percentage = match  
                labels.append(f"群体{segment_id}")  
                percentages.append(int(percentage))  
                descriptions.append(desc.strip())  
            
            segments = {  
                "labels": labels,  
                "data": percentages,  
                "descriptions": descriptions,  
                "title": "用户分群分布"  
            }  
        
        return segments  
    
    def _extract_transaction_metrics(self, text: str) -> Dict[str, Any]:  
        """提取交易指标数据"""  
        total_pattern = r"总交易量:\s*¥([\d,]+)"  
        avg_pattern = r"平均交易金额:\s*¥([\d,]+)"  
        freq_pattern = r"交易频率:\s*每用户每月平均([\d\.]+)笔"  
        
        total_match = re.search(total_pattern, text)  
        avg_match = re.search(avg_pattern, text)  
        freq_match = re.search(freq_pattern, text)  
        
        metrics = {}  
        if total_match or avg_match or freq_match:  
            labels = []  
            values = []  
            
            if total_match:  
                total_value = float(total_match.group(1).replace(',', ''))  
                labels.append("总交易量")  
                values.append(total_value)  
            
            if avg_match:  
                avg_value = float(avg_match.group(1).replace(',', ''))  
                labels.append("平均交易金额")  
                values.append(avg_value)  
            
            if freq_match:  
                freq_value = float(freq_match.group(1))  
                labels.append("月均交易频次")  
                values.append(freq_value)  
            
            metrics = {  
                "labels": labels,  
                "data": values,  
                "title": "交易指标概览"  
            }  
        
        return metrics  
    
    def _extract_risk_distribution(self, text: str) -> Dict[str, Any]:  
        """提取风险偏好分布数据"""  
        pattern = r"(保守型|平衡型|进取型):\s*(\d+)%\s*\(平均交易金额¥([\d,]+)\)"  
        matches = re.findall(pattern, text)  
        
        distribution = {}  
        if matches:  
            labels = []  
            percentages = []  
            avg_amounts = []  
            
            for match in matches:  
                risk_type, percentage, amount = match  
                labels.append(risk_type)  
                percentages.append(int(percentage))  
                avg_amounts.append(float(amount.replace(',', '')))  
            
            distribution = {  
                "labels": labels,  
                "percentages": percentages,  
                "avgAmounts": avg_amounts,  
                "title": "风险偏好分布"  
            }  
        
        return distribution  
    
    def _extract_user_value_tiers(self, text: str) -> Dict[str, Any]:  
        """提取用户价值分层数据"""  
        pattern = r"(高|中|低)价值用户:\s*(\d+)%\s*\(贡献(\d+)%交易额\)"  
        matches = re.findall(pattern, text)  
        
        tiers = {}  
        if matches:  
            labels = []  
            user_percentages = []  
            value_percentages = []  
            
            for match in matches:  
                tier, user_pct, value_pct = match  
                labels.append(f"{tier}价值用户")  
                user_percentages.append(int(user_pct))  
                value_percentages.append(int(value_pct))  
            
            tiers = {  
                "labels": labels,  
                "userPercentages": user_percentages,  
                "valuePercentages": value_percentages,  
                "title": "用户价值分层"  
            }  
        
        return tiers  
    
    def _extract_conversion_funnel(self, text: str) -> Dict[str, Any]:  
        """提取转化漏斗数据"""  
        stages_pattern = r"浏览→(.+)→忠诚用户"  
        rates_pattern = r"转化率:\s*100%→(.+)→(\d+)%"  
        
        stages_match = re.search(stages_pattern, text)  
        rates_match = re.search(rates_pattern, text)  
        
        funnel = {}  
        if stages_match and rates_match:  
            middle_stages = stages_match.group(1).split("→")  
            middle_rates = rates_match.group(1).split("→")  
            
            stages = ["浏览"] + middle_stages + ["忠诚用户"]  
            rates = [100] + [int(rate.strip().replace('%', '')) for rate in middle_rates] + [int(rates_match.group(2))]  
            
            funnel = {  
                "labels": stages,  
                "data": rates,  
                "title": "用户转化漏斗"  
            }  
        
        return funnel  
    
    def _extract_time_patterns(self, text: str) -> Dict[str, Any]:  
        """提取时间模式数据"""  
        pattern = r"高峰交易时间:\s*周一至周五\s*([\d:]+)-([\d:]+),\s*([\d:]+)-([\d:]+)"  
        match = re.search(pattern, text)  
        
        patterns = {}  
        if match:  
            morning_start, morning_end, afternoon_start, afternoon_end = match.groups()  
            
            hours = ["9:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00"]  
            activity = [30, 85, 95, 40, 25, 75, 90, 50, 20]  # 模拟数据  
            
            patterns = {  
                "labels": hours,  
                "data": activity,  
                "title": "交易时间分布"  
            }  
        
        return patterns  
    
    def _generate_charts_config(self, extracted_data: Dict[str, Any]) -> List[Dict[str, Any]]:  
        """生成多个图表配置"""  
        charts = []  
        
        # 用户分群饼图  
        if extracted_data["user_segments"]:  
            charts.append({  
                "id": "user_segments_chart",  
                "type": "pie",  
                "data": {  
                    "labels": extracted_data["user_segments"]["labels"],  
                    "datasets": [{  
                        "data": extracted_data["user_segments"]["data"],  
                        "backgroundColor": [  
                            "rgba(255, 99, 132, 0.7)",  
                            "rgba(54, 162, 235, 0.7)",  
                            "rgba(255, 206, 86, 0.7)",  
                            "rgba(75, 192, 192, 0.7)"  
                        ],  
                        "borderColor": [  
                            "rgba(255, 99, 132, 1)",  
                            "rgba(54, 162, 235, 1)",  
                            "rgba(255, 206, 86, 1)",  
                            "rgba(75, 192, 192, 1)"  
                        ],  
                        "borderWidth": 1  
                    }]  
                },  
                "options": {  
                    "responsive": True,  
                    "plugins": {  
                        "legend": {  
                            "position": "right"  
                        },  
                        "title": {  
                            "display": True,  
                            "text": extracted_data["user_segments"]["title"]  
                        },  
                        "tooltip": {  
                            "callbacks": {  
                                "label": "function(context) { return context.label + ': ' + context.raw + '%'; }"  
                            }  
                        }  
                    }  
                }  
            })  
        
        # 风险偏好分布双轴图表  
        if extracted_data["risk_distribution"]:  
            charts.append({  
                "id": "risk_distribution_chart",  
                "type": "bar",  
                "data": {  
                    "labels": extracted_data["risk_distribution"]["labels"],  
                    "datasets": [  
                        {  
                            "label": "用户占比",  
                            "data": extracted_data["risk_distribution"]["percentages"],  
                            "backgroundColor": "rgba(54, 162, 235, 0.7)",  
                            "borderColor": "rgba(54, 162, 235, 1)",  
                            "borderWidth": 1,  
                            "yAxisID": "y"  
                        },  
                        {  
                            "label": "平均交易金额",  
                            "data": extracted_data["risk_distribution"]["avgAmounts"],  
                            "type": "line",  
                            "borderColor": "rgba(255, 99, 132, 1)",  
                            "borderWidth": 2,  
                            "fill": False,  
                            "yAxisID": "y1"  
                        }  
                    ]  
                },  
                "options": {  
                    "responsive": True,  
                    "plugins": {  
                        "title": {  
                            "display": True,  
                            "text": extracted_data["risk_distribution"]["title"]  
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
                            }  
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
        
        # 用户价值分层图表  
        if extracted_data["user_value_tiers"]:  
            charts.append({  
                "id": "user_value_tiers_chart",  
                "type": "bar",  
                "data": {  
                    "labels": extracted_data["user_value_tiers"]["labels"],  
                    "datasets": [  
                        {  
                            "label": "用户占比",  
                            "data": extracted_data["user_value_tiers"]["userPercentages"],  
                            "backgroundColor": "rgba(54, 162, 235, 0.7)",  
                            "borderColor": "rgba(54, 162, 235, 1)",  
                            "borderWidth": 1  
                        },  
                        {  
                            "label": "贡献交易额占比",  
                            "data": extracted_data["user_value_tiers"]["valuePercentages"],  
                            "backgroundColor": "rgba(255, 99, 132, 0.7)",  
                            "borderColor": "rgba(255, 99, 132, 1)",  
                            "borderWidth": 1  
                        }  
                    ]  
                },  
                "options": {  
                    "responsive": True,  
                    "plugins": {  
                        "title": {  
                            "display": True,  
                            "text": extracted_data["user_value_tiers"]["title"]  
                        }  
                    },  
                    "scales": {  
                        "y": {  
                            "beginAtZero": True,  
                            "max": 100,  
                            "title": {  
                                "display": True,  
                                "text": "百分比 (%)"  
                            }  
                        }  
                    }  
                }  
            })  
        
        # 转化漏斗图表  
        if extracted_data["conversion_funnel"]:  
            charts.append({  
                "id": "conversion_funnel_chart",  
                "type": "bar",  
                "data": {  
                    "labels": extracted_data["conversion_funnel"]["labels"],  
                    "datasets": [{  
                        "data": extracted_data["conversion_funnel"]["data"],  
                        "backgroundColor": "rgba(75, 192, 192, 0.7)",  
                        "borderColor": "rgba(75, 192, 192, 1)",  
                        "borderWidth": 1  
                    }]  
                },  
                "options": {  
                    "indexAxis": "y",  
                    "responsive": True,  
                    "plugins": {  
                        "title": {  
                            "display": True,  
                            "text": extracted_data["conversion_funnel"]["title"]  
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
                            "max": 100,  
                            "title": {  
                                "display": True,  
                                "text": "转化率 (%)"  
                            }  
                        }  
                    }  
                }  
            })  
        
        # 交易时间分布折线图  
        if extracted_data["time_patterns"]:  
            charts.append({  
                "id": "time_patterns_chart",  
                "type": "line",  
                "data": {  
                    "labels": extracted_data["time_patterns"]["labels"],  
                    "datasets": [{  
                        "label": "交易活跃度",  
                        "data": extracted_data["time_patterns"]["data"],  
                        "fill": True,  
                        "backgroundColor": "rgba(153, 102, 255, 0.2)",  
                        "borderColor": "rgba(153, 102, 255, 1)",  
                        "tension": 0.4  
                    }]  
                },  
                "options": {  
                    "responsive": True,  
                    "plugins": {  
                        "title": {  
                            "display": True,  
                            "text": extracted_data["time_patterns"]["title"]  
                        }  
                    },  
                    "scales": {  
                        "y": {  
                            "beginAtZero": True,  
                            "title": {  
                                "display": True,  
                                "text": "活跃度指数"  
                            }  
                        }  
                    }  
                }  
            })  
        
        return charts  
    
    def _generate_charts_summary(self, charts_config: List[Dict[str, Any]]) -> str:  
        """生成图表摘要信息"""  
        summary_lines = []  
        for chart in charts_config:  
            chart_type = chart["type"].capitalize()  
            chart_title = chart["options"]["plugins"]["title"]["text"]  
            summary_lines.append(f"- {chart_title} ({chart_type}图)")  
        
        return "\n".join(summary_lines)  