import re
from typing import Dict, Any


def extract_metadata(text: str) -> Dict[str, Any]:
    meta = {}

    # 邮箱
    emails = re.findall(r'[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}', text)
    meta['emails'] = emails

    # ORCID
    orcid = re.search(r'\d{4}-\d{4}-\d{4}-\d{3}[\dX]', text)
    meta['orcid'] = orcid.group(0) if orcid else None

    # 机构
    inst_lines = []
    for line in text.split('\n'):
        if any(k in line for k in ['University', 'Institute', 'College', 'Hospital',
                                   'Center', 'Laboratory', 'School', 'Department']):
            inst_lines.append(line.strip())
    meta['affiliations'] = list(set(inst_lines))

    # 通讯作者邮箱
    corr = re.search(r'Correspondence[:\s]*([\w.+-]+@[\w-]+\.\w+)', text)
    meta['corresponding_email'] = corr.group(1) if corr else None

    # 利益冲突声明
    coi = re.search(
        r'(Conflict[s]? of Interest|Competing Interests)[:\s]*(.*?)(?=\n\n|\n[A-Z])',
        text, re.DOTALL | re.IGNORECASE
    )
    meta['coi_statement'] = coi.group(2).strip()[:500] if coi else None

    # 基金声明
    fund = re.search(
        r'(Funding|Acknowledgments?)[:\s]*(.*?)(?=\n\n|\n[A-Z])',
        text, re.DOTALL | re.IGNORECASE
    )
    meta['funding_statement'] = fund.group(2).strip()[:500] if fund else None

    # 作者姓名
    first_lines = '\n'.join(text.split('\n')[:30])
    authors = re.findall(r'([A-Z][a-z]+(?:\s+[A-Z]\.)*\s+[A-Z][a-z]+)', first_lines)
    meta['author_names'] = list(set(authors))[:20]

    # 投稿/接收日期
    rec = re.search(r'Received[:\s]*(\d{1,2}\s+\w+\s+\d{4})', text)
    if rec:
        meta['date_received'] = rec.group(1)
    acc = re.search(r'Accepted[:\s]*(\d{1,2}\s+\w+\s+\d{4})', text)
    if acc:
        meta['date_accepted'] = acc.group(1)

    # ===== 增强的特刊提取 =====
    si_text = None
    patterns = [
        r'This article is part of (?:the )?Special Issue[:\s]*([^\n]+)',
        r'Part of (?:the )?Special Issue[:\s]*([^\n]+)',
        r'Special Issue[:\s]*([^\n]+)',
        r'This article belongs to the Special Issue[:\s]*([^\n]+)',
    ]
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            si_text = m.group(1).strip()
            # 清理尾部标点或多余空格
            si_text = re.sub(r'[.,;:]+$', '', si_text).strip()
            break
    meta['special_issue'] = si_text

    # 学术编辑
    ed = re.search(r'Academic Editor[:\s]*([^\n]+)', text)
    meta['academic_editor'] = ed.group(1).strip() if ed else None

    return meta