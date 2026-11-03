# 知学 Agent Skill（Study）

让 WorkBuddy、Codex 等支持 Agent Skills 的智能体直接充当中文学习教练：先诊断、再引导、逐题练习、独立测评、复习计划。

> V0.1.0 是原生教学 Skill 样包，不是 DeepTutor 官方产品。默认不包含 DeepTutor 引擎，不需要 Docker/Python/API Key（宿主模型的使用规则仍然适用）。

## 普通人最省事的安装方式

复制以下指令发给有文件操作权限的 WorkBuddy 或其他智能体：

> 请从 https://github.com/mindnature/study 安装「知学 Agent」Skill。先阅读仓库的 SKILL.md 和 README.md，检查安全性。优先把 skills/zhixue-agent 目录安装到你的 Skills 目录，重新加载并确认启用。不要安装 Docker、Python 或 DeepTutor，不要运行远程脚本，不要索要 API Key。安装后用一道导数诊断题验证五步学习流程，并说明真实启用状态。如果当前客户端不能安装 Skill，请明确说明，不要假装成功。

安装完成后说：“使用知学 Agent 教我函数极限，先诊断，不要直接给答案。”

不支持从 GitHub 自动安装的客户端，可使用 [技能目录](skills/zhixue-agent/) 手动导入；CI 会构建 **Skill ZIP**，可在 [Actions](https://github.com/mindnature/study/actions) 的成功运行记录中下载构建产物。ZIP 文件的 `SKILL.md` 位于压缩包根目录；GitHub 仓库整体下载的 ZIP 不等于 Skill ZIP。

## 功能与边界

| 能力 | 默认原生模式 |
|---|---|
| 先测基础、分级提示（H1/H2/H3）、逐题练习 | 支持 |
| 无提示独立测评、变式迁移与复习建议 | 支持，基于宿主模型 |
| 上传资料问答 | 取决于宿主是否能读取文件，不声称原版 RAG |
| 自动保存学习进度 | 仅用户同意且宿主有文件写入权限时 |
| DeepTutor Mastery Path / CLI | **不包含**。有独立安装并配置的原版 CLI 后才可选接入 |

## 开发者入口

- [完整 Skill](skills/zhixue-agent/SKILL.md)
- [学习记录约定](skills/zhixue-agent/references/progress.md)
- [DeepTutor 可选接口](skills/zhixue-agent/references/deeptutor-engine.md)
- [本地静态校验](scripts/validate.py)
- [Skill ZIP 构建](scripts/build_release.py)
- [验收场景](examples/acceptance-tests.md)
- [第三方声明](THIRD_PARTY.md)

开发者可运行 `python scripts/build_release.py && python scripts/validate.py`。普通用户不需要执行。

## 许可与免责声明

原创 Skill 文档和辅助脚本采用 MIT License。借鉴 DeepTutor 的教学设计理念，但不包含其源码、不代表 HKUDS 官方出品。初版尚未在所有 WorkBuddy 版本上完成真实安装验证；不得将正常触发提示词误认为已接入 DeepTutor 引擎。
