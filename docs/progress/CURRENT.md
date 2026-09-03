# book-api 現在の進捗

## このファイルの役割

このファイルは、book-apiプロジェクトの「現在地」を管理するためのファイルです。

Codexは学習・開発を再開するとき、このファイルを確認し、

- 現在どのPhase・Stepにいるか
- 何が完了しているか
- 現在何をしているか
- 次に何をするか
- どこから講義を再開するか
- 未解決の問題があるか

を把握してください。

このファイルは履歴を長期間蓄積するためのものではありません。

過去の重要な完了事項・設計判断・問題と解決などは、
`docs/progress/HISTORY.md` に記録します。

---

# 現在地

## 現在のPhase

Phase 6：Book CRUDを完成させる

## 現在のStep

Step 6-1：Book作成。

アプリケーションの実装を開始しています。

---

# 完了済み

以下のプロジェクト方針文書を作成済みです。

- `docs/ROADMAP.md`
- `docs/TEACHING_RULES.md`
- `docs/DEVELOPMENT_LEARNING_POLICY.md`

以下の進捗管理ファイルを作成済みです。

- `docs/progress/CURRENT.md`
- `docs/progress/HISTORY.md`

Codexへの常設指示を記述した、
`AGENTS.md` も作成済みです。

Phase 0 / Step 0-1で、リポジトリ、Git・GitHub接続、
Python、PostgreSQLの現在の状態を確認済みです。

Phase 0 / Step 0-2で、読書の学びを仕事や日常で活用し、
新しい本との出会いを次の学びへつなげるサービスの目的を確認済みです。

Phase 0 / Step 0-3で、登録前の閲覧から、読みたいリスト、読書記録、
読了投稿、タイムライン、AI活用案、リマインドまでのユーザー操作を確認済みです。

Phase 0 / Step 0-4で、機能を一度に作るとエラーの原因範囲が広がるため、
1機能ずつ実装・動作確認する理由を確認済みです。

Phase 1 / Step 1-1からStep 1-3で、Python 3.14.7への更新、
`.venv` の作成と有効化、Pythonとpipの参照先の確認まで完了しています。

Phase 1 / Step 1-4で、最小構成としてFastAPIとUvicornを
プロジェクト専用の仮想環境へ導入しました。

Phase 1 / Step 1-5で、直接利用するライブラリの名前とバージョンを
`requirements.txt` に記録しました。

Phase 1 / Step 1-6で、最初はリポジトリ直下の `main.py` だけで始め、
機能が増えてから役割ごとのディレクトリへ分割する方針を決めました。

Phase 1 / Step 1-7で、プロジェクト直下の `.gitignore` に `.venv/` を記録し、
仮想環境をGit管理から除外する方針を確認しました。

Phase 2 / Step 2-1で、`main.py` にFastAPIアプリ本体、`GET /` のルート、
辞書を返す `read_root` 関数を作成しました。

Phase 2 / Step 2-2からStep 2-3でUvicornを起動し、ブラウザから `GET /` を送り、
`{"message": "book-api"}` が表示されることを確認しました。

Phase 2 / Step 2-4で、FastAPIはHTTPメソッドとURLパスの組み合わせから
実行する関数を選び、未登録パスは404、許可されないメソッドは405を返すと確認しました。

Phase 2 / Step 2-5でSwagger UIから `GET /` を実行し、
ステータス200と期待したJSONレスポンスを確認しました。

Phase 3 / Step 3-1で、最初のBookは `id`、`title`、`author`、任意の `isbn` を
持つことと、本を大量に事前登録しない方針を決めました。

Phase 3 / Step 3-2で、固定した『GANTZ 1』の4項目を返す
`GET /books/1` を作り、Swagger UIでステータス200とJSONを確認しました。

ローカル開発でUvicornを起動するときは、コード変更後の手動再起動を避けるため、
`python -m uvicorn main:app --reload` を使用します。

Phase 3 / Step 3-3で、3冊の固定Bookを `books` リストへまとめ、
`GET /books` がJSON配列を返すことをSwagger UIで確認しました。

Phase 3 / Step 3-4からPhase 4 / Step 4-1で、実行中のメモリへ追加したBookは
アプリ停止時に消えるため、永続保存するDBが必要だと確認しました。

Phase 4 / Step 4-2で、複数ユーザー、本番運用、データ間の関係や制約を扱う
サービス要件を踏まえ、PostgreSQLを採用しました。

Phase 4 / Step 4-3からStep 4-4で、`book_api`と専用ユーザーを作成し、
Pydantic Settings、SQLAlchemy、Psycopgを通した接続に成功しました。

Phase 4 / Step 4-5で、SQLAlchemyの `DeclarativeBase` を引き継ぐ
共通の `Base` と、`books` テーブルに対応する `Book` モデルを作成しました。
`id`、`title`、`author`、`isbn` の設計情報がSQLAlchemyへ登録されたことを
Python上で確認しました。PostgreSQLへのテーブル作成はまだ行っていません。

Phase 5 / Step 5-1からStep 5-5でAlembic 1.19.1を導入・初期化し、
`Base.metadata`とPostgreSQLを比較して最初のマイグレーションを作成しました。
マイグレーションを適用し、`books`と`alembic_version`が作成されたこと、
`books`のカラム・主キー・ISBNの重複禁止制約がモデルと一致することを確認しました。

ローカルの `main` ブランチはGitHubの `origin/main` に接続済みで、
プロジェクト管理文書の初回コミットを送信済みです。

---

# 現在行っていること

固定したPythonリストではなく、PostgreSQLの `books` テーブルへ
新しいBookを保存するAPIを一つずつ作ります。

---

# 次に行うこと

ROADMAPのPhase 6 / Step 6-1に従い、FastAPIのPOST処理から
SQLAlchemyを通してBookを1冊登録する流れを考えます。

---

# 再開地点

次回このプロジェクトを再開する場合は、

**Phase 6 / Step 6-1：Book作成**

から再開してください。

現在の具体的な次の作業は、

**APIから受け取ったBookをPostgreSQLへ保存するために必要な処理を整理すること**

です。

---

# 未解決・確認待ち

現時点では特になし。

---

# Codexへの更新ルール

このファイルは、開発・学習の進行に合わせてCodexが更新してください。

特に以下の場合は更新を検討してください。

- Stepを完了した
- 次のStepへ進んだ
- Phaseが変わった
- 作業を中断する
- 次回の再開地点が変わった
- 未解決の問題が発生した
- 未解決の問題が解決した

更新するときは、

**古い現在地を残し続けるのではなく、最新の状態がすぐ分かるように整理してください。**

長期的に残す必要がある情報は、
`docs/progress/HISTORY.md` へ移してください。

---

# 最重要事項

このファイルを読めば、新しいCodexセッションでも、

> 今どこにいるのか  
> 何が終わっているのか  
> 次に何をするのか  
> どこから講義を再開すればよいのか

が短時間で判断できる状態を維持してください。

このファイルは、

**book-apiプロジェクトの「しおり」**

として扱ってください。
