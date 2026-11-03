# 知学 Agent（Study） · v0.2.0

**一个面向 WorkBuddy、Codex 等支持 Agent Skills 的中文学习教练。** 上传学习材料、逐题互动、分级提示、独立测评、复习建议；可选在用户授权后将学习证据保存到本地工作区，供下次继续学习。

> 本仓库是独立 Skill 项目，不是 HKUDS/DeepTutor 官方发行版。原生模式使用宿主现有模型，不内置 DeepTutor Mastery Path、专用 RAG 或独立模型。普通用户不必安装 Docker/Python/Node 或另买 API Key（宿主服务本身可能有用量限制或费用）。

## 最省事的使用方式

把下面这段话复制给有 Skill 安装权限的 WorkBuddy / Codex：

> 请从 https://github.com/mindnature/study 安装「知学 Agent」Skill。安装目录是 skills/zhixue-agent，不是整个仓库根目录。先审核 SKILL.md 和脚本，只安装 Skills 文件到你支持的本地技能目录，重新加载并确认激活。不要安装 Docker、Python 或 DeepTutor，不运行远程安装脚本，不索要 API Key。安装后说出真正启用的技能名称与安装路径，再用一道数学题测试“一次只问一个问题”的行为；不要用普通聊天冒充 Skill 加载成功。

然后可以直接说：“用知学 Agent 教我函数极限，先测我一道题，不要直接给答案。”

如果你的客户端支持 ZIP 导入：在 [GitHub Actions](https://github.com/mindnature/study/actions) 找到最新成功的 Validate Skill 运行，下载 artifact **zhixue-agent-skill-v0.2.0**（需要登录 GitHub），解压外层 artifact 后导入里面的 zhixue-agent-skill-v0.2.0.zip。技能 ZIP **根目录直接有 SKILL.md**。不支持 ZIP 导入的客户端可通过技能目录手动安装，具体位置以宿主实际文档为准。

## 改进点

| V0.2 变化 | 使用者看到的效果 |
|---|---|
| 一次一问与教学状态机 | 不一次丢出多道问题；回答后再决定下一步 |
| 错因识别与分级提示 | 理解不足、计算错误等采取不同引导 |
| 证据式掌握评价 | 区分提示后完成、独立完成、迁移与延迟复测 |
| 文件来源可信约束 | 仅依据实际读到的教材生成回答，不编造页码 |
| 可选本地学习档案 | 获得授权后保存真实作答证据；下次读取 |
| 自动化代码测试 | CI 验证档案读写、错误处理、ZIP 结构 |

## 学习档案：用户授权后才启用

默认**不自动保存学习历史**，不能仅凭安装 Skill 就跨会话记忆。当用户说“记住我的错题”，智能体应先询问是否允许在**用户自己选择的工作区**建立 .zhixue/learning-records.json。之后在有文件工具且得到持续授权时才可更新。

具备 Python 的宿主可选运行零依赖的 [learning_store.py](skills/zhixue-agent/scripts/learning_store.py) 进行原子写入、重复提交去重和掌握度证据摘要；**不具备 Python 仍可正常学习**，有文件工具时可按 [存储规范](skills/zhixue-agent/references/progress.md) 写入。没有权限或数据文件时必须明确告知“无法恢复”，不能假装已经记住。

## 开发者与验证

~~~bash
python -m unittest discover -s tests -p 'test_*.py' -v
python scripts/build_release.py
python scripts/validate.py
~~~

自动化测试只验证**本地脚本逻辑、静态结构和可安装 ZIP 结构**，不能证明不同模型都会遵循全部教学指令。真实教学交互需按 [验收场景](evals/scenarios.json) 在各个宿主客户端进行人工测试；WorkBuddy V0.1 已有安装反馈，V0.2 仍需重新验证。

项目结构：
- [Skill 入口](skills/zhixue-agent/SKILL.md)
- [教学规则](skills/zhixue-agent/references/teaching.md)
- [评价规则](skills/zhixue-agent/references/assessment.md)
- [教材规则](skills/zhixue-agent/references/materials.md)
- [学习档案规则](skills/zhixue-agent/references/progress.md)
- [可选 DeepTutor 连接](skills/zhixue-agent/references/deeptutor-engine.md)
- [V0.1 → V0.2 升级说明](docs/UPGRADING.md)
- [更新日志](CHANGELOG.md)

## 许可证与隐私

原创 Skill 文件与脚本采用 MIT License；见 [第三方说明](THIRD_PARTY.md)。不要把教材或学习记录上传到 GitHub。高级 DeepTutor CLI 只能在用户要求并完成独立安装、配置和真实验证后启用，不得把原生教学模式冒充官方引擎。