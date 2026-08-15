# Repository作業ルール

- 配布するAgent Skillの正本は`skill/` directory全体とする。repository直下へ`SKILL.md`を追加しない。
- 1つのSkillは1つの明確なcapabilityに集中させる。
- instructionsだけでは不十分で、deterministicな処理が必要な場合にだけscriptを追加する。
- Skillの実行時に必要なscript、reference、assetは`skill/`内へ置く。repository-onlyのtestやfixtureは外側へ置いてよい。
- 配布後に存在しないrepository-only fileへSkill runtimeを依存させない。
- `SKILL.md`ではinput、output、boundary、failure handling、security assumptionを必要な粒度で明示する。
- credentialやmutable remote URLから取得したexecutableをcommitしない。security requirementは`SECURITY.md`に従う。
- 完了前に`make test`を実行する。`make test`には隔離したdistribution bundleの検証が含まれる。
