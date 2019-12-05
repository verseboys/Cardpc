请在 nsproject/settings.py 的 `STATICFILES_DIRS` 中添加：

```py
STATICFILES_DIRS = [
    ...
    os.path.join(BASE_DIR, 'natureself/assets'),
]
```
