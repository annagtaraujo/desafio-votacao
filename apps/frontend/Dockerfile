FROM nginx:alpine

# Copia o conteúdo estático
COPY index.html /usr/share/nginx/html/
COPY script.js /usr/share/nginx/html/

# Configuração apontamento do Nginx
COPY nginx.conf /etc/nginx/nginx.conf
