from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class Flag:
    """标准风险标记（与仓库原格式 + 3.1 模块均兼容）"""
    risk_type: str
    severity: str                # 'red', 'orange', 'yellow'
    detail: str                  # 人类可读的证据说明（原仓库 target/detail 均接受）
    location: str
    review_required: bool
    suggested_action: str
    detector: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DocumentContext:
    """跨层数据总线"""
    text: str = ""
    tables: List[List] = field(default_factory=list)
    inline_stats: List = field(default_factory=list)
    figure_data: List[Dict] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def has_tables(self) -> bool:
        return any(len(t) > 0 for t in self.tables)

    def has_inline_stats(self) -> bool:
        return len(self.inline_stats) > 0

    def has_figures(self) -> bool:
        return len(self.figure_data) > 0


class BaseDetector(ABC):
    """所有检测器的基类"""

    def __init__(self, config: dict):
        self.config = config
        self.detector_name = self.__class__.__name__

    @abstractmethod
    def detect(self, context: DocumentContext) -> List[Flag]:
        ...

    def should_run(self, context: DocumentContext) -> bool:
        return True