"""
pytest配置文件
"""

import pytest
import sys
from pathlib import Path

# 添加src目录到Python路径
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from retrieval_evaluator import RetrievalEvaluator, RetrievalBatchEvaluator
from models import RetrievedChunk, QAPair
