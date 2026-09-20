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

Phase 11：読書サービス機能を1つずつ追加する

## 現在のStep

Feature 6：代表ジャンルの取得・変換・保存が完了。

Bookに代表ジャンルを1つ保存し、Google Booksのカテゴリを
8種類のアプリ内部値へ変換する処理を実装しました。
検索レスポンス、Bookへの保存、手動確認、自動テストまで完了しています。
ジャンル検索と複数ジャンルの管理は作成しません。

GitHub ActionsによるCIも導入済みです。
main向けPRとmainへのpushを起点に、Python 3.14、PostgreSQL 17、
Alembic、pytestを使った検証を自動実行します。
PR #7でCIの成功を確認し、mainへのマージまで完了しました。

次はFeature 7の書籍詳細の要件を整理します。

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

Phase 6 / Step 6-1で、`BookCreate`による入力検証、リクエストごとのSession、
Book用ルーター、`POST /books`を実装しました。Swagger UIでステータス201と
自動生成されたIDを含むレスポンスを確認し、PostgreSQLへの保存も確認しました。

Phase 6 / Step 6-2で、`select(Book)`で一覧取得の問い合わせを作り、
`Session.scalars()`でPostgreSQLへ実行し、`.all()`で取得したBookを
一覧として返す `GET /books` を実装しました。Swagger UIで、
以前DBへ登録したBookがレスポンスに含まれることを確認しました。

Phase 6 / Step 6-3で、`/{book_id}` のパスパラメータでIDを受け取り、
`Session.get(Book, book_id)`で主キーに対応するBookを1件取得して返す
`GET /books/{book_id}` を実装しました。Swagger UIで、指定したIDと
レスポンスのBookが一致することを確認しました。

Phase 6 / Step 6-4で、Bookの部分更新にPATCHを採用し、入力用の
`BookUpdate` と `PATCH /books/{book_id}` を実装しました。
`model_dump(exclude_unset=True)`で送信された項目だけを取り出し、
`setattr()`で対象のBookへ反映して `commit()` で確定しました。
Swagger UIで、指定項目だけが更新され、未送信項目は変わらず、
続けてGETしても更新内容が残ることを確認しました。

Phase 6 / Step 6-5で、`DELETE /books/{book_id}` を実装しました。
`Session.get()`で対象を取得し、`Session.delete()`で削除対象として登録し、
`commit()`でPostgreSQLからの削除を確定する流れを実装しました。
削除確認用のBookを作成し、対象を確認後に削除し、
ステータス204と本文なしのレスポンスを確認しました。

Phase 6 / Step 6-6で、存在しないBookのGET・PATCH・DELETEに
404を返す処理を追加しました。PATCHでは、`title`・`author`への
`null`、更新項目なし、不正なISBNをPydanticの422で拒否することを
確認しました。POSTとPATCHのISBN重複は、DBの `IntegrityError` を
捕捉し、`rollback()`後に409 Conflictを返すようにしました。
重複した登録・更新がDBに反映されないこともGETで確認済みです。

Phase 7 / Step 7-1からStep 7-4で、POST入力用の `BookCreate`、
PATCH入力用の `BookUpdate`、出力用の `BookResponse` の
役割を整理しました。`BookResponse` は一般ユーザーに必要な
`id`・`title`・`author`だけを定義し、GET・POST・PATCHの
`response_model` に設定しました。Swagger UIでISBNがDBに残ったまま、
レスポンスからのみ除外されることを確認しました。

Phase 8 / Step 8-1からStep 8-5で、現在のコード構成と役割を
確認しました。`main.py` とBookルーター、DB設定、Session依存性は
すでに分離できています。現在はBookだけで規模が小さいため、
models・schemasの追加分割とservice / CRUD層は導入せず、
Userなどの機能を実際に追加する際に必要性から再検討します。

Phase 9 / Step 9-1で、読みたいリストや読書記録などを
個人ごとに管理するためにUserが必要だと整理しました。
Step 9-2で `id`・`username`・`email`・`hashed_password` を持つ
Userモデルを追加し、マイグレーション `28308531d9c5` を作成・確認・適用しました。
PostgreSQLで `users` テーブルの主キー、必須制約、
`username`・`email` のUNIQUE制約を確認済みです。

Phase 9 / Step 9-3で、`pwdlib` とArgon2を導入し、
生パスワードをハッシュ文字列へ変換する `hash_password()` を作成しました。
Step 9-4でUser用スキーマと `POST /users` を実装し、
レスポンスにパスワードやハッシュを含めず、DBにArgon2ハッシュだけが
保存されることを確認しました。重複するusername・emailは409、
不正なemail、短いpassword、空白だけのusernameは422で拒否することも確認済みです。

Phase 9 / Step 9-5からStep 9-6で、`POST /users/login` を実装しました。
emailでUserを取得し、入力パスワードと保存済みハッシュを照合します。
認証成功時はUser IDを `sub`、30分後を `exp` とするJWTをHS256で署名し、
`access_token` と `token_type: bearer` を返します。
Swagger UIで正常ログインが200とJWTを返すこと、存在しないemailと
間違ったpasswordは同じ401、不正なemail形式と空のpasswordは422に
なることを確認済みです。

Phase 9 / Step 9-7で、HTTP Bearer方式によりAuthorizationヘッダーから
JWTを受け取り、署名・有効期限・`sub` を検証する処理を実装しました。
`sub` のUser IDでDBからUserを取得する `get_current_user()` と、
各APIから再利用する `CurrentUserDep` を作成しました。
`GET /users/me` で正常なJWTは200と本人のUser情報、JWTなしと
不正・期限切れのJWTは401になることをSwagger UIで確認済みです。

Phase 9 / Step 9-8で、Bookの一覧・詳細取得は未ログインでも利用できる
公開APIとし、ユーザー個人に紐づく操作はログイン必須とする方針を整理しました。
Book本体の登録・更新・削除は、正確な共通書籍情報を守るため、
一般ユーザーには許可せず管理者またはシステム内部用とする方針を決めました。

Phase 9 / Step 9-9で、Userへ `is_admin` を追加し、既定値を `false` とする
マイグレーションを適用しました。`get_current_admin()` と `AdminUserDep` を作成し、
`POST /books`・`PATCH /books/{book_id}`・`DELETE /books/{book_id}` を
管理者専用にしました。一般ユーザーは403、管理者はPOSTが201、PATCHが200、
DELETEが204になることをSwagger UIで確認済みです。

Phase 11 / Feature 1で、UserとBookの関係を表す `UserBook` を追加し、
読みたい優先度を `high`・`medium`・`low` で管理できるようにしました。
外部キー、UserとBookの組み合わせの一意制約、PostgreSQLのEnumを含む
マイグレーションを開発用・テスト用DBに適用しました。
`POST`・`GET`・`PATCH`・`DELETE /users/me/books` を実装し、
関連テスト9件を追加しました。テスト全体22件が成功しています。

Phase 11 / Feature 2で、`UserBook`に `status` を追加し、
`want_to_read`・`reading`・`completed` の3状態をEnumで管理できるようにしました。
既存行を安全に移行するため、一時的なDB側デフォルトを使う
マイグレーションを開発用・テスト用DBに適用しました。
`PATCH /users/me/books/{book_id}/status` を追加し、読書中への変更、
おすすめ度なしの完読拒否409、不正値422、未登録404、JWTなし401を確認しました。
テスト全体27件が成功しています。

Phase 11 / Feature 3で、`UserBook`にNULL許可の
`recommendation_score` を追加し、CHECK制約でNULLまたは1〜5に限定しました。
`COMPLETED` の場合はおすすめ度を必須とする制約も追加しました。
完読とおすすめ度の同時更新と、
`PATCH /users/me/books/{book_id}/recommendation-score` による後からの変更を実装しました。
範囲外422、完読前409、未登録404、JWTなし401を含め、テスト全体34件が成功しています。

Phase 11 / Feature 4で、1つのUserBookに複数の学び・気づきを保存する
`Insight` モデルを追加しました。Insightは `user_book_id` と本文を持ち、
UserBook削除時は外部キーの `ON DELETE CASCADE` により同時に削除されます。
開発用・テスト用DBへマイグレーション `22f250f52ddb` を適用しました。
本人の本に対するInsightのPOST・GET・PATCH・DELETEを実装し、
他人のデータには404、JWTなしには401を返すことを確認しました。
一覧はInsight IDの昇順で返し、テスト全体52件が成功しています。

Phase 11 / Feature 5の検索API部分で、Google Books APIの `q` を使う
公開キーワード検索 `GET /books/search?q={keyword}` を実装しました。
検索結果は、Google側ID、タイトル、著者、ISBN-13が揃った書籍だけを返します。
未入力・空白は422、外部APIの応答異常と接続失敗は502、タイムアウトは504とし、
検索結果から選んだ本の `external_id` を使ってバックエンドが
Google Books APIから書籍情報を再取得する
`POST /users/me/books/from-search` も実装しました。
ISBNが同じ既存Bookは再利用し、存在しなければBookを作成した後、
ログイン中のユーザーのUserBookを作成します。
手動確認でBookとUserBookの保存・紐付きを確認し、
関連テスト46件、テスト全体77件が成功しています。

Phase 11 / Feature 6で、BookにNULL禁止の代表ジャンルを追加し、
マイグレーション `ae226236b2ef` を開発用・テスト用DBへ適用しました。
Google Booksの `mainCategory` を優先し、ない場合は `categories[0]` へ
フォールバックして8種類の内部値へ変換します。
検索レスポンスとBook保存へ反映し、全87テストが成功しています。

ローカルの `main` ブランチはGitHubの `origin/main` に接続済みで、
プロジェクト管理文書の初回コミットを送信済みです。

---

# 現在行っていること

Phase 11 / Feature 6の設計、DB変更、実装、手動確認、自動テストが完了しました。
現在は、Feature 7の書籍詳細へ進むところです。

---

# 次に行うこと

Feature 7を実装する前に、未登録・未ログインでも閲覧できる公開情報と、
ログイン中のユーザーにだけ必要な個人用情報を分けて考えます。

---

# 再開地点

次回このプロジェクトを再開する場合は、

**Phase 11 / Feature 7：書籍詳細の要件を整理する**

から再開してください。

現在の具体的な次の作業は、

**書籍詳細で全員に公開する値と、ログイン中のユーザーにだけ返す値を分けること**

です。

---

# 未解決・確認待ち

Starlette 1.6.0内部で、AnyIO 4.15.0が非推奨とした
`anyio.abc.BlockingPortal`を参照しているため、テスト時に警告が1件出ます。
テストは成功しており、アプリ側で警告を隠さず、ライブラリ側の更新を待ちます。

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
