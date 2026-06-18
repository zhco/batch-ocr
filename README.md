---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: 6bf887ea0b54f9e8c4a80e98ead3aa40_ec43825b6aa711f1a0095254002afed2
    ReservedCode1: Dysu+TicMNietQrkg9mDw3f1N+5Xpv+iEKaL573E6rER2A4ONKlIOaF8Rxfyy/WrDVMF76MoHmZ+Sg9Dun8e1Im+GzbK+GKHQ6iAVQkvU0rdyFR5vDUfAIlLdK5SBTgxVTKhMEJBcBiyB8ttg8rIkd6CDPmBu9x1wGiVLn97PGJ37IqfeKy6kEaBuJs=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: 6bf887ea0b54f9e8c4a80e98ead3aa40_ec43825b6aa711f1a0095254002afed2
    ReservedCode2: Dysu+TicMNietQrkg9mDw3f1N+5Xpv+iEKaL573E6rER2A4ONKlIOaF8Rxfyy/WrDVMF76MoHmZ+Sg9Dun8e1Im+GzbK+GKHQ6iAVQkvU0rdyFR5vDUfAIlLdK5SBTgxVTKhMEJBcBiyB8ttg8rIkd6CDPmBu9x1wGiVLn97PGJ37IqfeKy6kEaBuJs=
---

# 批量 OCR - Android App

逐页识别图片中的文字，支持中英文，结果保存为 txt 文件。

## 技术栈

- KivyMD 界面
- Tesseract OCR 引擎（支持中英文）
- GitHub Actions 自动编译 APK

## 上传到 GitHub 自动编译

### 1. 创建 GitHub 仓库

在 GitHub 新建仓库（如 `batch-ocr`），**不要勾选** Initialize with README。

### 2. 推送代码

```bash
cd batch_ocr_app
git init
git add .
git commit -m "init: 批量OCR App"
git branch -M main
git remote add origin https://github.com/你的用户名/batch-ocr.git
git push -u origin main
```

### 3. 等待编译

推送后 GitHub Actions 自动开始编译（约 20-30 分钟）。在仓库页面点击 **Actions** 标签查看进度。

### 4. 下载 APK

编译完成后，在 Actions 运行的 Artifacts 中下载 `batch-ocr-apk.zip`，解压得到 APK 文件。

## 手动触发编译

在 GitHub 仓库 → Actions → Build APK → Run workflow。

## 首次编译注意事项

- Tesseract 语言包（中英文）会在编译时自动下载
- 首次编译需要下载 Android SDK/NDK，耗时较长
- 后续编译会使用缓存，约 10-15 分钟
*（内容由AI生成，仅供参考）*
