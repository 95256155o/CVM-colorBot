# 快速修復指南 - SSH 認證錯誤

## 問題診斷

根據錯誤日誌，主要問題是：
```
ERROR: Permission denied (publickey)
```

這表示 SSH 認證失敗。

## 立即修復步驟

### 1. 檢查 GitHub Secrets（最重要）

前往：https://github.com/asenyeroao-ct/CVM-colorBot/settings/secrets/actions

確認以下三個 Secrets **都存在**且**名稱完全正確**：

- [ ] `GITEE_USER` = `asenyeroao-ct`
- [ ] `GITEE_PRIVATE_KEY` = （完整的 SSH 私鑰）
- [ ] `GITEE_TOKEN` = （Gitee 個人訪問令牌）

### 2. 驗證 SSH 私鑰格式

`GITEE_PRIVATE_KEY` 必須包含完整的私鑰，格式如下：

```
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAABlwAAAAdzc2gtcn
... (多行內容) ...
-----END OPENSSH PRIVATE KEY-----
```

**檢查要點：**
- ✅ 以 `-----BEGIN OPENSSH PRIVATE KEY-----` 開頭
- ✅ 以 `-----END OPENSSH PRIVATE KEY-----` 結尾
- ✅ 中間有多行 Base64 編碼內容（通常 20-30 行）
- ❌ 不能只有部分內容
- ❌ 不能缺少 BEGIN/END 標記

### 3. 確認公鑰已添加到 Gitee

1. 訪問：https://gitee.com/profile/sshkeys
2. 確認有一個標題為 `GitHub Actions Sync` 的公鑰
3. 如果沒有，請添加：
   - 運行：`Get-Content ~/.ssh/id_rsa.pub`
   - 複製公鑰內容
   - 在 Gitee 添加公鑰頁面貼上

### 4. 重新生成 SSH 密鑰對（如果問題持續）

如果現有密鑰有問題，可以重新生成：

```powershell
# 生成新的 SSH 密鑰對
ssh-keygen -t rsa -b 4096 -C "your_email@example.com" -f $env:USERPROFILE\.ssh\id_rsa_gitee

# 查看公鑰（添加到 Gitee）
Get-Content $env:USERPROFILE\.ssh\id_rsa_gitee.pub

# 查看私鑰（添加到 GitHub Secrets）
Get-Content $env:USERPROFILE\.ssh\id_rsa_gitee
```

然後：
1. 將**公鑰**添加到 Gitee（https://gitee.com/profile/sshkeys）
2. 將**私鑰**更新到 GitHub Secrets 的 `GITEE_PRIVATE_KEY`

### 5. 測試工作流程

1. 前往 GitHub Actions：https://github.com/asenyeroao-ct/CVM-colorBot/actions
2. 選擇 **Sync to Gitee** 工作流程
3. 點擊「Run workflow」手動觸發
4. 查看執行日誌，確認沒有錯誤

## 驗證清單

在重新運行工作流程前，請確認：

- [ ] `GITEE_USER` Secret 存在且值為 `asenyeroao-ct`
- [ ] `GITEE_PRIVATE_KEY` Secret 存在且包含完整的私鑰（包括 BEGIN/END）
- [ ] `GITEE_TOKEN` Secret 存在且有效
- [ ] SSH 公鑰已添加到 Gitee
- [ ] Gitee Token 有 `projects` 權限

## 如果問題仍然存在

請參考詳細的故障排除指南：
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - 完整的故障排除指南
- [CONFIG_STEPS.md](CONFIG_STEPS.md) - 詳細的配置步驟

## 常見錯誤對照

| 錯誤訊息 | 原因 | 解決方案 |
|---------|------|---------|
| `Permission denied (publickey)` | SSH 認證失敗 | 檢查 `GITEE_PRIVATE_KEY` Secret 和 Gitee 公鑰 |
| `已存在同地址倉庫` | 倉庫已存在 | 通常不影響同步，可忽略 |
| `權限不足` | Token 無效或權限不足 | 重新生成 Gitee Token 並確保有 `projects` 權限 |
