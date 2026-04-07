$root = "C:\SchoolManagement\School Management System"
$target = Join-Path $root "App_Run_Instructions.docx"
if (Test-Path $target) { Remove-Item $target -Force }
Add-Type -AssemblyName System.IO.Compression.FileSystem
$zip = [System.IO.Compression.ZipFile]::Open($target, "Create")
$bodyLines = @(
    "Running the School Management System",
    "",
    "1. Environment",
    "   - Use Python 3.12+ installed globally or the repo-local .venv.",
    "   - Optional: copy the provided .python312 runtime into this folder if you lack system Python.",
    "",
    "2. Install dependencies",
    "   - Activate the virtual environment: .venv\Scripts\activate",
    "   - Install packages: pip install -r requirements.txt",
    "",
    "3. Configure settings",
    "   - Set SECRET_KEY and DATABASE_URL for production, or leave defaults for SQLite.",
    "   - Configure SEED_DEMO_DATA=true if you want sample accounts auto-created.",
    "",
    "4. Reset the database",
    "   - python scripts/reset_accounts.py (clears all accounts and recreates tables).",
    "   - Register new users yourself after the reset.",
    "",
    "5. Start the server",
    "   - .venv\\Scripts\\python.exe run.py",
    "   - Visit http://127.0.0.1:5000 in your browser."
)
$body = ($bodyLines | ForEach-Object { "<w:p><w:r><w:t xml:space='preserve'>$_</w:t></w:r></w:p>" }) -join ""
$document = "<?xml version='1.0' encoding='UTF-8' standalone='yes'?><w:document xmlns:w='http://schemas.openxmlformats.org/wordprocessingml/2006/main'><w:body>${body}<w:sectPr><w:pgSz w:w='12240' w:h='15840'/><w:pgMar w:top='1440' w:right='1440' w:bottom='1440' w:left='1440'/></w:sectPr></w:body></w:document>"
$contentTypes = "<?xml version='1.0' encoding='UTF-8' standalone='yes'?><Types xmlns='http://schemas.openxmlformats.org/package/2006/content-types'><Default Extension='rels' ContentType='application/vnd.openxmlformats-package.relationships+xml'/><Default Extension='xml' ContentType='application/xml'/><Override PartName='/word/document.xml' ContentType='application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml'/></Types>"
$rootRels = "<?xml version='1.0' encoding='UTF-8' standalone='yes'?><Relationships xmlns='http://schemas.openxmlformats.org/package/2006/relationships'><Relationship Id='rId1' Type='http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument' Target='word/document.xml'/></Relationships>"
$docRels = "<?xml version='1.0' encoding='UTF-8' standalone='yes'?><Relationships xmlns='http://schemas.openxmlformats.org/package/2006/relationships'/>"
$entries = @{
    "[Content_Types].xml" = $contentTypes
    "_rels/.rels" = $rootRels
    "word/document.xml" = $document
    "word/_rels/document.xml.rels" = $docRels
}
foreach ($name in $entries.Keys) {
    $entry = $zip.CreateEntry($name)
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($entries[$name])
    $stream = $entry.Open()
    $stream.Write($bytes, 0, $bytes.Length)
    $stream.Dispose()
}
$zip.Dispose()
Write-Output "Created $target"
