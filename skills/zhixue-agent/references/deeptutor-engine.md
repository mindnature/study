# DeepTutor 原版引擎：可选连接指南

当前 Skill **不附带、不部署 DeepTutor**。它是一个宿主模型可立即执行的学习方法 Skill；只有当用户明确要求原版能力、具备终端权限且已有可运行 CLI 时，才尝试本指南。

官方项目：https://github.com/HKUDS/DeepTutor
官方 SKILL.md：https://github.com/HKUDS/DeepTutor/blob/v1.7.1/SKILL.md
CLI 文档：https://docs.deeptutor.info/cli/commands/
Agent 安装指南：https://github.com/HKUDS/DeepTutor/blob/v1.7.1/docs-for-dev/AGENT_SETUP.md

## 离线检查（不会发起计费请求）

先检查 `deeptutor` 是否在 PATH 中，执行 `deeptutor --help`、`deeptutor module list`、`deeptutor doctor --format json`。`doctor --online` 会产生真实模型请求，必须提前取得用户同意。仅凭文件存在或 `doctor` 本地通过，不能宣称模型已经实测可用。

本包提供纯 Python 标准库封装：

```bash
python scripts/deeptutor_bridge.py --check
```

安装位置取决于具体宿主；若无法找到脚本，直接使用等价的 CLI 命令即可。不需要 Python 来运行原生教学模式。

## 已安装且已配置时，调用真实模块

根据 `deeptutor module list` / `deeptutor plugin list` 的实际结果选择能力，不能假定全部模块存在：

```bash
# 单次解题，NDJSON 流
 deeptutor run deep_solve "求导数：sin(x^2)" --language zh --format json

# 生成题目（需要 questions 模块）
 deeptutor run deep_question "一元函数导数" --config num_questions=3 --language zh --format json

# 教材知识库（需要知识库模块和 Embedding）
 deeptutor kb create math --doc textbook.pdf
 deeptutor run chat "解释链式法则" --kb math --language zh --format json
```

命令前的空格仅用于文档排版；实际使用请去掉。CLI 的成功返回还需要检查输出的真实事件、错误及完成状态。默认不把 DeepTutor 的内部思维/工具事件全部暴露给终端用户。

### 使用本包封装器

```bash
python scripts/deeptutor_bridge.py --run deep_solve --message "求导数：sin(x^2)"
python scripts/deeptutor_bridge.py --run deep_question --message "一元函数导数" --num-questions 3
```

该脚本不会自动安装任何依赖，也不会创建知识库；若执行成功，会将 CLI 的 NDJSON 事件按原样输出。仅在用户明确同意调用现有 DeepTutor 模型服务时执行 `--run`，因为其背后可能产生 API 费用。

## 出错与安装

- `not found`：表明 CLI 不存在；不要默默退化后仍称“原版已运行”。
- 核心模块存在但 `deep_question` 缺失：需额外安装对应模块；遵循官方模块依赖和准确版本。
- API Key / 模型不可用：请用户在其机器上选择凭证来源，不在聊天中粘贴密钥。
- 没有 Embedding 时，资料问答可用宿主直接读取文件代替；不能称为 DeepTutor RAG。
- 如果用户请求首次自动安装：先审查官方 Agent Setup 和用户机器环境，提出计划，取得批准，再执行；无需 Docker 但 Python 和模型服务通常仍是必要条件。