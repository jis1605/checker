# プロジェクト概要
G-FinderのElasticsearchに登録されたドキュメントデータが正しく登録されているかを確認しやすくするためのツールとして開発した。

# 利用者向けセクション
## チュートリアル（ツールの基本的な使い方）

* １段目の出力には、選択フォームで選択した条件で絞り込んだデータ（資料のページ毎に別れたデータ）一覧が表示される。
* １段目の出力は、最大5,000件までしか表示しない。
* ２段目の出力には、選択フォームで選択した条件で絞り込んだデータをcode(自治体コード)毎に集計した結果が表示される。

# 開発者向けセクション
## 開発環境のセットアップ・ローカル実行の手順
### セットアップ
1. ```/streamlit_gfinder```のディレクトリ階層に移動する ※必要なら、仮想環境を構築してください。

2. 必要なパッケージをインストールする

    ```pip install -r requirements.txt```

3. ```/streamlit_gfinder```ディレクトリに下記情報を記載した.envファイルを作成する

    ```.env
    DEV_ELASTIC_ENDPOINT = "エンドポイントを入力する"
    DEV_ELASTIC_USER_ID = "IDを入力する"
    DEV_ELASTIC_PASSWORD = "パスワードを入力する"

    PROD_ELASTIC_ENDPOINT = "エンドポイントを入力する"
    PROD_ELASTIC_USER_ID = "IDを入力する"
    PROD_ELASTIC_PASSWORD = "パスワードを入力する"
    ```

    接続するElasticsearchへの接続情報・認証情報を入力する。
    ```DEV_*```と```PROD_*```のどちらかの入力でも動作する。

### ローカルでの実行
4. Streamlitを起動する。

    ```
    streamlit run streamlit_gfinder.py
    ```

## テスト方法・手順
ユニットテストは未実装。

## デプロイ手順
デプロイ手順は下記公式ドキュメントを参照すること。

[Streamlit Community Cloud公式ドキュメント - Deploy your app](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app)

## 設計資料・規約等の参照リンク
* 一覧に表示されるデータ項目について、下記ドキュメントを参照すること。

    [Elasticsearch Index Mapping設計書](https://www.notion.so/glocal-biz/Elasticsearch-Index-Mapping-73a570069d904a25b28a5a840a20c261)