# GitHub Cheat Sheet
## Open Design and Technology Final Project

This file is a quick guide for working in your project repository.

---

# 1. First setup

## Fork this repository
1. Click **Fork**.
2. Rename your fork using this format:


### Example
`ODT-2026-PixelWizards`

## Do not do this
- Do not keep the default repo name.
- Do not upload everything at the very end.
- Do not delete headings from the main `README.md`.

---

# 2. Folder structure

Your repository should look like this:

```text
project-repo/
├── README.md
├── CHEATSHEET.md
├── images/
├── code/
└── docs/
```

## What goes where

| Folder | What to put inside |
|---|---|
| `images/` | Sketches, photos, screenshots, UI mockups, circuit diagrams |
| `code/` | Main code files, test code, code notes |
| `docs/` | Extra notes, reference links, playtest notes |

---

# 3. Uploading files

## Upload an image
1. Open the repository.
2. Open the `images` folder.
3. Click **Add file**.
4. Click **Upload files**.
5. Drag your image into the browser.
6. Scroll down and click **Commit changes**.

## Upload code
1. Open the `code` folder.
2. Click **Add file**.
3. Click **Upload files**.
4. Upload your `.py`, `.ino`, `.txt`, or `.md` files.
5. Click **Commit changes**.

## Good file names
Use clean file names such as:
- `concept-sketch.jpg`
- `ui-mockup.png`
- `prototype-v1.jpg`
- `main.py`
- `ble-test.py`

## Avoid bad file names
Avoid names like:
- `IMG_4587.jpg`
- `finalfinalrealone.png`
- `new code latest.py`

---

# 4. Adding Images to your README


**Rule #1:** You must upload your image file to the `images/` folder *before* you can link it in the README. 

**Rule #2:** File names are case-sensitive. `Image.JPG` is not the same as `image.jpg`.

Shrike Lite image example 

---

### Example 1: The Basic Image (Markdown)
Use this for a standard, full-size image.

```html
<img src="images/Shrike-9-1-768x628.png" width="400">

```

### Example 2: Resizing an Image (HTML)
Phone photos are often massive. If an image takes up your whole screen, switch to HTML to control the width. *(Change `width="400"` to whatever number looks best).*

```html
<img src="images/Shrike-9-1-768x628.png" width="400">
```
<img src="images/Shrike-9-1-768x628.png" width="400">

### Example 3: Centering an Image
If you want your documentation to look clean and professional, you can center the image on the page using this HTML block.

```html
<p align="center">
  <img src="images/Shrike-9-1-768x628.png" width="400">
</p>
```
<p align="center">
<img src="images/Shrike-9-1-768x628.png" width="200">
</p>

### Example 4: Side-by-Side Images
Want to show the front and back of your build, or your app next to your hardware? Just put two HTML image tags on the exact same line with a space between them. 

```html
<img src="images/Shrike-9-1-768x628.png" width="300"> <img src="images/Shrike-9-1-768x628.png" width="300">
```
<img src="images/Shrike-9-1-768x628.png" width="300"> <img src="images/Shrike-9-1-768x628.png" width="300">

*(Note: Ensure their combined width is less than ~800 so they fit next to each other on most screens).*

---

### Quick Troubleshooting: "My image is just showing a broken link icon!"
If your image doesn't load when you click the **Preview** tab, check these 3 things:
1. **Path:** Did you include `images/` before the file name?
2. **Spelling/Spaces:** Does the code match your file name exactly? (Avoid spaces in file names—use dashes `-` instead).
3. **Extension:** Did you write `.png` but the file is actually a `.jpg`?
# 5. Editing README

## To edit the README directly on GitHub
1. Open `README.md`.
2. Click the pencil icon.
3. Add or update your content.
4. Scroll down.
5. Write a short commit message.
6. Click **Commit changes**.

## Update this file every hour
You should keep updating:
- task status,
- BOM,
- sketches,
- testing logs,
- playtesting notes,
- photos,
- bi hourly progress.

---

# 6. Creating folders on GitHub

GitHub does not create truly empty folders, so a folder is usually created by making a file inside it. [web:54][web:58]

## To create a folder from the GitHub website
1. Click **Add file**.
2. Click **Create new file**.
3. Type a path like:

```text
images/.gitkeep
```

4. Commit the change.

You can do the same for:
- `code/.gitkeep`
- `cad/.gitkeep`
- `docs/.gitkeep`

Typing a file path with a `/` is the usual way to create a folder in GitHub’s web interface. [web:54][web:57]

---

# 7. Commit message guide

Use short commit messages that explain what changed.

## Good examples
- `Added BOM and budget`
- `Uploaded concept sketch`
- `Updated week 2 progress`
- `Added BLE test code`
- `Uploaded final prototype photos`

## Bad examples
- `update`
- `stuff`
- `changes`
- `final`

---

# 8. Team workflow

## Suggested rule
At the end of every 2 hours, do these 4 things:
1. Upload new photos.
2. Update task status.
3. Add what worked and what failed.
4. Commit changes before leaving class.

## Team habit
One person can lead the build update for the day, but both team members are responsible for checking that the repo stays current.

---

# 9. If you make a mistake

## If you uploaded the wrong file
- Upload the correct file.
- Delete the wrong file.
- Write a clear commit message.

## If you deleted something important
- Tell your teammate immediately.
- Check the file history.
- Restore it from an earlier version if needed.

## If your README looks broken
- Check for missing `#`, `|`, or backticks.
- Preview before committing.

---

# 10. Minimum expectation each week

By the end of each week, your repository should show visible progress.

## Session 1
- Idea
- Sketch
- Inspiration
- BOM
- Task plan

## Session 2
- Tests
- Code or app progress
- Photos

## Session 3
- Integrated prototype
- Technical debugging
- Gameplay/playtesting notes

## Session 4
- Final build
- Final documentation
- Reflection
- Clean repo

---

# 11. Final reminder

This repository is not just a place to submit work.

It is:
- your project tracker,
- your evidence of process,
- your design notebook,
- your technical log,
- your final documentation.
