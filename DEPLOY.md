# Déploiement Trustline sur un VPS (Ubuntu 22.04 / 24.04, sans Docker)

Runbook pour la personne qui déploie. Pile : **Gunicorn** (serveur WSGI) +
**Nginx** (reverse proxy) + **PostgreSQL** + **Redis** + **systemd** (service).

> Remplacez partout : `VOTRE_DOMAINE` (ou l'IP), `MOT_DE_PASSE_DB`, et le chemin
> `/opt/trustline`. Les commandes `sudo` supposent un utilisateur non-root avec sudo.

---

## 1. Préparer le système
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-venv python3-pip git nginx \
                    postgresql postgresql-contrib redis-server
sudo systemctl enable --now postgresql redis-server nginx
```

## 2. Créer la base PostgreSQL
```bash
sudo -u postgres psql <<'SQL'
CREATE DATABASE trustline;
CREATE USER trustline_user WITH PASSWORD 'MOT_DE_PASSE_DB';
ALTER ROLE trustline_user SET client_encoding TO 'utf8';
ALTER ROLE trustline_user SET timezone TO 'Africa/Lome';
GRANT ALL PRIVILEGES ON DATABASE trustline TO trustline_user;
SQL
# PostgreSQL 15+ : donner aussi les droits sur le schéma public
sudo -u postgres psql -d trustline -c "GRANT ALL ON SCHEMA public TO trustline_user;"
```

## 3. Récupérer le code + environnement Python
```bash
sudo mkdir -p /opt/trustline && sudo chown $USER:$USER /opt/trustline
git clone VOTRE_REPO_GIT /opt/trustline
cd /opt/trustline

python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn            # serveur d'application (non inclus dans requirements)
```

## 4. Configurer le `.env` (production)
```bash
cp .env.example .env
# Générer une vraie clé secrète :
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
nano .env
```
Contenu `.env` en production :
```env
SECRET_KEY=<la_cle_generee_ci_dessus>
DEBUG=False
ALLOWED_HOSTS=VOTRE_DOMAINE,www.VOTRE_DOMAINE
DATABASE_URL=postgres://trustline_user:MOT_DE_PASSE_DB@localhost:5432/trustline
CACHE_URL=redis://127.0.0.1:6379/1
CORS_ALLOW_ALL_ORIGINS=True
```

## 5. Initialiser l'application
```bash
python manage.py migrate
python manage.py collectstatic --noinput      # requis car DEBUG=False
python manage.py createsuperuser
python manage.py seed_demo_data                # (optionnel) données de démo
# Test rapide avant de « systemd-iser » :
gunicorn config.wsgi:application --bind 127.0.0.1:8000   # Ctrl+C pour arrêter
```

## 6. Service systemd (Gunicorn)
```bash
sudo tee /etc/systemd/system/trustline.service > /dev/null <<'UNIT'
[Unit]
Description=Trustline Gunicorn
After=network.target postgresql.service redis-server.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/trustline
EnvironmentFile=/opt/trustline/.env
ExecStart=/opt/trustline/.venv/bin/gunicorn config.wsgi:application \
          --workers 3 --bind 127.0.0.1:8000
Restart=always

[Install]
WantedBy=multi-user.target
UNIT

sudo chown -R www-data:www-data /opt/trustline
sudo systemctl daemon-reload
sudo systemctl enable --now trustline
sudo systemctl status trustline --no-pager
```

## 7. Nginx (reverse proxy + fichiers statiques)
```bash
sudo tee /etc/nginx/sites-available/trustline > /dev/null <<'NGINX'
server {
    listen 80;
    server_name VOTRE_DOMAINE www.VOTRE_DOMAINE;

    location /static/ {
        alias /opt/trustline/staticfiles/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
NGINX

sudo ln -sf /etc/nginx/sites-available/trustline /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx
```

## 8. HTTPS (Let's Encrypt — recommandé)
```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d VOTRE_DOMAINE -d www.VOTRE_DOMAINE
# Renouvellement auto déjà planifié par le paquet certbot.
```

## 9. Pare-feu (optionnel)
```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

---

## Mettre à jour après un nouveau commit
```bash
cd /opt/trustline
sudo -u www-data git pull
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart trustline
```

## Vérifier / dépanner
```bash
curl -s http://127.0.0.1:8000/api/health/        # doit renvoyer {"status":"ok"}
sudo systemctl status trustline --no-pager        # état du service
sudo journalctl -u trustline -n 50 --no-pager     # logs Gunicorn/Django
sudo tail -f /var/log/nginx/error.log             # logs Nginx
```

---

## ⚠️ Notes importantes (à ne pas oublier avec `DEBUG=False`)

1. **CSRF admin en HTTPS** — Django 5 exige `CSRF_TRUSTED_ORIGINS` pour se
   connecter à `/admin/` derrière un domaine HTTPS. Ce réglage n'est pas encore
   lu depuis le `.env`. Deux options :
   - me demander d'ajouter le support `CSRF_TRUSTED_ORIGINS` dans
     `config/settings.py` (recommandé), **ou**
   - l'ajouter à la main dans `settings.py` :
     `CSRF_TRUSTED_ORIGINS = ["https://VOTRE_DOMAINE"]`.
2. **Fichiers statiques** — servis par Nginx (`/static/`). `collectstatic` est
   obligatoire à chaque déploiement car Django ne sert plus les statiques quand
   `DEBUG=False`.
3. **Redis** — ici on l'utilise vraiment en prod (`CACHE_URL`). Le rate limiting
   et le cache des vérifications de numéros s'appuient dessus.
4. **Secrets** — `.env` n'est pas versionné (`.gitignore`). Ne jamais commiter la
   `SECRET_KEY` ni le mot de passe DB.
