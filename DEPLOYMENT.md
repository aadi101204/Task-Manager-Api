# Deployment & Access Guide

This guide explains how to access the Task Manager application from other devices and how to deploy it to the cloud.

## 1. Local Network Access (Home/Office Wi-Fi)

To allow other devices (phones, laptops) on the same Wi-Fi network to access your running application:

### Prerequisites
1. Ensure your Windows Network usage is set to **Private** (to allow connections).
2. Find your computer's local IP address:
   - Open PowerShell and run: `ipconfig`
   - Look for "IPv4 Address" (e.g., `192.168.1.15`)

### Backend config
The backend running in Docker is already configured to listen on `0.0.0.0:8000`. It is accessible at:
`http://<YOUR_IP_ADDRESS>:8000`

### Frontend config
The Access-Control-Allow-Origin (CORS) check might fail if not configured.
1. Open `.env` in the root directory.
2. Update `BACKEND_CORS_ORIGINS` to include your Network IP:
   ```env
   BACKEND_CORS_ORIGINS='["http://localhost:5173", "http://<YOUR_IP_ADDRESS>:5173"]'
   ```
3. Restart Docker: `docker compose up -d`

### Accessing it
- On your other device, open a browser and go to: `http://<YOUR_IP_ADDRESS>:5173`

---

## 2. Public Access for Demos (Ngrok)

If you want to show your app to someone outside your network without deploying:

1. Download and install [Ngrok](https://ngrok.com/).
2. Run two tunnels (one for backend, one for frontend):

   **Backend:**
   ```bash
   ngrok http 8000
   ```
   *Copy the generated HTTPS URL (e.g., `https://api-123.ngrok-free.app`)*

   **Frontend:**
   ```bash
   ngrok http 5173
   ```
   *Copy the generated HTTPS URL (e.g., `https://front-456.ngrok-free.app`)*

3. **Update Configuration:**
   - Add the frontend Ngrok URL to `BACKEND_CORS_ORIGINS` in `.env`.
   - Update the frontend API URL in `frontend/src/pages/Register.tsx` (and others) to point to the backend Ngrok URL instead of `localhost`.

---

## 3. Cloud Deployment (Production)

For permanent access, deploy to a cloud provider.

### Vercel (Recommended for Full Stack)

This repository is configured for easy deployment on Vercel.

1. **Push your code to GitHub**.
2. **Import project into Vercel**.
3. **Environment Variables**:
   Add the following variables in Vercel project settings:
   - `DATABASE_URL`: Your production PostgreSQL database URL (e.g., from Neon or Supabase).
   - `SECRET_KEY`: A strong secret key.
   - `ALGORITHM`: `HS256`.
   - `ACCESS_TOKEN_EXPIRE_MINUTES`: `30`.
   - `BACKEND_CORS_ORIGINS`: `["https://your-vercel-app-url.vercel.app"]`.

### Alternative: Render / Railway

These platforms support Docker directly.

1. **Push your code to GitHub**.
2. **Create a new Service** on Render/Railway.
3. **Connect your repository**.
4. **Environment Variables**:
   Add the contents of your `.env` file to the dashboard environments variables.
   - Change `DATABASE_URL` to the production database provided by the platform.
   - Update `BACKEND_CORS_ORIGINS` to the production frontend URL.

### Docker Image
Your `Dockerfile` is production-ready.
- It uses a multi-stage build for small size.
- It runs with `gunicorn` for performance.
- It runs as a non-root user (`appuser`) for security.
