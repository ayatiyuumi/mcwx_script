from typing import List
from detectors.base import BaseDetector, DocumentContext, Flag

class DeclarationCheckDetector(BaseDetector):
    detector_name = "DeclarationCheckDetector"

    def should_run(self, ctx: DocumentContext) -> bool:
        return True

    def detect(self, ctx: DocumentContext) -> List[Flag]:
        flags = []
        meta = ctx.metadata
        coi = meta.get('coi_statement')
        params = self.config.get('detector_params', {}).get('DeclarationCheckDetector', {})
        weak_phrases = params.get('weak_coi_phrases', [
            'no conflict', 'no competing', 'none declared', 'declare no'
        ])

        # 利益冲突声明缺失
        if not coi:
            flags.append(Flag(
                risk_type="coi_missing",
                severity="orange",
                detail="未发现利益冲突声明",
                location="declarations",
                review_required=True,
                suggested_action="请作者补充利益冲突声明",
                detector=self.detector_name
            ))
        else:
            # 商业机构 + 声明为"无"
            affiliations = meta.get('affiliations', [])
            corp_kw = ['Corp', 'Inc', 'Ltd', 'LLC', 'Company', 'Technologies',
                       'Pharmaceutical', 'Biotech', 'Research Corporation']
            corps = [aff for aff in affiliations if any(k in aff for k in corp_kw)]
            if corps and any(p in coi.lower() for p in weak_phrases):
                flags.append(Flag(
                    risk_type="coi_contradiction",
                    severity="red",
                    detail=f"作者机构包含商业实体 {corps}，但利益冲突声明声称无冲突",
                    location="affiliations + declarations",
                    review_required=True,
                    suggested_action="需调查未公开的利益冲突",
                    detector=self.detector_name,
                    metadata={"commercial_entities": corps}
                ))

        # 基金声明缺失
        if not meta.get('funding_statement'):
            flags.append(Flag(
                risk_type="funding_missing",
                severity="yellow",
                detail="未发现基金资助声明",
                location="declarations",
                review_required=True,
                suggested_action="请作者补充基金信息",
                detector=self.detector_name
            ))

        return flags