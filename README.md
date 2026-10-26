# Smart File Organizer

A safe, modern Python desktop application built with Tkinter for scanning, categorizing, and organizing files into structured directories.

## Features

- **Safe & Non-Destructive Scanning:** Preview all files and their planned destination paths before making any changes. Files are only moved or copied upon explicit confirmation.
- **Automated Categorization:** Automatically identifies and sorts files into curated categories:
  - Documents (`.pdf`, `.docx`, `.txt`, `.md`, etc.)
  - Images (`.png`, `.jpg`, `.svg`, `.webp`, etc.)
  - Videos (`.mp4`, `.mkv`, `.mov`, `.avi`, etc.)
  - Audio (`.mp3`, `.wav`, `.flac`, `.aac`, etc.)
  - Spreadsheets (`.xlsx`, `.csv`, `.ods`, etc.)
  - Presentations (`.pptx`, `.key`, `.odp`, etc.)
  - Programming (`.py`, `.js`, `.ts`, `.html`, `.css`, `.json`, etc.)
  - Archives (`.zip`, `.rar`, `.7z`, `.tar.gz`, etc.)
  - Installers (`.exe`, `.msi`, etc.)
  - 3D & CAD (`.stl`, `.obj`, `.fbx`, `.step`, etc.)
  - Databases, Fonts, Ebooks, Design assets, and more.
- **Organized Structure:** Files are sorted by category and format (e.g., `Destination/Images/PNG/photo.png`).
- **Interactive UI:**
  - Real-time search and category filtering.
  - Summary metrics displaying total files, size, and skipped items.
  - Detailed results table with file source, destination, size, and category.
- **Safety Safeguards:**
  - Checks against circular moves or selecting destination inside source.
  - Ignores directory and file symlinks to prevent unexpected modifications.
  - Conflict resolution to avoid accidental overwrites.

## Prerequisites

- Python 3.8 or later (Tkinter is included with standard Windows Python installations).

## How to Run

1. Clone the repository:
   ```bash
   git clone https://github.com/barathsri918/smart-file-organizer.git
   cd smart-file-organizer
   ```

2. Run the application:
   ```bash
   python main.py
   ```

## Usage

1. **Select Source Folder:** Choose the folder containing the files you wish to organize.
2. **Select Destination Folder:** Choose where the organized hierarchy should be created.
3. **Scan Files:** Review the table of identified files, their sizes, categories, and target locations.
4. **Filter & Search:** Use the search bar or category dropdown to inspect specific files.
5. **Organize:** Confirm the action to copy or move files to their designated folders safely.

## License

This project is licensed under the MIT License - feel free to use and modify!