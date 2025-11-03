# Create directory structure
New-Item -ItemType Directory -Path "src/components", "src/layouts", "src/pages", "src/stores" -Force | Out-Null

Write-Host "✅ Creating fresh frontend structure..."
Write-Host "Directory structure created successfully!"
