[app]
title = 批量OCR
package.name = batchocr
package.domain = com.marvis
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0.0
requirements = python3,kivy==2.3.0,kivymd==1.2.0,pytesseract,Pillow,tesseract
orientation = portrait
fullscreen = 1

# 存储权限
android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,MANAGE_EXTERNAL_STORAGE,READ_MEDIA_IMAGES

android.api = 34
android.minapi = 24
android.ndk = 25c
android.sdk = 34
android.arch = armeabi-v7a
android.allow_backup = True
presplash.color = #1A237E
android.logcat_filters = *:S python:D

[buildozer]
log_level = 2
warn_on_root = 1
