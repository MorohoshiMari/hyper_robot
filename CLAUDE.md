# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 言語設定

- ユーザーへのレスポンスは必ず日本語で行うこと

## プロジェクト概要

「ハイパーロボット」ボードゲームのWebアプリケーション（localhost動作、対戦・ソルバ機能なし）。
仕様の詳細は `requirements.md` を参照。

## 技術スタック

- TypeScript / React / Vite

## コマンド

- `npm run dev` — 開発サーバー起動
- `npm run build` — プロダクションビルド
- `npm run preview` — ビルド結果のプレビュー

## アーキテクチャ

- `src/types.ts` — 型定義（Color, Position, Robots, Walls, Problem, GameState 等）
- `src/parser.ts` — 問題ファイル（テキスト形式）のパーサー
- `src/game.ts` — ゲームロジック（ロボット移動、移動先算出、クリア判定）
- `src/App.tsx` — メインUIコンポーネント（ボード描画、操作パネル、状態管理）
- `public/problems/` — 問題データ（.txtファイル + index.json）

## ゲームの要点

- 16×16グリッド上で4色（赤・青・黄・緑）のロボットを移動させるパズル
- ロボットは壁か他のロボットに当たるまで直進する
- 中央4マス (7,7),(7,8),(8,7),(8,8) は進入不可
- 指定色のロボットを対応するチップ位置に最小手数で到達させる

## 問題データ形式

`public/problems/` にテキストファイルを配置し、`index.json` にファイル名一覧を記載。
テキスト形式の詳細は `requirements.md` の「ボードの初期配置について」を参照。
