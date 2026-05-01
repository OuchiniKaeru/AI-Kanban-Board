# AIカンバンボードアプリ 仕様書

**バージョン:** 2.1  
**作成日:** 2026年4月30日  
**更新日:** 2026年5月1日  

---

## 改訂履歴

| バージョン | 日付 | 変更内容 |
|-----------|------|---------|
| 1.0 | 2026-04-30 | 初版作成 |
| 2.0 | 2026-05-01 | Agnoフレームワーク導入、プロジェクト機能・MCPサーバー・定期実行機能を追加 |
| 2.1 | 2026-05-01 | タスク単位定期実行・フォルダ/ファイル登録・シェルコマンド実行・実行結果自動追記機能を追加 |

---

## 1. プロジェクト概要

### 1.1 目的
個人ユーザーが直感的にタスク管理を行い、AIエージェントを通じて自然言語でタスクの作成・管理・分析を自動化できるカンバンボードアプリケーションを提供する。

### 1.2 背景
従来のカンバンボードアプリは手動でのタスク管理が中心であり、タスクの整理や進捗確認に時間がかかる。AIエージェントを統合することで、ユーザーはチャット形式で指示を出すだけでタスクの自動作成、期限管理、進捗レポート生成などを行えるようになり、生産性を向上させる。

v2.0では以下を追加実装する：
- **Agnoフレームワーク**による自律的な多段階AIエージェント
- **MCPサーバー**による外部AIエージェント（Claude Desktop、Cursor等）との連携
- **プロジェクト機能**によるカンバンの複数管理・横断検索
- **定期実行機能**によるスケジュールベースのAIコマンド自動実行

v2.1では以下を追加実装する：
- **タスク単位定期実行**による各タスクカードへのスケジュール設定
- **フォルダ・ファイル登録**によるリソースパス管理
- **シェルコマンド実行**（`shell`種別）によるOS操作・スクリプト定期実行
- **実行結果の自動追記**によるタスクdescriptionへの実行履歴蓄積

### 1.3 対象ユーザー
- 個人でのタスク管理を行うユーザー
- シンプルで軽量なツールを好むユーザー
- AIを活用した自動化に興味のあるユーザー

### 1.4 利用環境
- ローカル環境での実行（個人利用向け）
- Webブラウザからアクセス

---

## 2. 機能要件

### 2.1 カンバンボード基本機能

#### 2.1.1 カラム管理
| 項目 | 内容 |
|------|------|
| デフォルトカラム | ToDo（未着手）、Doing（進行中）、Done（完了） |
| カラム追加 | ユーザー定義のカラムを追加可能 |
| カラム編集 | カラム名の変更、順序の変更 |
| カラム削除 | 空のカラムのみ削除可能 |

#### 2.1.2 タスク管理（CRUD）
| 機能 | 詳細 |
|------|------|
| タスク作成 | タイトル、説明、期限日、優先度を設定 |
| タスク閲覧 | カンバンボード上で一覧表示 |
| タスク編集 | タイトル、説明、期限日、優先度の変更 |
| タスク削除 | 個別削除、一括削除 |
| タスク移動 | ドラッグ&ドロップでカラム間移動 |
| タスク検索 | タイトル・説明文での全文検索 |
| タスクフィルタ | 優先度、期限、キーワードでの絞り込み |

#### 2.1.3 タスク属性
| 属性 | 型 | 説明 |
|------|-----|------|
| id | INTEGER | 自動採番（主キー） |
| title | TEXT | タスク名（必須、最大100文字） |
| description | TEXT | 詳細説明（最大1000文字） |
| column_id | INTEGER | 所属カラムID（外部キー） |
| project_id | INTEGER | 所属プロジェクトID（外部キー）※v2.0追加 |
| priority | TEXT | 優先度（low / medium / high） |
| due_date | DATE | 期限日（オプション） |
| created_at | DATETIME | 作成日時 |
| updated_at | DATETIME | 更新日時 |
| order_index | INTEGER | カラム内での表示順 |

### 2.2 プロジェクト機能（v2.0新規）

複数のカンバンボードをプロジェクト単位で管理する。

| 機能 | 詳細 |
|------|------|
| プロジェクト作成 | 名前、説明、カラーを設定。作成時にデフォルトカラム（ToDo/Doing/Done）を自動生成 |
| プロジェクト一覧 | プロジェクト一覧表示・切り替え |
| プロジェクト編集 | 名前・説明・カラーの変更 |
| プロジェクト削除 | プロジェクトと関連カラム・タスクを一括削除 |
| 横断検索 | 全プロジェクトを横断してタスクをキーワード検索 |

### 2.3 AIエージェント機能

#### 2.3.1 タスク自動作成
- **自然言語入力**: 「来週の月曜日にプレゼン資料を作成するタスクを追加して」
- **一括作成**: 「買い物リスト：牛乳、卵、パンをタスクにして」
- **テンプレート作成**: 「毎週月曜日の朝9時に週次報告タスクを作成して」

#### 2.3.2 期限管理
- **期限設定**: 「プレゼン資料の期限を金曜日にして」
- **期限変更**: 「全てのDoingのタスクを3日延長して」
- **期限リマインダー**: 「期限が近いタスクを教えて」
- **期限切れ確認**: 「期限切れのタスクはある？」

#### 2.3.3 進捗レポート生成
- **サマリーレポート**: 「今週の進捗を教えて」
- **カラム別集計**: 「ToDoが何個ある？」「Doneの割合は？」
- **期限別集計**: 「今週期限のタスクを一覧表示して」
- **傾向分析**: 「最近完了したタスクの傾向を分析して」

#### 2.3.4 ステータス確認
- **タスク検索**: 「優先度が高いタスクを探して」
- **カラム確認**: 「Doingに何がある？」
- **統計情報**: 「今月完了したタスク数は？」
- **プロジェクト横断検索** *(v2.0)*: 「全プロジェクトから"報告"というキーワードのタスクを探して」

#### 2.3.5 タスク操作
- **移動**: 「プレゼン資料をDoneに移動して」
- **更新**: 「全ての買い物タスクの優先度を上げて」
- **削除**: 「期限切れのタスクを削除して」

### 2.4 チャットUI機能

#### 2.4.1 基本機能
| 機能 | 詳細 |
|------|------|
| メッセージ入力 | テキストエリアでの自由入力 |
| メッセージ送信 | Enterキーまたは送信ボタン |
| 履歴表示 | 過去の会話を時系列で表示 |
| 履歴保持 | 直近100件のメッセージを保持 |
| クリア機能 | チャット履歴のクリア |
| セッション管理 *(v2.0)* | `session_id`による会話コンテキスト継続 |

#### 2.4.2 AI応答表示
- **テキスト応答**: 自然言語での回答
- **タスクカード表示**: 作成・更新されたタスクのプレビュー
- **レポート表示**: 表形式やグラフでの集計結果
- **確認プロンプト**: 削除などの重要操作前に確認

#### 2.4.3 コマンド機能
| コマンド | 説明 | 例 |
|----------|------|-----|
| `/help` | 利用可能なコマンド一覧 | `/help` |
| `/create` | タスク作成（明示的） | `/create タイトル` |
| `/report` | レポート生成 | `/report weekly` |
| `/search` | タスク検索 | `/search キーワード` |
| `/clear` | チャット履歴クリア | `/clear` |

### 2.5 定期実行機能（v2.0新規）

タスクや通知を時間・日・週・月単位でスケジュール実行できる。

| 機能 | 詳細 |
|------|------|
| スケジュール作成 | 名前、コマンド（自然言語）、実行間隔（interval/cron）を設定 |
| スケジュール一覧 | 有効・無効状態と最終実行結果を表示 |
| スケジュール有効/無効 | 個別にON/OFFを切り替え |
| 手動実行 | APIまたはUIから即時実行 |
| 実行履歴 | 最終実行日時・ステータス・結果を記録 |

実行例：
- 「毎日9時に期限切れタスクを確認して通知」
- 「毎週月曜日に週次レポートを生成して」
- 「毎時間ToDoのタスク数を確認して」

### 2.6 タスク単位定期実行機能（v2.1新規）

v2.0の定期実行機能を拡張し、**タスク単位**でスケジュールを設定できるようにする。フォルダ・ファイルを登録してシェルコマンドを実行し、実行結果をタスクの説明欄に自動追記できる。

| 機能 | 詳細 |
|------|------|
| タスク単位スケジュール設定 | 各タスクカードの「⏰ 定期実行」ボタンからUIで設定・管理 |
| 実行種別 | `agent`（AIコマンド）または `shell`（シェルコマンド） |
| フォルダ・ファイル登録 | スケジュールに監視・操作対象パスを最大10件登録 |
| プレースホルダ展開 | コマンド内の `{resource_1}` 等を登録パスに自動展開 |
| 実行結果の自動追記 | タスクの `description` 末尾に実行日時・ステータス・結果を追記（最新50件保持） |
| 実行履歴テーブル | `task_schedule_logs` に全実行履歴を保存 |

設定例：
- 「`/var/log/app.log` を毎時監視してERROR件数をタスクに記録」
- 「特定フォルダ内のファイルを毎日処理して進捗をタスクに残す」

---

## 3. 非機能要件

### 3.1 パフォーマンス
| 項目 | 目標値 |
|------|--------|
| 初期表示時間 | 2秒以内 |
| タスク操作応答 | 500ms以内 |
| AI応答時間 | 3秒以内（目標） |
| 同時接続 | 単一ユーザー（ローカル利用） |

### 3.2 可用性
- ローカル環境での実行を前提
- オフライン動作可能（AI機能除く）
- データの自動保存（SQLiteへの即時書き込み）

### 3.3 セキュリティ
| 項目 | 対応 |
|------|------|
| APIキー管理 | 環境変数または設定ファイルで管理 |
| データ保護 | ローカルファイルのみ、外部送信なし（AI API除く） |
| 入力検証 | SQLインジェクション、XSS対策 |

### 3.4 拡張性
- プラグイン形式でのAIプロバイダー追加（OpenAI、Claude、Ollama等）
- カラム数・タスク数の制限緩和
- MCPプロトコルによる外部AIエージェントとの連携

---

## 4. 技術スタック

### 4.1 全体構成

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           外部AIエージェント                             │
│  (Claude Desktop, Cursor, 独自Agno Agent など)                          │
└─────────────────────────────┬───────────────────────────────────────────┘
                              │ MCP (Streamable HTTP / SSE)
┌─────────────────────────────▼───────────────────────────────────────────┐
│                         FastAPI アプリケーション                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────┐  │
│  │   REST API      │  │  MCP Server     │  │   Scheduler (APScheduler)│  │
│  │  /api/*         │  │  /mcp           │  │   定期実行エンジン       │  │
│  └────────┬────────┘  └────────┬────────┘  └───────────┬─────────────┘  │
│           │                    │                       │                │
│  ┌────────▼────────────────────▼───────────────────────▼─────────────┐  │
│  │                     共通サービス層                                │  │
│  │  TaskService / ColumnService / ProjectService / ScheduleService   │  │
│  └────────┬─────────────────────────────────────────────────────────┘  │
│           │                                                            │
│  ┌────────▼─────────────────────────────────────────────────────────┐  │
│  │                     SQLite (Async)                                │  │
│  │  projects / columns / tasks / schedules / chat_messages           │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │              内部AIエージェント (Agno Agent)                     │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │   │
│  │  │  @tool      │  │  MCP Tools  │  │  Schedule Receiver API  │  │   │
│  │  │  (直接呼出)  │  │  (MCP経由)  │  │  /api/agent/schedule    │  │   │
│  │  └─────────────┘  └─────────────┘  └─────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
         │ HTTP / WebSocket
┌────────▼────────┐
│   Web Browser   │
│  (htmx + HTML)  │
└─────────────────┘
```

### 4.2 フロントエンド
| 技術 | 用途 | 理由 |
|------|------|------|
| htmx | 動的UI更新 | シンプルな記述で部分的なDOM更新が可能 |
| HTML5 | マークアップ | 標準技術、htmxとの親和性 |
| CSS3 | スタイリング | カスタムデザイン、レスポンシブ対応 |
| Vanilla JS | 補助的な制御 | 最小限のJavaScriptでhtmxを補完 |

### 4.3 バックエンド
| 技術 | 用途 | 理由 |
|------|------|------|
| Python 3.11+ | 言語 | 豊富なライブラリ、AI連携のエコシステム |
| FastAPI | Webフレームワーク | 高速、非同期対応、自動APIドキュメント生成 |
| Uvicorn | ASGIサーバー | FastAPIの標準サーバー |
| SQLAlchemy | ORM | データベース抽象化、型安全 |
| Alembic | マイグレーション | スキーマ管理 |
| Pydantic | バリデーション | 型安全なデータモデル |
| python-multipart | フォーム解析 | htmxからのフォーム送信対応 |
| Jinja2 | テンプレートエンジン | サーバーサイドレンダリング |

### 4.4 データベース
| 技術 | 用途 | 理由 |
|------|------|------|
| SQLite | ローカルDB | セットアップ不要、ファイルベース、軽量 |

### 4.5 AI連携
| 技術 | 用途 | 理由 |
|------|------|------|
| **Agno** *(v2.0)* | AIエージェントフレームワーク | 自律的なツール選択・多段階実行・セッション永続化 |
| OpenAI API | GPTモデル連携 | 高い理解力、日本語対応 |
| Anthropic API | Claudeモデル連携 | 長文コンテキスト、安全性 |
| Ollama | ローカルLLM | オフライン利用、プライバシー保護 |
| **MCP** *(v2.0)* | 外部エージェント連携プロトコル | Claude Desktop/Cursor等との標準連携 |

### 4.6 リアルタイム通信
| 技術 | 用途 | 理由 |
|------|------|------|
| WebSocket | チャットのリアルタイム更新 | FastAPIネイティブ対応、双方向通信 |
| Server-Sent Events | AI応答ストリーミング・MCPエンドポイント | 逐次応答表示・外部エージェント接続 |

### 4.7 定期実行（v2.0新規）
| 技術 | 用途 | 理由 |
|------|------|------|
| APScheduler | スケジューラー | interval/cron両対応、asyncio統合 |

---

## 5. データモデル設計

### 5.1 ER図

```
┌──────────────┐       ┌──────────────┐       ┌──────────────┐
│   projects   │       │   columns    │       │    tasks     │
├──────────────┤       ├──────────────┤       ├──────────────┤
│ id (PK)      │──┐    │ id (PK)      │──┐    │ id (PK)      │
│ name         │  │    │ name         │  │    │ title        │
│ description  │  └───>│ project_id   │  └───>│ column_id    │
│ color        │       │ order_index  │       │ project_id ──┼──┐
│ created_at   │       │ created_at   │       │ description  │  │
│ updated_at   │       └──────────────┘       │ priority     │  │
└──────┬───────┘                              │ due_date     │  │
       │                                      │ order_index  │  │
       │ ┌────────────────────────────────────┘ created_at   │  │
       │ │                                      updated_at   │  │
       │ │                                      └──────────────┘  │
       │ │                                                         │
       └─┼─────────────────────────────────────────────────────────┘
         │
┌────────▼─────┐       ┌─────────────┐
│  schedules   │       │chat_messages│
├──────────────┤       ├─────────────┤
│ id (PK)      │       │ id (PK)     │
│ name         │       │ role        │
│ project_id   │       │ content     │
│ task_id(FK)──┼──┐    │ created_at  │
│ command      │  │    └─────────────┘
│ command_type │  │
│ schedule_type│  │   ┌──────────────────────┐
│ interval_mins│  │   │  schedule_resources   │
│ cron_expr    │  │   ├──────────────────────┤
│ is_enabled   │◄─┼──>│ id (PK)               │
│ append_to_   │  │   │ schedule_id (FK)      │
│  task_desc   │  │   │ resource_type         │
│ last_run_at  │  │   │ path                  │
│ last_run_stat│  │   │ created_at            │
│ last_run_res │  │   └──────────────────────┘
│ created_at   │  │
│ updated_at   │  │   ┌──────────────────────┐
└──────────────┘  │   │  task_schedule_logs   │
                  │   ├──────────────────────┤
                  └──>│ id (PK)               │
                      │ schedule_id (FK)      │
                      │ executed_at           │
                      │ status                │
                      │ result                │
                      │ execution_time_sec    │
                      │ created_at            │
                      └──────────────────────┘
```

### 5.2 テーブル定義

#### projects（プロジェクトテーブル）※v2.0新規
| カラム名 | 型 | 制約 | 説明 |
|----------|-----|------|------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | プロジェクトID |
| name | VARCHAR(100) | NOT NULL | プロジェクト名 |
| description | TEXT | | 説明 |
| color | VARCHAR(7) | DEFAULT '#3B82F6' | 表示カラー（HEX） |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 作成日時 |
| updated_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 更新日時 |

#### columns（カラムテーブル）
| カラム名 | 型 | 制約 | 説明 |
|----------|-----|------|------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | カラムID |
| name | VARCHAR(50) | NOT NULL | カラム名 |
| order_index | INTEGER | NOT NULL, DEFAULT 0 | 表示順 |
| project_id | INTEGER | FOREIGN KEY (projects.id) NOT NULL | 所属プロジェクト *(v2.0追加)* |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 作成日時 |

#### tasks（タスクテーブル）
| カラム名 | 型 | 制約 | 説明 |
|----------|-----|------|------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | タスクID |
| title | VARCHAR(100) | NOT NULL | タスク名 |
| description | TEXT | | 詳細説明 |
| column_id | INTEGER | FOREIGN KEY (columns.id) ON DELETE SET NULL | 所属カラム |
| project_id | INTEGER | FOREIGN KEY (projects.id) NOT NULL | 所属プロジェクト *(v2.0追加)* |
| priority | VARCHAR(10) | DEFAULT 'medium' | 優先度 |
| due_date | DATE | | 期限日 |
| order_index | INTEGER | NOT NULL, DEFAULT 0 | カラム内順序 |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 作成日時 |
| updated_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 更新日時 |

#### schedules（スケジュールテーブル）※v2.0新規
| カラム名 | 型 | 制約 | 説明 |
|----------|-----|------|------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | スケジュールID |
| name | VARCHAR(100) | NOT NULL | スケジュール名 |
| description | TEXT | | 説明 |
| project_id | INTEGER | FOREIGN KEY (projects.id) NULLABLE | 対象プロジェクト（NULLは全体） |
| **task_id** | INTEGER | FOREIGN KEY (tasks.id) ON DELETE CASCADE, NULLABLE | 紐づくタスクID。NULLの場合はプロジェクト単位スケジュール *(v2.1追加)* |
| command | TEXT | NOT NULL | 実行コマンド（自然言語またはシェル） |
| **command_type** | VARCHAR(20) | NOT NULL, DEFAULT 'agent' | 実行種別: `'agent'`（AIコマンド）/ `'shell'`（シェルコマンド） *(v2.1追加)* |
| schedule_type | VARCHAR(20) | NOT NULL | "interval" または "cron" |
| interval_minutes | INTEGER | | interval時の実行間隔（分） |
| cron_expression | VARCHAR(100) | | cron時の式（例: "0 9 * * 1"） |
| is_enabled | BOOLEAN | NOT NULL, DEFAULT TRUE | 有効/無効 |
| **append_to_task_description** | BOOLEAN | NOT NULL, DEFAULT TRUE | 実行結果をタスクdescriptionに追記するか *(v2.1追加)* |
| last_run_at | DATETIME | | 最終実行日時 |
| last_run_status | VARCHAR(20) | | "success" / "error" |
| last_run_result | TEXT | | 最終実行結果 |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 作成日時 |
| updated_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 更新日時 |

#### schedule_resources（スケジュールリソーステーブル）※v2.1新規
| カラム名 | 型 | 制約 | 説明 |
|----------|-----|------|------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | ID |
| schedule_id | INTEGER | FOREIGN KEY (schedules.id) ON DELETE CASCADE, NOT NULL | 所属スケジュール |
| resource_type | VARCHAR(20) | NOT NULL | `'folder'` または `'file'` |
| path | TEXT | NOT NULL | フォルダまたはファイルのパス |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 作成日時 |

#### task_schedule_logs（タスクスケジュール実行ログテーブル）※v2.1新規
| カラム名 | 型 | 制約 | 説明 |
|----------|-----|------|------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | ID |
| schedule_id | INTEGER | FOREIGN KEY (schedules.id) ON DELETE CASCADE, NOT NULL | 所属スケジュール |
| executed_at | DATETIME | NOT NULL | 実行日時 |
| status | VARCHAR(20) | NOT NULL | `'success'` / `'error'` / `'timeout'` |
| result | TEXT | | 実行結果（stdout/stderrまたはAI応答） |
| execution_time_sec | REAL | | 実行時間（秒） |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 記録日時 |

#### chat_messages（チャットメッセージテーブル）
| カラム名 | 型 | 制約 | 説明 |
|----------|-----|------|------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | メッセージID |
| role | VARCHAR(10) | NOT NULL | user / assistant |
| content | TEXT | NOT NULL | メッセージ内容 |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 作成日時 |

#### settings（設定テーブル）
| カラム名 | 型 | 制約 | 説明 |
|----------|-----|------|------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | 設定ID |
| key | VARCHAR(50) | NOT NULL, UNIQUE | 設定キー |
| value | TEXT | | 設定値 |

---

## 6. API設計

### 6.1 RESTful API

#### プロジェクト管理（v2.0新規）
| メソッド | エンドポイント | 説明 |
|----------|---------------|------|
| GET | `/api/projects` | プロジェクト一覧取得 |
| POST | `/api/projects` | プロジェクト作成 |
| GET | `/api/projects/{id}` | プロジェクト詳細取得 |
| PUT | `/api/projects/{id}` | プロジェクト更新 |
| DELETE | `/api/projects/{id}` | プロジェクト削除 |
| GET | `/api/projects/search?query=` | 全プロジェクト横断検索 |

#### カラム管理
| メソッド | エンドポイント | 説明 |
|----------|---------------|------|
| GET | `/api/columns` | カラム一覧取得 |
| POST | `/api/columns` | カラム作成 |
| PUT | `/api/columns/{id}` | カラム更新 |
| DELETE | `/api/columns/{id}` | カラム削除 |

#### タスク管理
| メソッド | エンドポイント | 説明 |
|----------|---------------|------|
| GET | `/api/tasks` | タスク一覧取得（クエリパラメータでフィルタ） |
| POST | `/api/tasks` | タスク作成 |
| GET | `/api/tasks/{id}` | タスク詳細取得 |
| PUT | `/api/tasks/{id}` | タスク更新 |
| DELETE | `/api/tasks/{id}` | タスク削除 |
| PUT | `/api/tasks/{id}/move` | タスク移動（カラム変更） |

#### チャット管理
| メソッド | エンドポイント | 説明 |
|----------|---------------|------|
| GET | `/api/chat/history` | チャット履歴取得 |
| DELETE | `/api/chat/history` | チャット履歴削除 |

#### レポート
| メソッド | エンドポイント | 説明 |
|----------|---------------|------|
| GET | `/api/reports/summary` | サマリーレポート取得 |
| GET | `/api/reports/weekly` | 週次レポート取得 |

#### スケジュール管理（v2.0新規 / v2.1拡張）
| メソッド | エンドポイント | 説明 |
|----------|---------------|------|
| GET | `/api/schedules` | スケジュール一覧取得（`task_id` でフィルタ可能） |
| POST | `/api/schedules` | スケジュール作成（`task_id`, `command_type` 対応） |
| GET | `/api/schedules/{id}` | スケジュール詳細取得（リソース一覧含む） |
| PUT | `/api/schedules/{id}` | スケジュール更新 |
| DELETE | `/api/schedules/{id}` | スケジュール削除 |
| POST | `/api/schedules/{id}/run` | 手動実行 |

#### スケジュールリソース管理（v2.1新規）
| メソッド | エンドポイント | 説明 |
|----------|---------------|------|
| GET | `/api/schedules/{id}/resources` | リソース一覧取得 |
| POST | `/api/schedules/{id}/resources` | リソース追加 |
| DELETE | `/api/schedules/{id}/resources/{resource_id}` | リソース削除 |

#### スケジュール実行履歴（v2.1新規）
| メソッド | エンドポイント | 説明 |
|----------|---------------|------|
| GET | `/api/schedules/{id}/logs` | 実行履歴一覧（最新50件） |
| DELETE | `/api/schedules/{id}/logs` | 実行履歴一括削除 |

#### タスク・スケジュール連携（v2.1新規）
| メソッド | エンドポイント | 説明 |
|----------|---------------|------|
| GET | `/api/tasks/{id}/schedules` | タスクに紐づくスケジュール一覧 |

#### AIエージェント
| メソッド | エンドポイント | 説明 |
|----------|---------------|------|
| POST | `/api/agent/process` | 自然言語処理（同期） |
| POST | `/api/agent/stream` | 自然言語処理（ストリーミング） |
| POST | `/api/agent/schedule` | 定期実行コマンドの受付・実行 *(v2.0新規)* |
| POST | `/api/agent/schedule/{id}/run` | スケジュールの手動実行 *(v2.0新規)* |

### 6.2 WebSocket API

#### チャットエンドポイント
| エンドポイント | 説明 |
|---------------|------|
| `/ws/chat` | AIチャットのリアルタイム通信 |

**メッセージ形式:**
```json
// クライアント → サーバー
{
  "type": "message",
  "content": "来週のタスクを作成して"
}

// サーバー → クライアント（ストリーミング）
{
  "type": "chunk",
  "content": "承知しました。"
}

// サーバー → クライアント（完了）
{
  "type": "complete",
  "content": "タスクを3件作成しました。",
  "actions": [
    {"type": "create_task", "data": {...}}
  ]
}
```

### 6.3 MCPサーバー（v2.0新規）

外部AIエージェントがMCPプロトコル経由でカンバンボードのツールを利用できる。

| エンドポイント | 説明 |
|---------------|------|
| `GET /mcp/sse` | MCP SSEエンドポイント（外部エージェント接続） |
| `POST /mcp/messages` | MCPメッセージ受信 |

**接続例（Claude Desktop / Cursor設定）:**
```
MCP Server URL: http://localhost:8000/mcp/sse
```

**MCPで提供するツール一覧:**
| ツール名 | 説明 |
|----------|------|
| `search_tasks` | タスク検索（プロジェクト・カラム・優先度・キーワードでフィルタ） |
| `get_task` | タスク詳細取得 |
| `create_task` | タスク作成 |
| `update_task` | タスク更新 |
| `delete_task` | タスク削除 |
| `move_task` | タスクのカラム移動 |
| `get_projects` | プロジェクト一覧取得 |
| `get_columns` | カラム一覧取得 |
| `generate_report` | レポート生成（summary / weekly） |
| `get_overdue_tasks` | 期限切れタスク取得 |
| `create_schedule` | スケジュール作成 |
| `list_schedules` | スケジュール一覧取得 |

### 6.4 AIエージェントAPIリクエスト/レスポンス形式

**リクエスト形式:**
```json
{
  "message": "来週の月曜日にプレゼン資料を作成するタスクを追加して",
  "session_id": "user-session-001",
  "context": {
    "current_view": "board",
    "selected_column": 1
  }
}
```

**レスポンス形式:**
```json
{
  "success": true,
  "message": "タスクを作成しました。",
  "session_id": "user-session-001",
  "actions": null,
  "requires_confirmation": false
}
```

---

## 7. UI/UX設計

### 7.1 画面構成

```
┌─────────────────────────────────────────────────────────────┐
│  Header: AIカンバンボード                    [設定] [ヘルプ] │
├──────────────────────────────┬──────────────────────────────┤
│                              │                              │
│    カンバンボードエリア       │      チャットパネル          │
│  [プロジェクト選択]          │                              │
│  ┌────────┐ ┌────────┐     │  ┌────────────────────────┐  │
│  │  ToDo  │ │ Doing  │ ... │  │ AI: こんにちは！何を    │  │
│  │        │ │        │     │  │     お手伝いできますか？ │  │
│  │ [タスク│ │ [タスク│     │  ├────────────────────────┤  │
│  │  カード│ │  カード│     │  │ User: 来週のタスクを    │  │
│  │  ...]  │ │  ...]  │     │  │       作成して          │  │
│  │        │ │        │     │  ├────────────────────────┤  │
│  │ [+追加]│ │        │     │  │ AI: 承知しました。3件   │  │
│  └────────┘ └────────┘     │  │     のタスクを作成しま  │  │
│                              │  │     した。              │  │
│                              │  │     [プレビュー表示]    │  │
│                              │  ├────────────────────────┤  │
│                              │  │ [メッセージを入力...]   │  │
│                              │  └────────────────────────┘  │
│                              │                              │
└──────────────────────────────┴──────────────────────────────┘
```

### 7.2 レイアウト
| 要素 | 幅 | 説明 |
|------|-----|------|
| カンバンボードエリア | 70% | 水平スクロール可能なカラム表示 |
| チャットパネル | 30% | 固定幅、垂直スクロール |
| 最小画面幅 | 1024px | レスポンシブ対応（モバイル時はタブ切替） |

### 7.3 インタラクション設計

#### カンバンボード
| アクション | 動作 |
|-----------|------|
| ドラッグ&ドロップ | タスクを別カラムに移動（htmx + SortableJS） |
| ダブルクリック | タスク編集モーダル表示（「基本情報」「定期実行」タブ） |
| 右クリック | コンテキストメニュー（編集/削除/複製） |
| ホバー | タスク詳細のツールチップ表示 |
| ⏰アイコンクリック *(v2.1)* | 定期実行設定モーダルを開く（スケジュール紐づき時に表示） |

#### チャットパネル
| アクション | 動作 |
|-----------|------|
| Enter | メッセージ送信 |
| Shift+Enter | 改行 |
| 上キー | 直前のメッセージを編集 |
| /コマンド | スラッシュコマンドのサジェスト表示 |

### 7.4 カラーパレット
| 用途 | カラー |
|------|--------|
| プライマリ | #3B82F6（青） |
| セカンダリ | #10B981（緑） |
| アクセント | #F59E0B（黄） |
| 警告 | #EF4444（赤） |
| 背景 | #F3F4F6（灰） |
| カード背景 | #FFFFFF（白） |

---

## 8. AIエージェント設計

### 8.1 アーキテクチャ

v2.0ではAgnoフレームワークを採用し、AIが自律的にツールを選択・実行する多段階エージェントを実現する。

```
ユーザーメッセージ
    ↓
[Agno Agent: 意図解析]
    ↓
[ツール自動選択・実行]
    ↓ (多段階実行: ツール結果を受けてさらに別ツールを呼ぶことも可能)
┌────────────────┬─────────────────┬───────────────┐
│  タスク操作    │  レポート生成   │  プロジェクト │
│  @tool群       │  @tool群        │  @tool群      │
└────────────────┴─────────────────┴───────────────┘
    ↓
[レスポンス生成（自然言語）]
    ↓
[セッション永続化 (SqliteDb)]
    ↓
[結果返却]
```

### 8.2 Agnoエージェント設定

| 設定項目 | 値 | 説明 |
|----------|-----|------|
| `add_history_to_context` | `True` | 過去の会話を文脈に含める |
| `num_history_runs` | `5` | 参照する過去会話数 |
| `add_datetime_to_context` | `True` | 現在日時を自動付与 |
| `tool_call_limit` | `20` | 1リクエストあたりの最大ツール呼び出し回数 |
| `markdown` | `True` | Markdown形式で応答 |
| `db` | `SqliteDb` | セッション永続化先DB |

### 8.3 AIエージェントツール一覧

| ツール名 | 説明 | 用途例 |
|----------|------|--------|
| `search_tasks` | タスク検索 | 「ToDoにあるタスクを教えて」 |
| `get_task_by_id` | タスク詳細取得 | 「ID:3のタスクを詳しく」 |
| `create_task` | タスク作成 | 「新しいタスクを追加して」 |
| `update_task` | タスク更新 | 「タスクの期限を変更して」 |
| `delete_task` | タスク削除 | 「タスクを削除して」 |
| `move_task` | タスク移動 | 「タスクをDoneに移動して」 |
| `get_columns` | カラム一覧取得 | 「カラムを教えて」 |
| `get_projects` *(v2.0)* | プロジェクト一覧取得 | 「プロジェクトを教えて」 |
| `search_across_projects` *(v2.0)* | 全プロジェクト横断検索 | 「全体で"報告"を検索して」 |
| `generate_summary_report` | サマリーレポート | 「進捗を教えて」 |
| `generate_weekly_report` | 週次レポート | 「今週のレポートを出して」 |
| `get_overdue_tasks` | 期限切れタスク取得 | 「期限切れのタスクはある？」 |

### 8.4 動作フロー例

#### 「ToDoにあるタスクを教えて」
```
ユーザー: "ToDoにあるタスクを教えて"
    ↓ FastAPI: /api/agent/process 受信
    ↓ KanbanAgnoAgent.process_message()
    ↓ Agno Agent: 意図解析 → "タスク検索が必要"
    ↓ search_tasks(column_name="ToDo") 実行
    ↓ DBからToDoカラムのタスクを取得
    ↓ AI: 結果を自然言語で回答生成
"ToDoカラムには以下のタスクがあります：
  - ID 1: プレゼン資料作成 (優先度: high, 期限: 2026-05-05)
  - ID 2: 買い物リスト作成 (優先度: medium, 期限: なし)"
    ↓ チャット履歴に保存 → ユーザーに返信
```

#### 「今週の進捗を教えて」
```
ユーザー: "今週の進捗を教えて"
    ↓ AI判断: "レポート生成が必要 → generate_weekly_report 呼び出し"
    ↓ generate_weekly_report() 実行
    ↓ AI: 結果を回答生成
"今週のレポートです：
  対象期間: 2026-04-27 〜 2026-05-03
  今週作成されたタスク: 5件
  今週完了したタスク: 3件"
```

#### 定期実行「毎日9時に期限切れタスクを確認して通知」
```
APScheduler: 毎日9:00 → POST /api/agent/schedule
    ↓ Agno Agent: get_overdue_tasks() 実行
    ↓ 結果をチャット履歴に保存・通知
    ↓ ScheduleService.update_last_run() で実行記録
```

### 8.5 システムプロンプト（エージェント指示）
```
あなたはカンバンボード管理のAIアシスタントです。
ユーザーの自然言語の指示を解析し、適切なツールを使用してタスク管理を支援してください。
タスクの検索、作成、更新、削除、移動、レポート生成ができます。
プロジェクト単位で管理されており、横断検索も可能です。
カラム名は 'ToDo', 'Doing', 'Done' などがあります。
回答は日本語で、親切で分かりやすく説明してください。
タスク一覧を表示する際は、ID、タイトル、優先度、期限を含めてください。
操作が成功した場合は確認メッセージを、失敗した場合はエラー内容を伝えてください。
定期実行の場合は、実行結果を簡潔にまとめてください。
```

### 8.6 エラーハンドリング
| エラー種別 | 動作 |
|-----------|------|
| 意図不明 | 「もう少し詳しく教えてください」と尋ねる |
| パラメータ不足 | 不足情報をユーザーに確認 |
| APIエラー | エラーメッセージを表示し、再試行を提案 |
| 制限超過 | 利用制限への対応を案内 |
| スケジュール実行エラー | `last_run_status: "error"` として記録 |

### 8.7 モデルプロバイダー切り替え

設定（`.env`）によりモデルを切り替え可能。

```
OPENAI_API_KEY=...      → OpenAI (GPT-4等) を使用
ANTHROPIC_API_KEY=...   → Anthropic (Claude等) を使用
USE_AGNO=true           → Agnoエージェントを使用（デフォルト）
```

### 8.8 タスク単位定期実行のバックエンド実装方針（v2.1新規）

#### スケジューラー拡張（`app/scheduler.py`）

`_execute_command` を `command_type` に対応させ、`shell` 種別の場合はリソースパスのプレースホルダ展開と `subprocess` 実行を行う。`agent` 種別の場合は従来通りAgnoエージェントに委譲する。実行完了後、ログ記録と `append_to_task_description` フラグに応じてタスクdescriptionへの追記を行う。

```python
async def _execute_command(self, schedule_id, command, project_id, task_id):
    # command_typeに応じてagentまたはshellを実行
    # 実行後: ScheduleService.add_log() → TaskService.append_schedule_result()
```

#### タスクdescription追記形式

```
---
[定期実行: スケジュール名] YYYY-MM-DD HH:MM:SS
ステータス: ✅ success | ⚠️ error | ⏱️ timeout
実行時間: X.Xs

結果:
（stdout/stderrまたはAI応答テキスト）
---
```

- 追記位置: `description` 末尾
- 最大履歴数: 最新50件（超過時は古いものから削除）
- `updated_at` は更新しない（タスク自体の更新日時を変えない）
- シェルコマンド出力は最大10,000文字（超過時は末尾から切り詰め）
- タイムアウトはデフォルト60秒、超過時は `timeout` ステータスで強制終了

---

## 9. セキュリティ・プライバシー

### 9.1 データ保護
- すべてのデータはローカルのSQLiteに保存
- 外部へのデータ送信はAI API呼び出し時のみ
- タスク内容の機密性に応じて、AI連携のON/OFFを設定可能

### 9.2 APIキー管理
- 環境変数 `.env` ファイルでの管理
- 設定画面での入力・更新
- キーの暗号化保存（オプション）

### 9.3 入力検証
| 検証項目 | 対策 |
|----------|------|
| SQLインジェクション | SQLAlchemy ORM使用、パラメータ化クエリ |
| XSS | テンプレートエンジンの自動エスケープ |
| CSRF | htmxの組み込みトークン対応 |
| ファイルアップロード | 不要（テキストのみ） |

### 9.4 シェルコマンド実行の安全策（v2.1新規）

| 項目 | 対策 |
|------|------|
| コマンドインジェクション | プレースホルダ展開のみ行い、シェルメタ文字エスケープはローカル・単一ユーザー利用前提として利用者の責任範囲とする |
| パストラバーサル | 登録パスを `os.path.abspath()` で正規化し、許可リスト方式を検討 |
| タイムアウト | デフォルト60秒、超過時は `timeout` ステータスで強制終了 |
| 出力制限 | 最大10,000文字、超過時は末尾から切り詰め |
| ファイルアクセス制限 | `.env` の `ALLOWED_PATH_PREFIXES` で許可パスプレフィックスを定義（例: `/home/user/projects,/var/log`）。定義外パスは登録時にバリデーションエラー |
| ローカル実行前提 | 本機能はローカル環境・単一ユーザー利用を前提。マルチユーザー化する場合はDockerなどサンドボックス化が必要 |

---

## 10. 依存パッケージ

```
# AIエージェントフレームワーク
agno>=1.0.0

# MCPプロトコル
mcp>=1.0.0

# スケジューラー
apscheduler>=3.10.0

# モデルプロバイダー
openai>=1.0.0
anthropic>=0.30.0

# Webフレームワーク
fastapi>=0.100.0
uvicorn[standard]>=0.23.0

# DB
sqlalchemy[asyncio]>=2.0.0
aiosqlite>=0.19.0
alembic>=1.12.0

# バリデーション・設定
pydantic>=2.0.0
pydantic-settings>=2.0.0

# テンプレート・フォーム
jinja2>=3.1.0
python-multipart>=0.0.6

# HTTP
httpx>=0.24.0
```

---

## 11. 開発スケジュール

### フェーズ1: MVP（2週間）
| 期間 | タスク |
|------|--------|
| Week 1 | プロジェクト構築、DB設計（projects/columns/tasks）、基本API実装 |
| Week 2 | カンバンボードUI、タスクCRUD、ドラッグ&ドロップ |

**成果物:** 基本的なカンバンボードアプリ（プロジェクト対応）

### フェーズ2: AI統合（2週間）
| 期間 | タスク |
|------|--------|
| Week 3 | チャットUI、WebSocket実装、Agnoエージェント統合 |
| Week 4 | 自然言語処理、タスク自動作成、期限管理、会話継続性 |

**成果物:** Agnoエージェント搭載カンバンボード

### フェーズ3: 高度機能（2週間）
| 期間 | タスク |
|------|--------|
| Week 5 | MCPサーバー実装、外部エージェント連携、定期実行機能（APScheduler） |
| Week 6 | レポート強化、設定画面、ドキュメント整備 |

**成果物:** 完成版アプリケーション（MCP対応・定期実行対応）

---

## 12. ディレクトリ構成

```
kanban_agent/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPIアプリ（MCPエンドポイント含む）
│   ├── config.py            # 設定管理
│   ├── database.py          # DB接続・セッション
│   ├── scheduler.py         # APScheduler定期実行エンジン ※v2.0新規
│   ├── mcp_server.py        # MCPサーバー実装 ※v2.0新規
│   ├── models/              # SQLAlchemyモデル
│   │   ├── __init__.py
│   │   ├── project.py       # ※v2.0新規
│   │   ├── column.py        # project_id追加
│   │   ├── task.py          # project_id追加
│   │   ├── schedule.py      # ※v2.0新規
│   │   ├── chat.py
│   │   └── setting.py
│   ├── routers/             # APIエンドポイント
│   │   ├── __init__.py
│   │   ├── projects.py      # ※v2.0新規
│   │   ├── columns.py
│   │   ├── tasks.py
│   │   ├── chat.py
│   │   ├── agent.py         # schedule受付API追加
│   │   ├── schedules.py     # ※v2.0新規
│   │   └── reports.py
│   ├── services/            # ビジネスロジック
│   │   ├── __init__.py
│   │   ├── project_service.py   # ※v2.0新規
│   │   ├── task_service.py      # ※v2.1: append_schedule_result追加
│   │   ├── column_service.py
│   │   ├── agno_agent.py        # ※v2.0新規（MCP対応版）
│   │   ├── agent_service.py     # 既存（フォールバック用に保持）
│   │   ├── schedule_service.py  # ※v2.0新規（v2.1: リソース管理・ログ記録追加）
│   │   ├── chat_service.py
│   │   └── report_service.py
│   ├── tools/               # Agnoエージェント用ツール ※v2.0新規
│   │   ├── __init__.py
│   │   └── kanban_tools.py  # @toolデコレータ定義
│   ├── templates/           # Jinja2テンプレート
│   │   ├── base.html
│   │   ├── board.html
│   │   ├── components/
│   │   │   ├── task_card.html   # ※v2.1: ⏰アイコン追加
│   │   │   ├── column.html
│   │   │   └── chat_panel.html
│   │   └── modals/
│   │       ├── task_form.html   # ※v2.1: 定期実行タブ追加
│   │       └── schedule_form.html  # ※v2.1新規
│   ├── static/
│   │   ├── css/style.css
│   │   └── js/app.js
│   └── schemas/             # Pydanticスキーマ
│       ├── __init__.py
│       ├── project.py       # ※v2.0新規
│       ├── task.py
│       ├── column.py
│       ├── schedule.py      # ※v2.0新規（v2.1: task_id, command_type, append_to_task_description追加）
│       ├── schedule_resource.py  # ※v2.1新規
│       └── chat.py          # session_id・ScheduleExecuteRequest追加
├── alembic/
│   └── versions/
├── tests/
│   ├── __init__.py
│   ├── test_api.py
│   └── test_agent.py
├── docs/
│   └── specification.md
├── .env.example
├── pyproject.toml           # uv管理（agno, mcp, apscheduler含む）
├── README.md
└── run.py
```

---

## 13. 移行・セットアップ手順

### Step 1: 依存関係のインストール
```bash
uv add agno mcp apscheduler openai anthropic
```

### Step 2: DBマイグレーション
```bash
alembic revision --autogenerate -m "add_projects_and_schedules"
alembic revision --autogenerate -m "add_task_schedules_and_resources"
alembic upgrade head
```

### Step 3: 実装ファイルの追加
1. `app/models/project.py` - プロジェクトモデル
2. `app/models/schedule.py` - スケジュールモデル（v2.1: task_id, command_type, append_to_task_description追加）
3. `app/models/schedule_resource.py` - スケジュールリソースモデル（v2.1新規）
4. `app/models/task_schedule_log.py` - タスクスケジュールログモデル（v2.1新規）
5. `app/models/column.py` - `project_id` 追加
6. `app/models/task.py` - `project_id` 追加
7. `app/services/project_service.py`
8. `app/services/schedule_service.py`（v2.1: リソース管理・ログ記録追加）
9. `app/services/agno_agent.py`
10. `app/services/task_service.py`（v2.1: `append_schedule_result` 追加）
11. `app/tools/kanban_tools.py`
12. `app/mcp_server.py`
13. `app/scheduler.py`（v2.1: `command_type` 対応・シェル実行追加）
14. `app/routers/projects.py`
15. `app/routers/schedules.py`（v2.1: リソース・ログエンドポイント追加）
16. `app/routers/agent.py` - スケジュールAPIを追加

### Step 4: 動作確認
```bash
# アプリ起動
uvicorn app.main:app --reload

# 内部エージェントテスト（チャット）
# "ToDoにあるタスクを教えて"
# "新しいタスクを追加して"
# "今週の進捗を教えて"

# MCP接続テスト（外部から）
# Claude Desktop や Cursor で http://localhost:8000/mcp/sse を設定

# 定期実行テスト
# POST /api/schedules でスケジュール作成
# POST /api/schedules/{id}/run で手動実行
```

---

## 14. ユースケース

### 14.1 内部AIエージェント（Agno）からの利用
```
ユーザー: "プロジェクトAのToDoタスクを教えて"
    ↓ Agno Agent: search_tasks(project_id=1, column_name="ToDo") を実行
    ↓ 結果を自然言語で回答
```

### 14.2 外部AIエージェント（Claude Desktop）からの利用
```
ユーザー: "カンバンボードのタスクを検索して"
    ↓ Claude Desktop: MCP Server (http://localhost:8000/mcp/sse) に接続
    ↓ MCP: search_tasks ツールを実行
    ↓ 結果をClaudeが自然言語で回答
```

### 14.3 定期実行
```
スケジュール: "毎日9時に期限切れタスクを確認して通知"
    ↓ APScheduler: 毎日9時に /api/agent/schedule を呼び出し
    ↓ Agno Agent: get_overdue_tasks() を実行 → 結果を通知・記録
```

### 14.4 タスク単位定期実行（v2.1）
```
タスク「本番ログ監視」にスケジュール設定:
    command_type: "shell"
    command: "cat {resource_1} | grep ERROR | wc -l"
    resource_1: "/var/log/app.log"
    interval: 毎時
    append_to_task_description: true
    ↓ APScheduler: 毎時実行
    ↓ シェルコマンド実行 → stdout取得
    ↓ TaskService.append_schedule_result() → タスクdescriptionに追記
    ↓ task_schedule_logs に記録
```

---

## 15. 今後の拡張案

### 15.1 短期（3ヶ月以内）
- [ ] タスクのラベル機能
- [ ] 繰り返しタスク（定期作成）
- [ ] タスクのコメント機能
- [ ] エクスポート/インポート（JSON/CSV）
- [ ] Ollama対応（ローカルLLM）
- [ ] タスク単位定期実行：実行結果のファイル出力（descriptionにはパスのみ記載）
- [ ] タスク単位定期実行：エラー時のSlack/Discord通知

### 15.2 中期（6ヶ月以内）
- [ ] カレンダー表示
- [ ] タイムライン（ガントチャート）表示
- [ ] タスクの添付ファイル
- [ ] 通知機能（メール・Slack連携）

### 15.3 長期（1年以内）
- [ ] マルチユーザー対応
- [ ] チーム共有機能
- [ ] モバイルアプリ
- [ ] 他ツール連携（Slack、Notion等）

---

## 16. 用語集

| 用語 | 説明 |
|------|------|
| カンバン | タスクを視覚的に管理する方法。カラムとカードで構成 |
| htmx | HTMLを拡張して動的なUIを実現するライブラリ |
| FastAPI | Pythonの高速Webフレームワーク |
| LLM | Large Language Model（大規模言語モデル） |
| Agno | 軽量でモデル非依存のAIエージェントフレームワーク |
| MCP | Model Context Protocol。AIエージェントとツールを接続する標準プロトコル |
| APScheduler | Pythonの非同期スケジューラーライブラリ |
| Function Calling | AIモデルが構造化された関数呼び出しを行う機能 |
| SSE | Server-Sent Events。サーバーからクライアントへの一方向ストリーミング |
| @tool | Agnoフレームワークのツール定義デコレータ |
| タスク単位定期実行 *(v2.1)* | 特定のタスクカードに紐づけて設定する定期実行スケジュール |
| command_type *(v2.1)* | 実行種別。`agent` はAIエージェントによる自然言語処理、`shell` はOSシェルコマンド実行 |
| リソース *(v2.1)* | スケジュールに登録するフォルダまたはファイルパスの総称 |
| 追記ブロック *(v2.1)* | タスクdescriptionに追記される、定期実行結果を `---` で区切ったテキストブロック |

---

## 17. 参考資料

- [htmx 公式ドキュメント](https://htmx.org/)
- [FastAPI 公式ドキュメント](https://fastapi.tiangolo.com/)
- [SQLAlchemy 公式ドキュメント](https://docs.sqlalchemy.org/)
- [Agno 公式ドキュメント](https://docs.agno.com)
- [MCP 公式ドキュメント](https://modelcontextprotocol.io/)
- [APScheduler 公式ドキュメント](https://apscheduler.readthedocs.io/)
- [OpenAI API ドキュメント](https://platform.openai.com/docs/)
- [Anthropic API ドキュメント](https://docs.anthropic.com/)
- [Ollama 公式サイト](https://ollama.com/)