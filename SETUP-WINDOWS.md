# Setup guide — Windows + VS Code

## 1. Clone your profile repository

This repository is already named correctly: `dusssi/dusssi`.

```powershell
git clone https://github.com/dusssi/dusssi.git
cd dusssi
code .
```

## 2. Install dependencies

Use Python 3.11 if possible. In the VS Code terminal:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r scripts/requirements.txt
```

If PowerShell blocks activation:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## 3. Add your photo locally

Copy a clear, front-facing photo to the repository root and name it `source-photo.jpg`. It is excluded by `.gitignore`; the source photo is not pushed to GitHub.

```powershell
python scripts/prep_photo.py .\source-photo.jpg
python scripts/make_ascii_svg.py
python scripts/make_info_card.py
```

Check `dusssi-ascii.svg` before committing. The first run of background removal may download a model. If `rembg` cannot be installed or run, the preparation script falls back to the source image on a white background.

## 4. Render the contribution calendar

```powershell
python scripts/fetch_contributions.py
python scripts/render_heatmap_svg.py
```

The fetcher reads GitHub's public contributions page without a personal access token. It reports an error instead of fabricating data if GitHub changes the page structure or blocks the request.

## 5. Commit and push

```powershell
git add README.md scripts data .gitignore .github SETUP-WINDOWS.md contrib-heatmap.svg dusssi-ascii.svg info-card.svg
git commit -m "Add animated profile art generator"
git push origin main
```

## 6. Run the scheduled workflow

Open the repository's **Actions** tab, select **Update profile art**, and choose **Run workflow**. After the first successful run, it will commit updated contribution JSON and SVG output. Scheduled workflows run daily at 06:17 UTC (11:47 AM India Standard Time), though GitHub may delay scheduled runs.

## Notes

- Contribution totals are displayed only when the public HTML exposes counts; no totals are hard-coded.
- Streak figures are estimates derived from the visible calendar, not official API metrics.
- The portrait is generated locally. The scheduled GitHub Action does not use or access your photo.
- SVG animation behavior can vary by rendering environment; check the published profile after the first commit.
