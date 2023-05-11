FROM nginx

# Replace the default configuration in NGINX image with our custom configuration
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d/default.conf