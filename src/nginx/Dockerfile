FROM nginx:alpine

# 必要なパッケージをインストール
RUN apk add --no-cache openssl

# 設定ファイルをコピー
COPY nginx.conf /etc/nginx/nginx.conf
COPY generate-ssl.sh /generate-ssl.sh

# 実行権限を付与
RUN chmod +x /generate-ssl.sh

# ポートを開放
EXPOSE 443

# 起動時にSSL証明書を生成し、Nginxを起動
CMD ["/bin/sh", "-c", "/generate-ssl.sh && nginx -g 'daemon off;'"]