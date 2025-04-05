sudo apt update
sudo apt install python3 python3-pip nginx

pip3 install flask gunicorn

gunicorn --bind 0.0.0.0:8000 wsgi:app


sudo vim /etc/systemd/system/emovia.service

[Unit]
Description=Gunicorn instance for Emovia
After=network.target

[Service]
User=user
Group=www-data
WorkingDirectory=/home/user/emovia
Environment="PATH=/home/user/emovia/venv/bin"
ExecStart=/home/user/emovia/venv/bin/gunicorn --workers 3 --bind unix:emovia.sock -m 007 wsgi:app

[Install]
WantedBy=multi-user.target

sudo systemctl start emovia
sudo systemctl enable emovia

sudo vim /etc/nginx/sites-available/emovia

server {
    listen 80;
    server_name ваш_домен_или_IP;

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/user/emovia/emovia.sock;
    }

    location /static {
        alias /home/user/emovia/static;
    }
}

sudo ln -s /etc/nginx/sites-available/emovia /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx

sudo ufw allow 'Nginx Full'

sudo chmod 664 /home/user/emovia/emovia.db
sudo chown www-data:www-data /home/user/emovia/emovia.db

sudo systemctl status emovia
sudo journalctl -u emovia
