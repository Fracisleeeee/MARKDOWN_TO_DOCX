# Project Idea

## Multi-Template Markdown Document Automation Engine

（多模板文档自动化生成引擎）

---

# 一、项目背景（Problem Statement）

在当前工作场景中存在以下问题：

1. 报告类型多样：

   * 技术报告
   * 合规说明
   * 审计材料
   * 国企/机关公文（方正仿宋规范）

2. 文档生产痛点：

   * 字体规范依赖人工调整
   * 目录与分页经常错误
   * 标题层级不统一
   * 不同报告风格混乱
   * 版本留痕不可追溯

3. 风险点：

   * 公文格式不合规
   * 字体丢失导致排版错乱
   * 审计追溯困难
   * 人工改 Word 不可复现

---

# 二、项目目标（Objective）

构建一个：

> Markdown 驱动的多模板标准化文档构建系统

实现：

* 支持不同报告场景调用不同 Word 模板
* 自动生成目录、编号、分页
* 自动应用国企公文规范字体
* 自动版本记录与 hash 留档
* 可在 CI/CD 中自动运行

---

# 三、核心技术架构

```
Markdown
   ↓
Pandoc
   ↓
Reference Template (docx)
   ↓
Lua Filter (结构增强)
   ↓
Python Build Pipeline
   ↓
Standardized Word Output
```

---

# 四、功能设计

## 1️⃣ 模板体系

目录结构建议：

```
/templates
    gov_template.docx
    tech_template.docx
    compliance_template.docx
```

模板中定义：

* 字体（如方正仿宋）
* 标题样式
* TOC 样式
* 页眉页脚
* 行距
* 段落规范

---

## 2️⃣ 构建系统

建议实现：

```python
build.py --type gov --input report.md --output report.docx
```

内部逻辑：

* 自动选择模板
* 插入目录
* 自动编号
* 一级标题自动分页
* 输出日志
* 生成 SHA256

---

## 3️⃣ Lua Filter（进阶）

实现：

* 一级标题自动新页
* 附录自动 A/B 编号
* 特定标题排除目录
* 强制目录独立页

---

## 4️⃣ 合规增强功能

可选增强模块：

* 自动插入版本号
* 自动写入生成时间
* 自动插入构建人
* 自动生成元数据页

---

# 五、使用场景分类

| 场景   | 模板         | 特点    |
| ---- | ---------- | ----- |
| 技术文档 | tech       | 英文优先  |
| 合规报告 | compliance | 双语混排  |
| 国企公文 | gov        | 方正仿宋  |
| 审计留档 | audit      | 强版本控制 |

---

# 六、技术可行性评估

| 项目              | 难度       | 可控性       |
| --------------- | -------- | --------- |
| Markdown → docx | 低        | 高         |
| 字体模板控制          | 低        | 高         |
| 自动分页            | 中        | 高         |
| 自动附录编号          | 中        | 高         |
| 自动嵌入字体          | 中        | 依赖授权      |
| 自动更新目录          | 高（需 COM） | 仅 Windows |

整体可行性：高。

---

# 七、扩展方向（Future Roadmap）

## 阶段 1（MVP）

* 支持多模板
* 支持目录
* 支持分页
* 支持编号
* 支持 hash 记录

## 阶段 2

* 自动插入封面
* 自动版本变更记录
* YAML front-matter 读取元数据

## 阶段 3

* Web UI（内部工具）
* Git Hook 自动构建
* Docker 化部署
* PDF 终版输出支持

---

# 八、风险评估

1. 字体授权问题（方正）
2. 目标机器未安装字体
3. Word 版本兼容性
4. 目录自动更新依赖 Office

---


---

# 十、建议项目名称

* DocForge
* GovDoc Engine
* Markdown Compliance Builder
* Structured Report Pipeline

---

# 十一、核心价值总结

这个项目解决的是：

> “结构化文档生产的工业化问题”

它把：

* 人工 Word 调整
  变成
* 可复现的自动构建流程




