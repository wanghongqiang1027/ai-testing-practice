"""
pytest配置文件
"""

import pytest
import sys
from pathlib import Path

# 添加src和tools目录到Python路径
src_path = Path(__file__).parent.parent / "src"
tools_path = Path(__file__).parent.parent / "tools"
sys.path.insert(0, str(src_path))
sys.path.insert(0, str(tools_path))

from models import Tool, ToolCall, AgentTestCase
from tools import Calculator, Search, Weather
