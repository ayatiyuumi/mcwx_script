# 3.1 投稿元数据与身份完整性检查 — 脚本原型

## 项目定位

本模块是"科研诚信辅助审查系统"的 **3.1 投稿元数据与身份完整性检查** 方向的功能脚本原型。

**核心目标**：在送审前从论文 PDF 中自动提取元数据，识别作者身份、机构、声明、特刊等维度的风险信号，输出结构化风险卡片，辅助编辑判断。

**系统定位**：工具只负责发现可解释的红旗、组织证据、提示人工复核，不替代编辑、审稿人、机构调查和作者申辩。

## 目录结构
integrity_check/
├── pipeline.py # 主流水线入口
├── summary.py # 批量查看审计结果
├── config.yaml # 阈值、权重配置
├── README.md
├── extractor/
│ ├── pdf_extractor.py # PDF → 文本
│ └── metadata_extractor.py # 文本 → 投稿元数据
├── detectors/
│ ├── base.py # 检测器基类 + 数据结构
│ ├── author_consistency.py # 作者邮箱/ORCID/姓名一致性
│ ├── affiliation_check.py # 机构异常/商业公司痕迹
│ ├── declaration_check.py # 声明完整性（COI/基金）
│ ├── special_issue_check.py # 特刊/审稿周期异常
│ ├── corresponding_author.py # 通讯作者账户一致性（预留）
│ └── reviewer_check.py # 审稿人异常检查（预留）
├── risk_engine/ # 风险评分（对接仓库）
├── reporter/ # 报告生成（对接仓库）
├── data/
│ └── input/ # 待审计 PDF
└── output/ # 审计报告 JSON


## 环境要求

- Python >= 3.10
- pymupdf
- pyyaml

```bash
pip install pymupdf pyyaml

使用方法：

    单篇审计
    python pipeline.py data/input/论文.pdf

    批量审计
        将所有 PDF 放入 data/input/

        逐条运行 python pipeline.py data/input/xxx.pdf

        运行 python summary.py 查看汇总结果

已实现的检测器：
检测器	功能	状态
AuthorConsistencyDetector	邮箱域名/ORCID/姓名格式检查	    ✅ 已实现
AffiliationCheckDetector	商业机构检测	                ✅ 已实现
DeclarationCheckDetector	COI/基金声明完整性检查	        ✅ 已实现
SpecialIssueCheckDetector	特刊匹配/审稿周期检查	        ⚠️ 部分可用
CorrespondingAuthorDetector	通讯作者账户一致性	            ⬜ 预留接口
ReviewerCheckDetector	    审稿人异常检查	                ⬜ 预留接口

各检测器可检出的风险信号
    AuthorConsistencyDetector

        免费邮箱域名与机构域名不匹配（如@gmail.com vs 高校机构）

    ORCID 标识缺失

        作者姓名仅为首字母缩写，无法核验身份

    AffiliationCheckDetector

        作者机构列表中包含商业公司（如 Corp、Inc、Ltd 等）

    DeclarationCheckDetector

        利益冲突声明缺失

        商业机构存在但 COI 声明为"无"

        基金资助声明缺失

    SpecialIssueCheckDetector

        特刊名称与论文标题关键词重叠度过低

        审稿周期过短（< 30 天）

验证结果
    已用 10 篇真实撤稿案例 PDF 完成批量测试，结果如下：

        命中率：预期可检测的信号（邮箱不匹配、ORCID缺失、商业机构、COI矛盾等）均能命中

        风险分级：HIGH_RISK 0 篇 / MEDIUM_RISK 5 篇 / LOW_RISK 5 篇

        无报错：所有 PDF 均正常完成审计

当前局限性
    特刊名称提取：部分出版商（Hindawi/Wiley）PDF 正文中不含特刊信息（在页眉里），导致 SpecialIssueCheckDetector 无法触发。需接入 Crossref API 获取结构化元数据。

    投稿系统数据依赖：CorrespondingAuthorDetector 和 ReviewerCheckDetector 需投稿系统数据（账户信息、审稿人列表），当前原型无法验证，接口已预留。

    机构真实性核验：当前仅检测商业公司关键词，未接入 ROR/GRID 等机构数据库验证机构是否真实存在。

    语义匹配：特刊-论文主题匹配当前使用关键词重叠法，可升级为 sentence-transformers 语义相似度计算。

下一步计划
    接入 Crossref API 补充特刊/期刊元数据

    优化机构名称清洗逻辑（去除括号前缀等噪音）

    对接投稿系统数据实现全量检测

    评估接入轻量语义模型的可行性

案例数据
案例 PDF 数据集位于 `案例数据集/` 目录下。，包含 10 篇真实撤稿论文（均来自 PLOS ONE、Frontiers、Hindawi/Wiley 等开放获取期刊），覆盖 3.1 方向下全部六个核心功能维度。

