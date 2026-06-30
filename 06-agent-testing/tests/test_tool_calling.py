"""
工具调用测试
测试各种工具的功能
"""

import pytest
from tools import Calculator, Search, Weather, get_tool


class TestCalculator:
    """计算器工具测试"""

    @pytest.mark.smoke
    def test_basic_calculation(self):
        """测试基本计算"""
        calc = Calculator()

        # 加法
        result = calc.execute("2 + 2")
        assert result["success"] is True
        assert result["result"] == 4

        # 乘法
        result = calc.execute("10 * 5")
        assert result["success"] is True
        assert result["result"] == 50

    def test_complex_calculation(self):
        """测试复杂计算"""
        calc = Calculator()

        # 带括号的表达式
        result = calc.execute("(10 + 20) * 3")
        assert result["success"] is True
        assert result["result"] == 90

        # 除法
        result = calc.execute("100 / 4")
        assert result["success"] is True
        assert result["result"] == 25

    def test_calculation_error(self):
        """测试计算错误"""
        calc = Calculator()

        # 除以零
        result = calc.execute("10 / 0")
        assert result["success"] is False
        assert "error" in result

    def test_invalid_expression(self):
        """测试无效表达式"""
        calc = Calculator()

        # 包含不允许的字符
        result = calc.execute("import os")
        assert result["success"] is False
        assert "不允许" in result["error"]

    def test_formatted_output(self):
        """测试格式化输出"""
        calc = Calculator()

        result = calc.execute("5 + 3")
        assert "formatted" in result
        assert "5 + 3 = 8" in result["formatted"]


class TestSearch:
    """搜索工具测试"""

    @pytest.mark.smoke
    def test_search_python(self):
        """测试搜索Python"""
        search = Search()

        result = search.execute("Python")
        assert result["success"] is True
        assert "Python" in result["result"]
        assert "编程语言" in result["result"]

    def test_search_java(self):
        """测试搜索Java"""
        search = Search()

        result = search.execute("Java")
        assert result["success"] is True
        assert "Java" in result["result"]

    def test_search_not_found(self):
        """测试搜索未找到"""
        search = Search()

        result = search.execute("未知的内容xyz123")
        assert result["success"] is True
        assert "未找到" in result["result"]

    def test_case_insensitive(self):
        """测试大小写不敏感"""
        search = Search()

        # 大写
        result1 = search.execute("PYTHON")
        # 小写
        result2 = search.execute("python")

        assert result1["result"] == result2["result"]


class TestWeather:
    """天气工具测试"""

    @pytest.mark.smoke
    def test_weather_beijing(self):
        """测试查询北京天气"""
        weather = Weather()

        result = weather.execute("北京")
        assert result["success"] is True
        assert result["city"] == "北京"
        assert "temperature" in result
        assert "condition" in result
        assert "humidity" in result

    def test_weather_multiple_cities(self):
        """测试查询多个城市"""
        weather = Weather()

        cities = ["北京", "上海", "深圳"]

        for city in cities:
            result = weather.execute(city)
            assert result["success"] is True
            assert result["city"] == city
            assert result["temperature"] > 0

    def test_weather_not_found(self):
        """测试查询不存在的城市"""
        weather = Weather()

        result = weather.execute("不存在的城市")
        assert result["success"] is False
        assert "error" in result

    def test_weather_formatted_output(self):
        """测试格式化输出"""
        weather = Weather()

        result = weather.execute("北京")
        assert "formatted" in result
        assert "北京" in result["formatted"]
        assert "天气" in result["formatted"]


class TestToolRegistry:
    """工具注册表测试"""

    def test_get_tool(self):
        """测试获取工具"""
        # 获取计算器
        calc = get_tool("calculator")
        assert isinstance(calc, Calculator)

        # 获取搜索
        search = get_tool("search")
        assert isinstance(search, Search)

        # 获取天气
        weather = get_tool("weather")
        assert isinstance(weather, Weather)

    def test_get_unknown_tool(self):
        """测试获取未知工具"""
        with pytest.raises(ValueError):
            get_tool("unknown_tool")


class TestToolIntegration:
    """工具集成测试"""

    def test_calculator_and_search(self):
        """测试计算器和搜索组合"""
        calc = Calculator()
        search = Search()

        # 先搜索
        search_result = search.execute("Python")
        assert search_result["success"] is True

        # 再计算
        calc_result = calc.execute("2024 - 1991")
        assert calc_result["success"] is True
        assert calc_result["result"] == 33

    def test_all_tools_available(self):
        """测试所有工具都可用"""
        tools = ["calculator", "search", "weather"]

        for tool_name in tools:
            tool = get_tool(tool_name)
            assert tool is not None
            assert hasattr(tool, "execute")


class TestToolParameters:
    """工具参数测试"""

    def test_calculator_parameters(self):
        """测试计算器参数"""
        calc = Calculator()

        assert calc.name == "calculator"
        assert "expression" in calc.parameters

    def test_search_parameters(self):
        """测试搜索参数"""
        search = Search()

        assert search.name == "search"
        assert "query" in search.parameters

    def test_weather_parameters(self):
        """测试天气工具参数"""
        weather = Weather()

        assert weather.name == "weather"
        assert "city" in weather.parameters
