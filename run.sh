#!/bin/bash

# Скрипт установки и настройки Emovia на Ubuntu сервере
# Сохраните как setup_emovia.sh, затем сделайте исполняемым: chmod +x setup_emovia.sh
# Запустите с sudo: sudo ./setup_emovia.sh

# Конфигурационные переменные
APP_NAME="emovia"
APP_USER="emoviauser"
APP_DIR="/opt/$APP_NAME"
APP_GROUP="www-data"
DOMAIN="ваш-домен-или-ip"  # Замените на ваш домен или IP

# Проверка на root
if [ "$(id -u)" -ne 0 ]; then
  echo "Этот скрипт должен выполняться с правами root. Используйте sudo." >&2
  exit 1
fi

# Установка зависимостей
echo "Установка системных зависимостей..."
apt update
apt install -y python3 python3-pip python3-venv nginx git

# Создание системного пользователя
echo "Создание пользователя $APP_USER..."
if ! id "$APP_USER" &>/dev/null; then
  adduser --system --group --no-create-home --disabled-login $APP_USER
fi

# Создание директории приложения
echo "Настройка директории приложения в $APP_DIR..."
mkdir -p $APP_DIR
chown $APP_USER:$APP_GROUP $APP_DIR
chmod 755 $APP_DIR

# Клонирование репозитория или копирование файлов
echo "Копирование файлов приложения..."
# Если используете git:
sudo -u $APP_USER git clone https://github.com/BadgerIvan/Emovia.git $APP_DIR
# Или копируйте файлы вручную в $APP_DIR

# Установка виртуального окружения и зависимостей
echo "Настройка Python окружения..."
sudo -u $APP_USER python3 -m venv $APP_DIR/venv
source $APP_DIR/venv/bin/activate
pip install --upgrade pip
pip install gunicorn flask

# Настройка сервиса Gunicorn
echo "Настройка службы Gunicorn..."
cat > /etc/systemd/system/$APP_NAME.service <<EOF
[Unit]
Description=Gunicorn instance for $APP_NAME
After=network.target

[Service]
User=$APP_USER
Group=$APP_GROUP
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
ExecStart=$APP_DIR/venv/bin/gunicorn --workers 3 --bind unix:$APP_DIR/$APP_NAME.sock -m 007 app:app

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl start $APP_NAME
systemctl enable $APP_NAME

# Настройка Nginx
echo "Настройка Nginx..."
cat > /etc/nginx/sites-available/$APP_NAME <<EOF
server {
    listen 80;
    server_name $DOMAIN;

    location / {
        include proxy_params;
        proxy_pass http://unix:$APP_DIR/$APP_NAME.sock;
    }

    location /static {
        alias $APP_DIR/static;
    }
}
EOF

ln -s /etc/nginx/sites-available/$APP_NAME /etc/nginx/sites-enabled
nginx -t
systemctl restart nginx

# Настройка брандмауэра
echo "Настройка UFW..."
ufw allow 'Nginx Full'
ufw enable

# Установка SSL (опционально, раскомментируйте если нужно)
echo "Установка SSL сертификата..."
apt install -y certbot python3-certbot-nginx
certbot --nginx -d $DOMAIN
systemctl restart nginx

echo "Установка завершена!"
echo "Ваше приложение доступно по адресу: http://$DOMAIN"
echo "Для управления сервисом:"
echo "  sudo systemctl restart $APP_NAME  # Перезапустить приложение"
echo "  sudo journalctl -u $APP_NAME      # Просмотр логов"