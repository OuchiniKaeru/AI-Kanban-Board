# AI Kanban Board

AIエージェント搭載の個人向けカンバンボードアプリケーション。
自然言語でタスクの作成・管理・分析を行えます。

## 機能

- **カンバンボード**: ToDo / Doing / Done の3列でタスク管理
- **ドラッグ&ドロップ**: タスクのカラム間移動
- **プロジェクト機能**: 複数のカンバンボードをプロジェクト単位で管理・横断検索
- **AIチャット**: 自然言語でタスク作成・期限管理・レポート生成
- **定期実行**: スケジュールベースでAIコマンドやシェルコマンドを自動実行
- **タスク単位定期実行**: 各タスクにスケジュールを設定し、フォルダ・ファイルを監視・操作
- **MCPサーバー**: Claude Desktop / Cursor などの外部AIエージェントと連携
- **レポート**: 進捗サマリー・週次レポート

## 技術スタック

- **フロントエンド**: htmx + HTML/CSS/JS
- **バックエンド**: Python + FastAPI
- **データベース**: SQLite
- **AI連携**: Agnoフレームワーク / OpenAI API / Anthropic Claude API / MCPプロトコル
- **定期実行**: APScheduler

## セットアップ

### 必要条件

- Python 3.11+
- uv

### インストール

```bash
# リポジトリをクローン
cd kanban_agent

# 依存関係をインストール
uv sync

# 環境変数を設定
cp .env.example .env
# .envファイルを編集してAPIキーを設定
```

### 環境変数

`.env`ファイルに以下を設定:

```env
# OpenAI
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-5.4-mini

# または Anthropic
ANTHROPIC_API_KEY=your_api_key_here
ANTHROPIC_MODEL=claude-4.5-haiku

# Agnoエージェント（デフォルトで有効）
USE_AGNO=true

# シェルコマンド実行の許可パス（カンマ区切り）
ALLOWED_PATH_PREFIXES=/home/user/projects,/var/log
```

## 起動

```bash
uv run uvicorn app.main:app --reload
```

ブラウザで http://localhost:8000/board にアクセス

## 使い方

### タスク管理

- **タスク作成**: カラム内の「+ タスクを追加」ボタンをクリック
- **タスク編集**: タスクカードをダブルクリック
- **タスク移動**: ドラッグ&ドロップで別カラムへ
- **タスク削除**: タスクカードの🗑️アイコンをクリック
- **定期実行設定**: タスクカードの⏰アイコンをクリック（v2.1）

### プロジェクト管理

- ヘッダーのプロジェクト選択ドロップダウンでプロジェクトを切り替え
- プロジェクトごとにカラム・タスクを独立管理
- 全プロジェクトを横断してタスクを検索可能

### AIチャット

画面右上の「AI Chat」ボタンでチャットパネルを開きます。

例:
- 「来週の月曜日にプレゼン資料を作成するタスクを追加して」
- 「期限が近いタスクを教えて」
- 「今週の進捗を教えて」
- 「プレゼン資料をDoneに移動して」
- 「全プロジェクトから"報告"というキーワードのタスクを探して」

### 定期実行

スケジュールを設定して自動実行できます:
- **Agent実行**: 自然言語コマンドをAIエージェントが定期実行
- **Shell実行**: シェルコマンドを実行し、結果をタスクに自動追記
- **リソース登録**: フォルダ・ファイルパスを登録してプレースホルダ展開

例:
- 「毎日9時に期限切れタスクを確認して通知」
- `/var/log/app.log` を毎時監視してERROR件数をタスクに記録

### MCPサーバー連携

Claude Desktop や Cursor などの外部AIエージェントからカンバンボードを操作できます。

設定例:
```
MCP Server URL: http://localhost:8000/mcp/sse
```

提供ツール: `search_tasks`, `create_task`, `update_task`, `delete_task`, `move_task`, `get_projects`, `get_columns`, `generate_report`, `get_overdue_tasks`, `create_schedule`, `list_schedules`

## APIエンドポイント

### 基本API

| メソッド | エンドポイント | 説明 |
|----------|---------------|------|
| GET | `/api/projects` | プロジェクト一覧 |
| POST | `/api/projects` | プロジェクト作成 |
| GET | `/api/projects/search` | 全プロジェクト横断検索 |
| GET | `/api/columns` | カラム一覧 |
| POST | `/api/columns` | カラム作成 |
| GET | `/api/tasks` | タスク一覧 |
| POST | `/api/tasks` | タスク作成 |
| PUT | `/api/tasks/{id}` | タスク更新 |
| DELETE | `/api/tasks/{id}` | タスク削除 |
| PUT | `/api/tasks/{id}/move` | タスク移動 |

### AI・レポートAPI

| メソッド | エンドポイント | 説明 |
|----------|---------------|------|
| POST | `/api/agent/process` | AIメッセージ処理（同期） |
| POST | `/api/agent/stream` | AIメッセージ処理（ストリーミング） |
| POST | `/api/agent/schedule` | 定期実行コマンド受付 |
| GET | `/api/reports/summary` | サマリーレポート |
| GET | `/api/reports/weekly` | 週次レポート |

### スケジュールAPI（v2.0/v2.1）

| メソッド | エンドポイント | 説明 |
|----------|---------------|------|
| GET | `/api/schedules` | スケジュール一覧 |
| POST | `/api/schedules` | スケジュール作成 |
| GET | `/api/schedules/{id}` | スケジュール詳細 |
| PUT | `/api/schedules/{id}` | スケジュール更新 |
| DELETE | `/api/schedules/{id}` | スケジュール削除 |
| POST | `/api/schedules/{id}/run` | 手動実行 |
| GET | `/api/schedules/{id}/resources` | リソース一覧 |
| POST | `/api/schedules/{id}/resources` | リソース追加 |
| DELETE | `/api/schedules/{id}/resources/{resource_id}` | リソース削除 |
| GET | `/api/schedules/{id}/logs` | 実行履歴 |
| GET | `/api/tasks/{id}/schedules` | タスクに紐づくスケジュール一覧 |

### MCPサーバー

| メソッド | エンドポイント | 説明 |
|----------|---------------|------|
| GET | `/mcp/sse` | MCP SSEエンドポイント |
| POST | `/mcp/messages` | MCPメッセージ受信 |

## ライセンス

MIT
