0. in GCP console

a. setup VM and eable http https
b. assign the whole_mouse_brain IP address to this VM

1. Install nginx and certbot

sudo apt update
sudo apt install nginx
sudo apt install certbot python3-certbot-nginx

sudo systemctl start nginx
sudo systemctl enable nginx
sudo systemctl status nginx.service

2. Create /etc/nginx/conf.d/myredirection.conf

a. copy nginx.no_ssl.conf

sudo cp ~/wmb-browser/nginx.no_ssl.conf /etc/nginx/conf.d/myredirection.conf

b. certbot to enable ssl

sudo certbot --nginx -d mousebrain.salk.edu

sudo systemctl restart nginx
sudo systemctl status nginx.service

c. add higlass

```
server {
    server_name mousebrain.salk.edu;
    listen 8001 ssl;

    ssl_certificate /etc/letsencrypt/live/mousebrain.salk.edu/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/mousebrain.salk.edu/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    location / {
        proxy_pass http://127.0.0.1:8989;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

d. modify higlass

Inside higlass docker, modify the uwsgi.ini file

/home/higlass/projects/uwsgi.ini

Change http = :8000 to http = :8001

```
[local]
ini = :base
http = :8001
# TODO: hgserver_nginx.conf says 8001: Is this one ignored?
```

sudo systemctl restart nginx
sudo systemctl status nginx.service

e. ingest higlass tileset

first ingest
hanqing-wmb-browser/notebooks/ingest_higlass.ipynb
then update uuid table
hanqing-wmb-browser/metadata/generate_higlass_tracks.ipynb

f. start gunicorn server
screen -R deploy
gunicorn -w 4 index:server -b 127.0.0.1:8000 --timeout 60 --access-logfile ~/access.log --error-logfile ~/error.log
