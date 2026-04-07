from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "App_Run_Instructions.docx"

paragraphs = [
    "Running the School Management System",
    "",
    "1. Environment",
    "   - Use Python 3.12+ installed globally or the repo-local .venv.",
    "   - Optional: copy the provided .python312 runtime into this folder if you lack system Python.",
    "",
    "2. Install dependencies",
    "   - Activate the virtual environment: .venv\\Scripts\\activate",
    "   - Install packages: pip install -r requirements.txt",
    "",
    "3. Configure settings",
    "   - Set SECRET_KEY and DATABASE_URL for production, or leave defaults for SQLite.",
    "   - Configure SEED_DEMO_DATA=true if you want sample accounts auto-created.",
    "",
    "4. Create or reset the database",
    "   - python scripts/reset_accounts.py (clears all accounts and recreates tables).",
    "   - Register new users via the /register and parent portals as needed.",
    "",
    "5. Start the server",
    "   - Run .venv\\Scripts\\python.exe run.py",
    "   - Visit http://127.0.0.1:5000 in your browser.",
]

def wrap_line(line: str) -> str:
    return f'<w:p><w:r><w:t xml:space="preserve">{line}</w:t></w:r></w:p>'

document_body = "\n    ".join(wrap_line(line) for line in paragraphs)

document_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
            xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
            xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"
            mc:Ignorable="w14 wp14">
  <w:body>
    {document_body}
    <w:sectPr>
      <w:pgSz w:w="12240" w:h="15840"/>
      <w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440"/>
    </w:sectPr>
  </w:body>
</w:document>"""

content_types = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>"""

root_rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>"""

document_rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"/>"""

with zipfile.ZipFile(OUTPUT, "w") as archive:
    archive.writestr("[Content_Types].xml", content_types)
    archive.writestr("_rels/.rels", root_rels)
    archive.writestr("word/document.xml", document_xml)
    archive.writestr("word/_rels/document.xml.rels", document_rels)

print(f"Wrote {OUTPUT}")
