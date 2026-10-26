
import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path

# Smart File Organizer
# Scanning is read-only. Files change only after explicit confirmation.

source_folder = ""
destination_folder = ""
scanned_files = []

CATEGORIES = {
    "Documents": [
        ".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt",
        ".md", ".pages"
    ],
    "Images": [
        ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg",
        ".webp", ".tiff", ".tif", ".heic", ".ico"
    ],
    "Videos": [
        ".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv",
        ".webm", ".m4v", ".mpeg", ".mpg", ".3gp"
    ],
    "Audio": [
        ".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma",
        ".m4a", ".aiff", ".opus"
    ],
    "Spreadsheets": [
        ".xlsx", ".xls", ".csv", ".ods", ".tsv"
    ],
    "Presentations": [
        ".ppt", ".pptx", ".odp", ".key"
    ],
    "Programming": [
        ".py", ".js", ".ts", ".jsx", ".tsx", ".html",
        ".css", ".java", ".c", ".cpp", ".h", ".cs",
        ".php", ".rb", ".go", ".rs", ".json", ".xml",
        ".yaml", ".yml", ".sh", ".bat", ".ps1", ".sql",
        ".ipynb"
    ],
    "Archives": [
        ".zip", ".rar", ".7z", ".tar", ".gz", ".bz2",
        ".xz", ".tgz"
    ],
    "Installers": [
        ".exe", ".msi", ".msix", ".appx", ".deb", ".rpm"
    ],
    "Databases": [
        ".db", ".sqlite", ".sqlite3", ".mdb", ".accdb"
    ],
    "Design": [
        ".psd", ".ai", ".blend", ".fig", ".sketch",
        ".xcf", ".indd"
    ],
    "3D_CAD": [
        ".stl", ".obj", ".step", ".stp", ".3mf",
        ".fbx", ".gltf", ".glb", ".dwg", ".dxf"
    ],
    "Fonts": [
        ".ttf", ".otf", ".woff", ".woff2"
    ],
    "Ebooks": [
        ".epub", ".mobi", ".azw", ".azw3"
    ],
}

EXTENSION_TO_CATEGORY = {
    extension: category
    for category, extensions in CATEGORIES.items()
    for extension in extensions
}


def get_category(file_path):
    return EXTENSION_TO_CATEGORY.get(
        file_path.suffix.lower(), "Others"
    )


def get_format_folder(file_path):
    return file_path.suffix[1:].upper() if file_path.suffix else "NO_EXTENSION"


def is_inside(path, parent):
    """Return True if path is parent or is inside parent."""
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def format_size(size):
    """Convert bytes into a readable file size."""
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024 or unit == "TB":
            return f"{size:.1f} {unit}" if unit != "B" else f"{size} B"
        size /= 1024
    return f"{size:.1f} TB"


def clear_results():
    global scanned_files
    scanned_files = []

    summary_label.config(text="Select folders, then click Scan Files.")
    search_entry.delete(0, tk.END)
    category_filter.set("All categories")

    for row in results_table.get_children():
        results_table.delete(row)


def select_source():
    global source_folder

    folder = filedialog.askdirectory(
        title="Select the folder you want to organize"
    )

    if folder:
        source_folder = folder
        source_label.config(text=folder)
        clear_results()


def select_destination():
    global destination_folder

    folder = filedialog.askdirectory(
        title="Select where organized files should be saved"
    )

    if folder:
        destination_folder = folder
        destination_label.config(text=folder)
        clear_results()


def scan_files():
    """Scan files without copying, moving, renaming, or deleting them."""
    global scanned_files

    if not source_folder or not destination_folder:
        messagebox.showwarning(
            "Missing folder",
            "Please select both source and destination folders."
        )
        return

    source = Path(source_folder).resolve()
    destination = Path(destination_folder).resolve()

    if not source.is_dir() or not destination.is_dir():
        messagebox.showerror(
            "Invalid folder",
            "The selected source and destination must both exist."
        )
        return

    if source == destination:
        messagebox.showerror(
            "Invalid folders",
            "Source and destination cannot be the same folder."
        )
        return

    if is_inside(destination, source):
        messagebox.showerror(
            "Unsafe destination",
            "Choose a destination outside the source folder.\n\n"
            "This prevents the organizer from scanning its own output."
        )
        return

    scanned_files = []
    skipped = 0

    try:
        # Do not follow directory symlinks.
        for root, dirs, files in os.walk(source, followlinks=False):
            # Avoid scanning symlinked directories.
            dirs[:] = [
                name for name in dirs
                if not (Path(root) / name).is_symlink()
            ]

            for filename in files:
                file_path = Path(root) / filename

                try:
                    # Ignore symlinked files to avoid unexpected targets.
                    if file_path.is_symlink() or not file_path.is_file():
                        skipped += 1
                        continue

                    size = file_path.stat().st_size
                    category = get_category(file_path)
                    format_folder = get_format_folder(file_path)

                    planned_destination = (
                        destination / category / format_folder / filename
                    )

                    scanned_files.append({
                        "source": file_path,
                        "name": filename,
                        "category": category,
                        "extension": file_path.suffix.lower() or "(none)",
                        "size": size,
                        "destination": planned_destination,
                    })

                except OSError:
                    skipped += 1

    except OSError as error:
        messagebox.showerror(
            "Scan error",
            f"Could not scan the selected folder:\n{error}"
        )
        return

    scanned_files.sort(
        key=lambda item: (
            item["category"].lower(),
            item["name"].lower()
        )
    )

    refresh_results()

    total_size = sum(item["size"] for item in scanned_files)

    summary_label.config(
        text=(
            f"Found {len(scanned_files)} files | "
            f"Total size: {format_size(total_size)} | "
            f"Skipped: {skipped}"
        )
    )

    if not scanned_files:
        messagebox.showinfo(
            "Scan complete",
            "No accessible files were found in the selected folder."
        )


def refresh_results():
    """Refresh the preview according to the search and category filters."""
    for row in results_table.get_children():
        results_table.delete(row)

    search_text = search_entry.get().strip().lower()
    selected_category = category_filter.get()

    visible_count = 0

    for item in scanned_files:
        if (
            selected_category != "All categories"
            and item["category"] != selected_category
        ):
            continue

        searchable_text = (
            f'{item["name"]} {item["category"]} '
            f'{item["extension"]} {item["source"]}'
        ).lower()

        if search_text and search_text not in searchable_text:
            continue

        results_table.insert(
            "",
            tk.END,
            values=(
                item["name"],
                item["category"],
                item["extension"],
                format_size(item["size"]),
                str(item["source"]),
                str(item["destination"]),
            )
        )

        visible_count += 1

    if scanned_files:
        summary_label.config(
            text=(
                f"Showing {visible_count} of {len(scanned_files)} files"
            )
        )


def get_unique_destination(destination):
    """Choose a new filename rather than overwrite an existing file."""
    if not destination.exists():
        return destination

    stem = destination.stem
    suffix = destination.suffix
    parent = destination.parent
    counter = 1

    while True:
        candidate = parent / f"{stem} ({counter}){suffix}"

        if not candidate.exists():
            return candidate

        counter += 1


def organize_files(operation):
    """Copy or move the scanned files after explicit confirmation."""
    if operation not in ("copy", "move"):
        return

    if not scanned_files:
        messagebox.showwarning(
            "Nothing to organize",
            "Scan the source folder first."
        )
        return

    source = Path(source_folder).resolve()
    destination = Path(destination_folder).resolve()

    if not source.is_dir() or not destination.is_dir():
        messagebox.showerror(
            "Folder unavailable",
            "The source or destination folder no longer exists."
        )
        return

    if source == destination or is_inside(destination, source):
        messagebox.showerror(
            "Unsafe folders",
            "Please choose a different destination and scan again."
        )
        return

    action = "COPY" if operation == "copy" else "MOVE"

    confirmed = messagebox.askyesno(
        f"Confirm {action.lower()}",
        f"Are you sure you want to {action.lower()} "
        f"{len(scanned_files)} files?\n\n"
        f"From:\n{source}\n\n"
        f"To:\n{destination}\n\n"
        + (
            "Original files will remain in the source folder."
            if operation == "copy"
            else "Original files will be moved. This changes their locations."
        )
    )

    if not confirmed:
        return

    successful = 0
    failed = 0
    errors = []

    # Process a snapshot of the preview.
    for item in list(scanned_files):
        original = Path(item["source"])

        try:
            # Verify that the source still belongs to the chosen folder.
            resolved_source = original.resolve(strict=True)

            if not is_inside(resolved_source, source):
                raise ValueError("File is no longer inside the source folder.")

            if not resolved_source.is_file() or original.is_symlink():
                raise ValueError("Source is no longer a regular file.")

            # Recalculate the destination from the current settings.
            category = get_category(resolved_source)
            format_folder = get_format_folder(resolved_source)

            target_directory = destination / category / format_folder
            target_directory.mkdir(parents=True, exist_ok=True)

            target = get_unique_destination(
                target_directory / resolved_source.name
            )

            # Avoid overwriting an existing destination.
            if operation == "copy":
                shutil.copy2(resolved_source, target)
            else:
                shutil.move(str(resolved_source), str(target))

            successful += 1

        except (OSError, shutil.Error, ValueError) as error:
            failed += 1
            errors.append(f"{original.name}: {error}")

    # Refresh the preview because moved files may no longer exist at source.
    if operation == "move":
        scan_files()
    else:
        summary_label.config(
            text=f"Copy complete: {successful} succeeded, {failed} failed."
        )

    result_message = (
        f"Operation: {action}\n\n"
        f"Successful: {successful}\n"
        f"Failed: {failed}"
    )

    if errors:
        result_message += "\n\nFirst errors:\n" + "\n".join(errors[:8])

        if len(errors) > 8:
            result_message += f"\n...and {len(errors) - 8} more."

    if failed:
        messagebox.showwarning("Operation finished", result_message)
    else:
        messagebox.showinfo("Operation finished", result_message)


# -------------------- GUI --------------------

root = tk.Tk()
root.title("Smart File Organizer")
root.geometry("1200x680")
root.minsize(850, 500)

main_frame = ttk.Frame(root, padding=12)
main_frame.pack(fill=tk.BOTH, expand=True)

title_label = ttk.Label(
    main_frame,
    text="Smart File Organizer",
    font=("Segoe UI", 20, "bold")
)
title_label.pack(anchor=tk.W, pady=(0, 10))

ttk.Label(
    main_frame,
    text="Scan first. Review the preview. Copy or move only after confirmation."
).pack(anchor=tk.W, pady=(0, 12))

# Folder selection
folder_frame = ttk.LabelFrame(
    main_frame, text="Folder Selection", padding=10
)
folder_frame.pack(fill=tk.X, pady=(0, 10))

ttk.Button(
    folder_frame,
    text="Select Source",
    command=select_source
).grid(row=0, column=0, sticky=tk.W, padx=(0, 8), pady=4)

source_label = ttk.Label(
    folder_frame,
    text="No source selected",
    wraplength=950
)
source_label.grid(row=0, column=1, sticky=tk.W, pady=4)

ttk.Button(
    folder_frame,
    text="Select Destination",
    command=select_destination
).grid(row=1, column=0, sticky=tk.W, padx=(0, 8), pady=4)

destination_label = ttk.Label(
    folder_frame,
    text="No destination selected",
    wraplength=950
)
destination_label.grid(row=1, column=1, sticky=tk.W, pady=4)

folder_frame.columnconfigure(1, weight=1)

# Search and filtering
filter_frame = ttk.Frame(main_frame)
filter_frame.pack(fill=tk.X, pady=(0, 8))

ttk.Label(filter_frame, text="Search:").pack(side=tk.LEFT)

search_entry = ttk.Entry(filter_frame, width=30)
search_entry.pack(side=tk.LEFT, padx=(6, 12))
search_entry.bind("<KeyRelease>", lambda event: refresh_results())

ttk.Label(filter_frame, text="Category:").pack(side=tk.LEFT)

category_filter = tk.StringVar(value="All categories")

category_dropdown = ttk.Combobox(
    filter_frame,
    textvariable=category_filter,
    values=["All categories"] + sorted(set(CATEGORIES) | {"Others"}),
    state="readonly",
    width=18
)
category_dropdown.pack(side=tk.LEFT, padx=6)
category_dropdown.bind(
    "<<ComboboxSelected>>",
    lambda event: refresh_results()
)

ttk.Button(
    filter_frame,
    text="Scan Files",
    command=scan_files
).pack(side=tk.RIGHT)

# Preview table
table_frame = ttk.Frame(main_frame)
table_frame.pack(fill=tk.BOTH, expand=True)

columns = (
    "name",
    "category",
    "extension",
    "size",
    "source",
    "destination",
)

results_table = ttk.Treeview(
    table_frame,
    columns=columns,
    show="headings",
    selectmode="extended"
)

headings = {
    "name": "File Name",
    "category": "Category",
    "extension": "Extension",
    "size": "Size",
    "source": "Current Location",
    "destination": "Planned Destination",
}

widths = {
    "name": 170,
    "category": 105,
    "extension": 80,
    "size": 85,
    "source": 300,
    "destination": 330,
}

for column in columns:
    results_table.heading(column, text=headings[column])
    results_table.column(
        column,
        width=widths[column],
        minwidth=60,
        anchor=tk.W
    )

vertical_scrollbar = ttk.Scrollbar(
    table_frame,
    orient=tk.VERTICAL,
    command=results_table.yview
)

horizontal_scrollbar = ttk.Scrollbar(
    table_frame,
    orient=tk.HORIZONTAL,
    command=results_table.xview
)

results_table.configure(
    yscrollcommand=vertical_scrollbar.set,
    xscrollcommand=horizontal_scrollbar.set
)

results_table.grid(row=0, column=0, sticky="nsew")
vertical_scrollbar.grid(row=0, column=1, sticky="ns")
horizontal_scrollbar.grid(row=1, column=0, sticky="ew")

table_frame.rowconfigure(0, weight=1)
table_frame.columnconfigure(0, weight=1)

# Summary and actions
summary_label = ttk.Label(
    main_frame,
    text="Select folders, then click Scan Files."
)
summary_label.pack(anchor=tk.W, pady=8)

action_frame = ttk.Frame(main_frame)
action_frame.pack(fill=tk.X, pady=(0, 2))

ttk.Button(
    action_frame,
    text="Copy Files",
    command=lambda: organize_files("copy")
).pack(side=tk.LEFT, padx=(0, 8))

ttk.Button(
    action_frame,
    text="Move Files",
    command=lambda: organize_files("move")
).pack(side=tk.LEFT, padx=(0, 8))

ttk.Button(
    action_frame,
    text="Clear Preview",
    command=clear_results
).pack(side=tk.LEFT)

ttk.Label(
    action_frame,
    text="Existing files are not overwritten.",
).pack(side=tk.RIGHT)

root.mainloop()
