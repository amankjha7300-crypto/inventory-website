# S60 Inventory & Rewards - Web Portal & API

Clean, standalone web deployment package containing only:
- Static Web Frontend (HTML, CSS, JS, Assets, Vendor icons)
- Essential FastAPI Serverless Backend (under `api/index.py` & `app/`)
- SQLite Seeded Database (`s60inventory.db`)
- Vercel Serverless Configuration (`vercel.json`)

## Deployment on Vercel

### Option 1: Via GitHub
1. Create a repository on GitHub (e.g. `inventory-website`).
2. Run:
   ```bash
   git remote add origin https://github.com/amankjha7300-crypto/inventory-website.git
   git push -u origin main
   ```
3. Import on [vercel.com/new](https://vercel.com/new) and click **Deploy**.

### Option 2: Via Vercel CLI
Run inside this directory:
```bash
npx vercel
```
