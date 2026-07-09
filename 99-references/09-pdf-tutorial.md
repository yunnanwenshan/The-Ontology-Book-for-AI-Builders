# AI 本体论实战 · 完整教程（PDF 版）

> 📄 **`The-LLM-Grounding-Playbook.pdf`**（452 KB / 19 KB Markdown）

## 文件

| 文件 | 大小 | 说明 |
|------|------|------|
| `The-LLM-Grounding-Playbook.pdf` | 452 KB | **最终 PDF 教程**（可打印） |
| `The-LLM-Grounding-Playbook.md` | 19 KB | Markdown 源文件（可编辑） |
| `tutorial.html` | 41 KB | 中间 HTML（pandoc 生成） |
| `tutorial.css` | 2.6 KB | PDF 样式 |

## 章节

1. 第 0 章 · 写在前面
2. 第 1 章 · 哲学源流（2400 年）
3. 第 2 章 · 知识表示（60 年演变）
4. 第 3 章 · AI 时代为什么需要本体
5. 第 4 章 · RDF：所有事实的最小单元
6. 第 5 章 · RDFS/OWL：让机器"懂"
7. 第 6 章 · SPARQL：本体的 SQL
8. 第 7 章 · SHACL：业务规则守门员
9. 第 8 章 · 5 分钟跑通第一个 demo
10. 第 9 章 · 7 个真实业务案例
11. 第 10 章 · Palantir Foundry 风格平台
12. 第 11 章 · AIP / MCP：让 LLM 调本体
13. 第 12 章 · 工程化进阶（ABAC / CDC / 仪表盘）
14. 第 13 章 · 30 道实战作业
15. 附录 A · 资源与工具速查
16. 附录 B · 常见陷阱与最佳实践
17. 附录 C · 术语表

## 如何生成

```bash
# 1. Markdown → HTML
pandoc 99-references/The-LLM-Grounding-Playbook.md \
  -o 99-references/tutorial.html \
  --standalone --toc --toc-depth=2 \
  --css 99-references/tutorial.css

# 2. HTML → PDF
python3 -c "from weasyprint import HTML; HTML('99-references/tutorial.html').write_pdf('99-references/The-LLM-Grounding-Playbook.pdf')"
```

## 重新生成

如果更新了 Markdown：

```bash
cd ~/Documents/projects/ai/ontology
bash 99-references/build_pdf.sh    # （可选脚本，需要创建）
```

或者手动跑上面两条命令。

## 设计

- **暗色 + 蓝色标题**：类似 Palantir Workshop 风格
- **A4 纸 + 1.5cm 边距**：可双面打印
- **代码块蓝边**：突出"可运行"内容
- **表格交替色**：清晰对比
- **每页页码**：方便引用
