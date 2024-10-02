# ベースイメージを指定
FROM python:3.9-slim

# 環境変数の設定
ENV PYTHONUNBUFFERED=1

# 作業ディレクトリを作成
WORKDIR /app

# 必要なパッケージをインストール
# RUN apt-get update && apt-get install -y netcat-openbsd
RUN apt-get update && apt-get install -y \
    gcc \
    bash \
    musl-dev \
    libjpeg-dev \
    zlib1g-dev \
    libffi-dev \
    libcairo2-dev \
    libpango1.0-dev \
    libgdk-pixbuf2.0-dev \
    netcat-openbsd \
    redis-tools

# requirements.txtをコピー
COPY requirements.txt .

# 依存関係をインストール
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションのソースコードをコピー
COPY . .

# エントリーポイントスクリプトをコピー
COPY script/entrypoint.sh .

# エントリーポイントスクリプトに実行権限を付与
RUN chmod +x entrypoint.sh

# ポートを開放
EXPOSE 4242

# デフォルトコマンドとしてエントリーポイントスクリプトを指定
ENTRYPOINT ["./entrypoint.sh"]