import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import json
import subprocess
import re

class TagManager:
    def __init__(self, root):
        self.root = root
        self.root.title('Tag Manager')
        self.root.geometry('700x550')
        
        self.tags = []
        self.target_folder = os.getcwd()
        
        self.create_widgets()
        self.folder_var.set(self.target_folder)
        self.load_default_json()
    
    def load_default_json(self):
        default_json = os.path.join(os.getcwd(), 'tags.json')
        if os.path.exists(default_json):
            try:
                with open(default_json, 'r', encoding='utf-8') as f:
                    self.tags = json.load(f)
                self.refresh_tag_list()
            except:
                pass
    
    def create_widgets(self):
        top_frame = ttk.Frame(self.root)
        top_frame.pack(fill='x', padx=5, pady=3)
        
        ttk.Label(top_frame, text='文件夹:').pack(side='left')
        self.folder_var = tk.StringVar()
        ttk.Entry(top_frame, textvariable=self.folder_var, width=45).pack(side='left', padx=3)
        ttk.Button(top_frame, text='选择', command=self.select_folder).pack(side='left')
        
        middle_frame = ttk.Frame(self.root)
        middle_frame.pack(fill='both', expand=True, padx=5, pady=3)
        
        left_frame = ttk.LabelFrame(middle_frame, text='标签')
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 2))
        
        self.tag_listbox = tk.Listbox(left_frame, height=5, selectmode='extended')
        self.tag_listbox.pack(fill='both', expand=True, padx=2, pady=2)
        
        tag_btn_frame = ttk.Frame(left_frame)
        tag_btn_frame.pack(fill='x', padx=2, pady=2)
        ttk.Button(tag_btn_frame, text='JSON', command=self.import_json).pack(side='left', padx=1)
        ttk.Button(tag_btn_frame, text='+', width=2, command=self.add_tag_dialog).pack(side='left', padx=1)
        ttk.Button(tag_btn_frame, text='-', width=2, command=self.delete_tag).pack(side='left', padx=1)
        ttk.Button(tag_btn_frame, text='查标签', command=self.scan_existing_tags).pack(side='left', padx=1)
        
        right_frame = ttk.LabelFrame(middle_frame, text='操作')
        right_frame.pack(side='left', fill='both', expand=True, padx=(2, 0))
        
        op_btn_frame = ttk.Frame(right_frame)
        op_btn_frame.pack(padx=5, pady=5)
        
        ttk.Button(op_btn_frame, text='添加Tag', command=self.add_tags).pack(fill='x', pady=1)
        ttk.Button(op_btn_frame, text='删除Tag', command=self.delete_tags).pack(fill='x', pady=1)
        ttk.Button(op_btn_frame, text='搜索', command=self.search_selected_tags).pack(fill='x', pady=1)
        
        result_frame = ttk.LabelFrame(self.root, text='结果 (双击打开, 右键操作)')
        result_frame.pack(fill='both', expand=True, padx=5, pady=3)
        
        self.result_tree = ttk.Treeview(result_frame, columns=('状态', '文件', '标签', '原文'), show='tree headings', height=10)
        self.result_tree.heading('#0', text='#')
        self.result_tree.heading('状态', text='状态')
        self.result_tree.heading('文件', text='文件')
        self.result_tree.heading('标签', text='标签')
        self.result_tree.heading('原文', text='原文')
        self.result_tree.column('#0', width=25)
        self.result_tree.column('状态', width=50)
        self.result_tree.column('文件', width=150)
        self.result_tree.column('标签', width=80)
        self.result_tree.column('原文', width=300)
        self.result_tree.pack(fill='both', expand=True, padx=2, pady=2)
        
        self.result_tree.bind('<Double-1>', self.open_file)
        self.result_tree.bind('<Button-3>', self.show_context_menu)
        
        scrollbar = ttk.Scrollbar(result_frame, orient='vertical', command=self.result_tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.result_tree.configure(yscrollcommand=scrollbar.set)
    
    def select_folder(self):
        folder = filedialog.askdirectory(initialdir=self.target_folder)
        if folder:
            self.target_folder = folder
            self.folder_var.set(folder)
    
    def import_json(self):
        file_path = filedialog.askopenfilename(filetypes=[('JSON', '*.json')], initialdir=self.target_folder)
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    tags = json.load(f)
                self.tags = tags
                self.refresh_tag_list()
            except Exception as e:
                messagebox.showerror('错误', f'JSON解析失败: {e}')
    
    def refresh_tag_list(self):
        self.tag_listbox.delete(0, tk.END)
        for tag in self.tags:
            self.tag_listbox.insert(tk.END, tag)
    
    def add_tag_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title('添加')
        dialog.geometry('220x70')
        
        ttk.Label(dialog, text='标签:').pack(side='left', padx=5)
        tag_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=tag_var, width=12).pack(side='left', padx=3)
        
        def confirm():
            tag = tag_var.get().strip()
            if tag and tag not in self.tags:
                self.tags.append(tag)
                self.refresh_tag_list()
            dialog.destroy()
        
        ttk.Button(dialog, text='确定', command=confirm).pack(side='left', padx=5)
        dialog.bind('<Return>', lambda e: confirm())
    
    def delete_tag(self):
        selection = self.tag_listbox.curselection()
        for i in reversed(selection):
            tag = self.tag_listbox.get(i)
            self.tags.remove(tag)
        self.refresh_tag_list()
    
    def get_files(self):
        if not self.target_folder:
            messagebox.showwarning('警告', '请先选择目标文件夹')
            return []
        files = []
        for root, dirs, filenames in os.walk(self.target_folder):
            for file in filenames:
                if file.endswith('.md') or file.endswith('.txt'):
                    files.append(os.path.join(root, file))
        return files
    
    def read_file(self, path):
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def write_file(self, path, content):
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def check_tag_exists(self, content, tag):
        pattern = rf'#{re.escape(tag)}(?:\s|$|#)'
        return bool(re.search(pattern, content))
    
    def find_context(self, content, keyword, radius=30):
        pattern = re.escape(keyword)
        match = re.search(pattern, content)
        if not match:
            return ''
        
        start = max(0, match.start() - radius)
        end = min(len(content), match.end() + radius)
        
        context = content[start:end].replace('\n', ' ')
        
        if start > 0:
            context = '...' + context
        if end < len(content):
            context = context + '...'
        
        return context
    
    def add_tags(self):
        if not self.tags:
            messagebox.showwarning('警告', '请先添加标签')
            return
        
        files = self.get_files()
        if not files:
            return
        
        self.result_tree.delete(*self.result_tree.get_children())
        
        for i, file_path in enumerate(files):
            content = self.read_file(file_path)
            added_tags = []
            context_snippet = ''
            
            for tag in self.tags:
                if tag in content and not self.check_tag_exists(content, tag):
                    tag_line = f'\n#{tag}'
                    content += tag_line
                    added_tags.append(tag)
                    if not context_snippet:
                        context_snippet = self.find_context(content, tag)
            
            if added_tags:
                self.write_file(file_path, content)
                status = '已添加'
            else:
                status = '无需处理'
            
            rel_path = os.path.relpath(file_path, self.target_folder)
            self.result_tree.insert('', 'end', text=str(i+1), 
                                   values=(status, rel_path, ', '.join(added_tags), context_snippet))
        
        messagebox.showinfo('完成', f'处理完成，共 {len(files)} 个文件')
    
    def delete_tags(self):
        if not self.tags:
            messagebox.showwarning('警告', '请先添加标签')
            return
        
        files = self.get_files()
        if not files:
            return
        
        self.result_tree.delete(*self.result_tree.get_children())
        
        for i, file_path in enumerate(files):
            content = self.read_file(file_path)
            removed_tags = []
            context_snippet = ''
            
            for tag in self.tags:
                pattern = rf'#{re.escape(tag)}(?:\s|$|#)'
                if re.search(pattern, content):
                    content = re.sub(pattern, '', content)
                    if tag not in removed_tags:
                        removed_tags.append(tag)
                        if not context_snippet:
                            context_snippet = self.find_context(content, tag)
            
            content = content.strip()
            content = re.sub(r'\n\n+', '\n', content)
            
            if removed_tags:
                self.write_file(file_path, content)
                status = '已删除'
            else:
                status = '无需处理'
            
            rel_path = os.path.relpath(file_path, self.target_folder)
            self.result_tree.insert('', 'end', text=str(i+1),
                                   values=(status, rel_path, ', '.join(removed_tags), context_snippet))
        
        messagebox.showinfo('完成', f'处理完成，共 {len(files)} 个文件')
    
    def search_selected_tags(self):
        selection = self.tag_listbox.curselection()
        if selection:
            tags_to_search = [self.tag_listbox.get(i) for i in selection]
        else:
            tags_to_search = self.tags
        
        if not tags_to_search:
            messagebox.showwarning('警告', '请先选择标签')
            return
        
        if not self.target_folder:
            messagebox.showwarning('警告', '请先选择目标文件夹')
            return
        
        files = self.get_files()
        self.result_tree.delete(*self.result_tree.get_children())
        
        results = []
        for file_path in files:
            content = self.read_file(file_path)
            matched_tags = []
            for tag in tags_to_search:
                if self.check_tag_exists(content, tag):
                    matched_tags.append(tag)
                    context = self.find_context(content, tag)
                    rel_path = os.path.relpath(file_path, self.target_folder)
                    results.append((rel_path, tag, context))
        
        for idx, (rel_path, tag, context) in enumerate(results):
            self.result_tree.insert('', 'end', text=str(idx+1),
                                   values=('匹配', rel_path, f'#{tag}', context))
        
        messagebox.showinfo('完成', f'找到 {len(results)} 个匹配')
    
    def scan_existing_tags(self):
        if not self.target_folder:
            messagebox.showwarning('警告', '请先选择目标文件夹')
            return
        
        files = self.get_files()
        all_tags = set()
        
        for file_path in files:
            content = self.read_file(file_path)
            tag_pattern = r'#([^\s#\[\],]+)'
            found = re.findall(tag_pattern, content)
            all_tags.update(found)
        
        existing_tags = sorted(all_tags)
        
        if not existing_tags:
            messagebox.showinfo('完成', '未找到任何标签')
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title('已有标签')
        dialog.geometry('300x400')
        
        ttk.Label(dialog, text=f'找到 {len(existing_tags)} 个标签:').pack(pady=5)
        
        listbox = tk.Listbox(dialog, selectmode='extended', height=15)
        listbox.pack(fill='both', expand=True, padx=5, pady=5)
        for tag in existing_tags:
            listbox.insert(tk.END, tag)
        
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=5)
        
        def add_selected():
            selection = listbox.curselection()
            for i in selection:
                tag = listbox.get(i)
                if tag not in self.tags:
                    self.tags.append(tag)
            self.refresh_tag_list()
            dialog.destroy()
        
        ttk.Button(btn_frame, text='添加到列表', command=add_selected).pack()
    
    def show_context_menu(self, event):
        item = self.result_tree.identify_row(event.y)
        if not item:
            return
        
        self.result_tree.selection_set(item)
        values = self.result_tree.item(item, 'values')
        if len(values) < 4:
            return
        
        status, rel_path, tags_str, context = values
        tag = tags_str.replace('#', '').strip() if tags_str else ''
        
        if not tag:
            return
        
        menu = tk.Menu(self.root, tearoff=0)
        
        has_tag = status == '已添加' or status == '匹配'
        
        if has_tag:
            menu.add_command(label=f'删除 tag: {tag}', command=lambda: self.toggle_tag_single(rel_path, tag, False))
        else:
            menu.add_command(label=f'添加 tag: {tag}', command=lambda: self.toggle_tag_single(rel_path, tag, True))
        
        menu.post(event.x_root, event.y_root)
    
    def toggle_tag_single(self, rel_path, tag, add):
        file_path = os.path.join(self.target_folder, rel_path)
        
        if not os.path.exists(file_path):
            messagebox.showerror('错误', f'文件不存在: {file_path}')
            return
        
        content = self.read_file(file_path)
        
        if add:
            if not self.check_tag_exists(content, tag):
                content += f'\n#{tag}'
                self.write_file(file_path, content)
                status = '已添加'
        else:
            if self.check_tag_exists(content, tag):
                pattern = rf'#{re.escape(tag)}'
                content = re.sub(pattern, '', content)
                content = content.strip()
                content = re.sub(r'\n\n+', '\n', content)
                self.write_file(file_path, content)
                status = '已删除'
            else:
                status = '无需处理'
        
        for item in self.result_tree.get_children():
            if self.result_tree.item(item, 'values')[1] == rel_path:
                context = self.find_context(content, tag)
                self.result_tree.item(item, values=(status, rel_path, tag, context))
                break
        
        messagebox.showinfo('完成', f'{rel_path} - {status}')
    
    def open_file(self, event):
        selection = self.result_tree.selection()
        if selection:
            item = self.result_tree.item(selection[0])
            rel_path = item['values'][1]
            file_path = os.path.join(self.target_folder, rel_path)
            if os.path.exists(file_path):
                subprocess.Popen(['cmd', '/c', 'start', '', file_path])

if __name__ == '__main__':
    root = tk.Tk()
    app = TagManager(root)
    root.mainloop()