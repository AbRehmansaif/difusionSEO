#!/bin/bash
# ==============================================================================
#  DifusionSEO — VPS Deployment Script
#  Server: 38.242.254.102  |  Domain: difusionseo.com
#
#  HOW TO USE:
#  1. Upload your project:  scp -r "d:\Products\difusionseo" root@38.242.254.102:/var/www/
#  2. SSH in:               ssh root@38.242.254.102
#  3. Run this script:      bash /var/www/difusionseo/deploy/deploy.sh
# ==============================================================================
set -e

echo "🚀 Starting DifusionSEO deployment..."

# ── STEP 1: Install system dependencies ───────────────────────────────────────
echo "[1/8] Installing system packages..."
apt-get update -q
apt-get install -y python3 python3-pip python3-venv nginx git

# ── STEP 2: Set up Python virtual environment ─────────────────────────────────
echo "[2/8] Setting up virtual environment..."
cd /var/www/difusionseo
python3 -m venv env
source env/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q

# ── STEP 3: Create the production .env file ───────────────────────────────────
echo "[3/8] Creating /var/www/difusionseo/.env ..."
# Generate a random secret key automatically
SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))")
cat > /var/www/difusionseo/.env << EOF
DEBUG=False
SECRET_KEY=${SECRET}
ALLOWED_HOSTS=difusionseo.com,www.difusionseo.com,38.242.254.102
EOF
echo "✅ .env created with a generated SECRET_KEY."

# ── STEP 4: Run Django setup commands ─────────────────────────────────────────
echo "[4/8] Running migrate and collectstatic..."
python manage.py migrate --noinput
python manage.py collectstatic --noinput
deactivate

# ── STEP 5: Create log directories ────────────────────────────────────────────
echo "[5/8] Creating Gunicorn log directory..."
mkdir -p /var/log/gunicorn
touch /var/log/gunicorn/difusionseo-access.log
touch /var/log/gunicorn/difusionseo-error.log

# ── STEP 6: Create the systemd service at /etc/systemd/system/ ───────────────
echo "[6/8] Writing /etc/systemd/system/difusionseo.service ..."
cat > /etc/systemd/system/difusionseo.service << 'EOF'
[Unit]
Description=Gunicorn daemon for difusionseo
After=network.target

[Service]
User=root
Group=www-data
WorkingDirectory=/var/www/difusionseo
ExecStart=/var/www/difusionseo/env/bin/gunicorn \
          --access-logfile /var/log/gunicorn/difusionseo-access.log \
          --error-logfile /var/log/gunicorn/difusionseo-error.log \
          --workers 3 \
          --bind unix:/run/difusionseo.sock \
          difusionseo.wsgi:application

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable difusionseo
systemctl restart difusionseo
sleep 2
echo "Gunicorn status:"
systemctl status difusionseo --no-pager

# ── STEP 7: Create the Nginx server block at /etc/nginx/sites-available/ ──────
echo "[7/8] Writing /etc/nginx/sites-available/difusionseo ..."
cat > /etc/nginx/sites-available/difusionseo << 'EOF'
server {
    listen 80;
    server_name difusionseo.com www.difusionseo.com 38.242.254.102;

    access_log /var/log/nginx/difusionseo-access.log;
    error_log  /var/log/nginx/difusionseo-error.log;

    location /static/ {
        alias /var/www/difusionseo/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }

    location / {
        proxy_pass         http://unix:/run/difusionseo.sock;
        proxy_http_version 1.1;
        proxy_set_header   Host              $host;
        proxy_set_header   X-Real-IP         $remote_addr;
        proxy_set_header   X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto $scheme;
        proxy_read_timeout 120;
    }
}
EOF

# Enable it (symlink) and test — won't break your existing project
ln -sf /etc/nginx/sites-available/difusionseo /etc/nginx/sites-enabled/difusionseo
echo "[8/8] Testing Nginx config and reloading..."
nginx -t
systemctl reload nginx

echo ""
echo "✅ Deployment complete!"
echo "─────────────────────────────────────────────────────────────"
echo "  Live at:  http://difusionseo.com"
echo ""
echo "  To enable HTTPS run:"
echo "  apt-get install -y certbot python3-certbot-nginx"
echo "  certbot --nginx -d difusionseo.com -d www.difusionseo.com"
echo "─────────────────────────────────────────────────────────────"
