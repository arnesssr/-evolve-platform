# Evolve Payments Platform Documentation

This directory contains all project documentation, including both technical documentation and developer guides.

## 📁 Documentation Structure

```
docs/
├── assets/                 # Web assets for documentation site
│   └── style.css          # Styling for HTML documentation
├── index.html             # 🏠 Developer Documentation Homepage
├── architecture.html      # 🏗️ System Architecture Overview
├── folder-structure.html  # 📁 Codebase Structure Guide
├── getting-started.html   # 🚀 Development Setup Guide
├── DOCKER.md             # 🐳 Docker Deployment Guide
└── README.md             # 📝 This file
```

## 🌐 Live Documentation Site

The HTML documentation is automatically deployed to GitHub Pages whenever changes are pushed to this directory.

**Access the live documentation at:**
`https://[your-username].github.io/evolve-payments-platform/`

## 📋 Documentation Types

### 🖥️ Interactive Developer Documentation (HTML)
- **Purpose:** Internal team reference and onboarding
- **Audience:** Developers, technical team members
- **Features:** Dark theme, searchable, responsive design
- **Pages:**
  - **Homepage:** Project overview, tech stack, quick commands
  - **Architecture:** System design, modules, security layers
  - **Folder Structure:** Detailed codebase organization
  - **Getting Started:** Complete development setup guide

### 📄 Technical Documentation (Markdown)
- **Purpose:** Specific technical guides and deployment instructions
- **Files:**
  - `DOCKER.md` - Docker containerization and deployment
  - Additional `.md` files for specific topics

## 🔄 Auto-Deployment

Documentation is automatically deployed via GitHub Actions:
- **Trigger:** Changes to any file in `docs/` directory
- **Workflow:** `.github/workflows/deploy-docs.yml`
- **Security:** Includes robots.txt to prevent search engine indexing

## ✍️ Contributing to Documentation

### Adding New HTML Pages
1. Create your HTML file in the `docs/` directory
2. Follow the existing structure and styling
3. Update navigation in existing pages if needed
4. Test locally by opening `index.html` in a browser

### Adding New Markdown Documentation
1. Create `.md` files for specific technical topics
2. Use clear headings and code examples
3. Link to from the main HTML documentation where relevant

### Updating Existing Documentation
1. Edit the relevant HTML or Markdown files
2. Ensure all links and references remain valid
3. Push changes - deployment happens automatically

## 🎯 Best Practices

- **Keep it current:** Update documentation when code changes
- **Be developer-focused:** Write for your team, not external users
- **Use examples:** Include code samples and practical examples
- **Link related content:** Cross-reference between different docs
- **Test locally:** Verify changes work before pushing

## 🔧 Local Development

To preview the documentation site locally:

```bash
# Navigate to docs directory
cd docs/

# Open index.html in your browser
# Or use a simple HTTP server:
python -m http.server 8080
# Then visit http://localhost:8080
```

## 📞 Need Help?

If you need to update or modify the documentation:
1. Check existing examples in this directory
2. Follow the established patterns and styling
3. Ask team members for review on complex changes
4. Remember: documentation is for the team, keep it practical and useful!
