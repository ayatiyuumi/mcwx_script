import re
from datetime import datetime
from typing import List
from detectors.base import BaseDetector, DocumentContext, Flag

class SpecialIssueCheckDetector(BaseDetector):
    detector_name = "SpecialIssueCheckDetector"

    def should_run(self, ctx: DocumentContext) -> bool:
        return bool(ctx.metadata.get('special_issue') or
                    (ctx.metadata.get('date_received') and ctx.metadata.get('date_accepted')))

    def detect(self, ctx: DocumentContext) -> List[Flag]:
        flags = []
        meta = ctx.metadata
        params = self.config.get('detector_params', {}).get('SpecialIssueCheckDetector', {})
        min_overlap = params.get('min_keyword_overlap', 1)   # 降低阈值
        warn_days = params.get('review_period_warning_days', 30)

        special_issue = meta.get('special_issue')
        if special_issue:
            # 提取特刊关键词：字母长度>=4
            issue_words = set(w for w in re.findall(r'[a-zA-Z]{4,}', special_issue.lower()))
            # 取前10行作为标题区域
            title_text = '\n'.join(ctx.text.split('\n')[:10])
            title_words = set(w for w in re.findall(r'[a-zA-Z]{4,}', title_text.lower()))
            overlap = issue_words & title_words
            # 排除停用词
            stopwords = {
                'that','this','with','from','have','were','been','into','such','also',
                'than','them','then','only','other','over','each','about','after',
                'they','which','their','there','these','those','being','does','doing',
                'animal','animals','human','humans','study','studies','data','effect',
                'effects','results','conclusion','introduction','method','methods',
                'materials','model','models','using','based','analysis','role','impact',
                'review'
            }
            meaningful_overlap = overlap - stopwords
            if len(meaningful_overlap) < min_overlap:
                flags.append(Flag(
                    risk_type="special_issue_mismatch",
                    severity="orange",
                    detail=f"特刊“{special_issue[:80]}”与论文标题关键词重叠度低（有效重叠{len(meaningful_overlap)}个）",
                    location="special_issue_metadata",
                    review_required=True,
                    suggested_action="请确认论文是否符合该特刊征稿范围",
                    detector=self.detector_name,
                    metadata={
                        "overlap_count": len(meaningful_overlap),
                        "issue_words": list(issue_words)[:20],
                        "title_words": list(title_words)[:20]
                    }
                ))

        # 审稿周期
        rec = meta.get('date_received')
        acc = meta.get('date_accepted')
        if rec and acc:
            try:
                received = datetime.strptime(rec, '%d %B %Y')
                accepted = datetime.strptime(acc, '%d %B %Y')
                days = (accepted - received).days
                if 0 < days < warn_days:
                    flags.append(Flag(
                        risk_type="review_period_short",
                        severity="yellow",
                        detail=f"投稿到接收仅 {days} 天",
                        location="review_timeline",
                        review_required=True,
                        suggested_action="请检查快速审稿是否合理",
                        detector=self.detector_name,
                        metadata={"days": days}
                    ))
            except ValueError:
                pass

        return flags