# Wipe 工作流

清空或删除知识库内容，所有删除操作均经用户确认，文件移入回收站可恢复。

> 📌 **路径约定**: 本文档中的 `raw/`、`wiki/` 均指当前知识库的绝对路径，由 SKILL.md 路由时确定（`KB_RAW`、`KB_WIKI`）。

## 核心原则

1. **人工确认** — 所有删除操作必须列出文件清单，经用户确认后才执行
2. **回收站机制** — 删除 = 移入 `wiki/.trash/`，不是真删除，支持恢复
3. **不动原始素材** — `raw/` 目录永远不动
4. **清理关联** — 删除页面时同步清理 index.md、overview.md 及其他页面的 Related 链接

## 回收站

路径：`wiki/.trash/`

- 删除时按原目录结构存放，如 `wiki/concepts/swiglu.md` → `wiki/.trash/concepts/swiglu.md`
- 同名文件冲突时，旧文件加时间戳后缀：`swiglu.2026-04-13.md`
- 恢复时移回原路径，并重新更新 index.md、overview.md、关联页面的 Related
- 用户可随时 `/wiki wipe trash` 查看回收站内容，`/wiki wipe restore` 恢复文件，`/wiki wipe empty-trash` 永久清空回收站

## 使用方式

- `/wiki wipe` — 交互式选择操作
- `/wiki wipe all` — 全量重置
- `/wiki wipe <关键词>` — 删除匹配的页面
- `/wiki wipe trash` — 查看回收站
- `/wiki wipe restore` — 从回收站恢复页面
- `/wiki wipe empty-trash` — 永久清空回收站

## 工作流程

### 1. 确定操作模式

#### 无参数 — 交互式选择

```json
{
  "questions": [{
    "question": "选择知识库操作：",
    "header": "操作类型",
    "multiSelect": false,
    "options": [
      {"label": "全量重置", "description": "清空所有 wiki 页面到回收站，回到初始状态（raw/ 不受影响）"},
      {"label": "删除指定素材", "description": "删除一个素材及其产生的关联页面（移入回收站）"},
      {"label": "删除指定页面", "description": "删除一个或多个 entity/concept/analysis 页面（移入回收站）"},
      {"label": "查看/恢复回收站", "description": "查看回收站内容，恢复已删除页面"}
    ]
  }]
}
```

### 2. 全量重置流程

#### 2a. 盘点当前内容

读取 `wiki/index.md`，统计将要移入回收站的文件：
- `wiki/sources/*.md`
- `wiki/entities/*.md`
- `wiki/concepts/*.md`
- `wiki/analyses/*.md`

#### 2b. 确认（必须）

```json
{
  "questions": [{
    "question": "确认全量重置？以下 N 个文件将移入回收站（wiki/.trash/）：\n\n素材摘要: X 个\n实体页面: X 个\n概念页面: X 个\n分析页面: X 个\n\n⚠️ 可通过 /wiki wipe restore 恢复\n⚠️ raw/ 目录不受影响",
    "header": "确认重置",
    "multiSelect": false,
    "options": [
      {"label": "确认重置", "description": "将所有 wiki 页面移入回收站，重置 index/overview"},
      {"label": "取消", "description": "不做任何操作"}
    ]
  }]
}
```

#### 2c. 执行重置

用户确认后：

1. **创建回收站目录**（如不存在）：`mkdir -p wiki/.trash/{sources,entities,concepts,analyses}`

2. **移动所有内容页面到回收站**：
   ```bash
   mv wiki/sources/*.md wiki/.trash/sources/
   mv wiki/entities/*.md wiki/.trash/entities/
   mv wiki/concepts/*.md wiki/.trash/concepts/
   mv wiki/analyses/*.md wiki/.trash/analyses/
   ```
   同名冲突时给旧文件加时间戳后缀再移动。

3. **重置 index.md** 为空索引模板：
   ```markdown
   # Wiki Index

   > 此文件由 LLM 自动维护，是 wiki 的内容目录。按类别组织所有页面，每页一行摘要。
   > LLM 在回答查询时优先阅读此文件以定位相关页面。

   ## Overview

   - [Overview](overview.md) — Wiki 总览与当前知识图谱摘要

   ## Sources

   ## Entities

   ## Concepts

   ## Analyses
   ```

4. **重置 overview.md**：保留 frontmatter，统计清零，清空图谱摘要和近期活动。

5. **在 log.md 顶部追加记录**：
   ```markdown
   ## [YYYY-MM-DD] wipe | 全量重置

   - 移入回收站: 素材摘要 X 个, 实体 X 个, 概念 X 个, 分析 X 个
   - 重置 index.md 和 overview.md
   - 可通过 /wiki wipe restore 恢复
   ```

6. **输出结果**：
   ```
   ✅ 知识库已重置
      移入回收站: N 个页面
      raw/ 目录保留: M 个素材可随时重新 /wiki ingest
      💡 /wiki wipe restore 可恢复
   ```

### 3. 选择性删除流程

#### 3a. 确定删除目标

**按素材删除**：
1. 读取 `wiki/index.md`，列出素材供用户选择（或根据关键词匹配）
2. 找到素材摘要页 `wiki/sources/xxx.md`
3. 分析影响范围：
   - "将删除"：仅由该素材产生的页面（`sources` 字段仅含该素材）
   - "将更新"：还有其他素材引用的页面（保留但移除关联）

**按页面删除**：
1. 用户指定或从列表选择要删除的页面
2. 分析哪些其他页面的 Related 引用了目标页面

#### 3b. 确认（必须）

```json
{
  "questions": [{
    "question": "删除《目标》将产生以下影响：\n\n🗑️ 移入回收站:\n- wiki/sources/xxx.md\n- wiki/entities/yyy.md（仅此素材引用）\n\n✏️ 将更新（移除关联）:\n- wiki/concepts/zzz.md（还有其他素材引用，保留）\n\n确认执行？",
    "header": "确认删除",
    "multiSelect": false,
    "options": [
      {"label": "确认删除", "description": "执行上述删除和更新操作"},
      {"label": "仅删除摘要页", "description": "只删除 source 页面，保留所有 entity/concept"},
      {"label": "取消", "description": "不做任何操作"}
    ]
  }]
}
```

#### 3c. 执行删除

用户确认后：

1. **移动目标页面到回收站**（按原目录结构）
2. **更新受影响页面**：
   - 从 `sources` frontmatter 移除被删素材引用
   - 从 Related 区块移除指向已删页面的链接
   - 更新 `updated` 日期
3. **更新 index.md** — 移除已删页面条目
4. **更新 overview.md** — 更新统计和知识图谱摘要
5. **在 log.md 顶部追加记录**
6. **运行 `python <skill-dir>/scripts/lint.py --wiki-dir <KB_WIKI> --raw-dir <KB_RAW>`** 检查是否产生新的断链或孤岛
7. **输出结果**：
   ```
   ✅ 删除完成
      移入回收站: N 个页面
      更新: M 个页面（移除关联）
      lint: 通过
      💡 /wiki wipe restore 可恢复
   ```

### 4. 回收站操作

#### `/wiki wipe trash` — 查看回收站

扫描 `wiki/.trash/` 目录，按类别列出所有文件及其删除前的原路径。如果回收站为空，提示"回收站为空"。

#### `/wiki wipe restore` — 恢复页面

1. 列出回收站中的所有文件，供用户选择（支持多选）
2. **确认恢复**：展示将恢复的文件列表，确认后执行
3. 执行恢复：
   - 将文件从 `wiki/.trash/` 移回原路径
   - 重新在 index.md 中添加条目
   - 重新在相关页面的 Related 区块中添加链接
   - 更新 overview.md 统计
   - 在 log.md 追加恢复记录
4. 运行 `python <skill-dir>/scripts/lint.py --wiki-dir <KB_WIKI> --raw-dir <KB_RAW>` 检查恢复后的一致性

#### `/wiki wipe empty-trash` — 永久清空回收站

1. 列出回收站所有文件
2. **确认**：⚠️ 此操作不可逆（除非 git 恢复），要求用户确认
3. 确认后 `rm -rf wiki/.trash/*`

## 注意事项

- **永远不删除 raw/** — 原始素材不属于 wiki 内容，只读不写
- **log.md 只追加不清空** — 重置历史本身有价值
- 回收站目录 `wiki/.trash/` 建议加入 `.gitignore`，避免回收站内容进入版本控制
- 如果用户想清空 raw/，需自行手动操作，skill 提示但不代执行
