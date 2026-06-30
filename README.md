# Stock and Inventory Web Hosting Project

This is the web-hostable version of the stock and inventory project.

## Project Requirements

1. Host a web application or service.
2. Use a public DNS name.
3. Configure SSL/HTTPS.

## Recommended Free Hosting

Use Render as a Web Service:

- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app`
- Public DNS name: Render provides a URL like `https://your-app-name.onrender.com`
- SSL certificate: Render provides HTTPS automatically for the public URL

## Run Locally

```bash
pip install -r requirements.txt
python app.py
```

Open:

```text
http://localhost:5000
```

## Deployment Steps

1. Put this `web_inventory_app` folder into a GitHub repository.
2. Create a Render account.
3. Choose **New +** then **Web Service**.
4. Connect your GitHub repository.
5. Use:

```text
Build Command: pip install -r requirements.txt
Start Command: gunicorn app:app
```

6. Deploy the app.
7. Open the Render public URL using `https://`.

## Screenshots to Submit

- GitHub repository files
- Render Web Service settings
- Build command and start command
- Public URL
- Website opened with HTTPS
- Browser lock icon / SSL certificate
