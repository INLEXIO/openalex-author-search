[theme]
primaryColor = "#164A78"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

[server]
maxUploadSize = 200
```

---

## Step 2: Deploy to Streamlit Cloud (Free)

1. **Create a GitHub account** (if you don't have one): github.com

2. **Create a new repository**:
   - Go to github.com/new
   - Name it: `openalex-author-search`
   - Make it Public
   - Click "Create repository"

3. **Upload your files**:
   - Click "uploading an existing file"
   - Drag and drop:
     - `streamlit_app.py`
     - `requirements.txt`
     - `.streamlit/config.toml` (optional)
   - Click "Commit changes"

4. **Deploy to Streamlit Cloud**:
   - Go to: https://share.streamlit.io
   - Click "New app"
   - Connect your GitHub account
   - Select your repository: `openalex-author-search`
   - Main file: `streamlit_app.py`
   - Click "Deploy!"

5. **Wait 2-3 minutes** - Your app will be live at:
```
   https://[your-username]-openalex-author-search.streamlit.app