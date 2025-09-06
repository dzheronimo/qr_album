#!/usr/bin/env python3
"""
Скрипт для проверки структуры пакета py-commons
"""

import os
import sys

def check_package_structure():
    print("Проверяю структуру пакета py-commons...")
    
    # Проверяем структуру пакета
    py_commons_path = "packages/py-commons"
    
    if not os.path.exists(py_commons_path):
        print(f"❌ Директория {py_commons_path} не найдена")
        return False
    
    print(f"✅ Директория {py_commons_path} найдена")
    
    # Проверяем файлы
    files_to_check = [
        "health.py",
        "http.py", 
        "pyproject.toml",
        "commons/__init__.py",
        "commons/security.py",
        "commons/settings.py"
    ]
    
    for file_path in files_to_check:
        full_path = os.path.join(py_commons_path, file_path)
        if os.path.exists(full_path):
            print(f"✅ {file_path} найден")
        else:
            print(f"❌ {file_path} не найден")
    
    # Проверяем pyproject.toml
    pyproject_path = os.path.join(py_commons_path, "pyproject.toml")
    if os.path.exists(pyproject_path):
        with open(pyproject_path, 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"✅ pyproject.toml найден")
            print(f"Содержимое pyproject.toml:")
            print(content[:500] + "..." if len(content) > 500 else content)
    
    return True

if __name__ == "__main__":
    check_package_structure()
