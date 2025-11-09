"""Analyze docs folder and create organization recommendations"""
import os
from pathlib import Path
from datetime import datetime

docs_dir = Path("docs")

# Categorize files
categories = {
    "Setup & Configuration": [],
    "API & Technical": [],
    "Deployment & DevOps": [],
    "Testing & Quality": [],
    "QuickBooks Integration": [],
    "Status & Progress": [],
    "Troubleshooting": [],
    "Archive (Outdated)": [],
    "Metrics": []
}

# Read each file's first few lines to understand content
for file in docs_dir.rglob("*.md"):
    rel_path = file.relative_to(docs_dir)
    size = file.stat().st_size
    modified = datetime.fromtimestamp(file.stat().st_mtime).strftime("%Y-%m-%d")
    
    # Read first 500 chars
    try:
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read(500).lower()
    except:
        content = ""
    
    # Categorize
    filename = file.name.lower()
    
    if "archive" in str(rel_path):
        categories["Archive (Outdated)"].append((rel_path, size, modified, "In archive folder"))
    elif "metrics" in str(rel_path) or "baseline" in filename:
        categories["Metrics"].append((rel_path, size, modified, "Metrics data"))
    elif any(x in filename for x in ["setup", "config", "git_secret", "new_machine", "quick_reference"]):
        categories["Setup & Configuration"].append((rel_path, size, modified))
    elif any(x in filename for x in ["api", "field_mapping", "logging"]):
        categories["API & Technical"].append((rel_path, size, modified))
    elif any(x in filename for x in ["deploy", "render", "github_actions", "workflow"]):
        categories["Deployment & DevOps"].append((rel_path, size, modified))
    elif any(x in filename for x in ["test", "troubleshoot"]):
        categories["Testing & Quality"].append((rel_path, size, modified))
    elif "quickbooks" in filename or "qb" in filename:
        categories["QuickBooks Integration"].append((rel_path, size, modified))
    elif any(x in filename for x in ["status", "progress", "phase", "complete", "next_steps", "summary"]):
        categories["Status & Progress"].append((rel_path, size, modified))
    else:
        # Default to technical
        categories["API & Technical"].append((rel_path, size, modified))

# Print analysis
print("="*80)
print("DOCUMENTATION ORGANIZATION ANALYSIS")
print("="*80)
print()

for category, files in categories.items():
    if files:
        print(f"\n{category} ({len(files)} files)")
        print("-"*80)
        for item in sorted(files):
            if len(item) == 4:
                path, size, mod, note = item
                print(f"  {str(path):50s} {size:>8,} bytes  {mod}  [{note}]")
            else:
                path, size, mod = item
                print(f"  {str(path):50s} {size:>8,} bytes  {mod}")

print("\n")
print("="*80)
print("RECOMMENDATIONS")
print("="*80)
