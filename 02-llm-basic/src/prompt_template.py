"""
Prompt 模板管理
加载和渲染 Prompt 模板
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from models import PromptTemplate


class PromptManager:
    """
    Prompt 模板管理器

    Example:
        manager = PromptManager("prompts/system_prompts.yaml")
        template = manager.get_template("customer_service")
        prompt = template.render(company="ABC", product="手机")
    """

    def __init__(self, config_file: str):
        """
        初始化管理器

        Args:
            config_file: YAML配置文件路径
        """
        self.config_file = Path(config_file)
        self.templates: Dict[str, PromptTemplate] = {}
        self._load_templates()

    def _load_templates(self):
        """从YAML文件加载模板"""
        if not self.config_file.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_file}")

        with open(self.config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        for name, data in config.items():
            self.templates[name] = PromptTemplate(
                name=name,
                system_prompt=data.get("system_prompt", ""),
                variables=data.get("variables", []),
                temperature=data.get("temperature", 0.7),
                max_tokens=data.get("max_tokens")
            )

    def get_template(self, name: str) -> Optional[PromptTemplate]:
        """
        获取模板

        Args:
            name: 模板名称

        Returns:
            PromptTemplate对象，如果不存在返回None
        """
        return self.templates.get(name)

    def list_templates(self) -> list[str]:
        """列出所有模板名称"""
        return list(self.templates.keys())

    def render(self, template_name: str, **kwargs) -> str:
        """
        渲染模板

        Args:
            template_name: 模板名称
            **kwargs: 模板变量

        Returns:
            渲染后的文本
        """
        template = self.get_template(template_name)
        if not template:
            raise ValueError(f"Template not found: {template_name}")

        return template.render(**kwargs)
