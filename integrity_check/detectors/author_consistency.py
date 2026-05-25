import re
from typing import List
from detectors.base import BaseDetector, DocumentContext, Flag


class AuthorConsistencyDetector(BaseDetector):
    detector_name = "AuthorConsistencyDetector"

    def should_run(self, ctx: DocumentContext) -> bool:
        return bool(ctx.metadata)

    def detect(self, ctx: DocumentContext) -> List[Flag]:
        flags = []
        meta = ctx.metadata
        emails = meta.get('emails', [])
        affiliations = meta.get('affiliations', [])

        params = self.config.get('detector_params', {}).get('AuthorConsistencyDetector', {})
        free_domains = set(params.get('free_email_domains', [
            'gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com',
            '163.com', 'qq.com', '126.com', 'sina.com'
        ]))

        inst_domains = set()
        for aff in affiliations:
            m = re.search(r'@?([\w-]+\.[a-zA-Z]{2,})', aff)
            if m:
                inst_domains.add(m.group(1).lower())

        for email in emails:
            dom = email.split('@')[-1].lower()
            if dom in free_domains and inst_domains:
                flags.append(Flag(
                    risk_type="free_email_mismatch",
                    severity="yellow",
                    detail=f"免费邮箱域名 '{dom}' 与机构域名不匹配",
                    location="author_metadata",
                    review_required=True,
                    suggested_action="请核实作者身份是否与声称机构一致",
                    detector=self.detector_name,
                    metadata={"email": email, "domain": dom}
                ))

        if not meta.get('orcid'):
            flags.append(Flag(
                risk_type="orcid_missing",
                severity="yellow",
                detail="未发现 ORCID 标识",
                location="author_metadata",
                review_required=True,
                suggested_action="请作者提供 ORCID",
                detector=self.detector_name
            ))

        for name in meta.get('author_names', []):
            parts = name.split()
            if len(parts) >= 2 and len(parts[0]) <= 2 and parts[0].endswith('.'):
                flags.append(Flag(
                    risk_type="abbreviated_author_name",
                    severity="yellow",
                    detail=f"作者姓名仅为首字母缩写: {name}",
                    location="author_metadata",
                    review_required=True,
                    suggested_action="请作者提供完整姓名以便身份核验",
                    detector=self.detector_name
                ))
                break

        return flags