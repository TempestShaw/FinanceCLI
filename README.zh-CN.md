<h1 align="center">Finance CLI</h1>

<p align="center">给你的 AI agent 配备金融研究工具，让每一步都有据可查。</p>

<p align="center">
  <a href="https://github.com/TempestShaw/FinanceCLI/blob/main/README.md" lang="en">English</a> | <strong>简体中文</strong>
</p>

<p align="center">
  <a href="https://tempestshaw.github.io/FinanceCLI/">网站</a> ·
  <a href="https://tempestshaw.github.io/FinanceCLI/ai/">AI 集成与 Skills</a> ·
  <a href="https://tempestshaw.github.io/FinanceCLI/quickstart/">快速开始</a> ·
  <a href="https://tempestshaw.github.io/FinanceCLI/research-examples/">研究案例</a>
</p>

<p align="center">
  <a href="https://pypi.org/project/finresearch-cli/"><img alt="PyPI：finresearch-cli" src="https://img.shields.io/badge/PyPI-finresearch--cli-blue"></a>
  <img alt="Python 3.10 或更高版本" src="https://img.shields.io/badge/Python-3.10%2B-3776AB">
  <a href="https://github.com/TempestShaw/FinanceCLI/blob/main/LICENSE"><img alt="Apache-2.0 许可证" src="https://img.shields.io/badge/license-Apache--2.0-111827"></a>
</p>

Finance CLI 为你的 agent 提供 SEC 文件检索、财务报表查询、文档读取和金融计算工具。用自然语言提出公司研究问题，再沿着来源与输入核对答案。你也可以在终端中直接运行所有命令。

## 从一个问题开始

[完成 CLI 和 skill 设置](https://tempestshaw.github.io/FinanceCLI/ai/)后，可以这样问你的 agent：

```text
用 Finance CLI 研究苹果公司最新的年度报告。说明它如何赚钱，以及
披露的三项风险。每项发现都要注明文件日期和来源。如果摘录被截断，
请继续获取证据，并明确报告缺失的数据或数据源错误。
```

你的 agent 选择命令并撰写解释，Finance CLI 提供披露文件证据和计算结果。你可以查阅引用的来源，核对 agent 的解读。

下面是一个可以直接复现的小例子：计算数值在三年内从 100 增长到 150 的年复合增长率。

```bash
finance formula.cagr start=100 end=150 periods=3 --output md
```

以下为 CLI 的实际输出，使用示例输入，不需要外部数据：

```text
**CAGR = 14.47%**

_Inputs_
| Field | Value |
| --- | --- |
| start | 100 |
| end | 150 |
| periods | 3 |

method: (end / start) ** (1 / periods) - 1
```

## 为什么使用 Finance CLI？

- **证据可以核对。** 文件查询在可用时保留来源 URL、申报编号等信息，缺失数据和数据源错误会明确呈现。
- **计算可以复现。** 公式命令返回输入与计算方法。保存易读的 Markdown 或结构化 JSON，便于重跑和检查研究步骤。
- **让 agent 自由选择研究路径。** 从寻找文件、阅读表格到计算指标，按问题组合小工具。研究不同公司时，可以复用这些步骤，减少重复编写数据获取脚本。

## 搭配你的 AI agent 使用

1. 用下方命令安装 CLI。你的 agent 需要能够访问安装了 `finance` 的终端环境。
2. [下载 skill](https://tempestshaw.github.io/FinanceCLI/skills/finance-cli-skills.zip)，按照 [skill 设置指南](https://tempestshaw.github.io/FinanceCLI/ai/#3-install-the-skill)将其添加到 agent 的本地 skills 目录。
3. 提出上面的研究问题。访问 SEC 前，请先按快速开始指南设置真实联系信息。

Skill 帮助 agent 选择工具并处理来源；只下载 skill 并不会安装 CLI。你需要自行提供能够执行本地命令的 agent 及其 AI 模型。Finance CLI 不包含托管聊天服务。

## 直接在终端使用

需要 Python 3.10 或更高版本。建议使用独立虚拟环境；[快速开始](https://tempestshaw.github.io/FinanceCLI/quickstart/)包含 macOS、Linux 和 Windows 的设置方法。

```bash
python -m pip install -U finresearch-cli
finance formula.cagr start=100 end=150 periods=3 --output md
```

读取年度报告前，请为 SEC 请求设置姓名和真实邮箱。在 macOS 或 Linux 上，将下方示例联系信息替换为你自己的：

```bash
export FINANCE_SEC_USER_AGENT="Your Name your.email@example.com"
finance filings.read AAPL section=business max_chars=4000 --output md
```

命令返回文件摘录。得出结论前，请检查日期、来源和截断信息。[快速开始](https://tempestshaw.github.io/FinanceCLI/quickstart/)也提供对应的 Windows 设置方法。

## 包含哪些能力？

| 研究任务 | 工具 |
| --- | --- |
| 查找和阅读公司披露 | SEC 文件、章节、XBRL 财务报表、文件中的报告表格 |
| 阅读研究文档 | 原生 PDF/HTML 文本、文本搜索、指定范围读取 |
| 补充公司与市场背景 | 报价、历史价格、基本面、公开电话会议记录、投资者关系演示文稿发现 |
| 检查假设与计算 | 金融公式、估值情景、DCF/NPV/IRR |

SEC 研究和基础计算不需要付费数据密钥。依赖外部数据源的结果受可用性和覆盖范围影响；分析师一致预期需要 FMP 密钥。详见[数据源说明](https://tempestshaw.github.io/FinanceCLI/data-sources/)。

按需安装高级能力：

```bash
python -m pip install -U "finresearch-cli[tables]"
python -m pip install -U "finresearch-cli[ocr]"
python -m pip install -U "finresearch-cli[backtest]"
```

以上分别添加 PDF 表格提取、OCR 和 VectorBT 回测。可合并为 `"finresearch-cli[tables,ocr,backtest]"`。OCR 首次运行可能下载模型。

## 深入使用与参与贡献

- [完整研究案例](https://tempestshaw.github.io/FinanceCLI/research-examples/)与[更多命令示例](https://github.com/TempestShaw/FinanceCLI/blob/main/EXAMPLES.md)。
- [命令参考](https://tempestshaw.github.io/FinanceCLI/commands/)、[输出格式](https://tempestshaw.github.io/FinanceCLI/agent-output-formats/)与 [shell 自动补全](https://github.com/TempestShaw/FinanceCLI/blob/main/EXAMPLES.md#shell-completion)。
- 集成开发入口：[Agent Guide](https://tempestshaw.github.io/FinanceCLI/agents/)、[llms.txt](https://tempestshaw.github.io/FinanceCLI/llms.txt) 和 [tools.json](https://tempestshaw.github.io/FinanceCLI/tools.json)。
- [报告问题或提出研究需求](https://github.com/TempestShaw/FinanceCLI/issues/new)。请附上命令和错误信息，移除凭据和私人文档。如果它帮助了你的研究，欢迎分享可复现的案例，或为仓库点一个 star。

中英文 README 使用相同结构与示例；修改设置或功能说明时，请同步更新两版。详细文档目前为英文。

## 信任与许可证

CLI 在本地运行，不收集使用遥测。API 凭据从环境变量读取。详见[信任说明](https://tempestshaw.github.io/FinanceCLI/trust/)和 [Apache-2.0 许可证](https://github.com/TempestShaw/FinanceCLI/blob/main/LICENSE)。

Finance CLI 用于研究与自动化，不提供投资建议或证券买卖推荐。
