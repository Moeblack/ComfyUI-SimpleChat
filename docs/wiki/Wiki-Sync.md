# Wiki Sync（GitHub 原生 Wiki 自动发布）

本仓库采用 **GitHub 原生 Wiki**，并使用 GitHub Actions 把 `docs/wiki/` 自动同步到 Wiki 仓库。

---

## 1) 需要在 GitHub 仓库里打开 Wiki 功能

进入 GitHub 仓库：
- Settings -> Features -> 勾选 **Wiki**

若未启用，Actions 会在访问 `${repo}.wiki.git` 时失败。

### 1.1) 首次初始化（非常重要）

GitHub 的 Wiki git 仓库（`${repo}.wiki.git`）通常需要**先创建第一篇 Wiki 页面**才会真正生成。

做法：
- 打开仓库的 Wiki：`https://github.com/<owner>/<repo>/wiki`
- 点击 **Create the first page**
- 保存（即使只写一行也可以）

完成后，再触发一次同步（重新 push，或手动运行 `Publish Wiki` 工作流）即可。

---

## 2) 文档如何更新

请直接改动仓库内：
- `docs/wiki/*.md`

推送到 `main/master` 后会自动发布到 Wiki。

---

## 3) 同步工作流文件在哪里

自动发布配置位于：
- `.github/workflows/publish-wiki.yml`

同步逻辑：
- 把 `docs/wiki/` rsync 到 Wiki 仓库根目录
- 自动提交并 push

