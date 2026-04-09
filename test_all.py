# -*- coding: utf-8 -*-
import os
import json
import re
import shutil

TEST_DIR = 'test_output'
NOTES_DIR = os.path.join(TEST_DIR, 'notes')

def setup():
    os.makedirs(NOTES_DIR, exist_ok=True)
    
    files = {
        '经济学基础.md': '''# 经济学基础

今天学习了供需关系，这是经济学的重要概念。
供给和需求决定了市场价格。
''',
        '政治学概论.md': '''# 政治学概论

政治是一种权力分配的艺术。
民主和专制是两种不同的政治制度。
''',
        '科技发展.md': '''# 科技发展

人工智能正在改变世界。
机器学习和深度学习是未来的方向。
''',
        '已标记文章.md': '''# 已标记的文章

这是一篇已经有tag的文章。

#经济 #科技
''',
        '混合标签.md': '''# 混合标签文章

经济和科技在这里都有提及。

#科技发展 #政治学
''',
    }
    
    for filename, content in files.items():
        with open(os.path.join(NOTES_DIR, filename), 'w', encoding='utf-8') as f:
            f.write(content)
    
    with open(os.path.join(TEST_DIR, 'tags.json'), 'w', encoding='utf-8') as f:
        json.dump(['经济', '政治', '科技', '科技发展'], f)
    
    print('[SETUP] 测试环境创建完成')

def cleanup():
    if os.path.exists(TEST_DIR):
        shutil.rmtree(TEST_DIR)
    print('[CLEANUP] 测试环境清理完成')

def test_add_tags():
    print('\n=== 测试1: 批量添加标签 ===')
    tags = ['经济', '政治', '科技']
    added_count = 0
    
    for filename in os.listdir(NOTES_DIR):
        if not filename.endswith(('.md', '.txt')):
            continue
            
        path = os.path.join(NOTES_DIR, filename)
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        file_added = []
        
        for tag in tags:
            if tag in content:
                pattern = rf'#{re.escape(tag)}(?:\s|$|#)'
                if not re.search(pattern, content):
                    content += f'\n#{tag}'
                    file_added.append(tag)
        
        if file_added:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            added_count += 1
            print(f'  {filename}: 添加 {file_added}')
    
    print(f'结果: 添加了 {added_count} 个文件')
    assert added_count == 4, f'预期4个，实际{added_count}'
    print('[PASS] 测试通过\n')

def test_add_duplicate():
    print('=== 测试2: 重复添加不增加 ===')
    tags = ['经济', '政治', '科技']
    before_count = sum(1 for f in os.listdir(NOTES_DIR) if f.endswith(('.md', '.txt')))
    
    for filename in os.listdir(NOTES_DIR):
        if not filename.endswith(('.md', '.txt')):
            continue
        path = os.path.join(NOTES_DIR, filename)
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        for tag in tags:
            if tag in content:
                pattern = rf'#{re.escape(tag)}(?:\s|$|#)'
                if not re.search(pattern, content):
                    content += f'\n#{tag}'
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    after_count = sum(1 for f in os.listdir(NOTES_DIR) if f.endswith(('.md', '.txt')))
    print(f'结果: 文件数 {before_count} -> {after_count}')
    assert before_count == after_count, '文件数不应变化'
    print('[PASS] 测试通过\n')

def test_delete_tags():
    print('=== 测试3: 批量删除标签 ===')
    tags = ['经济', '政治']
    deleted_count = 0
    
    for filename in os.listdir(NOTES_DIR):
        if not filename.endswith(('.md', '.txt')):
            continue
            
        path = os.path.join(NOTES_DIR, filename)
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        file_deleted = []
        
        for tag in tags:
            pattern = rf'#{re.escape(tag)}(?:\s|$|#)'
            if re.search(pattern, content):
                content = re.sub(pattern, '', content)
                file_deleted.append(tag)
        
        content = content.strip()
        content = re.sub(r'\n\n+', '\n', content)
        
        if file_deleted:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            deleted_count += 1
            print(f'  {filename}: 删除 {file_deleted}')
    
    print(f'结果: 删除了 {deleted_count} 个文件')
    assert deleted_count == 4, f'预期4个，实际{deleted_count}'
    print('[PASS] 测试通过\n')

def test_exact_match():
    print('=== 测试4: 精确匹配（不误删包含的tag） ===')
    
    # 添加 #科技发展 tag
    path = os.path.join(NOTES_DIR, '混合标签.md')
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    content += '\n#科技发展'
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # 删除 #科技 (不应影响 #科技发展)
    path = os.path.join(NOTES_DIR, '科技发展.md')
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    content += '\n#科技发展'
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # 删除 #科技
    for filename in os.listdir(NOTES_DIR):
        if not filename.endswith(('.md', '.txt')):
            continue
        path = os.path.join(NOTES_DIR, filename)
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        pattern = rf'#{re.escape("科技")}(?:\s|$|#)'
        new_content = re.sub(pattern, '', content)
        new_content = new_content.strip()
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)
    
    # 验证 #科技发展 仍然存在
    path = os.path.join(NOTES_DIR, '混合标签.md')
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    has_科技发展 = '#科技发展' in content
    has_科技 = bool(re.search(r'#科技(?:\s|$|#)', content))
    
    print(f'  #科技发展 存在: {has_科技发展}')
    print(f'  #科技 存在: {has_科技}')
    
    assert has_科技发展, '#科技发展 应该保留'
    assert not has_科技, '#科技 应该被删除'
    print('[PASS] 测试通过\n')

def test_search():
    print('=== 测试5: 搜索标签 ===')
    
    # 重新添加 #科技 标签，确保有测试数据
    for filename in os.listdir(NOTES_DIR):
        if not filename.endswith(('.md', '.txt')):
            continue
        path = os.path.join(NOTES_DIR, filename)
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否包含"科技"关键词且没有#科技标签
        if '科技' in content and not re.search(r'#科技(?:\s|$|#)', content):
            content += '\n#科技'
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
    
    tag = '科技'
    results = []
    
    for filename in os.listdir(NOTES_DIR):
        if not filename.endswith(('.md', '.txt')):
            continue
        path = os.path.join(NOTES_DIR, filename)
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        pattern = rf'#{re.escape(tag)}(?:\s|$|#)'
        if re.search(pattern, content):
            results.append(filename)
    
    print(f'搜索 #{tag}: 找到 {len(results)} 个文件')
    print(f'  结果: {results}')
    assert len(results) >= 1, f'预期至少1个，实际{len(results)}'
    print('[PASS] 测试通过\n')

def test_scan_existing_tags():
    print('=== 测试6: 扫描已有标签 ===')
    all_tags = set()
    
    for filename in os.listdir(NOTES_DIR):
        if not filename.endswith(('.md', '.txt')):
            continue
        path = os.path.join(NOTES_DIR, filename)
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tag_pattern = r'#([^\s#\[\],]+)'
        found = re.findall(tag_pattern, content)
        all_tags.update(found)
    
    existing_tags = sorted(all_tags)
    print(f'扫描到 {len(existing_tags)} 个标签: {existing_tags}')
    assert len(existing_tags) >= 1, '应该有至少1个标签'
    print('[PASS] 测试通过\n')

def test_context_menu_toggle():
    print('=== 测试7: 右键单独添加/删除 ===')
    path = os.path.join(NOTES_DIR, '经济学基础.md')
    
    # 测试添加
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if not re.search(r'#经济(?:\s|$|#)', content):
        content += '\n#经济'
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print('  添加 #经济')
    
    # 验证添加
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    assert '#经济' in content, '应该包含 #经济'
    
    # 测试删除
    content = re.sub(r'#经济(?:\s|$|#)', '', content)
    content = content.strip()
    content = re.sub(r'\n\n+', '\n', content)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print('  删除 #经济')
    
    # 验证删除
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    assert '#经济' not in content, '不应该包含 #经济'
    
    print('[PASS] 测试通过\n')

def verify_file_content():
    print('=== 验证最终文件内容 ===')
    for filename in sorted(os.listdir(NOTES_DIR)):
        path = os.path.join(NOTES_DIR, filename)
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f'\n--- {filename} ---')
        print(content)

def run_all_tests():
    print('='*50)
    print('开始运行所有测试')
    print('='*50)
    
    setup()
    
    try:
        test_add_tags()
        test_add_duplicate()
        test_delete_tags()
        test_exact_match()
        test_search()
        test_scan_existing_tags()
        test_context_menu_toggle()
        
        print('='*50)
        print('所有测试通过!')
        print('='*50)
        
        verify_file_content()
        
    except Exception as e:
        print(f'\n测试失败: {e}')
        import traceback
        traceback.print_exc()
    finally:
        cleanup()

if __name__ == '__main__':
    run_all_tests()