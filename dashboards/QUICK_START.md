# 🚀 Quick Start - Diagram Viewer

## ⚡ Fastest Way to View (30 seconds)

### Windows:
1. Double-click: `launch_viewer.bat`
2. Browser opens automatically
3. Done! ✅

### Manual (Any OS):
```bash
cd "agent-orchestrator"
python -m http.server 8000
```
Then open: `http://localhost:8000/dashboards/diagram_viewer.html`

### Windows PowerShell (Alternative):
```powershell
# If 'python' command not recognized, use 'py' launcher:
cd agent-orchestrator
py -m http.server 8000

# Or use virtual environment Python directly:
.venv\Scripts\python.exe -m http.server 8000
```

---

## 📋 What You Get

- **6 Interactive Diagrams:**
  - Master System Architecture
  - PRE_EVT Operator View
  - COMM_EVT Operator View
  - FLOOR_EVT Operator View
  - FINAL_EVT Operator View
  - IMPL_EVT Operator View

- **Features:**
  - ✅ Tab navigation
  - ✅ Zoom in/out
  - ✅ Fullscreen mode
  - ✅ Export to PNG
  - ✅ Mobile-friendly

---

## 🌐 Want to Host Online?

**Easiest:** GitHub Pages (free, public)
**Best:** Netlify (free, CDN, auto-deploy)
**Control:** Self-hosted (your server)

See `DIAGRAM_VIEWER_README.md` for full hosting guide.

---

## 🤖 Need More Features?

Ask Codex to add:
- Search/filter nodes
- Click-to-navigate
- Side-by-side comparison
- Dark mode
- API integration

---

**Ready to go!** 🎉
