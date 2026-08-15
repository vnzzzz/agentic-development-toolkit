---
name: replace-with-skill-name
description: このSkillが何を行い、どの状況でtriggerし、どの状況ではtriggerしないかを具体的に記載する。
license: MIT
compatibility: 必要なruntime、tool、network access、対応Agentを記載する。
---

# Skillタイトルを記載する

## 入力

必須inputと任意inputを記載する。

## 手順

1. 実行内容を命令形かつ検証可能なstepで記載する。
2. deterministicな実行が必要な場合を除き、scriptよりinstructionsを優先する。
3. 現在のtaskに必要なsupporting fileだけを読む。

## 出力

出力contractを具体的に記載する。

## 安全性と失敗時の扱い

trust boundary、禁止操作、validation、recovery behaviorを記載する。
