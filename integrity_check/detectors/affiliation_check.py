from typing import List
from detectors.base import BaseDetector, DocumentContext, Flag

class AffiliationCheckDetector(BaseDetector):
    detector_name = "AffiliationCheckDetector"

    def should_run(self, ctx: DocumentContext) -> bool:
        return bool(ctx.metadata.get('affiliations'))

    def detect(self, ctx: DocumentContext) -> List[Flag]:
        flags = []
        affiliations = ctx.metadata.get('affiliations', [])
        params = self.config.get('detector_params', {}).get('AffiliationCheckDetector', {})
        corp_keywords = params.get('corp_keywords', [
            'Corp', 'Inc', 'Ltd', 'LLC', 'Company', 'Co.,',
            'Technologies', 'Pharmaceutical', 'Biotech', 'Biosciences',
            'Research Corporation'
        ])

        corps = [aff for aff in affiliations if any(k in aff for k in corp_keywords)]
        if corps:
            flags.append(Flag(
                risk_type="commercial_entity_in_affiliations",
                severity="orange",
                detail=f"发现商业机构: {'; '.join(corps)}",
                location="affiliations",
                review_required=True,
                suggested_action="请核实商业机构参与情况，并检查利益冲突声明",
                detector=self.detector_name,
                metadata={"commercial_entities": corps}
            ))
        return flags