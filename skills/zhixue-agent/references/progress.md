# 学习进度与持久化约定

本技能没有内建数据库；持久化完全依赖宿主提供的文件工具，并需要用户明确同意。默认只在聊天上下文内保持状态。

## 可选的本地数据文件

在用户确认后，将学习证据保存到**用户明确选择的工作区**内，例如 `.zhixue/learning-records.json`。不要写进 Skill 安装目录、系统目录或聊天外部云盘。避免保存完整教材、API 凭据、敏感身份信息、学生个人信息。

推荐 JSON 结构：

```json
{
  "schema_version": "0.1.0",
  "courses": [
    {"id": "calculus", "title": "微积分", "objectives": ["链式法则"]}
  ],
  "attempts": [
    {
      "course_id": "calculus",
      "objective": "链式法则",
      "question_id": "chain-001",
      "attempted_at": "2026-11-03",
      "hint_level": 0,
      "answer_outcome": "correct",
      "assessment": "本次独立完成",
      "verification": "substitution_or_teacher_review",
      "notes": "已能区分内外函数"
    }
  ],
  "review_plan": [{"objective": "链式法则", "suggested_after_days": [1,3,7]}]
}
```

`verification` 只描述真实采取的验证方式：没有核对则设 `unverified`。`hint_level` 为 0–3。`assessment` 不应因为一次提示后做对变成“完全掌握”。日期必须使用当前会话准确日期，不能猜测。

## 写入/读出规则

- 先检测宿主是否有明确的工作区文件权限；只在用户同意后写入。
- 新记录以追加方式保留，不覆盖历史尝试；更新前先读取文件和保留备份。
- 出错时不丢数据，不将写入失败宣称为完成。
- 在另一会话无法读取该文件时，明确告知学习记录不可用。
- 间隔复习只是建议日期；定时提醒需另外的任务调度能力。