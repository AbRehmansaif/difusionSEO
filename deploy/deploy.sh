#!/bin/bash
# ==============================================================================
#  DifusionSEO — VPS Deployment Script
#  Repo:   https://github.com/AbRehmansaif/difusionSEO.git
#  Server: 38.242.254.102  |  Domain: difusionseo.com
#
#  HOW TO USE:
#  1. SSH into your server:  ssh root@38.242.254.102
#  2. Run this one command:
#     bash <(curl -s https://raw.githubusercontent.com/AbRehmansaif/difusionSEO/main/deploy/deploy.sh)
# ==============================================================================
set -e

echo "🚀 Starting DifusionSEO deployment..."

# ── STEP 1: Install system dependencies ───────────────────────────────────────
echo "[1/8] Installing system packages..."
apt-get update -q
apt-get install -y python3 python3-pip python3-venv nginx git curl

# ── STEP 2: Clone the project from GitHub ─────────────────────────────────────
echo "[2/8] Cloning project from GitHub..."
if [ -d "/var/www/difusionseo/.git" ]; then
    echo "   → Repo already exists, pulling latest changes..."
    cd /var/www/difusionseo
    git pull origin main
else
    echo "   → Fresh clone..."
    rm -rf /var/www/difusionseo
    git clone https://github.com/AbRehmansaif/difusionSEO.git /var/www/difusionseo
    cd /var/www/difusionseo
fi

# ── STEP 3: Set up Python virtual environment ─────────────────────────────────
echo "[3/8] Setting up virtual environment..."
python3 -m venv /var/www/difusionseo/env
source /var/www/difusionseo/env/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q

# ── STEP 4: Create the production .env file ───────────────────────────────────
echo "[4/8] Creating /var/www/difusionseo/.env ..."
if [ -f "/var/www/difusionseo/.env" ]; then
    echo "   → .env already exists, skipping to preserve your settings."
else
    SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))")
    cat > /var/www/difusionseo/.env << EOF
DEBUG=False
SECRET_KEY=${SECRET}
ALLOWED_HOSTS=difusionseo.com,www.difusionseo.com,38.242.254.102
EOF
    echo "   → .env created with auto-generated SECRET_KEY."
fi

# ── STEP 5: Run Django setup commands ─────────────────────────────────────────
echo "[5/8] Running migrate and collectstatic..."
python manage.py migrate --noinput
python manage.py collectstatic --noinput
deactivate

# ── STEP 6: Create Gunicorn log directory ─────────────────────────────────────
echo "[6/8] Creating Gunicorn log directory..."
mkdir -p /var/log/gunicorn
touch /var/log/gunicorn/difusionseo-access.log
touch /var/log/gunicorn/difusionseo-error.log

# ── STEP 7: Create systemd service at /etc/systemd/system/ ───────────────────
echo "[7/8] Writing /etc/systemd/system/difusionseo.service ..."
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

# ── STEP 8: Create Nginx server block at /etc/nginx/sites-available/ ──────────
echo "[8/8] Writing /etc/nginx/sites-available/difusionseo ..."
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

ln -sf /etc/nginx/sites-available/difusionseo /etc/nginx/sites-enabled/difusionseo
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
