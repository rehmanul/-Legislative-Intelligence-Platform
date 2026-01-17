# Interactive Diagram Viewer - Setup & Hosting Guide

## 📋 Overview

This guide explains how to use and host the interactive Mermaid diagram viewer for the Agent Orchestrator system.

---

## 🚀 Quick Start

### Option 1: Local File (Simplest)

1. **Open directly in browser:**
   ```
   file:///C:/Users/phi3t/12.20%20dash/1.5.2026/agent-orchestrator/dashboards/diagram_viewer.html
   ```

   **⚠️ Note:** This may have CORS issues loading `.mmd` files. Use Option 2 or 3 instead.

### Option 2: Local HTTP Server (Recommended for Development)

1. **Using Python:**
   ```bash
   cd "c:\Users\phi3t\12.20 dash\1.5.2026\agent-orchestrator"
   python -m http.server 8000
   ```

2. **Open in browser:**
   ```
   http://localhost:8000/dashboards/diagram_viewer.html
   ```

3. **Using Node.js (http-server):**
   ```bash
   npx http-server -p 8000
   ```

### Option 3: VS Code Live Server

1. Install "Live Server" extension in VS Code
2. Right-click `diagram_viewer.html`
3. Select "Open with Live Server"

---

## 🌐 Hosting Options

### 1. GitHub Pages (Free, Easy)

**Steps:**
1. Create a GitHub repository
2. Push your files:
   ```bash
   git init
   git add .
   git commit -m "Add diagram viewer"
   git remote add origin https://github.com/yourusername/agent-orchestrator.git
   git push -u origin main
   ```
3. Go to repository Settings → Pages
4. Select branch `main` and folder `/ (root)`
5. Your viewer will be at: `https://yourusername.github.io/agent-orchestrator/dashboards/diagram_viewer.html`

**Pros:**
- Free
- Automatic HTTPS
- Easy updates (just push)

**Cons:**
- Public (unless private repo + GitHub Pro)
- Limited customization

---

### 2. Netlify (Free Tier, Best for Static Sites)

**Steps:**
1. Go to [netlify.com](https://netlify.com)
2. Drag and drop your `agent-orchestrator` folder
3. Or connect GitHub repo for auto-deploy
4. Your site will be live at: `https://random-name.netlify.app`

**Pros:**
- Free tier
- Automatic HTTPS
- Custom domains
- Continuous deployment
- Fast CDN

**Cons:**
- Public by default (can password protect on paid plan)

---

### 3. Vercel (Free Tier, Great for Next.js)

**Steps:**
1. Install Vercel CLI: `npm i -g vercel`
2. Run: `vercel` in your project directory
3. Follow prompts

**Pros:**
- Free tier
- Fast global CDN
- Easy deployment

---

### 4. Self-Hosted (Full Control)

**Using Nginx:**
```nginx
server {
    listen 80;
    server_name diagrams.yourdomain.com;
    
    root /path/to/agent-orchestrator;
    index dashboards/diagram_viewer.html;
    
    location / {
        try_files $uri $uri/ =404;
    }
}
```

**Using Apache:**
```apache
<VirtualHost *:80>
    ServerName diagrams.yourdomain.com
    DocumentRoot /path/to/agent-orchestrator
    
    <Directory /path/to/agent-orchestrator>
        Options Indexes FollowSymLinks
        AllowOverride All
        Require all granted
    </Directory>
</VirtualHost>
```

---

## 🔧 Configuration

### Update File Paths

If your `.mmd` files are in a different location, edit `diagram_viewer.html`:

```javascript
const diagramFiles = {
    master: '../.userInput/agent orchestrator 1.6.mmd',
    pre_evt: '../.userInput/agent orchestrator 1.6_PRE_EVT_operator_view.mmd',
    // ... update paths as needed
};
```

### Custom Styling

Edit the `<style>` section in `diagram_viewer.html` to customize:
- Colors
- Fonts
- Layout
- Animations

---

## 📱 Features

### Current Features:
- ✅ Tab navigation between diagrams
- ✅ Zoom in/out/reset controls
- ✅ Fullscreen mode
- ✅ Export to PNG
- ✅ Responsive design (mobile-friendly)
- ✅ Loading states
- ✅ Error handling

### Future Enhancements (Codex can help):
- Search/filter nodes
- Click-to-navigate between related diagrams
- Side-by-side comparison
- Print-friendly layout
- Dark mode
- Keyboard shortcuts
- Shareable links to specific diagrams

---

## 🤖 Codex Integration

### What Codex Can Help With:

1. **Enhanced Interactivity:**
   - Add click handlers to nodes
   - Create drill-down views
   - Add tooltips with detailed info

2. **Advanced Features:**
   - Real-time updates from API
   - User annotations/comments
   - Version history
   - Collaborative editing

3. **Integration:**
   - Embed in existing dashboards
   - Connect to agent registry
   - Show live system state

4. **Customization:**
   - Theme customization
   - Layout adjustments
   - Additional export formats (PDF, SVG)

### How to Request Codex Help:

**Example prompts:**
- "Add click handlers to state nodes that show detailed information in a modal"
- "Create a side-by-side comparison view for two operator views"
- "Add a search bar to filter nodes by name"
- "Integrate this viewer with the agent registry API"

---

## 🐛 Troubleshooting

### CORS Errors

**Problem:** Browser blocks loading `.mmd` files

**Solution:**
- Use a local HTTP server (Option 2)
- Or host on a web server (GitHub Pages, Netlify, etc.)

### Diagrams Not Rendering

**Check:**
1. Mermaid.js CDN is loading (check browser console)
2. File paths are correct
3. `.mmd` files exist at specified paths
4. No syntax errors in `.mmd` files

### Export Not Working

**Solution:**
- Some browsers block downloads. Try:
  - Chrome/Edge: Should work
  - Firefox: May need permission
  - Safari: May have limitations

---

## 📊 File Structure

```
agent-orchestrator/
├── dashboards/
│   ├── diagram_viewer.html          ← Main viewer
│   └── DIAGRAM_VIEWER_README.md      ← This file
├── .userInput/
│   ├── agent orchestrator 1.6.mmd   ← Master diagram
│   ├── agent orchestrator 1.6_PRE_EVT_operator_view.mmd
│   ├── agent orchestrator 1.6_COMM_EVT_operator_view.mmd
│   ├── agent orchestrator 1.6_FLOOR_EVT_operator_view.mmd
│   ├── agent orchestrator 1.6_FINAL_EVT_operator_view.mmd
│   └── agent orchestrator 1.6_IMPL_EVT_operator_view.mmd
└── ...
```

---

## ✅ Recommended Setup

**For Development:**
- Use Python HTTP server (Option 2)
- Or VS Code Live Server

**For Production:**
- GitHub Pages (if public)
- Netlify (best balance)
- Self-hosted (if you need control)

---

## 🎯 Next Steps

1. **Test locally** using HTTP server
2. **Choose hosting** based on your needs
3. **Customize** styling/features as needed
4. **Request Codex enhancements** for advanced features

---

**Last Updated:** 2026-01-20  
**Version:** 1.0.0
