# pdf-merger
PDF Certificate Merger A minimalist desktop utility that lets you gather scattered certificates (PDF, JPG, PNG) into one professionally-ordered PDF—perfect for university or job applications. Built with Python and PySimpleGUI, it runs on Windows, macOS, and Linux and can be packaged as a single double-clickable executable.

## Features
* Combine multiple PDFs / images into one PDF
* Re-order pages with Up / Down buttons
* Progress bar while merging
* Works on Windows / macOS / Linux

## Quick start (dev mode)
```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
python pdf_merger.py
```
## One-file build 
```bash
pip install pyinstaller
pyinstaller --onefile --noconsole --icon=pdf_merger_single.ico pdf_merger.py
