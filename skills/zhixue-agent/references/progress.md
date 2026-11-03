# 跨会话学习档案（V0.2）

## 保存前必须授权
默认只在当前对话内维护学习状态。用户首次要求“记住错题 / 保存学习记录 / 继续追踪”时，应先说明存储内容，并让用户选择**本地工作区**。得到明确同意后，在该工作区的 .zhixue/learning-records.json 中记录最少必要学习证据；以后只在相同授权范围追加。用户撤销授权时立即停止读写，不自行删除旧数据；删除需单独确认。

禁止把记录放进 Skill 安装目录、公共 Git 仓库、未经批准的云盘。不要保存学生真实姓名、身份证、完整教材内容、完整答题文本、账户或 API 凭据。

## 格式与升级
schema_version 为 0.2.0。attempts 是追加式事件，每条应有稳定 attempt_id；重试相同 ID 不应重复。记录 course、objective、question_id、activity（diagnostic/practice/transfer/delayed）、result（correct/incorrect/uncertain）、hint_level（0–3）、verification、error_type、attempted_at。掌握度是由证据计算出来的结果，不保存随意修改的百分比。

可选 stdlib 本地工具 scripts/learning_store.py：
~~~bash
python scripts/learning_store.py --workspace "/user/selected/workspace" init --consent
python scripts/learning_store.py --workspace "/user/selected/workspace" record --course "经济数学" --objective "商法则" --question-id "q1" --activity practice --result correct --hint-level 0 --verification checked --error-type none --attempt-id "attempt-001"
python scripts/learning_store.py --workspace "/user/selected/workspace" summary
~~~
这里的 --consent 只是计算机参数，**绝不代替向用户取得真实授权**。只有用户授权且宿主确实存在 Python 时才使用；否则通过已有的宿主文件工具实现同样存储约定，若做不到则诚实告知当前不能跨会话记忆。

## 记录与恢复
- 记录应原子更新、保留备份，出错不丢已有历史；不得用新状态覆盖旧作答。
- “下次复习”是建议日期，没有接入任务调度时不要宣称已创建提醒。
- 下次用户说“继续学习”时先读取实际可访问的数据，讲明上次目标、最近困难和建议下一题。读取失败不虚构。
- V0.1 使用过的 JSON 文件不可直接假设兼容；先备份并检查字段，再决定迁移。V0.2 工具对不认识的旧结构只读并报错，不悄悄覆盖。