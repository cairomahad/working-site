#!/usr/bin/env python3
"""
Анализ используемых компонентов фронтенда
"""

import os
import re
from pathlib import Path

def find_imports_in_file(file_path):
    """Найти все импорты в файле"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Найти импорты из локальных файлов
        local_imports = re.findall(r'import.*from\s+[\'"]\.\/([^\'"]+)[\'"]', content)
        return local_imports
    except:
        return []

def analyze_used_components():
    """Анализ используемых компонентов"""
    src_path = Path('/app/frontend/src')
    all_files = set()
    used_files = set()
    
    # Найти все JS файлы
    for file in src_path.glob('*.js'):
        all_files.add(file.stem)
    
    print("📁 Все файлы в /app/frontend/src:")
    for file in sorted(all_files):
        print(f"  - {file}.js")
    
    # Начать с main файлов
    to_check = ['App', 'index']
    checked = set()
    
    while to_check:
        current = to_check.pop()
        if current in checked:
            continue
            
        checked.add(current)
        used_files.add(current)
        
        file_path = src_path / f"{current}.js"
        if file_path.exists():
            imports = find_imports_in_file(file_path)
            for imp in imports:
                imp_name = imp.split('.')[0]  # Убрать расширение если есть
                if imp_name not in checked:
                    to_check.append(imp_name)
    
    print(f"\n✅ Используемые файлы ({len(used_files)}):")
    for file in sorted(used_files):
        print(f"  - {file}.js")
    
    unused_files = all_files - used_files
    print(f"\n❌ Неиспользуемые файлы ({len(unused_files)}):")
    for file in sorted(unused_files):
        print(f"  - {file}.js")
    
    return used_files, unused_files

if __name__ == "__main__":
    used, unused = analyze_used_components()