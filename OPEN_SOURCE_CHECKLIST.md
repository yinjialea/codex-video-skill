# 开源提交清单

开源时不要提交整个上级目录，只提交 `knowledge-video-workflow-skill/` 这个 Skill 目录。

## 建议提交

```text
knowledge-video-workflow-skill/
├─ .gitignore
├─ SKILL.md
├─ README.md
├─ LOCAL_SETUP.md
├─ CODEX_SETUP_GUIDE.md
├─ OPEN_SOURCE_CHECKLIST.md
├─ requirements.txt
├─ agents/
│  └─ openai.yaml
├─ assets/
│  └─ dark-tech-template/
│     ├─ DESIGN.md
│     ├─ index.html
│     └─ scene-data.example.js
├─ references/
│  ├─ input-schema.md
│  ├─ troubleshooting.md
│  └─ workflow-steps.md
├─ scripts/
│  ├─ common.py
│  ├─ compose_video.py
│  ├─ generate_covers.py
│  ├─ generate_subtitles.py
│  ├─ generate_voice.py
│  ├─ plan_content.py
│  ├─ render_video.py
│  ├─ sync_timeline.py
│  ├─ validate_input.py
│  └─ workflow.py
└─ tests/
   ├─ test_commands.py
   ├─ test_common.py
   ├─ test_generate_subtitles.py
   ├─ test_plan_content.py
   ├─ test_sync_timeline.py
   ├─ test_validate_input.py
   └─ test_workflow.py
```

## 不要提交

这些已经写入 `.gitignore`：

```text
.venv/
venv/
__pycache__/
*.py[cod]
.pytest_cache/
output/
smoke-output/
logs/
*.mp4
*.wav
*.mp3
*.srt
*.ass
.env
.env.*
.idea/
.vscode/
examples/
ai-agent-15s-index.html
workflow-input.ai-agent-15s.json
workflow-input.json
.DS_Store
Thumbs.db
```

## 开源前建议检查

在仓库根目录执行：

```powershell
git status --ignored
```

确认 `.venv/`、`output/`、`examples/`、音视频产物和本地配置都在 ignored 里。

再做一次敏感信息粗查：

```powershell
rg -n "OPENAI_API_KEY|sk-|C:\\Users|E:\\桌面|lenove" .
```

如果命中私有路径、用户名、Key、客户文案，先处理掉再提交。

