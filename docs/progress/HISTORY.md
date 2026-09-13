# book-api 開発・学習履歴

## このファイルの役割

このファイルは、book-apiプロジェクトでこれまで行った

- 開発作業
- 学習内容
- 完了したPhase / Step
- 重要な設計判断
- 技術選定とその理由
- 発生した問題
- 原因
- 解決方法
- 後から変更した設計
- 重要な気づき

を時系列で記録するためのファイルです。

このファイルの目的は、

**「過去に何をやり、なぜそうしたのか」を後から確認できるようにすること**

です。

---

# CURRENT.mdとの役割の違い

`docs/progress/CURRENT.md`

```text
現在地を管理する
↓
今どこにいる？
何が終わっている？
次に何をする？
どこから再開する？
```

`docs/progress/HISTORY.md`

```text
過去を記録する
↓
何を実装した？
何を学んだ？
何を判断した？
どんな問題が起きた？
どう解決した？
```

`CURRENT.md` は常に最新状態へ更新します。

`HISTORY.md` は過去の重要な記録を削除せず、
時系列で追加していきます。

---

# 記録ルール

Codexは、重要な作業や学習が完了したときに、
このファイルへの記録を検討してください。

特に以下は記録対象です。

## Phase / Stepの完了

例：

```text
Phase 2 Step 2-1
最小のFastAPIアプリを作成した。
```

---

## 新しく学んだ重要な概念

例：

```text
FastAPIとUvicornの役割の違いを確認。

FastAPI：
APIのルーティングや処理を定義するWebフレームワーク。

Uvicorn：
FastAPIアプリを実際に起動し、
HTTPリクエストを受け取るASGIサーバー。
```

---

## 技術選定

「何を選んだか」だけでなく、

**なぜそれを選んだか**

も記録してください。

例：

```text
DBとしてPostgreSQLを採用。

理由：
今回のサービスでは将来的に本番環境でも
PostgreSQLを利用することを想定しているため。

学習用としてSQLiteを先に構築してから
PostgreSQLへ移行する方法は採用しなかった。

不要な作り直しを避けながら、
PostgreSQLを使ってDBの基礎を学習する方針とした。
```

---

## 設計判断

例：

```text
BookとGenreは1対1ではなく、
1冊のBookが複数Genreを持てる設計にすることを決定。

理由：
今回のサービス要件として、
1冊の本を複数ジャンルへ分類できる必要があるため。
```

---

## 発生した問題

エラーや問題については、

```text
何が起きた？
↓
原因は何だった？
↓
どう調査した？
↓
どう修正した？
↓
なぜそれで直った？
```

が後から分かるように記録してください。

例：

```text
問題：
FastAPI起動時にModuleNotFoundErrorが発生。

原因：
実行しているPython環境に必要なパッケージが
インストールされていなかった。

確認：
使用中のPythonと仮想環境を確認。

解決：
正しい仮想環境を有効化して依存関係をインストール。

学び：
ターミナルで実行されるPythonと、
パッケージをインストールしたPython環境が
一致している必要がある。
```

---

## 設計変更・リファクタリング

以前の設計を変更した場合、

```text
以前どうしていた？
↓
何が問題になった？
↓
何に変更した？
↓
なぜ変更した？
```

を記録してください。

単に、

```text
routerを分割した
```

だけで終わらせず、

**設計が変わった理由**

を残してください。

---

# 記録しなくてよいもの

すべての操作を記録する必要はありません。

例えば、

```text
ファイルを開いた
lsを実行した
ディレクトリを移動した
誤字を修正した
```

など、後から参照する価値が低い作業は原則として記録不要です。

HISTORY.mdが巨大な作業ログになることを避けてください。

記録する基準は、

**「数週間・数か月後に見返したとき、開発や学習の判断材料になるか」**

です。

---

# 記録形式

新しい記録は、原則として時系列で下へ追加してください。

基本形式：

```text
## YYYY-MM-DD

### Phase X / Step X-X：タイトル

#### 実施内容

何をしたか。

#### 学んだこと

何を理解したか。

#### 判断・理由

どんな判断をし、なぜそうしたか。

#### 問題・解決

問題があった場合のみ記録。

#### 次につながること

この作業が次の工程にどうつながるか。
```

すべての項目を毎回埋める必要はありません。

内容がない項目は省略して構いません。

---

# 初期履歴

## プロジェクト準備

### 実施内容

新しい `book-api` プロジェクトの開発・学習を開始する前に、
プロジェクトの進行方法を整理した。

以下の管理文書を作成した。

```text
docs/ROADMAP.md
docs/TEACHING_RULES.md
docs/DEVELOPMENT_LEARNING_POLICY.md
docs/progress/CURRENT.md
docs/progress/HISTORY.md
```

また、Codexへの常設指示を記述するため、

```text
AGENTS.md
```

をプロジェクトルートに作成した。

### 方針

今回のプロジェクトでは、
以前作成したFastAPIプロジェクトをコピーするのではなく、
新しいプロジェクトをゼロから構築する。

ただし、単純にすべての技術を最初からやり直すのではない。

実際のアプリ開発の流れに沿って、

```text
必要性
↓
問題
↓
選択肢
↓
実務的な判断
↓
技術選定
↓
実装
↓
検証
```

という順序で進める。

### 重要な判断

「小さく始めること」と
「後で捨てる構成をわざわざ作ること」は区別する。

例えば、今回の要件からPostgreSQLを採用することが
合理的だと判断できる場合、

学習目的だけでSQLite版を先に構築し、
その後PostgreSQLへ移行するような
不要な二度手間は原則として行わない。

ただし、SQLiteとPostgreSQLの違いや、
なぜPostgreSQLを選択するのかなど、
技術選定に必要な基礎理解は省略しない。

### 学習方針

Codexが完成コードを作ることを目的とせず、

受講者自身が、

- 次に何が必要か考える
- 技術を選択する
- コードを書く
- エラーを調査する
- 設計を考える
- 自分の言葉で仕組みを説明する

ことを重視する。

---

# Codexへの更新指示

このファイルは、重要な学習・開発上の出来事が発生したときに、
Codexが追記してください。

ただし、毎回機械的に追記するのではなく、

**将来振り返る価値がある情報だけを残してください。**

過去の記録を勝手に書き換えて、
当時の判断や経緯を失わせないでください。

後から判断が変更された場合は、
古い記録を削除するのではなく、

```text
以前の判断
↓
新しい問題・要件
↓
新しい判断
↓
変更理由
```

が追えるように、新しい履歴として追加してください。

現在の状態については、
`docs/progress/CURRENT.md` を最新状態へ更新してください。

---

## 2026-09-02

### Phase 0 / Step 0-1：現在の状態を確認する

#### 実施内容

アプリケーションを実装する前に、リポジトリのファイル、
Git・GitHub接続、Python、PostgreSQLの現在の状態を確認した。

- プロジェクト管理文書は作成済みで、アプリ実装は未開始
- ローカルGitリポジトリは初期化済み
- コミットはまだ0件で、`AGENTS.md` と `docs/` は未追跡
- GitHubなどのremoteは未登録
- Homebrew版Python 3.14.0が利用可能
- `python` と `python3` は同じPython実行ファイルを使用
- `book-api` 専用の仮想環境は未作成
- Homebrew版PostgreSQL 17.10のサーバーはサービスとして稼働中

#### 学んだこと

PC上のファイル保存、ローカルGitの履歴、GitHub上のremoteリポジトリは
別々の状態であることを確認した。

Python本体はMacにインストールされ、複数プロジェクトから利用できる。
一方、依存ライブラリは今後作成するプロジェクト用仮想環境で分離する必要がある。

PostgreSQLについては、`psql` クライアントの存在と、
PostgreSQLサーバーが接続を受け付けている状態は別々に確認する必要がある。

#### 判断・理由

今回のサービスで将来的にDBを使うことは予測できるため、
PostgreSQL・SQLAlchemy・Alembicの早期採用を検討する。

また、型チェックなど、後から導入すると修正負担が増える開発基盤は、
Phase 1の初期段階で導入を検討する。

ただし、Pythonライブラリは仮想環境と依存関係の管理方法を決める前に導入しない。

#### 次につながること

Phase 0 / Step 0-2で、今回作る読書サービスの目的を確認する。

### Phase 0 / Step 0-2：サービスの目的を確認する

#### 実施内容

誰のためのサービスか、ユーザーは何をしたいのか、
最終的にどのような体験を作りたいのかを確認した。

#### 判断・理由

対象は、本を読んでも学びや気づきを活用できず、
読んだだけで終わってしまう人、および次に読む本との出会いを求める人とする。

サービスは、読書から得た学び・気づきを記録するだけでなく、
仕事や日常で実際に活用するための提案を行う。

また、他のユーザーの評価やおすすめを通じて新しい本との出会いを生み、
その本から新たな学びを得る好循環によって、ユーザーの人生を豊かにすることを目指す。

#### 次につながること

Phase 0 / Step 0-3で、この目的を実現するために、
ユーザーがサービス上でできる必要があることを整理する。

### Phase 0 / Step 0-3：ユーザーができることを確認する

#### 実施内容

サービスの目的を実現するための主要なユーザー操作と画面間の流れを整理した。

#### 判断・理由

- 未登録・未ログインでも、本の検索、書籍詳細、公開読了投稿を閲覧できる
- 保存・評価・投稿など、ユーザー個人に紐づく操作には登録・ログインが必要
- 本の保存先の現在名称は「読みたいリスト」とし、将来の名称変更は許容する
- 読みたい本の優先度は「すぐ読みたい」「そのうち読みたい」「いつか読みたい」の3段階
- 読書中に学び・気づきを随時記録できる
- 完読時に1〜5のおすすめ度登録を必須とし、完読者の平均おすすめ度を書籍詳細で使用する
- 読了投稿は任意とし、投稿する場合はおすすめ度とおすすめ理由の両方を必須とする
- 公開投稿から、いいね、読みたいリストへの追加、書籍詳細、投稿者プロフィールへ移動できる
- プロフィールではユーザーアイコン、ユーザー名、フォロー操作、非公開分も含む完読冊数を表示する
- プロフィールの公開本棚には、公開読了投稿がある本だけを表示する
- タイムラインは「おすすめ」と「フォロー中」の2タブとし、両方とも対象の公開投稿を新着順で表示する
- AI活用案は学び・気づきごとにボタン操作で生成して保存し、再生成時は以前の提案を上書きする
- 読書リマインドは登録メールアドレスへ送信し、読書中から14日後、さらに7日後の最大2回とする
- 完読した場合は、以後の読書リマインドを送信しない
- フロントエンドはCodexが作成し、受講者はバックエンド開発を主な学習対象とする
- フロントエンドとバックエンドのリクエスト・レスポンスの境界は説明する

#### 次につながること

Phase 0 / Step 0-4で、これらの機能を一度に作らず、
最小構成から1機能ずつ増やす理由を確認する。

### GitHubへの初回保存

#### 実施内容

GitHub上に非公開の `book-api` リポジトリを作成した。

プロジェクト管理文書6ファイルを、
`docs: 開発・学習方針を追加` として最初のローカルコミットに保存した。

ローカルリポジトリに `origin` を登録し、
`main` ブランチをGitHubの `origin/main` へ送信した。

#### 学んだこと

PC上のファイル、ローカルGitのコミット、GitHubのリモートリポジトリは、
それぞれ別の段階であることを確認した。

`git remote add origin` は接続先の登録、`git remote -v` は登録内容の確認、
`git push` はローカルコミットをGitHubへ送信する操作である。

### Phase 0 / Step 0-4：いきなり全機能を作らない理由を考える

#### 学んだこと

認証、Book、投稿、フォロー、AIなどの複数機能を一度に実装すると、
変更箇所と関係する処理が増え、エラーがどの機能で発生したのか特定しにくくなる。

機能を1つずつ実装し、その都度動作確認することで、
エラーの原因を直前の変更範囲へ絞りやすくなることを確認した。

#### 次につながること

Phase 0の整理は完了。
次はPhase 1 / Step 1-1で、今回使用するPython環境を確認する。

### Phase 1 / Step 1-1からStep 1-2：Python環境と仮想環境

#### 実施内容

Homebrew版Pythonを3.14.0から3.14.7へ更新し、
`python` と `python3` がPython 3.14.7を参照することを確認した。

プロジェクトごとにPythonとライブラリの参照先を分離し、
ライブラリのバージョン競合を防ぐため、`.venv` を作成した。

#### 講義ルールの追加

コマンドの説明では構文の分解だけで終わらせず、
実行時に内部で何が起き、なぜその出力になるのかを処理順に説明する。

コマンド末尾のパスについても、ファイル内容を読む対象なのか、
検索・確認・入力・出力の対象なのかを明示する。

#### 次につながること

Phase 1 / Step 1-3で `.venv` を有効化し、
Pythonとpipの参照先がどう変化するか確認する。

### Phase 1 / Step 1-3：仮想環境を有効化する

#### 実施内容

`source .venv/bin/activate` で仮想環境を有効化した。

`which python` と `which pip` の結果から、どちらも `.venv/bin` 内のものが
優先して選ばれる状態になったことを確認した。

#### 学んだこと

仮想環境の有効化はPythonを起動し続ける操作ではなく、
現在のシェルの `PATH` を変更し、`.venv/bin` を検索順の先頭へ置く操作である。

#### 次につながること

Phase 1 / Step 1-4で、FastAPIアプリを動かすために必要な
最小限の依存パッケージを考えて導入する。

### Phase 1 / Step 1-4：最小限の依存パッケージを導入する

#### 実施内容

最小限のFastAPIアプリを動かすため、FastAPIとUvicornを
プロジェクト専用の `.venv` へ導入した。

`python -m pip list` を使い、FastAPI、Uvicorn、およびそれらが必要とする
依存ライブラリが仮想環境へインストールされたことを確認した。

#### 学んだこと

FastAPIはAPIの処理を定義し、Uvicornは外部からHTTP通信を受け取って
FastAPIとの間でリクエストとレスポンスを受け渡す。

仮想環境を有効化した状態で `python -m pip install` を実行すると、
現在選ばれている `.venv/bin/python` に所属するpipが使われ、
ライブラリはプロジェクト専用の仮想環境へインストールされる。

#### 次につながること

Phase 1 / Step 1-5で、導入した依存関係を別の環境でも
再現できるようにする管理方法を考える。

### Phase 1 / Step 1-5：依存関係の管理方法を考える

#### 実施内容

`pip freeze` によって現在の仮想環境全体を記録する方法を確認した。

そのうえで、学習初期に直接利用するライブラリを明確にするため、
`requirements.txt` にはFastAPIとUvicornの名前とバージョンだけを記録した。

#### 学んだこと

`requirements.txt` にライブラリ本体が入っているのではなく、
必要なライブラリの名前とバージョンが記録されている。

別の環境では、pipがこの情報を読み取り、PyPIからライブラリ本体と
必要な依存ライブラリを取得して仮想環境へインストールする。

#### 次につながること

Phase 1 / Step 1-6で、最小のFastAPIアプリに必要な
ファイルとディレクトリ構成を考える。

### Phase 1 / Step 1-6：最低限のディレクトリ構成を考える

#### 判断・理由

次に作るAPIは `GET /` の1つだけであり、現時点では処理も少ないため、
最初はリポジトリ直下の `main.py` だけで開始する方針とした。

`routers`、`models`、`schemas`、`services`、`tests` などは先に作らず、
機能が増えて分割する必要が生じた時点で追加する。

#### 次につながること

Phase 1 / Step 1-7で、アプリケーションコードを作る前に
Gitの管理状態と除外設定を確認する。

### Phase 1 / Step 1-7：Git管理状態を確認する

#### 実施内容

プロジェクト直下に `.gitignore` を作成し、`.venv/` を除外対象として記録した。

`git status` で、学習記録、`requirements.txt`、`.gitignore` は
コミット対象にでき、`.venv/` は表示されないことを確認した。

#### 学んだこと

先頭に `.` が付く名前はmacOSなどで隠しファイルとして扱われるが、
それだけでGitの追跡対象外になるわけではない。

`.gitignore` 自身はGitHubで共有し、そこに書いた `.venv/` は
Gitの追跡対象から除外するという役割の違いを確認した。

#### 次につながること

Phase 1の開発環境準備は完了。
次はPhase 2 / Step 2-1で、`main.py` に最小のFastAPIアプリを作る。

### Phase 2 / Step 2-1：最小のFastAPIアプリを作る

#### 実施内容

リポジトリ直下に `main.py` を作成した。

FastAPIパッケージから `FastAPI` を読み込み、アプリ本体を作成した。
さらに、`GET /` と `read_root` 関数を結び付け、
`{"message": "book-api"}` を返す最小のAPIを定義した。

#### 学んだこと

`FastAPI()` はアプリ本体を作り、`app` という名前に結び付ける。
`@app.get("/")` は、`GET /` を受け取ったときに直下の関数を
実行するという対応関係をFastAPIへ登録する。

この時点ではAPIの処理は定義されているが、外部通信を受け取る
Uvicornはまだ起動していない。

#### 次につながること

Phase 2 / Step 2-2でUvicornを起動し、`main.py` のFastAPIアプリを読み込ませる。

### Phase 2 / Step 2-2からStep 2-3：起動とブラウザからのアクセス

#### 実施内容

`python -m uvicorn main:app` でUvicornを起動した。

ブラウザから `http://127.0.0.1:8000/` へアクセスし、
`{"message": "book-api"}` が表示されることを確認した。

#### 学んだこと

Uvicornは8000番ポートでHTTPリクエストを受け取り、FastAPIへ渡す。
FastAPIは `GET /` に登録された `read_root` 関数を実行し、
関数が返したPythonの辞書をJSONレスポンスへ変換する。

Uvicornは、そのレスポンスをブラウザへ送り返す。

#### 次につながること

Phase 2 / Step 2-4で、URLとHTTPメソッドがPython関数へ
どのように結び付けられているか整理する。

### Phase 2 / Step 2-4：FastAPIのルーティングを理解する

#### 学んだこと

FastAPIは、HTTPメソッドとURLパスの組み合わせを、実行するPython関数と結び付ける。

登録されていないURLパスへのリクエストには404 Not Foundを返す。
URLパスは登録されていても、そのHTTPメソッドが許可されていない場合は
405 Method Not Allowedを返す。

また、Uvicornを `--reload` なしで起動している場合、`main.py` を変更しても
起動中のアプリには自動反映されず、停止と再起動が必要になる。

#### 次につながること

Phase 2 / Step 2-5で、FastAPIが自動生成するSwagger UIを確認する。

### Phase 2 / Step 2-5：Swagger UIを確認する

#### 実施内容

ブラウザで `/docs` を開き、Swagger UIに `GET /` が表示されることを確認した。

`Try it out`からAPIを実行し、HTTPステータス200と、
期待したレスポンス本文が表示されることを確認した。

#### 学んだこと

Swagger UIは、FastAPIに登録されたAPIの情報を画面で確認し、
ブラウザからリクエストを試行するための仕組みである。

`Try it out`による実行でも、UvicornがHTTPリクエストを受け取り、
FastAPIが対象関数を実行してレスポンスを返す流れは通常のアクセスと同じである。

#### 次につながること

Phase 2は完了。
次はPhase 3 / Step 3-1で、Bookを扱うために必要なデータを考える。

### Phase 3 / Step 3-1：Bookに必要なデータを考える

#### 判断・理由

最初のBookデータは、内部識別番号の `id`、`title`、`author`、
存在しない場合もある任意項目の `isbn` を持つ方針とした。

`id` はbook-api内部でBookを識別し、ISBNは現実の書籍の版や形式を
識別する情報として役割を分ける。

本を大量に手作業で事前登録する方式は採用しない。
開発段階では少数の固定データを使い、検索機能の実装時に外部書籍APIを検討する。
将来はユーザーが検索結果から選んだ本を必要に応じてDBへ保存し、
ISBNなどを使って重複を防ぐ方針とする。

#### 次につながること

Phase 3 / Step 3-2で、DBを使わずに固定値のBookデータを返すAPIを作る。

### Phase 3 / Step 3-2：Bookデータを返すAPIを作る

#### 実施内容

`GET /books/1` と `read_book` 関数を追加し、固定した『GANTZ 1』の
`id`、`title`、`author`、`isbn` を辞書で返すようにした。

Swagger UIから実行し、HTTPステータス200と、
4項目を持つJSONレスポンスが返ることを確認した。

#### 学んだこと

Book自身の識別番号には `id` を使い、将来ほかのデータから
Bookを参照する項目には `book_id` を使うという役割の違いを確認した。

ISBNは計算する数値ではなく、ハイフンを含む識別情報であるため文字列として扱う。

#### 次につながること

Phase 3 / Step 3-3で、複数のBookをリストとして返すAPIを作る。

### ローカル開発時のUvicorn起動方法

#### 判断・理由

コード変更のたびにUvicornを停止して再起動する単純作業を避けるため、
今後のローカル開発では `python -m uvicorn main:app --reload` を使用する。

`--reload` はPythonファイルの変更を検知し、更新後のアプリを自動的に
読み直す開発用の機能であり、本番環境では使用しない。

#### 講義ルールへの反映

一つずつ学習することを理由に、理解へつながらない反復作業を増やさない。
安全で一般的な効率化が予測できる場合は事前に提示し、内部処理と注意点を説明する。

仕組みの理解に手動操作が必要な場合も目的を先に伝え、
一度確認できた後は速やかに効率的な方法へ切り替える。

### Phase 3 / Step 3-3：複数のBookを扱う

#### 実施内容

3冊のBook辞書を `books` リストへまとめ、`GET /books` と
`read_books` 関数を追加した。

`GET /books/1` は重複した固定辞書を返すのではなく、
同じデータ源である `books[0]` を返すように整理した。

Swagger UIで `GET /books/1` が1冊のJSONオブジェクトを、
`GET /books` が3冊のJSON配列を返すことを確認した。

#### 学んだこと

Pythonの辞書は1冊のBookを表し、辞書を入れたリストは複数のBookを表す。
Pythonのリストは位置を0から数えるため、`books[0]` は先頭のBookを取得する。

#### 次につながること

Phase 3 / Step 3-4で、アプリ実行中に追加・変更されたBookデータを
アプリ停止後も残すために何が必要か考える。

### Phase 3 / Step 3-4からPhase 4 / Step 4-1：DBが必要な理由

#### 判断・理由

Pythonの `books` リストへ実行中に追加したデータはメモリ上にだけ存在し、
Uvicornの停止や再起動によって消える。

ユーザーが追加・変更したBookをアプリ停止後も残す必要があるため、
アプリとは別にデータを永続保存するDBを使用する。

#### 次につながること

Phase 4 / Step 4-2で、今回のサービスに使用するDBを確定する。

### Phase 4 / Step 4-2：今回使用するDBを確定する

#### 判断・理由

今回のサービスは、複数ユーザーによるBook保存、評価、投稿、いいね、
フォローなどの関連データを扱い、最終的に本番環境へデプロイする。

その要件を踏まえ、ローカルファイルとして扱えるSQLiteではなく、
アプリとは別のサーバーとして動作するPostgreSQLを採用した。

#### 次につながること

Phase 4 / Step 4-3でPostgreSQLの現在の稼働状態を確認し、
FastAPIからDBへ接続する経路を作る。

### 初登場するコード要素の説明ルール

#### 発生した問題

SQLAlchemyの `URL.create()` を初めて提示した際に、
`URL` が何であり、`create` がどこに属する機能かを事前に説明しなかった。

#### 今後の対応

初めて登場する名前は、コードの入力や実行を求める前に、読み方、読み込み元、
モジュール・クラス・関数・メソッドなどの種類、役割、入力、内部処理、戻り値を説明する。

`.` でつながる表記についても各要素を分け、なぜその形で呼び出せるかを説明する。

### Phase 4 / Step 4-3からStep 4-4：DB接続とSQLAlchemy

#### 実施内容

PostgreSQLに専用ユーザー `book_api_user` と専用DB `book_api` を作成した。
専用ユーザーにはDB作成、ユーザー作成、スーパーユーザーの権限を与えず、
`book_api` の所有者として設定した。

DB接続情報はGit管理から除外した `.env` に保存し、
Pydantic Settingsで読み込み、必須項目と型を検証する構成にした。

SQLAlchemy 2.0.52、Psycopg 3.3.5、Pydantic Settings 2.15.0を導入し、
SQLAlchemyのEngineからPsycopgを通して `book_api` への接続に成功した。

#### 学んだこと

SQLAlchemyはPythonでDB構造と操作を表現してSQLを組み立て、
PsycopgはSQLAlchemyとPostgreSQLの間の通信を担当する。

`URL.create()` は接続先情報を表すURLオブジェクトを作り、
`create_engine()` は接続を管理するEngineオブジェクトを作る。
実際のDB通信は `engine.connect()` が呼ばれた時点で始まる。

#### 次につながること

Phase 4 / Step 4-5で、最初のBookモデルをSQLAlchemyで定義する。

### Phase 4 / Step 4-5：最初のBookモデルを作る

#### 実施内容

SQLAlchemyの `DeclarativeBase` を引き継ぐ共通の `Base` を作成し、
`models.py` に `Book` モデルを定義した。

`Book` は `books` テーブルに対応し、整数の主キー `id`、必須の文字列である
`title` と `author`、任意かつ重複禁止の `isbn` を持つ設計にした。
ISBN-13はハイフンを除いた13文字で保存する方針とした。

PythonからSQLAlchemyのテーブル設計情報を読み取り、テーブル名が `books`、
カラム名が `id`、`title`、`author`、`isbn` と認識されていることを確認した。

#### 学んだこと

`Mapped` はPython属性がDBカラムに対応することとPython側の型を表し、
`mapped_column()` は主キー、文字列長、NULLの許可、重複禁止などの
具体的なカラム設定を表す。

モデルを定義しただけではPostgreSQLにテーブルは作成されず、
この時点で存在するのはSQLAlchemyが管理するPython上の設計情報である。

#### 次につながること

Phase 5 / Step 5-1で、この設計をPostgreSQLへ反映し、
その後のテーブル変更も再現可能にする管理方法を考える。

### 提案時に今後の設計まで確認する講義ルール

#### 発生した問題

Alembicの `target_metadata` を設定する際、最初に `Book.metadata` を提案した。
現在の1モデルでは動作するが、今後Userなどのモデルとテーブルが増える
プロジェクト全体の設計を考えると、共通の `Base.metadata` を渡す方が適切だった。

#### 今後の対応

コードを提案する前に、現在の処理だけでなくROADMAP上の今後の機能、
共通化される対象、モデルや依存関係の増加を確認する。

現在の学習段階に必要な最小構成を保ちつつ、近い将来に明らかに必要となる
拡張を妨げない設計を選び、その理由を説明してから受講者へ提示する。

### Phase 5：AlembicでDB変更を管理する

#### 実施内容

Alembic 1.19.1を導入し、マイグレーション環境を初期化した。
`env.py`では `.env` から構築したDB接続URLを実行時の設定へ渡し、
全モデルの設計を対象にできるよう `Base.metadata` を設定した。

SQLAlchemyモデルとPostgreSQLを比較し、`books`テーブルを作成する
最初のマイグレーション `ba3bb4e64342` を自動生成した。
生成内容を確認してから `upgrade head` で適用した。

PostgreSQL上に `books` と `alembic_version` が存在することを確認し、
`books`の4カラム、主キー、自動採番、ISBNの重複禁止制約が
SQLAlchemyモデルと一致することを確認した。

#### 学んだこと

SQLAlchemyモデルは現在目指すテーブル設計を表し、マイグレーションは
現在のDBから次の構造へ変更する手順を履歴として残す。

`upgrade()`はDB構造を新しい状態へ進め、`downgrade()`は変更前へ戻す。
自動生成されたマイグレーションはすぐ適用せず、意図した変更だけか確認する。

#### 次につながること

Phase 6 / Step 6-1で、FastAPIからSQLAlchemyを通して
PostgreSQLへBookを登録する処理を作る。

### BookCreateをStep 6-1で導入する順序変更

#### 判断・理由

ROADMAPではCRUDの後にPydanticによる入出力整理を予定していたが、
POSTによるBook作成には入力データの形と検証が必要になる。

辞書やクエリパラメータによる一時的な入力を作ってすぐ捨てることを避け、
Step 6-1で入力用の最小限の `BookCreate` だけを導入する。

Create / Update / Responseを一度に作ることはせず、Phase 7では
実装済みCRUDを基に各スキーマの役割と配置を改めて整理する。

#### スキーマの配置

CRUDとPhase 7で複数のスキーマが必要になることが明確なため、
`BookCreate` を一時的に `main.py` へ置かず、`schemas.py` を作成する。

現時点では単一ファイルに留め、BookやUserごとのパッケージ分割は、
ファイルの責務と規模が増えてからPhase 8で検討する。

#### Bookルーターの配置

Book CRUDでエンドポイントが続けて増えることが明確なため、
Book関連の処理を一時的に `main.py` へ増やさず、`routers/books.py` へ配置する。

複数のルーターから再利用するSession依存性は `dependencies.py` へ移し、
`main.py` はFastAPIアプリの作成とルーター登録を主な責務とする。

この時点では、必要性がまだないservice層やCRUD層は追加しない。

### 処理の流れを考える講義方法

#### 受講者からの要望

処理の流れはCodexが最初から完成形を示さず、受講者自身が考える。
その際は一度に大きく問わず、小さなヒントを段階的に渡す。

答えに未学習の処理や名称が必要な場合は、受講者へ推測させる前に
その部分を短く説明し、既に学んだ内容を使って次の一段階を考えてもらう。

#### 今後の対応

`現在分かっていることの確認 → 未学習部分の説明 → 小さなヒント
→ 受講者が考える → 必要な場合だけ追加ヒント` の順で進める。

### Phase 6 / Step 6-1：Book作成

#### 実施内容

リクエストごとにSQLAlchemy Sessionを作成し、処理後に必ず閉じる
`get_db()`と、FastAPIで共有する `SessionDep` を作成した。

入力用の `BookCreate` を `schemas.py` に定義し、タイトルと著者の空文字・
空白だけの入力、255文字超過、ISBN-13の形式をDBへ送る前に検証する構成にした。

Book関連のエンドポイントを `routers/books.py` へ配置し、
`main.py`からBookルーターをFastAPI本体へ登録した。

`POST /books`でBookオブジェクトを作成し、Sessionへの追加、保存確定、
DBからの再読み込みを行って保存結果を返す処理を実装した。
Swagger UIでステータス201と自動生成されたIDを含むレスポンスを確認し、
PostgreSQLの `books` テーブルにも保存されていることを直接確認した。

#### 学んだこと

`db.add()`は追加対象としてSessionへ登録し、`db.commit()`でSQLの送信と
保存を確定する。`db.refresh()`はDBが生成したIDなどの現在値を読み直す。

FastAPIの依存性注入により、各リクエストへSessionを渡し、
成功・失敗にかかわらず処理後にSessionを閉じられる。

#### 次につながること

Phase 6 / Step 6-2で、固定したPythonリストではなく、
PostgreSQLからBook一覧を取得する処理へ変更する。

### Phase 6 / Step 6-2：Book一覧取得

#### 実施内容

`GET /books` が固定したPythonリストではなく、PostgreSQLの
`books`テーブルからBook一覧を取得して返すように変更した。

`select(Book)`で取得する対象を表す問い合わせを作成し、
`Session.scalars()`でその問い合わせを実行し、`.all()`で全Bookを取り出した。

Swagger UIで `GET /books` を実行し、以前PostgreSQLへ登録した
Bookがレスポンスに含まれることを確認した。

#### 学んだこと

`select(Book)`は問い合わせ内容を作る段階であり、その時点では
PostgreSQLへの問い合わせは実行されない。`Session.scalars(statement)`を
呼び出したときに問い合わせが実行される。

SessionはDBとのやり取りの窓口だが、Sessionのメソッドを
使うこととSQLがその場で実行されることは常に同じではない。

#### 次につながること

Phase 6 / Step 6-3で、URLから受け取ったIDに対応するBookを
PostgreSQLから1件取得する処理へ変更する。

### Phase 6 / Step 6-3：Book詳細取得

#### 実施内容

`GET /books/{book_id}` でパスパラメータの `book_id` を整数として受け取り、
`Session.get(Book, book_id)`で主キーが一致するBookを1件取得して返すように変更した。

Swagger UIでDBに存在するIDを指定し、ステータス200と、指定したIDに
対応する `title`、`author`、`isbn` を含むBookが返ることを確認した。

#### 学んだこと

FastAPIは `/{book_id}` と関数引数 `book_id: int` を対応させ、URL上の値を
整数へ変換・検証して関数へ渡す。

一覧取得では `select(Book)`、`Session.scalars()`、`.all()` を使い、
主キーを指定した1件取得では `Session.get(Book, book_id)` を使う。

#### 次につながること

Phase 6 / Step 6-4で、PUTとPATCHの違いを理解し、
Book更新APIで使う方法を考える。

### Book本体の管理者と一般ユーザーの操作範囲を修正

#### 変更前の問題

ROADMAPに「ユーザーが自分のBookだけを変更・削除できる」という記述があり、
Book本体がユーザー所有のデータであるように読める状態だった。

しかし、同じ書籍を複数ユーザーで共有するサービスで、一般ユーザーに
Book本体の手入力・更新・削除を許可すると、入力負担、重複データ、
書誌情報のばらつき、他ユーザーが参照するBookの変更・削除という問題が起こる。

#### 変更後の設計

Bookはサービス全体で共有する書籍マスタとし、一般ユーザーはBook本体を
手入力で登録・更新・削除しない設計に変更した。

将来、ユーザーが外部書籍APIの検索結果から本を選んだときは、
バックエンドがISBNなどで既存Bookを確認し、必要な場合だけ保存する。
ユーザーが登録・更新・削除するのは、読みたいリスト、読書記録、
学び・気づき、評価、投稿などの自分に紐づくデータとする。

Phase 6のBook CRUDは、CRUDとDB操作を学ぶための基礎実装として続け、
最終的には運営・管理用またはシステム内部用として保護する。

#### Step 6-4への影響

Bookの書誌情報を一部だけ修正する運営・管理用途を想定し、
Book更新APIにはPUTではなくPATCHを採用する。

### Phase 6 / Step 6-4：Book更新

#### 実施内容

運営・管理側がBookの書誌情報を部分的に修正する用途として、
`PATCH /books/{book_id}` を実装した。

更新用の `BookUpdate` を作成し、`title`、`author`、`isbn` を
未送信にできるようにしつつ、既存の文字数とISBN形式の制約を維持した。

`Session.get()`で更新対象を取得し、
`model_dump(exclude_unset=True)`で送信された項目だけを辞書にした。
辞書の各項目を `setattr()` でBookへ反映し、`commit()` で更新を確定後、
`refresh()` でDBの現在値を読み直して更新後のBookを返した。

Swagger UIでタイトルだけをPATCHし、タイトルが変更され、
未送信の著者とISBNは変わらないことを確認した。
続けてGETしても更新内容が残っていることから、PostgreSQLへの保存も確認した。

DB移行前に使っていたPythonの固定 `books` リストは、すべてのBook取得が
PostgreSQLを使うようになったため削除した。DB内のBookには影響しない。

#### 学んだこと

PUTはリソース全体の置き換え、PATCHは送信した変更の適用を表す。
今回はBookの一部項目を修正するためPATCHを採用した。

`exclude_unset=True` は値が `None` の項目を一律に除外するのではなく、
入力時に設定されなかった項目を除外する。そのため、未送信と
明示的な `null` を区別できる。

`setattr(target_book, field, value)` は、`field` が示す属性を
`value` で上書きする。その時点ではPython上のBookが変更された段階であり、
`commit()` でPostgreSQLへ更新を送って確定する。

#### 次につながること

Phase 6 / Step 6-5で、運営・管理用のBook削除処理を実装する。
その後、Step 6-6で存在しないBookとPATCHの不正な `null` を含む
異常系の処理を整理する。

### Phase 6 / Step 6-5：Book削除

#### 実施内容

CRUD学習と運営・管理用の基礎実装として、
`DELETE /books/{book_id}` を実装した。

`Session.get(Book, book_id)`で対象を取得し、`Session.delete(target_book)`で
Sessionの削除対象として登録後、`Session.commit()`でPostgreSQLへDELETEを送って
削除を確定する処理を作成した。

削除後に返す本文がないため、成功時のステータスを
`204 No Content` とした。削除専用のBookを新規登録し、そのIDと内容を
確認してからDELETEし、204とレスポンス本文がないことを確認した。

#### 学んだこと

`Session.delete()`は対象を削除予定としてSessionへ登録する段階であり、
`Session.commit()`で削除をPostgreSQLへ送って確定する。

Bookの行を削除しても、PostgreSQLのID発行用sequenceは過去に発行した値へ戻らない。
そのため、同じ内容を再登録しても削除したIDは再利用されず、
次のIDが発行される。IDは件数ではなく、データを一意に識別する値である。

現時点でBookに関連テーブルはないため行を物理削除した。将来、
読書記録や投稿がBookを参照する段階で、関連データがある場合の削除制限、
無効化、論理削除などを要件に合わせて再設計する。

#### 次につながること

Phase 6 / Step 6-6で、存在しないBook IDに対するGET・PATCH・DELETEと、
PATCHで必須項目へ明示的な `null` が送信された場合を扱う。

### Phase 6 / Step 6-6：Bookの異常系処理

#### 実施内容

存在しないBook IDをGET・PATCH・DELETEした場合に、
`404 Not Found` とBookが存在しないことを示す `detail` を返すようにした。

`BookUpdate`にPydanticの検証を追加し、`title`・`author`への
明示的な `null` と、更新項目が1つもないrequest bodyを
`422 Unprocessable Content` で拒否するようにした。

POST・PATCHで既存と同じISBNを保存すると、PostgreSQLのUNIQUE制約違反が
SQLAlchemyの `IntegrityError` として通知される。これを `db.commit()` の周囲で
捕捉し、`db.rollback()` 後に利用者向けの `409 Conflict` へ変換した。

Swagger UIで各異常系のステータスとレスポンスを確認し、
重複POSTで新しいBookが登録されないこと、重複PATCHで元のISBNが
維持されることもGETで確認した。

#### 学んだこと

Pydanticはrequest bodyの形式・型・個々の検証を担当するが、
DBに現在何が保存されているかまでは判断しない。
一方、UNIQUE制約は同時リクエストがあってもDB自身が重複を防ぐ。

`IntegrityError` はDBの整合性制約違反をアプリ内部へ伝える例外で、
`HTTPException` はその原因をHTTPステータスと利用者向けの説明に変換する。
`commit()` が失敗したSessionは、後続のDB操作前に `rollback()` が必要になる。

#### 次につながること

Phase 7 / Step 7-1で、実装済みの `BookCreate` と `BookUpdate` を比較し、
POSTとPATCHのrequest bodyに必要な項目の違いを整理する。

### Phase 7：PydanticとAPIの入出力整理

#### 実施内容

POSTではBookを新規作成するため `title`・`author` を必須とする
`BookCreate` を使い、PATCHでは送信した項目だけを更新できる
`BookUpdate` を使うという入力スキーマの役割を整理した。

一般ユーザー向けの出力は `id`・`title`・`author` に絞る方針とし、
出力専用の `BookResponse` を追加した。Bookを返すGET・POST・PATCHの
デコレータに `response_model` を設定し、一覧取得では
`list[BookResponse]` を使用した。DELETEは204で本文を返さないため設定していない。

Swagger UIで詳細・一覧・作成・更新を確認し、DBにはISBNが保存されたまま、
HTTPレスポンスからのみISBNが除外されることを確認した。

#### 学んだこと

入力スキーマはAPIが受け取る項目と検証を定義し、
出力スキーマはAPIが外部へ公開する項目を定義する。
同じBookでも、作成・部分更新・出力で必要な項目が異なるため、
`BookCreate`・`BookUpdate`・`BookResponse` の3つに役割を分ける。

`response_model` はDBのデータを変更するものではなく、
関数が返したデータをHTTPレスポンスの形に変換する際に、
スキーマに定義した項目だけに検証・フィルタリングする。

#### 次につながること

Phase 8 / Step 8-1で、現在の `main.py` と `routers/books.py` の役割を確認し、
コードが増えた際にrouterを機能ごとに分ける必要性を整理する。

### Phase 8：コード構成の整理

#### 確認内容

`main.py` はFastAPIアプリの作成とrouter登録、
`routers/books.py` はBook関連のエンドポイントという役割に
すでに分けられていることを確認した。

DB関連も、`config.py` が設定、`database.py` がEngine・Session・Base、
`dependencies.py` がFastAPIへSessionを渡す依存性という役割に分かれている。

#### 設計判断

現在はBookモデル1つ、Bookスキーマ3つの小さな構成であり、
models・schemasをさらに分割する利益より、ファイルとimportが増える負担が大きい。
そのため、Userや投稿などの機能を実際に追加し、責務が混在し始めた時点で
機能単位の分割を検討する。

router内のDB処理もまだ小さく、複数のエンドポイントから
共通利用するビジネスロジックが十分に生じていない。
service / CRUD層は形だけ先に導入せず、重複や再利用の必要が発生したときに追加する。

#### 次につながること

Phase 9 / Step 9-1で、ユーザー個人に紐づくデータを管理するために
Userが必要な理由を整理する。

### Phase 9 / Step 9-1からStep 9-2：Userの必要性とDBモデル

#### 実施内容

読みたいリスト、読書記録、学び・気づき、評価、投稿などを
「誰のデータか」区別するためにUserが必要だと整理した。

`users` テーブルに `id`、`username`、`email`、`hashed_password` を持つ
Userモデルを追加した。`id` は主キー、`username`・`email` は
必須かつ重複禁止、`hashed_password` は必須とした。

Alembicでマイグレーション `28308531d9c5_create_users_table.py` を生成し、
Userテーブル以外に意図しない変更がないことを確認後、PostgreSQLへ適用した。
`alembic current` と `psql` の `\d users` で、適用位置とテーブル構造を確認した。

#### 学んだこと

`username`・`email` はユーザーを識別するためUNIQUE制約が必要だが、
`hashed_password` はユーザーを一意に識別する値ではないため重複禁止にしない。

モデルを追加しただけではDBテーブルは作られない。
Alembicのautogenerateでモデルと現在のDBを比較して変更手順を生成し、
`upgrade head` はモデル自体ではなく生成済みのマイグレーションを適用する。

#### 開発順序の変更

元のROADMAPはユーザー登録後にパスワードハッシュを学ぶ順序だったが、
生パスワードを一時的にもDBへ保存する実装と、すぐ書き直す二度手間を避けるため、
受講者と合意のうえでStep 9-3をパスワードハッシュ、
Step 9-4をユーザー登録の順に変更した。

#### 次につながること

Phase 9 / Step 9-3で、生パスワードをDBへ保存しないための
パスワードハッシュを学び、登録APIの前提を作る。

### Phase 9 / Step 9-3からStep 9-4：パスワードハッシュとユーザー登録

#### 実施内容

FastAPI公式ドキュメントの推奨に合わせ、`pwdlib[argon2]` を導入した。
`security.py` に `PasswordHash.recommended()` のインスタンスと、
生パスワードをArgon2ハッシュへ変換する `hash_password()` を作成した。

Bookに加えてUserのスキーマが必要になったため、単一の `schemas.py` を
`schemas/books.py` と `schemas/users.py` の機能別パッケージに整理した。
User登録の入力用に `UserCreate`、出力用に `UserResponse` を追加した。
emailは `EmailStr` で検証するため `email-validator` も導入した。

`routers/users.py` を作成し、`POST /users` でユーザー登録を実装した。
request bodyの生パスワードをハッシュ化し、SQLAlchemyのUserには
`hashed_password` だけを渡してDBへ保存する。
`UserResponse` により、レスポンスは `id`・`username` だけに制限した。

usernameまたはemailのUNIQUE制約違反は `IntegrityError` として捕捉し、
`rollback()` 後に `409 Conflict` と利用者向けの説明を返すようにした。

#### 動作確認

Swagger UIで正常登録が201を返し、レスポンスにemail・password・hashed_passwordが
含まれないことを確認した。PostgreSQLで、生パスワードではなく
`$argon2id$` で始まるハッシュが保存されていることを確認した。

同じusername・emailの再登録は409、メール形式違反、8文字未満のpassword、
空白だけのusernameはPydanticの検証により422となることを確認した。

#### 学んだこと

利用者から受け取るのは `password` であり、`hashed_password` はバックエンドが
生成・保存する。登録時の入力にもレスポンスにも `hashed_password` は含めない。
ハッシュは復号してログインするのではなく、入力された生パスワードと
保存済みハッシュが対応するかを照合する。

#### 次につながること

Phase 9 / Step 9-5で、ユーザーをDBから取得し、
入力パスワードと保存済みハッシュを照合するログイン処理へ進む。

### Phase 9 / Step 9-5からStep 9-6：ログインとJWT発行

#### 実施内容

ログイン入力用の `UserLogin` と、JWTを返す `LoginResponse` を追加した。
`POST /users/login` はemailでUserを1件取得し、Userが存在しない場合と
`verify_password()` が偽を返した場合の両方で、同じメッセージの
`401 Unauthorized` を返すようにした。

PyJWTを導入し、`.env` のJWT秘密鍵をPydantic Settingsから読み取る構成にした。
JWTの有効時間は設定値として30分とし、署名アルゴリズムはHS256に固定した。
`create_access_token()` はUser IDを文字列へ変換して `sub` に入れ、
UTCの現在時刻から30分後を `exp` に入れて署名付きJWTを生成する。
ログイン成功時は `access_token` と `token_type: bearer` を返す。

#### 動作確認

Swagger UIで、正しいemail・passwordによるログインが200を返し、
レスポンスに `access_token` と `token_type: bearer` が含まれることを確認した。
存在しないemailと間違ったpasswordは同じ401、不正なemail形式と
空のpasswordはPydanticの入力検証により422になることを確認した。

#### 学んだこと

emailはDBから対象Userを探すために使い、生パスワードはDBの
`hashed_password` と照合する。Userの存在確認前にハッシュへアクセスすると、
`None` に属性がないため意図しない500エラーになる。

JWTは暗号化された秘密箱ではなく、内容を読み取ることはできる。
秘密鍵と署名により改ざんを検出し、`exp` によって利用可能な期間を制限する。
JWTにはpasswordやハッシュを入れず、Userを一意に識別するIDを `sub` に入れる。

#### 次につながること

Phase 9 / Step 9-7で、クライアントが送ったBearerトークンを受け取り、
JWTを検証して `sub` のUser IDからログインユーザーを取得する。

### Phase 9 / Step 9-7：JWTからログインユーザーを取得

#### 実施内容

HTTP Bearer方式を採用し、`HTTPBearer` でAuthorizationヘッダーの
`Bearer` とJWT文字列を分離する入口を作成した。現在のログインAPIは
email・passwordをJSONで受け取る独自形式のため、フォーム形式を前提とする
OAuth2 Password Flowの `OAuth2PasswordBearer` は使用しなかった。

`security.py` に `decode_access_token()` を作成した。
秘密鍵と許可するHS256を指定してJWTの署名と有効期限を検証し、
ペイロードの `sub` を整数のUser IDへ変換して返す。

`dependencies.py` に `get_current_user()` と `CurrentUserDep` を追加した。
JWT検証に失敗した場合、`sub` を整数へ変換できない場合、User IDに対応する
UserがDBに存在しない場合は、詳細な内部原因を外部へ区別せず401を返す。
認証失敗の401には `WWW-Authenticate: Bearer` ヘッダーを付ける。

`GET /users/me` を追加し、`CurrentUserDep` から受け取ったUserを
`UserResponse` により `id`・`username` だけに制限して返すようにした。

#### 動作確認

Swagger UIのAuthorizeへJWT文字列だけを設定し、正常なJWTでは
`GET /users/me` が200とテストUserの情報を返すことを確認した。
JWTなしは `HTTPBearer` が401と `Not authenticated` を返し、
不正なJWTは独自の認証処理が401と共通メッセージを返すことを確認した。
期限切れJWTについても401になることを確認した。

#### 学んだこと

クライアントは `Authorization: Bearer <JWT>` として認証情報を送る。
`HTTPBearer` はヘッダーを分解するが、JWTの署名や有効期限までは検証しない。
JWT検証、`sub` の変換、DBからのUser取得はアプリ側で実装する必要がある。

`Annotated` は基本の型にFastAPI向けの `Depends` 情報を付加できる。
`CurrentUserDep` に認証処理をまとめることで、各APIは引数に追加するだけで
同じログインUser取得処理を再利用できる。

#### 次につながること

Phase 9 / Step 9-8で、公開APIとログイン必須APIを分類し、
ユーザー個人に紐づく操作へ `CurrentUserDep` を適用する。

### Phase 9 / Step 9-8からStep 9-9：APIの公開範囲と管理者認可

#### 実施内容

本の一覧・詳細取得は未ログインでも使える公開APIとし、個人に紐づく操作は
ログイン必須とする方針を整理した。共通のBook情報は正確性が必要なため、
Book本体の登録・更新・削除は一般ユーザーに許可せず、管理者または
システム内部用として保護する設計にした。

Userモデルへ `is_admin` を追加し、Python側とPostgreSQL側の既定値を
ともに `false` とした。Alembicマイグレーションを作成・適用し、
既存ユーザーを含めて `is_admin` がNOT NULLかつfalseになることを確認した。

`get_current_admin()` は `CurrentUserDep` から認証済みUserを受け取り、
`is_admin` がfalseなら `403 Forbidden`、trueならUserを返す。
これを再利用する `AdminUserDep` を作り、`POST /books`、
`PATCH /books/{book_id}`、`DELETE /books/{book_id}`へ適用した。

#### 動作確認

Swagger UIで、有効なJWTを持つ一般ユーザーがBookの登録・更新・削除を
実行すると403になり、処理されないことを確認した。
テストユーザーを管理者へ変更して、登録は201、更新は200、削除は204となり、
削除後の取得が404になることを確認した。

#### 学んだこと

認証は「誰であるか」を確認し、認可は「その人に操作を許可するか」を判断する。
JWTを確認できない場合は401、本人を確認できても権限がない場合は403を使う。
JWTにはUser IDを保持し、管理者権限はリクエストごとにDBの最新の
`is_admin` を参照して判断する。

#### 次につながること

Phase 10 / Step 10-1で、ここまでの手動確認だけでは足りない理由を整理し、
基本APIの自動テスト導入へ進む。

### Phase 10 / Step 10-1からStep 10-6：基本テストの導入

#### 実施内容

pytestとテストクライアント用の依存関係を開発用requirementsへ追加した。
開発用DBを誤って変更しないよう、PostgreSQLに専用DB `book_api_test`を作成し、
FastAPIの`get_db()`をテスト用Sessionへ差し替えた。

fixtureでテスト用Book・一般User・管理者User・JWT・入力データを準備し、
`yield`後にテストデータを削除する構成にした。Bookの取得・登録・更新・削除、
User登録・正常ログイン・本人取得・誤ったパスワード、Book登録時の401・403・
ISBN重複409を含む13件を作成した。

#### 動作確認

テスト全体をまとめて実行し、`13 passed`となることを確認した。
Starlette内部のAnyIO非推奨API参照による警告が1件残るが、
テスト結果には影響しないため隠さず、ライブラリ側の更新を待つ方針とした。

#### 学んだこと

fixtureはテストに必要なデータや依存関係を準備し、`yield`後に後片付けできる。
APIレスポンスだけでなくDBを直接確認することで、保存・更新・削除が
実際に反映されたことまで保証できる。認証情報なしは401、認証済みでも
権限不足なら403として、認証と認可を分けてテストする。

#### 次につながること

Phase 11 / Feature 1で、読みたいリスト・優先度管理の設計へ進む。

### Phase 11 / Feature 1：読みたいリスト・優先度管理

#### 実施内容

UserとBookの関係を表す `UserBook` モデルと `user_books` テーブルを追加した。
User・Bookへの外部キーと、同じUserが同じBookを重複登録しないための
複合一意制約を設定した。優先度は `ReadingPriority` とPostgreSQLの
`reading_priority` Enumを使い、`high`・`medium`・`low` で表現した。

Alembicマイグレーションを開発用・テスト用DBに適用し、
JWTから取得したログインUserに対する `POST`・`GET`・`PATCH`・
`DELETE /users/me/books` を実装した。一覧取得では `relationship()` と
`joinedload()` を使い、関連するBook情報も返すようにした。

#### 動作確認

正常登録、重複409、Bookなし404、JWTなし401、不正な優先度422、
一覧取得、優先度更新、未登録Bookの更新404、削除の9件をテストした。
既存テストと合わせた全22件が成功した。

#### 学んだこと

`ForeignKey`、`Enum`、`UniqueConstraint` がそれぞれ保証する内容を整理した。
`relationship()` はPython上で関連オブジェクトをたどる仕組み、
`joinedload()` は一覧取得時のN+1クエリを避ける取得方法として学んだ。

また、テストが成功しても、URLやIDの参照対象を間違えると
本来の意図と違う理由で成功する偽陽性が起こり得ることを確認した。

#### 次につながること

Phase 11 / Feature 2で、「読みたい・読書中・完読」などの
読書ステータス管理の設計へ進む。

### Phase 11 / Feature 2：読書ステータス管理

#### 実施内容

`ReadingStatus` を追加し、`want_to_read`・`reading`・`completed` の
3状態を定義した。`status` はBook共通の情報ではなく、
各UserとBookの関係に属するため `UserBook` に保持する設計とした。
新規登録時はクライアントに状態を指定させず、アプリ側で
`want_to_read` を初期値にする方針とした。

PostgreSQLに `reading_status` Enum型とNOT NULLの `status` 列を追加した。
既存行のNULLを避けるため、列追加時だけ `WANT_TO_READ` の
`server_default` を使い、追加後にDB側デフォルトを削除した。
開発用・テスト用DBともに `a0d07068cbd1 (head)` まで適用した。

`PATCH /users/me/books/{book_id}/status` を追加し、ログインUserの
UserBookだけを更新するようにした。完読にはおすすめ度が必要なため、
Feature 3の実装前は `completed` への変更を409で拒否する。

#### 動作確認

新規UserBookの初期状態がAPIレスポンスとDBの両方で
`want_to_read` となることを確認した。読書中への更新200、
おすすめ度なしの完読409、不正な状態422、未登録UserBook 404、
JWTなし401を個別テストした。既存テストと合わせた全27件が成功した。

#### 学んだこと

優先度は「どれくらい読みたいか」、読書状態は
「現在どこまで進んでいるか」を表す別の概念である。
また、モデルの `default` はSQLAlchemy側、マイグレーションの
`server_default` はPostgreSQL側で値を設定する違いを整理した。
既存テーブルにNOT NULL列を追加する際は、既存行を
どの値で移行するか決める必要がある。

#### 次につながること

Phase 11 / Feature 3で、1〜5のおすすめ度を保存し、
おすすめ度と同時に完読へ変更できる設計へ進む。

### Phase 11 / Feature 3：おすすめ度評価

#### 実施内容

おすすめ度はUserごとにBookへ対して異なるため、
`UserBook.recommendation_score` としてNULLまたは1〜5の整数を保存する設計とした。
`ck_user_books_recommendation_score_range` で値の範囲を、
`ck_user_books_completed_requires_recommendation_score` で完読時の必須条件をDBにも保持した。
マイグレーション `3d757aa40a02` を開発用・テスト用DBに適用した。

状態変更APIで、おすすめ度と同時なら `completed` へ変更できるようにした。
また、完読済みのUserBookに限り、
`PATCH /users/me/books/{book_id}/recommendation-score` でおすすめ度を後から変更できるようにした。
完読を取り消した場合は、おすすめ度もNULLへ戻す設計とした。

#### 動作確認

完読とおすすめ度5の同時登録、完読後の5から4への変更を確認した。
完読前のおすすめ度変更は409、0と6は422、
未登録UserBookは404、JWTなしは401になることを確認した。
既存テストと合わせた全34件が成功した。

#### 学んだこと

計算対象となるおすすめ度はEnumではなく整数で保存し、
Pydanticの `Field(ge=1, le=5)` とPostgreSQLの `CheckConstraint` で二重に範囲を保護する。
「AならB」という条件は、SQLでは「Aではない OR B」と表現できる。
また、pytestの `parametrize` で同じテストを0と6の複数データで実行した。

#### 次につながること

Phase 11 / Feature 4で、1冊に対して複数の学び・気づきを
その都度追加できるデータ構造とAPIを設計する。

### Phase 11 / Feature 4：学び・気づき記録

#### 実施内容

1つのUserBookに複数の記録を持たせるため、`Insight` モデルを追加した。
Insightは主キー、UserBookへの外部キー、本文を持つ。
UserBook削除時に紐づくInsightも削除するため、外部キーへ
`ON DELETE CASCADE` を設定し、SQLAlchemyのrelationshipも整えた。

マイグレーション `22f250f52ddb` を開発用・テスト用DBへ適用した。
Insightの入力・出力スキーマと専用ルーターを作成し、本人の本に対する
POST・GET・PATCH・DELETEを実装した。一覧はIDの昇順で返す設計とした。

#### 動作確認

Swagger UIで複数登録、一覧取得、空配列、本文更新、削除を確認した。
空白本文は422、対象のUserBookまたはInsightがなければ404、
JWTがなければ401となることも確認した。

自動テストでは、レスポンスだけでなくDBへの保存・更新・削除、
UserBookとの紐づき、他人のInsightを変更・削除できないことも確認した。
既存テストと合わせた全52件が成功した。

#### 学んだこと

一覧レスポンスは `list[InsightResponse]` で表し、SQLAlchemyの
`order_by(Insight.id)` で返却順を明示する。404と空配列を区別するため、
最初に本人のUserBookを確認し、その後Insightを検索する構成とした。

エラーのステータスだけでなく、拒否された更新・削除の後にDBを確認することで、
他人のデータや元の本文が変化していないことまでテストできる。

#### 次につながること

Phase 11 / Feature 5で、未登録・未ログインのユーザーも利用できる
タイトル・著者による本の検索方法と、外部書籍APIの利用を検討する。
