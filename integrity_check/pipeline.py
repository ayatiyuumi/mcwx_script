"""
Stat Integrity Checker — 主流水线（3.1 模块验证版）
"""
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional

from detectors.base import DocumentContext


def load_config(config_path: str = "config.yaml") -> dict:
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def run_pipeline(filepath: str, config: dict, domain: Optional[str] = None) -> Dict[str, Any]:
    # 1. 提取层
    from extractor.pdf_extractor import parse_pdf
    context: DocumentContext = parse_pdf(filepath)

    # 2. 初始化 3.1 检测器（只跑我们自己的）
    from detectors.author_consistency import AuthorConsistencyDetector
    from detectors.affiliation_check import AffiliationCheckDetector
    from detectors.declaration_check import DeclarationCheckDetector
    from detectors.special_issue_check import SpecialIssueCheckDetector

    detectors = [
        AuthorConsistencyDetector(config),
        AffiliationCheckDetector(config),
        DeclarationCheckDetector(config),
        SpecialIssueCheckDetector(config),
    ]

    all_flags = []
    for det in detectors:
        if det.should_run(context):
            try:
                flags = det.detect(context)
                all_flags.extend(flags)
            except Exception as e:
                print(f"[警告] {det.detector_name} 运行失败: {e}")

    # 3. 风险评分（若 scorer 不可用，给一个简单汇总）
    try:
        from risk_engine.scorer import RiskScorer
        scorer = RiskScorer(config)
        risk_assessment = scorer.score(all_flags)
    except Exception:
        # 简易评分
        red = sum(1 for f in all_flags if f.severity == 'red')
        orange = sum(1 for f in all_flags if f.severity == 'orange')
        yellow = sum(1 for f in all_flags if f.severity == 'yellow')
        total = red * 10 + orange * 5 + yellow * 2
        level = 'LOW_RISK'
        if total >= 15 or (red >= 1 and total >= 5):
            level = 'HIGH_RISK'
        elif total >= 6:
            level = 'MEDIUM_RISK'
        risk_assessment = {
            'total_score': total,
            'risk_level': level,
            'red_count': red,
            'orange_count': orange,
            'yellow_count': yellow
        }

    # 4. 组装报告
    report = {
        "module": "metadata_integrity_check",
        "source_file": Path(filepath).name,
        "timestamp": None,
        "risk_assessment": risk_assessment,
        "flags": [
            {
                "detector": f.detector,
                "risk_type": f.risk_type,
                "severity": f.severity,
                "evidence": f.detail,
                "location": f.location,
                "review_required": f.review_required,
                "suggested_action": f.suggested_action,
                "metadata": f.metadata
            }
            for f in all_flags
        ],
        "summary": {
            "total_flags": len(all_flags)
        }
    }
    return report


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("用法: python pipeline.py <文件路径>")
        sys.exit(1)

    filepath = sys.argv[1]
    config = load_config()
    report = run_pipeline(filepath, config)

    out_dir = Path("output")
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / (Path(filepath).stem + "_audit.json")
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')

    ra = report['risk_assessment']
    print(f"\n审计完成: {Path(filepath).name}")
    print(f"风险等级: {ra.get('risk_level', 'N/A')} (总分 {ra.get('total_score', 0)})")
    print(f"标记总数: {len(report['flags'])}")
    print(f"报告已保存: {out_path}")