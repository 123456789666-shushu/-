import os

# 创建文件夹结构
folders = [
    'templates',
    'static/css',
    'static/js',
    'static/profile_pics'
]

for folder in folders:
    os.makedirs(folder, exist_ok=True)
    print(f"Created folder: {folder}")

print("All folders created successfully!")