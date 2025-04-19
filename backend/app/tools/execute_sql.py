from crewai.tools import BaseTool  
from typing import Optional, List, Dict, Any  
from app.core.logger import logger  
import pandas as pd  
import json  
import re  

class ExecuteSQLTool(BaseTool):  
    name: str = "ExecuteSQL"  
    description: str = "执行SQL查询并返回结果，输入是SQL查询语句"  
    
    def _run(self, sql_query: str) -> str:  
        try:  
            # 保存原始查询用于错误报告  
            original_query = sql_query  
            
            # 预处理SQL查询  
            sql_query = self._preprocess_sql(sql_query)  
            
            # 使用同步版本的SQL查询函数  
            from app.db.crud import sync_execute_custom_query  
            
            try:  
                # 执行查询  
                results = sync_execute_custom_query(sql_query)  
                
                # 处理结果  
                if not results:  
                    return "查询执行成功，但没有返回任何结果。"  
                
                import pandas as pd  
                df = pd.DataFrame(results)  
                
                # 格式化输出  
                if len(df) > 10:  
                    preview = df.head(10).to_markdown()  
                    stats = df.describe().to_markdown()  
                    return f"查询结果（前10行）:\n{preview}\n\n统计摘要:\n{stats}\n\n共返回{len(df)}行数据。"  
                else:  
                    return f"查询结果:\n{df.to_markdown()}\n\n共返回{len(df)}行数据。"  
            except Exception as db_error:  
                # 数据库错误单独捕获，确保返回明确的错误信息   
                error_msg = f"数据库查询错误: {str(db_error)}\n原始查询: {original_query}\n处理后查询: {sql_query}"  
                logger.error(f"数据库查询错误: {str(db_error)}")  
                return error_msg  
                    
        except Exception as e:  
            error_msg = f"执行SQL查询时出错: {str(e)}"  
            logger.error(error_msg)  
            return error_msg  # 返回具体错误信息而非默认响应  
    
    def _preprocess_sql(self, sql_query: str) -> str:  
        """预处理SQL查询，检查和修复常见问题"""  
        # 去除多余空格和结尾的分号  
        sql_query = sql_query.strip()  
        if sql_query.endswith(';'):  
            sql_query = sql_query[:-1]  
        
        # 检查是否包含'table'占位符  
        if " table " in sql_query.lower() or "from table" in sql_query.lower():  
            # 替换为实际表名  
            sql_query = sql_query.replace(" table ", " users ")  
            sql_query = sql_query.replace("FROM table", "FROM users")  
            sql_query = sql_query.replace("from table", "from users")  
        
        # 修复常见的表和列名错误  
        sql_query = self._fix_column_names(sql_query)  
        
        # 确保查询是SELECT语句  
        if not sql_query.lower().startswith('select'):  
            sql_query = "SELECT * FROM users LIMIT 10"  
            return sql_query  
        
        # 智能添加LIMIT子句  
        sql_query = self._add_limit_clause(sql_query)  
        
        # 返回处理后的SQL  
        return sql_query  
    
    def _fix_column_names(self, sql_query: str) -> str:  
        """修复SQL查询中的列名错误"""  
        # 基本列名修复  
        sql_query = sql_query.replace("t.product_type", "p.product_name")  
        sql_query = sql_query.replace("t.id", "t.transaction_id")  
        sql_query = sql_query.replace("u.id", "u.user_id")   
        sql_query = sql_query.replace("u.username", "u.name")  
        sql_query = sql_query.replace("p.id", "p.product_id")  
        
        # 修复user_profiles表中不存在的列  
        # registration_date -> created_at (从users表获取)  
        if "up.registration_date" in sql_query:  
            sql_query = sql_query.replace("up.registration_date", "u.created_at")  
        
        # location (不存在，移除或替换为其他相关字段)  
        if "up.location" in sql_query:  
            # 如果是SELECT中的字段，替换为常量  
            sql_query = re.sub(r"SELECT\s+(.*)up\.location(.*?)FROM",   
                              r"SELECT \1'未知地区' AS location\2FROM",   
                              sql_query,   
                              flags=re.IGNORECASE | re.DOTALL)  
            
            # 如果是WHERE子句中的条件，移除该条件  
            sql_query = re.sub(r"WHERE\s+(.*?)(?:AND\s+)?up\.location\s*=\s*['\"](.*?)['\"](.*?)",   
                              r"WHERE \1\3",   
                              sql_query,   
                              flags=re.IGNORECASE | re.DOTALL)  
        
        # age_group (替换为基于users.age的计算字段)  
        if "up.age_group" in sql_query:  
            # 如果是SELECT中的字段，用CASE表达式替换  
            age_group_replacement = """  
            CASE   
                WHEN u.age < 25 THEN '年轻群体'   
                WHEN u.age BETWEEN 25 AND 35 THEN '青年群体'   
                WHEN u.age BETWEEN 36 AND 50 THEN '中年群体'   
                ELSE '老年群体'   
            END AS age_group"""  
            
            sql_query = re.sub(r"SELECT\s+(.*)up\.age_group(.*?)FROM",   
                             fr"SELECT \1{age_group_replacement}\2FROM",   
                             sql_query,   
                             flags=re.IGNORECASE | re.DOTALL)  
            
            # 如果是WHERE或GROUP BY中使用，也进行替换  
            sql_query = re.sub(r"GROUP\s+BY\s+(.*)up\.age_group(.*?)",   
                             fr"GROUP BY \1{age_group_replacement}\2",   
                             sql_query,   
                             flags=re.IGNORECASE | re.DOTALL)  
            
            # WHERE子句中的条件，使用对应的age范围替代  
            sql_query = re.sub(r"WHERE\s+(.*?)(?:AND\s+)?up\.age_group\s*=\s*['\"]年轻群体['\"](.*)$",   
                             r"WHERE \1 AND u.age < 25 \2",   
                             sql_query,   
                             flags=re.IGNORECASE | re.DOTALL)  
            
            sql_query = re.sub(r"WHERE\s+(.*?)(?:AND\s+)?up\.age_group\s*=\s*['\"]青年群体['\"](.*)$",   
                             r"WHERE \1 AND u.age BETWEEN 25 AND 35 \2",   
                             sql_query,   
                             flags=re.IGNORECASE | re.DOTALL)  
        
        # 可以根据需要添加更多的列名修复规则  
        
        return sql_query  
    
    def _add_limit_clause(self, sql_query: str) -> str:  
        """智能添加LIMIT子句到SQL查询"""  
        # 检查是否已有LIMIT  
        has_limit = bool(re.search(r'\bLIMIT\s+\d+\b', sql_query, re.IGNORECASE))  
        
        if not has_limit:  
            # 检查查询的基本结构  
            has_group_by = bool(re.search(r'\bGROUP\s+BY\b', sql_query, re.IGNORECASE))  
            has_order_by = bool(re.search(r'\bORDER\s+BY\b', sql_query, re.IGNORECASE))  
            has_having = bool(re.search(r'\bHAVING\b', sql_query, re.IGNORECASE))  
            
            # 对于包含GROUP BY的查询，确保LIMIT被正确添加  
            if has_group_by:  
                if has_having:  
                    # 如果有HAVING，在HAVING子句后面添加LIMIT  
                    having_pattern = r'(HAVING\s+.*?)(?:\s*$|\s+LIMIT\s+\d+)'  
                    having_match = re.search(having_pattern, sql_query, re.IGNORECASE)  
                    if having_match:  
                        having_part = having_match.group(1)  
                        sql_query = re.sub(having_pattern, f"{having_part} LIMIT 100", sql_query, flags=re.IGNORECASE)  
                    else:  
                        # 如果没有匹配到HAVING模式，添加到末尾  
                        sql_query += " LIMIT 100"  
                elif has_order_by:  
                    # 如果有ORDER BY，在ORDER BY子句后面添加LIMIT  
                    order_pattern = r'(ORDER\s+BY\s+.*?)(?:\s*$|\s+LIMIT\s+\d+)'  
                    order_match = re.search(order_pattern, sql_query, re.IGNORECASE)  
                    if order_match:  
                        order_part = order_match.group(1)  
                        sql_query = re.sub(order_pattern, f"{order_part} LIMIT 100", sql_query, flags=re.IGNORECASE)  
                    else:  
                        # 如果没有匹配到ORDER BY模式，添加到末尾  
                        sql_query += " LIMIT 100"  
                else:  
                    # GROUP BY后直接添加LIMIT  
                    group_pattern = r'(GROUP\s+BY\s+.*?)(?:\s*$|\s+LIMIT\s+\d+)'  
                    group_match = re.search(group_pattern, sql_query, re.IGNORECASE)  
                    if group_match:  
                        group_part = group_match.group(1)  
                        sql_query = re.sub(group_pattern, f"{group_part} LIMIT 100", sql_query, flags=re.IGNORECASE)  
                    else:  
                        # 如果没有匹配到GROUP BY模式，添加到末尾  
                        sql_query += " LIMIT 100"  
            elif has_order_by:  
                # 如果有ORDER BY但没有GROUP BY  
                order_pattern = r'(ORDER\s+BY\s+.*?)(?:\s*$|\s+LIMIT\s+\d+)'  
                order_match = re.search(order_pattern, sql_query, re.IGNORECASE)  
                if order_match:  
                    order_part = order_match.group(1)  
                    sql_query = re.sub(order_pattern, f"{order_part} LIMIT 100", sql_query, flags=re.IGNORECASE)  
                else:  
                    # 如果没有匹配到ORDER BY模式，添加到末尾  
                    sql_query += " LIMIT 100"  
            else:  
                # 简单查询，直接在末尾添加LIMIT  
                sql_query += " LIMIT 100"  
                
        return sql_query  
    
    def _provide_default_response(self) -> str:  
        """提供默认响应，当SQL查询失败时"""  
        return """  
        无法执行SQL查询，可能的原因：  
        1. 表名不正确  
        2. SQL语法错误  
        3. 查询包含不支持的操作  
        
        可用的表结构：  
        
        ### users表  
        - user_id: 用户ID (int)  
        - name: 用户名 (varchar)  
        - age: 年龄 (int)  
        - account_balance: 账户余额 (decimal)  
        - deposit_amount: 存款金额 (decimal)  
        - withdrawal_amount: 提取金额 (decimal)  
        - investment_risk_tolerance: 投资风险承受能力 (enum: 'low','moderate','high')  
        - investment_horizon: 投资周期 (varchar)  
        - monthly_income: 月收入 (decimal)  
        - monthly_expenses: 月支出 (decimal)  
        - created_at: 创建时间 (datetime)  
        
        ### transactions表  
        - transaction_id: 交易ID (int)  
        - user_id: 用户ID (int)  
        - transaction_type: 交易类型 (enum: 'buy','sell')  
        - amount: 交易金额 (decimal)  
        - transaction_date: 交易日期 (datetime)  
        - price_per_ounce: 每盎司价格 (decimal)  

        ### products表  
        - product_id: 产品ID (int)  
        - product_name: 产品名称 (varchar)  
        - price_per_ounce: 每盎司价格 (decimal)  
        - created_at: 创建时间 (datetime)  

        ### user_profiles表  
        - profile_id: 档案ID (int)  
        - user_id: 用户ID (int)  
        - risk_profile: 风险偏好 (enum: 'conservative','balanced','aggressive')  
        注意: user_profiles表没有registration_date、location、age_group等字段  

        ### marketing_campaigns表  
        - campaign_id: 活动ID (int)  
        - title: 活动标题 (varchar)  
        - description: 活动描述 (text)  
        - status: 活动状态 (enum: 'IN_PROGRESS','NOT_STARTED','EXPIRED')  
        - start_date: 开始日期 (datetime)  
        - end_date: 结束日期 (datetime)  
        
        ### 示例有效查询  
        SELECT * FROM users WHERE investment_risk_tolerance = 'high' LIMIT 10;  
        SELECT t.transaction_id, t.user_id, t.amount FROM transactions t JOIN users u ON t.user_id = u.user_id LIMIT 10;  
        
        SELECT   
            u.user_id,   
            u.name,   
            up.risk_profile,  
            COUNT(t.transaction_id) AS transaction_count   
        FROM   
            users u   
        LEFT JOIN  
            user_profiles up ON u.user_id = up.user_id  
        LEFT JOIN   
            transactions t ON u.user_id = t.user_id   
        GROUP BY   
            u.user_id, u.name, up.risk_profile   
        LIMIT 10;  
        """  