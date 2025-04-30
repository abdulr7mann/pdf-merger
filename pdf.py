#!/usr/bin/env python3
import io, threading
from pathlib import Path
import PySimpleGUI as sg
from pypdf import PdfWriter, PdfReader
import img2pdf

sg.theme("DarkGrey14")
EXTS = {".pdf", ".jpg", ".jpeg", ".png"}

def scan(folder: Path):
    return [f for f in sorted(folder.iterdir()) if f.suffix.lower() in EXTS]

def img_to_pdf(path: Path):
    return io.BytesIO(img2pdf.convert(str(path)))

def merge(paths, out_path, window):
    writer = PdfWriter()
    total = len(paths)
    for i, p in enumerate(paths, 1):
        window.write_event_value("-PROG-", (i, total))
        reader = PdfReader(img_to_pdf(p)) if p.suffix.lower() in (".jpg", ".jpeg", ".png") else PdfReader(p)
        writer.append(reader)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("wb") as fh:
        writer.write(fh)
    window.write_event_value("-DONE-", str(out_path))

file_col = [
    [sg.Text("Source folder"),
     sg.Input(key="-FOLDER-", expand_x=True, readonly=True, enable_events=True),
     sg.FolderBrowse()],
    [sg.Listbox([], size=(40,16), key="-LIST-", enable_events=True,
                select_mode=sg.LISTBOX_SELECT_MODE_SINGLE,
                expand_x=True, expand_y=True)],
    [sg.Button("▲  Up", key="-UP-", size=(6,1), disabled=True),
     sg.Button("▼  Down", key="-DOWN-", size=(6,1), disabled=True),
     sg.Button("Delete", key="-DEL-", disabled=True)]
]

out_col = [
    [sg.Text("Output file"),
     sg.Input("Combined.pdf", key="-OUT-", expand_x=True),
     sg.FileSaveAs("Browse", file_types=(("PDF","*.pdf"),))],
    [sg.ProgressBar(max_value=100, orientation="h", size=(30,20), key="-BAR-")],
    [sg.Push(), sg.Button("Merge", key="-MERGE-", disabled=True), sg.Button("Exit")]
]

window = sg.Window("PDF Certificate Merger",
                   [[sg.Column(file_col, expand_y=True),
                     sg.VSeparator(),
                     sg.Column(out_col)]],
                   finalize=True, resizable=True)

paths = []

while True:
    ev, vals = window.read()
    if ev in (sg.WIN_CLOSED, "Exit"):
        break

    # folder chosen/typed -> auto-load
    if ev == "-FOLDER-":
        folder = Path(vals["-FOLDER-"])
        paths = scan(folder) if folder.is_dir() else []
        window["-LIST-"].update([p.name for p in paths])
        for k in ("-MERGE-","-UP-","-DOWN-","-DEL-"):
            window[k].update(disabled=not paths)

    if ev == "-LIST-":
        has_sel = bool(vals["-LIST-"])
        for k in ("-UP-","-DOWN-","-DEL-"):
            window[k].update(disabled=not has_sel)

    if ev in ("-UP-","-DOWN-") and vals["-LIST-"]:
        sel = vals["-LIST-"][0]
        idx = [p.name for p in paths].index(sel)
        new_idx = idx-1 if ev=="-UP-" else idx+1
        if 0 <= new_idx < len(paths):
            paths[idx], paths[new_idx] = paths[new_idx], paths[idx]
            window["-LIST-"].update([p.name for p in paths], set_to_index=new_idx)

    if ev == "-DEL-" and vals["-LIST-"]:
        sel = vals["-LIST-"][0]
        idx = [p.name for p in paths].index(sel)
        paths.pop(idx)
        window["-LIST-"].update([p.name for p in paths])
        if paths:
            window["-LIST-"].update(set_to_index=min(idx, len(paths)-1))
        else:
            for k in ("-MERGE-","-UP-","-DOWN-","-DEL-"):
                window[k].update(disabled=True)

    if ev == "-MERGE-" and paths:
        out = Path(vals["-OUT-"] or "Combined.pdf")
        if out.suffix.lower() != ".pdf":
            out = out.with_suffix(".pdf")
        threading.Thread(target=merge, args=(paths, out, window), daemon=True).start()

    if ev == "-PROG-":
        done, total = vals[ev]
        window["-BAR-"].update(done/total*100)

    if ev == "-DONE-":
        window["-BAR-"].update(0)
        sg.popup_ok(f"✅  Saved to\n{vals[ev]}")

window.close()
