"""
工具定义
提供Agent可以调用的工具
"""

from typing import Any, Dict


class BaseTool:
    """
    工具基类
    """
    def __init__(self, name: str, description: str, parameters: Dict[str, Any]):
        self.name = name
        self.description = description
        self.parameters = parameters

    def execute(self, **kwargs) -> Dict[str, Any]:
        """执行工具"""
        raise NotImplementedError


class Calculator(BaseTool):
    """
    计算器工具

    执行基础数学运算
    """

    def __init__(self):
        super().__init__(
            name="calculator",
            description="执行数学计算，支持加减乘除和基本运算",
            parameters={
                "expression": {
                    "type": "string",
                    "description": "数学表达式，如 '2+2' 或 '10*5'"
                }
            }
        )

    def execute(self, expression: str) -> Dict[str, Any]:
        """
        执行计算

        Args:
            expression: 数学表达式

        Returns:
            计算结果
        """
        try:
            # 安全评估（仅允许数学运算）
            allowed_chars = set("0123456789+-*/().,[] ")
            if not all(c in allowed_chars for c in expression):
                return {
                    "success": False,
                    "error": "表达式包含不允许的字符"
                }

            result = eval(expression)

            return {
                "success": True,
                "result": result,
                "formatted": f"{expression} = {result}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


class Search(BaseTool):
    """
    搜索工具

    模拟搜索功能（实际项目中应接入真实搜索API）
    """

    def __init__(self):
        super().__init__(
            name="search",
            description="搜索信息，查询知识",
            parameters={
                "query": {
                    "type": "string",
                    "description": "搜索查询词"
                }
            }
        )

        # 模拟知识库
        self.knowledge_base = {
            "python": "Python是一种高级编程语言，由Guido van Rossum于1991年发布。",
            "java": "Java是一种广泛使用的面向对象编程语言，由Sun Microsystems于1995年发布。",
            "javascript": "JavaScript是一种脚本语言，主要用于Web开发，由Brendan Eich于1995年创建。",
            "ai": "人工智能(AI)是计算机科学的一个分支，致力于创建能够执行通常需要人类智能的任务的系统。",
        }

    def execute(self, query: str) -> Dict[str, Any]:
        """
        执行搜索

        Args:
            query: 搜索查询

        Returns:
            搜索结果
        """
        query_lower = query.lower()

        # 简单匹配
        for key, value in self.knowledge_base.items():
            if key in query_lower:
                return {
                    "success": True,
                    "query": query,
                    "result": value
                }

        # 未找到
        return {
            "success": True,
            "query": query,
            "result": f"未找到关于'{query}'的信息"
        }


class Weather(BaseTool):
    """
    天气查询工具

    模拟天气查询（实际项目中应接入天气API）
    """

    def __init__(self):
        super().__init__(
            name="weather",
            description="查询城市天气信息",
            parameters={
                "city": {
                    "type": "string",
                    "description": "城市名称"
                }
            }
        )

        # 模拟天气数据
        self.weather_data = {
            "北京": {"temperature": 25, "condition": "晴天", "humidity": 60},
            "上海": {"temperature": 28, "condition": "多云", "humidity": 70},
            "深圳": {"temperature": 30, "condition": "雨天", "humidity": 85},
            "杭州": {"temperature": 27, "condition": "晴天", "humidity": 65},
        }

    def execute(self, city: str) -> Dict[str, Any]:
        """
        查询天气

        Args:
            city: 城市名称

        Returns:
            天气信息
        """
        if city in self.weather_data:
            data = self.weather_data[city]
            return {
                "success": True,
                "city": city,
                "temperature": data["temperature"],
                "condition": data["condition"],
                "humidity": data["humidity"],
                "formatted": f"{city}天气：{data['condition']}，温度{data['temperature']}°C，湿度{data['humidity']}%"
            }
        else:
            return {
                "success": False,
                "error": f"未找到城市'{city}'的天气数据"
            }


# 工具注册表
AVAILABLE_TOOLS = {
    "calculator": Calculator,
    "search": Search,
    "weather": Weather,
}


def get_tool(tool_name: str) -> BaseTool:
    """
    获取工具实例

    Args:
        tool_name: 工具名称

    Returns:
        工具实例
    """
    if tool_name not in AVAILABLE_TOOLS:
        raise ValueError(f"Unknown tool: {tool_name}")

    return AVAILABLE_TOOLS[tool_name]()
