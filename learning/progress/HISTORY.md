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

`learning/progress/CURRENT.md`

```text
現在地を管理する
↓
今どこにいる？
何が終わっている？
次に何をする？
どこから再開する？
```

`learning/progress/HISTORY.md`

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
learning/ROADMAP.md
learning/TEACHING_RULES.md
learning/DEVELOPMENT_LEARNING_POLICY.md
learning/progress/CURRENT.md
learning/progress/HISTORY.md
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
`learning/progress/CURRENT.md` を最新状態へ更新してください。

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

### Phase 11 / Feature 5（前半）：Google Booksキーワード検索

#### 実施内容

未登録・未ログインのユーザーも利用できる
`GET /books/search?q={keyword}` を追加した。
検索方法はタイトルの完全一致ではなく、Google Books API標準の
`q` を使ったキーワード検索とした。

Google Books APIとの通信処理は `services/google_books.py` に分離した。
APIキーはサーバー側の `.env` から読み込み、`x-goog-api-key` ヘッダーで送信する。
外部APIのレスポンスから、外部ID、タイトル、著者、ISBN-13を取り出し、
必要な値がすべて揃った本だけを `BookSearchResult` として返す設計とした。
複数の著者は ` / ` で連結する。

#### 入力検証とエラー処理

検索語は `StringConstraints` によって1文字以上とし、前後の空白を除去する。
検索語が未指定、空文字、空白のみの場合はFastAPIとPydanticが422を返す。

外部APIがエラーステータスを返した場合と接続に失敗した場合は502、
制限時間内に応答しなかった場合は504へ変換する設計とした。
外部APIから届いたレスポンスには `raise_for_status()` を実行し、
正常ではないHTTPステータスを `HTTPStatusError` として検出する。

#### 動作確認

実際のGoogle Books APIで「GANTZ」を検索し、整形済みの検索結果が
Swagger UIから返ることを確認した。

自動テストでは正常系、検索語の検証、外部APIのHTTPエラー・接続失敗・
タイムアウト、空の検索結果、不完全な書籍の除外、レスポンス整形を確認した。
検索機能のテスト11件、既存機能を含む全63件が成功した。

#### 学んだこと

FastAPIが受け取るリクエストと、`httpx2` が外部APIへ送るリクエストは
別の通信である。`httpx2.get()` はレスポンスを受け取り、
`raise_for_status()` はそのHTTPステータスを検査する。
一方、タイムアウトや接続失敗はレスポンスを受け取る前に発生する。

pytestの `monkeypatch` を使い、実際のGoogle Books APIへ通信せずに、
ルーターやサービスが各結果・例外を正しく処理することを確認した。
テストコードが `return` より後ろに入って実行されない場合や、
関数名が `test_` で始まらず収集されない場合でも成功表示になり得るため、
pytestの収集件数を確認する重要性も学んだ。

#### 次につながること

Feature 5後半では、選択した検索結果を外部IDで再取得し、
ISBNが一致する既存Bookを再利用するか、新しいBookを作成したうえで、
ログインUserのUserBook（読みたいリスト）へ追加するAPIを設計する。

### Phase 11 / Feature 5（後半）：検索結果から読みたいリストへ追加

#### 実施内容

`external_id` と `priority` を受け取る `UserBookFromSearchCreate` を作成し、
ログイン中のユーザーが検索結果から本を読みたいリストへ追加する
`POST /users/me/books/from-search` を実装した。

クライアントからタイトル・著者・ISBNを信頼して受け取らず、
バックエンドが `external_id` を使ってGoogle Books APIから書籍情報を再取得する。
取得処理は `get_google_book()`、検索と共通の整形処理は
`_parse_google_book()` に分離した。

取得したISBNで既存Bookを検索し、存在する場合は再利用する。
存在しない場合だけBookを作成し、`flush()` でBook IDを取得した後、
UserBookを作成して同じトランザクションで `commit()` する構成とした。

同じ本の重複登録は409、Google Booksに本が存在しない場合は404、
必要な書籍情報が不足する場合は422、接続失敗と異常応答は502、
タイムアウトは504とするエラー処理を追加した。

#### 動作確認

自動テストで、新規BookとUserBookの作成、既存Bookの再利用、
重複登録、JWTなし、入力検証、書籍情報不足、Google Booksの404・500、
接続失敗、タイムアウトを確認した。
Google Booksの1冊取得処理についても、正常応答の整形と
`raise_for_status()` による異常応答の検出をテストした。

検索・UserBook関連のテスト46件と、既存機能を含む全テスト77件が成功した。
Swagger UIで実際に検索結果から追加し、201レスポンスと、
`GET /users/me/books` によるBookとUserBookの保存・紐付きも確認した。

#### 学んだこと

`flush()` はトランザクションを確定せずにSQLをDBへ送り、
自動採番されたIDなどを取得できる。`commit()` は未送信の変更も送信し、
トランザクションを確定する。失敗時は `rollback()` でまとめて取り消せる。

その他に、SQLAlchemyのORMオブジェクトとSessionの所有関係、
検索後の同時実行でUNIQUE制約違反が起こる可能性、
`monkeypatch` で置き換える実際の参照先、通信前・応答後それぞれの
HTTP例外が持つRequestとResponseの違いを確認した。

#### 次につながること

Phase 11 / Feature 6で、1冊のBookに複数ジャンルを設定するための
データ構造と多対多の関係、ジャンル検索APIの要件を整理する。

### Phase 11 / Feature 6：ジャンル機能の見送り

#### 方針変更

2026-09-16、ジャンル属性の保存とジャンル検索は、
今回の実装対象から外すことを決定した。
本の検索は、Feature 5で実装したGoogle Books APIの
`q` を使うキーワード検索に一本化する。

この決定により、Genreモデル、genresテーブル、
BookとGenreの中間テーブル、Google Booksのcategoriesの保存、
ジャンル検索APIは作成しない。
ジャンル機能を利用するコードはまだ実装していないため、
既存コードとDBの削除・変更は発生しない。

#### 影響範囲

書籍詳細の表示候補からジャンルを外した。
関連書籍レコメンドで予定していた「同じジャンル」という条件も使わず、
同機能に着手するときに利用可能なデータから改めて設計する。

#### 次につながること

Phase 11 / Feature 7の書籍詳細へ進み、公開情報と
ログイン中のユーザーだけに必要な個人用情報を整理する。

### Phase 11 / Feature 6：代表ジャンルの追加へ方針修正

#### 方針変更

ジャンル検索は引き続き実装しないが、
書籍詳細で本の種類を理解しやすくするため、
Bookに代表ジャンルを1つ保存する方針へ修正した。

Google Booksの `volumeInfo.mainCategory` をそのままフロントエンドへ返さず、
バックエンドでアプリ内部の値へ変換してBookに保存する。
初期値は `manga`、`novel`、`business`、`self_help`、
`technology`、`humanities`、`science`、`other` の8種類とし、
未知のGoogle Booksカテゴリは `other` に変換する。

#### 実装範囲

Genreモデル、BookとGenreの中間テーブル、複数ジャンルの管理、
ジャンル検索APIは作成しない。
フロントエンドは、APIから受け取ったアプリ内部値を
対応する日本語のジャンル名として表示する。

#### 次につながること

Bookの代表ジャンルに使う型、NULLの扱い、
Google Booksのカテゴリからアプリ内部値への変換ルールを設計する。

### Phase 11 / Feature 6：代表ジャンルの取得・変換・保存

#### 実施内容

`BookGenre` を追加し、`manga`、`novel`、`business`、`self_help`、
`technology`、`humanities`、`science`、`other` の8種類を定義した。
BookにNULL禁止の `genre` を追加し、値を指定しない新規Bookは
SQLAlchemy側の既定値で `other` とする設計とした。

マイグレーション `ae226236b2ef` でPostgreSQLの `book_genre` Enum型と
`books.genre` を追加した。既存Bookには一時的な `server_default="OTHER"` で
値を入れ、追加後にDB側の既定値を削除した。
開発用・テスト用DBの両方へ適用済み。

Google Booksの `mainCategory` を優先し、値がない場合は
`categories[0]` を使うフォールバックを追加した。
英語カテゴリのキーワードを8種類のアプリ内部値へ変換し、
カテゴリがない場合と未対応カテゴリは `other` とする。

検索レスポンスに `genre` を追加した。
検索結果から新規Bookを作成する場合は変換後のジャンルを保存し、
既存Bookは現在値が `other` でGoogle Books側が具体的なジャンルの場合だけ補完する。
既存の具体的なジャンルは上書きしない。

#### 動作確認

カテゴリ変換の9ケース、`mainCategory` と `categories`の両経路、
新規Bookへの保存、既存Bookの補完、既存ジャンルの保護を自動テストした。
既存機能を含む全87件が成功した。

Swagger UIから `GET /books/search?q=Clean Code` を実行し、
Google Booksのカテゴリから `technology` へ変換された検索結果を確認した。
カテゴリ自体がない本や、`Reference / General` など現在の
変換ルールにないカテゴリは `other` になることも確認した。

#### 学んだこと

SQLAlchemy側の `default` とPostgreSQL側の `server_default` の担当範囲、
既存行があるテーブルへNULL禁止カムを追加する方法、
Enum型を作成・削除するマイグレーションの順序を確認した。

また、フォールバックの役割、空リストの真偽値、
文字列とリストの `[0]` の違い、大文字・小文字を揃えた
部分一致によるカテゴリ変換を学んだ。

#### 次につながること

Phase 11 / Feature 7で、代表ジャンルを含む書籍詳細と、
未ログインの閲覧者にも公開する値、ログイン中のユーザーにだけ返す値を設計する。

### 開発基盤：GitHub ActionsによるCIの導入

#### 実施内容

2026-09-20、`.github/workflows/ci.yml` を追加し、
main向けのPull Requestとmainへのpush時にCIを実行するようにした。

GitHubが用意するUbuntu環境でPython 3.14をセットアップし、
`requirements.txt` と `requirements-dev.txt` から依存関係をインストールする。
PostgreSQL 17をサービスコンテナとして起動し、`pg_isready` による
ヘルスチェック後、Alembicの最新マイグレーションとpytestを順番に実行する。

CI環境では実際の秘密情報を使わず、DB接続、JWT、Google Books APIに
テスト専用値を設定した。pipのダウンロードキャッシュも有効にした。

#### 動作確認

ローカルでテストDBへのAlembicマイグレーションと全87件のテスト成功を確認した。
PR #7でGitHub Actions上のCI成功を確認し、mainへマージした。

#### 学んだこと

Workflow、Job、Stepの階層、`uses` と `run` の違い、
Job側とPostgreSQLサービス側の環境変数の役割を確認した。
また、ポートマッピング、ヘルスチェック、pipキャッシュの必要性と、
CIは人間のように設計をレビューするのではなく、定義した検査を自動実行する仕組みだと理解した。

#### 次につながること

Phase 11 / Feature 7の書籍詳細の要件整理から開発を再開する。

### Phase 11 / Feature 7：書籍詳細

#### 設計判断

未登録・未ログインでも閲覧できる公開書籍詳細と、
ログインユーザー本人のUserBook状態を含む書籍詳細を分けた。
公開APIは `GET /books/{book_id}`、認証済みAPIは
`GET /users/me/books/{book_id}` とした。
ログイン済みの画面は認証済みAPIだけを呼び、公開APIとの
2回のHTTPリクエストを必要としない設計にした。

公開情報はBookのID、タイトル、著者、代表ジャンル、平均おすすめ度とした。
ISBNは照合・重複防止には必要だが、利用者向け詳細には表示しない。
他ユーザーのおすすめ理由は読了投稿がまだ存在しないため、Feature 8以降へ延期した。

#### 実施内容

`BookDetailResponse` と `UserBookDetailResponse` を追加した。
共通処理は `services/book_detail.py` の
`get_book_with_average_score()` に分離し、Bookと
`UserBook.recommendation_score` の平均を1回のDB問い合わせで取得する。
平均計算はPostgreSQLの `AVG`、小数第1位への丸めはPythonが担当する。
おすすめ度がない場合は `null` を返す。

認証済みAPIは共通サービスの結果に加え、ログインユーザーとBookの
組み合わせに一致するUserBookを取得する。未登録の場合も404にはせず、
`is_registered=false` と個人項目の `null` をステータス200で返す。
Book自体が存在しない場合は404、不正なBook IDは422、JWTなしは401とした。
既存のModelと外部キーで実現できるため、ModelとMigrationは追加していない。

#### 動作確認

公開APIの平均なし・平均あり・404・422・認証不要をテストした。
平均は3人のおすすめ度 `5`、`4`、`4` から得られる値を
小数第1位の `4.3` へ丸めることも確認した。
認証済みAPIでは登録済み、未登録、JWTなし、404、422を確認した。
既存機能を含む全99件が成功した。

#### 学んだこと

HTTPリクエスト数と、1回のAPI処理内で行うDB問い合わせ数は別である。
認証はアクセス中のUserを特定する処理であり、Bookの共通情報や
本人のUserBook状態を取得する処理とは役割が異なる。
また、外部結合によってUserBookがないBookも取得できること、
通常列と集約関数を同時に取得するときの `GROUP BY`、
SQLAlchemyの行データのアンパックを確認した。

#### 次につながること

Phase 11 / Feature 8で、読了投稿に必要なデータ、UserBookとの関係、
公開状態、おすすめ度を重複保存するかを設計する。

### Phase 11 / Feature 8：読了投稿

#### 設計判断

読了投稿は将来のいいね・タイムラインといった拡張を考慮し、
UserBookとは別の `reading_posts` テーブルとした。
1件のUserBookに対してReadingPostは0または1件とし、
`user_book_id` のUNIQUE制約でDBにも重複禁止を保証させた。

ReadingPostにはID、UserBookへの外部キー、おすすめ理由、
公開状態、作成日時を保存する。
おすすめ度はUserBookを正とし、ReadingPostへ重複保存しない。
公開状態の初期値は `true` とし、作成時の明示的な `false` も受け付ける。

投稿作成は本人のUserBookが `completed` で、
おすすめ度が登録済みの場合に限定した。
ReadingPostが存在する間は、UserBookの削除と
`completed` 以外への状態変更を409で拒否する。

#### 実施内容

`ReadingPost` ModelとAlembic migration `f7094080c4f4` を追加し、
開発用・テスト用PostgreSQLへ適用した。
おすすめ理由は1〜1000文字、空白のみを禁止し、
PydanticとPostgreSQLの両方で制約した。

本人用の次のAPIを追加した。

- `POST /users/me/books/{book_id}/reading-post`
- `GET /users/me/books/{book_id}/reading-post`
- `PATCH /users/me/books/{book_id}/reading-post`
- `DELETE /users/me/books/{book_id}/reading-post`

POSTでは通常の事前重複チェックに加え、
同一UserBookへの同時リクエストでUNIQUE制約違反が起き得るため、
`IntegrityError` を捕捉して `rollback()` 後に409を返すようにした。

#### 動作確認

作成・取得・おすすめ理由の更新・削除の正常系に加え、
UserBookなし、ReadingPostなし、未認証、他人の投稿、
不正なおすすめ理由、重複作成をテストした。
`monkeypatch` でDBのUNIQUE制約違反相当の `IntegrityError` を再現し、
409応答と `rollback()` 実行も確認した。
既存機能を含む全133件のテストが成功した。

#### 学んだこと

1対1関係の `Mapped` 型、relationshipと外部キーの役割の違い、
`DateTime(timezone=True)`、DB側の `server_default`、
名前付きのUNIQUE・CHECK制約を確認した。
また、事前チェックだけでは同時リクエストを防げず、
DB制約を最後の保証とし、APIがDB例外を適切なHTTP応答へ変換する必要があると学んだ。

#### 次につながること

Phase 11 / Feature 9で、本人が読了投稿の
公開・非公開を後から切り替えられるようにする。

### Phase 11 / Feature 9：投稿公開設定

#### 設計判断

おすすめ理由の更新と公開状態の更新を分け、
各APIの役割を明確にするため、公開状態専用の
`PATCH /users/me/books/{book_id}/reading-post/visibility` を採用した。

入力は `ReadingPostVisibilityUpdate` の `is_public: bool` だけとし、
更新後は既存の `ReadingPostResponse` を返す。
`is_public` はFeature 8でReadingPostに追加済みのため、
ModelとMigrationは追加しない。

#### 実施内容

認証中のUser IDとBook IDの組み合わせで本人のUserBookを取得し、
ReadingPostがある場合だけ `is_public` を更新するAPIを追加した。
UserBookまたはReadingPostがない場合と、
他ユーザーのデータに対する操作は404を返す。

#### 動作確認

公開から非公開への変更とDB保存、
必須値なし・`null`・boolへ変換できない文字列の422を確認した。
また、JWTなしの401、他ユーザーと対象不存在の404、
失敗時に所有者の公開状態が変更されないことをテストした。

読了投稿テスト40件、既存機能を含む全141件が成功した。

#### 学んだこと

`user_book.reading_post` はDBの関連行をPython上のReadingPost
ORMオブジェクトとして取得すること、ローカル変数への代入は
オブジェクトのコピーではなく同じオブジェクトへの参照であることを確認した。
また、未認証は401、認証済みでも本人の対象がない場合は
404とする認証と所有者確認の違いを確認した。

#### 次につながること

Phase 11 / Feature 10で、公開された読了投稿に対するいいねの
要件、UserとReadingPostの関係、重複禁止の保証場所を設計する。

### Phase 11 / Feature 10：いいね

#### 設計判断

Likeは、いいねしたUserと対象のReadingPostを結ぶ独立した
`likes` テーブルとした。1人のUserは複数のLikeを持ち、
1件のReadingPostも複数のLikeを持てる。
1件のLikeは1人のUserと1件のReadingPostに所属する。

Likeの存在自体をいいね済みの状態として扱い、`is_liked` は持たせない。
同じUserが同じReadingPostへ複数回いいねできないよう、
`user_id` と `reading_post_id` の組み合わせに複合UNIQUE制約を設けた。
UserまたはReadingPostが削除された場合は、外部キーの
`ON DELETE CASCADE` により関連するLikeも削除する。

いいねと解除は、対象投稿をURLで明確にするため次のAPIとした。

- `POST /reading-posts/{reading_post_id}/likes`
- `DELETE /reading-posts/{reading_post_id}/likes`

ログイン中のユーザーは、他ユーザーの公開投稿だけをいいねできる。
自分の投稿は409、存在しない投稿と非公開投稿は404、
重複いいねは409、本人のLikeがない解除は404とした。

#### 実施内容

`Like` Model、`LikeResponse` Schema、Like Router、
Alembic migration `3e68536e19a9` を追加した。
Migrationは開発用・テスト用PostgreSQLへ適用し、主キー、NOT NULL、
複合UNIQUE制約、2つのCASCADE外部キー、作成日時の既定値を確認した。

POSTでは通常の事前重複チェックに加え、同時リクエストによる
UNIQUE制約違反に備えて `IntegrityError` を捕捉し、
`rollback()` 後に409へ変換する。DELETEでは、ログイン中の
ユーザーと対象投稿の組み合わせに一致するLikeだけを削除する。

#### 動作確認

作成・解除の正常系に加え、未認証、対象投稿なし、非公開投稿、
自分の投稿、重複いいね、Likeなしの解除、他ユーザーのLikeを
削除しないこと、DB制約違反時のrollbackを確認した。
また、複合UNIQUE制約が別ユーザーによる同じ投稿へのいいねと、
同じユーザーによる別投稿へのいいねを許可することも確認した。

User削除時とReadingPost削除時にLikeがCASCADE削除されることを含め、
Like機能のテスト17件、既存機能を含む全158件が成功した。

#### 学んだこと

Likeの存在を状態として表す設計、複合UNIQUE制約の対象範囲、
2つの外部キーのどちらの親が削除されてもLike行全体が削除されること、
事前SELECTとDB制約が異なる役割を持つことを確認した。
また、セット内包表記を使い、DBから取得したLikeの
`reading_post_id` を順序に依存せず比較する方法を確認した。

#### 次につながること

Phase 11 / Feature 11で、User同士のフォロー関係、
重複フォローと自分自身へのフォローをどう扱うか設計する。

### Phase 11 / Feature 11：フォロー

#### 設計判断

Followは、フォローするUserとフォローされるUserを結ぶ独立した
`follows` テーブルとした。`follower_id` はフォローする側、
`followed_id` はフォローされる側を表し、どちらも `users.id` を参照する。

同じUser同士の重複フォローは、`follower_id` と `followed_id` の
複合UNIQUE制約で禁止する。自己フォローはAPIで事前確認するとともに、
`follower_id != followed_id` のCHECK制約をDBの最終保証とした。
どちらのUserが削除された場合も、2本の外部キーに設定した
`ON DELETE CASCADE` により関連するFollowを削除する。

フォロー登録・解除は次のAPIとした。

- `POST /users/{followed_user_id}/follow`
- `DELETE /users/{followed_user_id}/follow`

POST成功はFollow情報を201で返し、DELETE成功は本文なしの204とする。
対象Userなしと本人のFollowなしは404、未認証は401、
自己フォローと重複フォローは409とした。

今回のAPI範囲は登録・解除だけとし、フォロー中・フォロワー一覧は
Feature 12以降で必要性とレスポンスを設計する。

#### 実施内容

`Follow` Model、`FollowResponse` Schema、Follow Router、
Alembic migration `8b0cbe61798d` を追加した。
Migrationは開発用・テスト用PostgreSQLへ適用し、主キー、NOT NULL、
複合UNIQUE、自己フォロー禁止CHECK、2本のCASCADE外部キー、
作成日時の既定値を確認した。

User側には `following_relationships` と `follower_relationships`、
Follow側には `follower` と `followed` を追加した。
同じ `users` テーブルへ2本の外部キーがあるため、各relationshipへ
使用する `foreign_keys` と対応する `back_populates` を明示した。
User側は複数のFollow、Follow側は各1人のUserとして型を定義し、
DBのCASCADEと連携する削除設定も追加した。

POSTでは対象User、自己フォロー、重複Followを事前確認する。
同時リクエストによるUNIQUE制約違反に備え、`commit()`の
`IntegrityError` を捕捉して `rollback()` 後に409へ変換する。
DELETEでは、ログイン中のUserと対象Userの組み合わせに一致する
本人のFollowだけを削除する。

#### 動作確認

登録・解除の正常系、未認証、対象Userなし、自己フォロー、重複、
Followなしの解除、他ユーザーのFollowを削除できないこと、
DB制約違反時のrollbackを確認した。

複合UNIQUE制約が、同じUserによる異なるUserへのフォローと、
異なるUserによる同じUserへのフォローを許可することを確認した。
CHECK制約による自己フォロー拒否、4つのrelationship、
フォローする側・される側それぞれのUser削除時のCASCADEもテストした。
Follow機能のテスト17件、既存機能を含む全175件が成功した。

#### 学んだこと

同じテーブルを2本の外部キーで参照する自己参照関係では、
`relationship()`へ使用する `foreign_keys` を明示する必要がある。
User側は `Mapped[list["Follow"]]`、Follow側は `Mapped[User]` とし、
複数と単数の関係を型で表すことを確認した。

また、`Session.expire_all()`によって保持中のORM状態を期限切れにし、
次の属性アクセス時にDBから最新状態を読み直す流れを確認した。
`pytest.raises()`で期待するDB例外を捕捉し、`IntegrityError.orig`から
原因となったCHECK制約まで確認する方法も学んだ。

#### 次につながること

Phase 11 / Feature 12で、ユーザープロフィール・公開本棚に表示する情報、
完読冊数の集計範囲、公開するBookの条件と必要なAPIを設計する。

### Phase 11 / Feature 12：ユーザープロフィール・公開本棚

#### 設計判断

未ログインユーザーも閲覧できる公開APIとして、
`GET /users/{user_id}/profile` を採用した。
レスポンスはユーザー名、bio、完読冊数、フォロワー数、
公開本棚を含む。完読冊数は非公開分も数え、
公開本棚は公開ReadingPostがある本だけを新着順で返す。

プロフィール画像はバックエンドで保存せず、現時点では
フロントエンドの既定画像で表示する方針とした。
UserにNULL許可の `bio` を追加し、1〜160文字とし、
空白のみの値をDBのCHECK制約で禁止した。

複数テーブルの取得・集計とレスポンス構築を行うため、
処理は `services/profile.py` へ分離し、RouterはHTTP入出力と
Serviceが返した `None` の404への変換を担当する構成とした。

#### 実施内容

UserのbioとCHECK制約を追加するAlembic migration
`6a686afe7bbf` を開発用・テスト用DBに適用した。
`UserProfileResponse` と `PublicBookshelfBookResponse`、
Profile Service、Profile Routerを追加し、`main.py` へ登録した。

公開本棚はUserBook、Book、ReadingPostをJOINし、
必要なカラムだけを選択して `mappings()` でキー付きの行として取得し、
Schemaへキーワード引数として渡した。

ReadingPostのレスポンスに現在の
`UserBook.recommendation_score` を含めるため、
共通の `_build_reading_post_response()` を追加した。

#### 動作確認

プロフィールの全項目、存在しないUserの404、bio・件数・公開本が
空の状態、非公開ReadingPostの除外、公開本の新着順を確認した。
bioの161文字と空白のみをDB制約が拒否し、
`rollback()` 後も不正値が保存されないことも確認した。

追加したテスト8件を含め、既存機能を含む全183件が成功した。

#### 学んだこと

ORMクラスのカラム属性はSQL条件を作る表現として使えること、
JOINしたModelのカラムをWHERE条件に使えること、
`execute()`・`mappings()`・`all()`の役割を確認した。
また、外部キーで参照する子データを親より先に削除する必要と、
`try / finally` によるテストデータの後片付けも確認した。

#### 次につながること

Phase 11 / Feature 13で、全ユーザーの公開投稿を表示する
「おすすめ」と、フォロー中ユーザーの公開投稿を表示する
「フォロー中」のタイムラインを設計する。

### Phase 11 / Feature 13：タイムライン

#### 設計判断

タイムラインは新しいデータを保存せず、ReadingPost、UserBook、
Book、User、Followの既存データをJOINして構築するため、
新しいModel・テーブル・Migrationは追加しない。

認証条件と取得条件を明確に分けるため、
次の2つのAPIを採用した。

- `GET /timeline/recommended`：未ログインでも閲覧可能
- `GET /timeline/following`：ログイン必須

おすすめは全ユーザーの公開ReadingPost、フォロー中は
ログイン中ユーザーがフォローしている相手の公開ReadingPostだけを、
どちらも `ReadingPost.created_at` の降順で返す。

両APIは同じ `TimelinePostResponse` を使い、ReadingPost ID、
投稿者のUser ID・ユーザー名、Book ID・タイトル、現在のおすすめ度、
おすすめ理由、投稿日時を返す。

#### 実施内容

`schemas/timelines.py`、`services/timelines.py`、`routers/timelines.py`、
`tests/test_timelines.py` を追加し、Routerを `main.py` へ登録した。

Serviceでは、ReadingPostを起点にUserBookを経由して
BookとUserをJOINする共通Statementを
`_build_base_timeline_statement()` で組み立てる。
おすすめは公開条件を追加し、フォロー中はさらに
`Follow.followed_id == User.id` でFollowをJOINし、
`Follow.follower_id == current_user.id` で閲覧者のフォロー関係へ絞り込む。

Statementを `db.execute()` で実行し、`mappings().all()` で取得した
RowMappingを1件ずつ `TimelinePostResponse` へ変換して返す。

#### 動作確認

おすすめの全項目、非公開投稿の除外、新着順、0件時の空リスト、
未認証での閲覧を確認した。フォロー中は全項目、非公開投稿の除外、
未フォローユーザーの除外、未認証の401、新着順を確認した。

タイムラインテスト9件、既存機能を含む全192件が成功した。

#### 学んだこと

JOINはORMオブジェクトを順番に取得する処理ではなく、
複数テーブルの行をどの条件で接続するかを定義する処理である。
`select()`・`select_from()`・`join()`・`where()`・`order_by()` は
Statementの設計図を作り、`db.execute()` で初めてDBへ問い合わせる。

また、リスト内包表記は実際のリストを作り、
`list[TimelinePostResponse]` はリストの要素型を表す型情報であることも確認した。

#### 次につながること

Phase 11 / Feature 14で、現在のBook・ジャンル・平均おすすめ度を使った
単純な関連書籍レコメンドを設計する。

### Phase 11 / Feature 14：表紙画像URL対応

#### 設計判断

関連書籍、書籍詳細、検索結果、読了投稿、本棚で表紙を表示するため、
画像ファイル自体ではなくGoogle Booksが返す画像URLをBookへ保存する。
URLは長さの明確な業務上限がないため `Text`、画像がない本も扱うため
NULL許可の `cover_image_url` とした。

保存するURLは `small`、`thumbnail`、`smallThumbnail` の順に選び、
すべてない場合はNULLとする。1つの比較的大きな画像を保存し、
一覧表示ではフロントエンドのCSSで縮小する方針を採用した。

#### 実施内容

BookモデルとMigration `5a7df84bc82c` に `cover_image_url` を追加し、
開発用・テスト用DBへ適用した。Google Booksの検索結果を解析して
画像URLを選び、新規Bookへ保存する処理を追加した。

同じISBNの既存Bookでは、画像URLがNULLの場合だけGoogle Booksの値で
補完し、すでにURLがある場合は上書きしない。

`BookResponse`、`BookSearchResult`、`TimelinePostResponse`、
`PublicBookshelfBookResponse`へ画像URLを追加し、検索結果、書籍詳細、
マイ本棚、おすすめ・フォロー中タイムライン、公開本棚で返せるようにした。

#### 動作確認

Google Booksの3サイズの優先順位と画像なし、Bookへの新規保存・補完・
既存URLの保護、書籍詳細、マイ本棚、2種類のタイムライン、公開本棚を確認した。
既存機能を含む全198件のテストが成功した。

#### 次につながること

保存した表紙画像URLを利用し、未ログインでも取得できる関連書籍APIの
関連条件、並び順、最大件数、レスポンス項目を設計する。

### Phase 11 / Feature 14：関連書籍レコメンド

#### 設計判断

書籍詳細画面の下側で未ログインユーザーにも関連書籍を見せるため、
`GET /books/{book_id}/related` を公開APIとして追加した。

最初の単純な関連条件は対象本と同じ代表ジャンルとし、対象本自身は除外する。
平均おすすめ度の降順で、未評価本は最後に並べ、最大4件を返す。
未評価本も関連候補として残すため、BookからUserBookへは `outerjoin()` を使用する。

レスポンスはBook ID、タイトル、表紙画像URL、平均おすすめ度とし、
平均おすすめ度は既存の書籍詳細APIと同じく小数第1位へ丸める。

#### 実施内容

`RelatedBookResponse`、`services/related_books.py`、
`GET /books/{book_id}/related`、`tests/test_related_books.py` を追加した。

ServiceではBookごとに `group_by(Book.id)` し、UserBookのおすすめ度を
`AVG()` で集計する。`desc().nulls_last()` で評価ありを高い順、
未評価を最後に並べ、`limit(4)` で最大件数を制限する。

対象本がない場合は404、対象本があり関連書籍がない場合は
200と空リストを返す。0以下のBook IDは `Path(gt=0)` により422とする。

#### 動作確認

同じジャンルの取得、対象本自身と別ジャンルの除外、表紙画像URL、
平均値の小数第1位への丸め、未評価本、空リスト、404、最大4件、
平均おすすめ度の降順とNULLの最後配置、0と負数IDの422を確認した。
関連書籍テスト8件、既存機能を含む全206件が成功した。

#### 学んだこと

`group_by(Book.id)` は結合後の複数UserBookを本1冊ごとにまとめ、
その単位で平均値を計算するために必要である。
`mappings()` はSELECTした列名と値をRowMappingとして対応付け、
`**` はマッピングのキーと値をキーワード引数へ展開する。

また、同じ規則で複数値を作る場合はリスト内包表記、
入力値だけが異なり期待結果が同じテストは `pytest.mark.parametrize`、
成否にかかわらず後片付けを行う場合は `try/finally` を使うと確認した。

#### 次につながること

Phase 11 / Feature 15で、読書中の本を一定期間更新していないユーザーへの
読書リマインド要件を整理する。

### Phase 11 / Feature 15：読書リマインド要件

#### 確定事項

- ログイン中のユーザーが、自分の読書中のUserBookへ明示的に設定する
- 設定日の7日後の20時に、登録メールアドレスへ1回だけ送信する
- 送信前に読書中以外へ変わった場合は、メールを送信せず終了する
- 手動解除とメール内の解除リンクは実装しない
- 送信に失敗しても再試行せず、失敗状態で終了する
- 終了後も読書中の場合は再設定でき、既存のReadingReminderを再利用する
- メール送信にはResendを使用する
- 配信結果を受信するWebhookは実装しない
- 送信対象は5分ごとに実行するコマンドで確認する
- 状態は `ACTIVE`、`SEND_ACCEPTED`、`READING_STATUS_CHANGED`、
  `SEND_FAILED` の4種類とする

#### 次に行うこと

`enums.py`へ追加する読書リマインド状態Enumを設計する。

### Phase 11 / Feature 15：読書リマインド実装完了

#### 設計判断

ReadingReminderはUserBookと1対1で紐づけ、設定日時、
次回送信予定時刻、処理状態を保存する。
送信時はReadingReminder、UserBook、User、Bookを1回の問い合わせで結合し、
リマインダー、読書状態、宛先、書籍名をまとめて取得する。

Resendへの重複送信を防ぐため、ReadingReminder IDと
`next_send_at` を組み合わせた冪等性キーを使用する。
Resendが送信要求を受け付けた場合は `SEND_ACCEPTED`、
送信処理で例外が発生した場合は `SEND_FAILED`、
読書中以外に変わっていた場合は `READING_STATUS_CHANGED` とする。

定期処理はFastAPIのHTTPリクエスト内で実行せず、
`commands/send_reading_reminders.py` を1回実行するごとに
現在の送信対象を処理する。ローカルで定期起動は設定せず、
本番配置時に外部スケジューラーから5分ごとに呼び出す。

#### 実施内容

`ReadingReminderStatus`、`ReadingReminder`、Migration `c9107ce826ea`、
設定・状態取得API、送信対象取得Service、Resendメール送信Service、
1件ごとと複数件の処理Service、定期実行用コマンドを追加した。

GitHub ActionsにはResendの実キーを渡さず、
Settings読み込み用のダミー値を設定した。

#### 動作確認

送信対象の抽出、対象外の除外、読書状態変更時の終了、
Resend受付・失敗時の状態更新、冪等性キー、複数件処理、
コマンドの時刻とDBセッションの受け渡しをテストした。
既存機能を含む全235件が成功した。

開発用DBで送信対象を1件に限定し、コマンドを1回実行した。
実メールの受信、状態の `SEND_ACCEPTED` への更新、
次回の送信対象が0件になることを確認した。

#### 次に行うこと

Feature 15の変更差分をレビューし、Gitへの記録準備を行う。

### Phase 11 / Feature 16：AI転用提案の生成・保存POSTとローカル検証

#### 設計判断

本人のInsightに対し、気づきの整理・深掘り・活用方法・次の行動を生成して保存する。
Insightと0対1で紐づけ、再生成時は既存提案を上書きする。
OpenAI公式Python SDKとgpt-6-lunaを採用し、Pydanticの4項目へ構造化して受け取る。
実生成の比較後、推論と生成量の明示指定は省略する方針を選択した。

#### 実施内容

AISuggestion Model、Migration 07fb83edbd05、Schema、Service、
POST /users/me/books/{book_id}/insights/{insight_id}/ai_suggestionを追加した。
新規作成は201、再生成は200とし、本人の気づきが見つからなければ404を返す。
生成失敗・保存失敗は500とし、保存時のIntegrityErrorではrollbackする。
CIにはSettings読み込み用のダミーAPIキーとモデル名を設定した。

#### 動作確認

新規・更新のレスポンスとDB保存、認証・所有者確認、IDの入力制約、
生成・保存失敗、rollback、SDK応答の処理を検証した。
AI提案の15ケースを含む全250テストが成功した。
実生成で4項目を受け取り、CI環境変数だけでSettingsを読み込めることも確認した。
GitHub Actions上の実行は未確認。

#### 次に行うこと

当初予定していた取得GET・提案単体削除DELETEを実装する。
2026-10-07に受講者の指摘で未実装を再確認し、Feature全体の完了判断を訂正した。

### Phase 11 / Feature 16：取得・削除を含むローカル実装完了（2026-10-07）

#### 実施内容・設計判断

AI提案のGET・DELETEを追加し、生成・保存・取得・単体削除を揃えた。
取得は200、削除は本文なし204、対象なしは404とした。
提案・気づき・本棚をJOINし、気づきID・本ID・本人IDで取得対象を絞る。
削除は取得Serviceを再利用し、所有者確認を共有する。
認証と認可、外部キーとUNIQUE制約の役割を振り返った。

#### 動作確認

GET・DELETEの正常系、未登録・未認証・不正ID・他人の提案・本ID不一致を検証した。
削除拒否時に提案が残り、再生成失敗時にも既存提案が保持されることを確認した。
AI提案の34ケースを含む全269テストが成功した。
次はGitへの記録準備。GitHub Actions上の実行は未確認。

PR #18をmainへマージ（fefd1f9）。ローカルmainとorigin/mainの同期を確認した。
受講者からブランチの片付け完了の報告を受けた。次の候補はPhase 12 / Step 12-1。

### デバッグ基礎実習（2026-10-08）

一時ファイルでPython標準のpdbを使い、変数確認・ステップ実行・ブレークポイントを学習した。
期待値との違いから原因を調べ、修正後の再実行で解決を確認した。練習ファイルは削除し、Gitへは追加していない。

### Phase 11 / フォロー中・フォロワー一覧の追加（2026-10-08）

本人限定のGET /users/me/following・GET /users/me/followersを追加した。
既存のFollowとUserをJOINし、相手のid・usernameをリストで返す。0件は200と[]、未認証は401とした。
短い取得処理は既存構成に合わせてRouterへ配置し、両APIでSchemaを共有した。
JOINはUserとFollowの関係を結び、WHEREで本人の関係に絞る役割を振り返った。
各APIの2人取得・0件・未認証・他人の関係除外を検証し、全277テストが成功した。
次はGitへの記録準備。その後、Phase 12の主要ユーザーフロー確認へ進む。

PR #19をmainへマージ（e98af42）。ローカルmainとorigin/mainの同期、ローカル作業ブランチの削除を確認した。

### Phase 12 / 書籍検索・登録の改善（2026-10-08）

Google Booksの取得上限を40件に変更し、ISBN-13なしの本も検索・登録できるようにした。
Bookにnullable・一意制約付きのexternal_idを追加し、既存本はexternal_idを優先して検索、必要に応じてISBNで照合する。既存本の不足情報を補完する。
開発用・テスト用DBのマイグレーション適用と、全285テストの成功を確認した。PR #20をmainへマージ（993cc4d）。次は検索から登録・本人の一覧取得までの実操作確認。

### Phase 12 / Step 12-1：主要ユーザーフローの確認（2026-10-09）

Swagger UIで『嫌われる勇気』の検索・読みたい登録・読書中への変更・気づき記録・完読と評価・公開の読了投稿・タイムライン表示を、保存後の取得まで確認した。
別ユーザーの新規登録・ログイン後にも同じ公開投稿を確認し、検索から他ユーザーによる発見までの流れが成立した。次はStep 12-2のDBリレーション見直し。


### Phase 12 / 本一覧の切り替えと気づきの独立保存（2026-10-09）

list_typeで読みたい一覧（未読・読書中）と完読一覧を切り替えられるようにした。
気づきをUser・Bookへ直接紐づけ、本の登録削除後も気づき・AI提案を保持する。気づきに本ID・タイトルを返し、気づきの明示的な削除ではAI提案も削除する。
既存データを引き継ぐマイグレーションを両DBへ適用し、実操作と全295テストの成功を確認した。PR #21をmainへマージ（3833bb2）。

### Phase 12 / 読了投稿と評価の独立保存（2026-10-11）

評価をBookRatingへ分離し、読了投稿もUser・Bookへ直接紐づけ、UserBookの削除後も保持するようにした。
投稿には作成時の評価を保存し、現在の評価を変更しても投稿の評価は変わらない。平均評価・関連本はBookRating、タイムライン・公開本棚は投稿時の評価を参照する。
既存データを引き継ぐマイグレーションを両DBへ適用し、データを失うdowngradeは拒否する。全299テストが成功した。
受講者がSwagger UIでリスト削除後の投稿取得・更新・削除と、再登録時の評価保持を確認した。PR #22をmainへマージ（6ed872f）。ローカルmainとorigin/mainの参照一致・ローカル作業ブランチ削除を確認した。

### Phase 12 / リストから独立した評価更新（2026-10-11）

PATCH /users/me/books/{book_id}/book-ratingを追加し、登録済みの本人の評価をリスト登録・読書状態に関係なく変更できるようにした。未登録は404とし、新規作成は行わない。
BookRating.bookのリレーションからタイトルを取得し、評価ID・本ID・タイトル・更新後の評価を返す。既存のrecommendation-score APIは残した。
正常系・未登録・未認証・不正な本ID・他人の評価・範囲外の9ケースを含む全308テストが成功した。受講者がSwagger UIでもリスト削除後の評価変更を確認した。

PR #23をmainへマージ（0c72a70）。ローカルmainとorigin/mainの参照一致・ローカル作業ブランチ削除を確認した。

### Phase 12 / 完読記録の独立保存（2026-10-12）

CompletedBookで本人・本ごとの完読記録を保存し、リスト削除後もプロフィールの完読冊数を保持する。同じ本を再読しても1冊として数える。
完読済みUserBookと既存BookRatingから重複を除いて引き継ぐマイグレーションを両DBへ適用し、開発用DBの対象3件の保持を確認した。全310テストが成功し、受講者がSwagger UIでも削除後の完読冊数保持を確認した。
