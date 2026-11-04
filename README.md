# 知学 Agent · V1.0.0

**把 AI 变成真正会教、能检测学习效果、能继续上次学习的中文学习教练。**

本项目是适用于 WorkBuddy、Codex 等支持 Agent Skills 的**独立开源 Skill**。普通用户使用现有宿主模型，不需要另装 DeepTutor、Docker、Python、Node.js，也不需要额外购买大模型 API。宿主平台自身的订阅或模型调用可能有费用。

> 注意：知学 Agent **不是 DeepTutor 本体**，不包含 HKUDS 原版 Mastery Path 或 RAG 引擎；只借鉴掌握导向的教学设计。原版 DeepTutor CLI 仅为可选高级连接。

## 一句话安装（推荐）

把下面内容复制给 WorkBuddy、Codex 等有 Skills 和文件权限的智能体：

> 请从 https://github.com/mindnature/study 安装最新版「知学 Agent」。阅读 SKILL.md 后仅安装 skills/zhixue-agent 目录到用户级 Skills 文件夹，不覆盖其他技能和学习数据。不要安装 Python、Docker、Node.js 或 DeepTutor，不索要 API Key，不执行远程安装脚本。安装后重载技能，报告实际启用的技能名称、版本和路径，再用一道数学题检验每轮只问一个问题。若没成功，请明确报告问题。

**或者：** [直接下载最新 Skill ZIP](https://github.com/mindnature/study/releases/latest) → 在 WorkBuddy 支持 ZIP 导入时导入，或交给智能体完成解压和安装。注意：**Code → Download ZIP** 是整个仓库，不是专用 Skill ZIP。

[详细安装与排错](INSTALL.md) · [技能入口](skills/zhixue-agent/SKILL.md) · [版本发布](https://github.com/mindnature/study/releases)

## 用法
- “知学 Agent，教我函数极限，一次只问一道题。”
- “根据我上传的讲义出三道题，每次先给我一道。”
- “这题我不会，先给我一点提示。”
- “不要再提示了，考考我是不是真的学会。”
- “帮我保存错题记录，下一次继续学习。”（首次需要授权本地文件位置）
- “直接告诉我答案。”（尊重用户选择）

## 功能边界

| 能力 | 当前提供方式 |
|---|---|
| 分级提示、一次一问、个性化错误诊断 | 宿主模型遵循 Skill 规则；仍需客户端实测 |
| 无提示独立测评、变式、延迟复测 | 证据式规则 + 可选本地学习记录 |
| 依据教材问答、生成练习 | 取决于宿主真实文件读取能力，不伪造引用 |
| 跨会话恢复学习历史 | 用户明确授权、且宿主具备文件读写权限时 |
| 自动提醒、云端同步、多学生后台 | 未包含 |
| DeepTutor 原版 Mastery Path | 未包含；若另装并配置 CLI，才可选连接 |

默认 **不保存历史**。用户第一次同意并选定本地工作区后，学习证据可以保存在 \`.zhixue/learning-records.json\`。支持文件工具的宿主直接读写；已有 Python 的宿主还可选用零依赖的脚本进行原子写入。**基础教学绝不依赖运行脚本。**

## 安全、可验证与分发

- 学习档案、教材及密钥不应提交到 GitHub；用户可以随时撤销文件写入授权。
- v1.0.0 包通过 Linux、Windows CI 自动测试后，由 GitHub Releases 发布永久 ZIP 并附 SHA256SUMS。
- 自动测试负责本地代码正确性、压缩包结构与脚本行为，**不证明 WorkBuddy/Codex 的每种模型都能按规则教学**；真实设备验收请见 [验收指南](examples/acceptance-tests.md)。
- 有关 V0.1/V0.2 升级，请见 [迁移与升级说明](docs/UPGRADING.md)。

## 开发者

~~~bash
python -m unittest discover -s tests -p 'test_*.py' -v
python scripts/build_release.py
python scripts/validate.py
~~~

以上命令仅供开发维护，普通用户**不需要**运行。原创 Skill 代码与文档使用 [MIT 许可](LICENSE)，第三方声明见 [THIRD_PARTY.md](THIRD_PARTY.md)。
