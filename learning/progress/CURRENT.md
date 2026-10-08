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
`learning/progress/HISTORY.md` に記録します。

---

# 現在地

## 現在のPhase

Phase 11：読書サービス機能を1つずつ追加する

## 現在のStep

Feature 14：関連書籍レコメンドが完了。

未ログインで利用できる `GET /books/{book_id}/related` を追加し、
対象本と同じジャンルの別の本を最大4件返せる状態にしました。
平均おすすめ度が高い順に並べ、未評価本も除外せず最後に返します。

関連書籍テスト8件と、既存機能を含む全206件のテストが
成功しています。

現在はFeature 15：読書リマインドが完了しています。

`ReadingReminder` Model、Migration、レスポンスSchema、Service、
`POST /users/me/books/{book_id}/reminder` を実装しました。
新規設定、終了済みリマインダーの再設定、未登録、対象外の読書状態、
重複設定、未認証、不正なBook ID、DB競合を検証する11ケースを追加しました。

さらに `GET /users/me/books/{book_id}/reminder` を実装し、
正常取得、UserBook未登録、ReadingReminder未設定、
不正なBook ID、未認証を検証する7ケースを追加しました。
送信対象の取得、1件ごとの状態確認とメール送信、
Resendの冪等性キー、定期実行用コマンドを実装しました。
`commands/send_reading_reminders.py` の `main()` が、日本時間と
DBセッションをサービス処理へ渡すテストも追加しています。
既存機能を含む全235件のテストが成功しています。

開発用DBの対象を1件に限定し、実メールを受信し、
`ReadingReminder.status` が `SEND_ACCEPTED` へ更新されることも確認しました。

Feature 15の変更はPR #17で `main` ブランチへマージ済みです。
Feature 16：AI転用提案の生成・保存POSTとローカル検証が完了しました。
本人のInsightに対し、OpenAIで生成した4項目を保存し、再生成時は上書きします。
取得GET・提案単体の削除DELETEも実装し、全269テストが成功しました。
CI用ダミー環境変数だけでSettingsを読み込めることは確認済みです。設計の振り返りと最終レビュー、PR #18のmainへのマージも完了しました。GitHub Actionsの結果は未確認です。

---

# 完了済み

以下のプロジェクト方針文書を作成済みです。

- `learning/ROADMAP.md`
- `learning/TEACHING_RULES.md`
- `learning/DEVELOPMENT_LEARNING_POLICY.md`

以下の進捗管理ファイルを作成済みです。

- `learning/progress/CURRENT.md`
- `learning/progress/HISTORY.md`

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

Phase 11 / Feature 7で、公開書籍詳細
`GET /books/{book_id}` と、認証済みユーザー用書籍詳細
`GET /users/me/books/{book_id}` を実装しました。
PostgreSQLの `AVG` でNULL以外のおすすめ度を集計し、
Pythonで小数第1位へ丸めて返します。
認証済みAPIでは、Bookの共通情報に本人のUserBook登録状態、
優先度、読書状態、おすすめ度を組み合わせます。
新しいModel・Migrationは追加せず、全99テストが成功しています。

Phase 11 / Feature 8で、UserBookと1対1で紐づくReadingPostを追加し、
本人用の作成・取得・更新・削除APIを実装しました。
Feature 9では公開状態だけを変更する専用APIを追加しました。
読了投稿の入力制約、所有者確認、重複作成、公開状態の変更を含め、
既存機能を含む全141件のテストが成功しています。

Phase 11 / Feature 10で、UserとReadingPostをLikeで結び、
公開された他ユーザーの投稿へのいいね・いいね解除を実装しました。
複合UNIQUE制約による重複禁止と、User・ReadingPost削除時の
CASCADE削除をDBで保証しています。正常系、異常系、DB例外、
制約の許可範囲、CASCADE削除を含む全158件のテストが成功しています。

Phase 11 / Feature 11で、User同士をFollowで結び、
フォロー登録・解除APIを実装しました。
同じ組み合わせの重複禁止、自己フォロー禁止、2本の外部キーによる
CASCADE削除をDBでも保証しています。UserとFollow間の4つの
relationship、正常系、異常系、DB制約、認可、CASCADE削除を含む
全175件のテストが成功しています。

Phase 11 / Feature 12で、未ログインでも他ユーザーの
プロフィールと公開本棚を取得できるAPIを実装しました。
完読冊数は非公開分も含め、公開本棚は公開ReadingPostが
ある本だけを新着順で返します。UserにbioとDB制約も追加し、
既存機能を含む全183件のテストが成功しています。

Phase 11 / Feature 13で、全ユーザーの公開投稿を取得する
「おすすめ」と、ログイン中ユーザーがフォローしている
相手の公開投稿を取得する「フォロー中」の
2種類のタイムラインAPIを実装しました。
新着順、公開範囲、フォロー範囲、未認証を含む9テストを追加し、
既存機能を含む全192件のテストが成功しています。

ローカルの `main` ブランチはGitHubの `origin/main` に接続済みで、
プロジェクト管理文書の初回コミットを送信済みです。

---

# 現在行っていること

受講者の希望により、途中の進捗はCURRENT.mdで管理し、HISTORY.mdは機能実装完了時に従来の分量でまとめます。
Feature 16の途中経過を細かく分けたHISTORY.mdの追記は削除しました。現在の判断・確認結果は本ファイルに残しています。

Phase 11 / Feature 15：読書リマインドが完了しました。

ログイン中のユーザーが、読書中のUserBookへ明示的に設定します。
設定日の7日後の20時に、登録メールアドレスへ1回だけ送信します。
送信前に読書中以外へ変わった場合は、送信せず終了します。

メール送信にはResendを使用します。Webhook、手動解除、
メール内の解除リンク、送信の再試行は実装しません。

`ReadingReminderStatus`、`ReadingReminder`モデル、
マイグレーション `c9107ce826ea` を作成しました。
開発用・テスト用DBへ適用済みです。

`ReadingReminderResponse` を設定APIと状態取得APIで共有し、
`POST /users/me/books/{book_id}/reminder` と
`GET /users/me/books/{book_id}/reminder` の実装・テストが完了しました。

送信対象となる `ReadingReminder`、`UserBook.status`、
`User.email`、`Book.title` をDBからまとめて取得し、
1件ごとに読書状態の確認、Resendへの送信要求、
リマインダー状態の更新を行うサービス処理を実装しました。

`commands/send_reading_reminders.py` を追加し、日本時間の現在時刻と
DBセッションを準備してサービス処理を1回呼び出せる状態です。
コマンド用テストを含む全235件のテストが成功しています。

GitHub Actionsに `RESEND_API_KEY` と `RESEND_FROM_EMAIL` の
テスト用ダミー値を追加しました。
`.env` がない状態でも、CI用環境変数だけで
`Settings` を作成できることを確認済みです。

開発用DBで、自分が受信確認できる1件だけを
送信対象にし、コマンドを1回実行しました。
実メールを受信し、対象の状態が `SEND_ACCEPTED` へ更新され、
次回の送信対象が0件になることを確認しました。

ローカルで5分ごとの自動起動は設定せず、
本番配置時に外部のスケジューラーからコマンドを呼び出す方針です。

Feature 15の変更はPR #17で `main` ブランチへマージ済みです。
Feature 16：AI転用提案の生成・保存POSTとローカル検証が完了しました。

- AISuggestion Model、Migration 07fb83edbd05、入力・出力Schema、Service、Routerを追加しました。
- Insightと0対1で紐づけ、insight_idのUNIQUEとON DELETE CASCADEを設定しています。
- POST /users/me/books/{book_id}/insights/{insight_id}/ai_suggestionは新規201、再生成200です。
- 気づき未登録・他人の気づきは404、生成失敗・保存失敗は500として返します。
- OpenAI公式Python SDK 3.24.0とgpt-6-lunaを採用し、4項目を構造化出力で受け取ります。
- instructionsは読者に役立つ内容に集中し、AI側の生成方針や情報不足の断り書きを出しません。
- 同じ入力で推論設定あり・省略の実生成を比較し、受講者がreasoningとmax_output_tokensの明示指定を両方省略する方針を選びました。
- APIError変換、解析済み結果なし、成功時の返却を通信クライアントのMockで検証しました。
- commitのIntegrityErrorはrollback後AISuggestionSaveErrorへ変換し、rollback呼び出し・DB未保存をテストしています。制約別の原因判別はしていません。
- AI提案の34ケースを含む全269テストが成功しました。Codexによるテスト追加は受講者の明示依頼に基づいて行いました。
- CIへOPENAI_API_KEYのダミー値とOPENAI_MODELを追加し、.envを無効にしてCI環境変数だけでSettingsを読み込めることを確認しました。
- 読書リマインドのPOSTも既定201・更新時200へ書き方を統一しました。

実キーは.envに保存され、Git管理対象外です。自動テストではOpenAIへの実通信を置き換えています。
GET・DELETEを追加し、2026-10-07に全269テストが成功しました。GETは200、DELETEは本文なし204、対象なしは404です。
AISuggestion → Insight → UserBookをJOINし、気づきID・本ID・本人IDで絞ります。DELETEは取得Serviceを再利用します。
GET・DELETEとも正常系、提案未登録404、未認証401、不正ID422、他人の提案404、本ID不一致404を検証済みです。削除を拒否した場合に提案が残ることも確認しました。
再生成失敗時に既存提案のID・4項目・件数が維持されることも検証しました。
所有者確認・UNIQUE制約・再生成失敗時の保持を振り返り、変更差分を確認しました。Feature 16のローカル実装・検証は完了です。
PR #18はmainへマージ済み（fefd1f9）で、ローカルmainもorigin/mainと同期しています。受講者からブランチの片付け完了の報告を受けました。GitHub Actionsの結果は未確認です。

フォルダ移動前の絶対パスが仮想環境に残っていたため、現在の場所で`.venv`を再作成し、
両requirementsファイルからライブラリを導入しました。
依存関係、Alembic・pytestの起動、モデルの読み込みは確認済みです。
旧環境は`.venv-backup-20261004`に残しています。
AI回答方針のローカル参考資料は`local-notes/feature-16-ai-suggestion-policy.md`です。

---

# 次に行うこと

Phase 11 / Feature 16はPR #18のmainへのマージまで完了しました。
受講者の希望により、Phase 12へ進む前にフォロワー・フォロー中の一覧取得を追加します。本人限定の一覧APIと各4ケースのテストを追加し、全277テストが成功しました。JOINとWHEREの役割も振り返り、PR #19をmainへマージしました。ローカルmainとorigin/mainの同期・ローカル作業ブランチの削除を確認済みです。次はPhase 12 / Step 12-1です。GitHub Actionsの結果は未確認です。

---

# 再開地点

**Phase 12 / Step 12-1：書籍検索の改善**

GET・DELETEの実装と正常系・異常系テストが揃い、全269テストが成功しています。
設計の振り返り、差分確認、PR #18のマージ、ローカルmainへのpullまで完了しています。
本人限定のGET /users/me/following・GET /users/me/followersを追加しました。既存Followを使い、相手のUserのid・usernameをShowFollowResponseのリストで返します。0件は200と[]、未認証は401です。
両APIの2人取得・0件・未認証・他人の関係除外を検証し、全277テストが成功しました。並び順・ページ分割は未指定です。
設計の振り返りとPR #19のマージ（e98af42）が完了しました。ローカルmainとorigin/mainは同期しており、ローカルブランチはmainのみです。
Phase 12 / Step 12-1で検索から登録までを確認中、検索結果が少なく目的の本を選べない問題を発見しました。Googleからの取得が既定最大10件で、ISBN-13なしの候補をアプリが除外しています。実通信で嫌われる勇気10件中1件、益田ミリ10件中2件だけ残ることを確認しました。
検索時にmaxResults=40を指定し、ISBN-13なしの本も検索・詳細取得の結果に含めるよう変更しました。Bookにnullable・一意制約付きのexternal_idを追加し、開発用・テスト用DBともマイグレーション適用済みです。登録時はexternal_idで既存本を探し、見つからずISBNがある場合はISBNで探します。既存本の不足しているexternal_id・ジャンル・表紙を補います。
関連テストを修正・追加し、ISBNなしの新規登録・重複登録、既存本の再利用、複数ユーザーによる同じ本の登録を検証しました。全285テストが成功しています。次は実際の検索結果から読みたいリストへ登録し、本人の一覧で取得できることを確認します。

---

# 未解決・確認待ち

## 後で行うこと

- 関数名を見直す。検索・詳細取得・既存本の登録・検索結果からの登録など、名前から役割の違いを判断できるか確認する。Phase 12のAPI設計見直し・リファクタリング時に扱う。

2026-10-08に一時ファイルでpdbの基礎実習を完了しました。変数確認、行単位実行、関数へのステップイン、ブレークポイント、修正後の再実行を経験しました。練習ファイルは削除済みで、Gitには追加していません。追加実習では、TracebackからNoneの受け渡しをたどり、検索条件のID取り違えを特定・修正して期待する結果を確認しました。練習ファイルは再度削除済みです。

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
`learning/progress/HISTORY.md` へ移してください。

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
