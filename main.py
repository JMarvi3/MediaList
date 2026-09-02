import tkinter as tk
import ttkwidgets
from tkinter import ttk
from tkinterdnd2 import DND_FILES, TkinterDnD
from pathlib import Path
from pymediainfo import MediaInfo
import re

def convert_time(seconds):
    seconds = int(seconds)
    minutes, seconds = divmod(seconds, 60)
    if minutes < 60:
        return f"{minutes}:{seconds:02d}"
    else:
        hours, minutes = divmod(minutes, 60)
        return f"{hours}:{minutes:02d}:{seconds:02d}"

def show_popup(event):
    try:
        context_menu.tk_popup(event.x_root, event.y_root)
    except:
        context_menu.grab_release()

def on_tree_select(event):
    widget = event.widget
    total_seconds = 0
    for id in widget.selection():
        item = widget.item(id)
        total_seconds += item["values"][-1]
    item_count = len(widget.selection())
    label.config(text=f"{item_count} items: {convert_time(total_seconds)}")

def sort_key(s):
    return [int(c) if c.isdigit() else c.lower() for c in re.split(r'(\d+)', s)]

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    root = TkinterDnD.Tk()
    root.geometry("800x768")
    root.title("Runtime calculator")

    columns = ('file', 'length', 'secs')
    tree = ttk.Treeview(root, columns=columns, show='headings')
    tree.column('file', width=700, stretch=True)
    tree.column('length', stretch=True)
    tree.column('secs', width=0, stretch=False)
    tree.heading('file', text='File', anchor="w")
    tree.heading('length', text='Length', anchor="w")

    files = set()
    def on_drop(event):
        new_files = sorted(root.tk.splitlist(event.data), key=sort_key)
        for path in new_files:
            if path in files: continue
            p = Path(path)
            media_info = MediaInfo.parse(p)
            if len(media_info.video_tracks) > 0:
                secs = int(float(media_info.video_tracks[0].duration) / 1000)
                duration = convert_time(secs)
            else:
                duration = ""
                secs = 0
            item_id = tree.insert('', 'end', values=(p.name, duration, secs))
            files.add(path)
            tree.selection_add(item_id)

    def clear_list():
        tree.delete(*tree.get_children())
        files.clear()

    def select_all():
        tree.selection_set(tree.get_children())

    def delete_selected():
        for item_id in list(tree.selection()):
            tree.delete(item_id)

    tree.drop_target_register(DND_FILES)
    tree.dnd_bind('<<Drop>>', on_drop)
    tree.bind('<<TreeviewSelect>>', on_tree_select)

    context_menu = tk.Menu(root, tearoff=0)
    # context_menu.add_command(label="Exit", command=lambda: do_something("Exit"))
    context_menu.add_command(label="Select all", command=select_all)
    context_menu.add_command(label="Clear list", command=clear_list)

    root.bind("<Button-3>", show_popup)
    root.bind("<Control-a>", lambda e: select_all())
    root.bind("<Delete>", lambda e: delete_selected())

    label = tk.Label(root)
    scrollbar = ttk.Scrollbar(root, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)

    label.pack(side=tk.BOTTOM, fill=tk.X, pady=10, padx=10)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
    root.mainloop()
