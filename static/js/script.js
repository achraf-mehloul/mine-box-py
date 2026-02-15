class MindBoxApp {
    constructor() {
        this.data = { files: [], entries: [] };
        this.currentFile = null;
        this.currentEntry = null;
        this.selectedMood = '😊';
        this.selectedColor = '#9d4edd';
        this.user = null;
        this.init();
    }

    async init() {
        const savedUser = localStorage.getItem('mindbox_user');
        if (!savedUser) {
            window.location.href = '/login';
            return;
        }

        this.user = JSON.parse(savedUser);
        this.showDate();
        await this.loadData();
        this.render();
        this.attachEvents();
    }

    toArabicNumber(num) {
        const arabicNumbers = ['٠', '١', '٢', '٣', '٤', '٥', '٦', '٧', '٨', '٩'];
        return num.toString().split('').map(digit => arabicNumbers[parseInt(digit)] || digit).join('');
    }

    showDate() {
        const dateElement = document.getElementById('currentDate');
        const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
        let today = new Date().toLocaleDateString('ar-SA', options);
        today = today.replace(/\d/g, d => this.toArabicNumber(d));
        dateElement.textContent = today;
    }

    async loadData() {
        try {
            const response = await fetch(`/api/files?user_id=${this.user.id}`);
            const result = await response.json();
            if (result.success) {
                this.data.files = result.files;
            }

            const entriesResponse = await fetch(`/api/entries?user_id=${this.user.id}`);
            const entriesResult = await entriesResponse.json();
            if (entriesResult.success) {
                this.data.entries = entriesResult.entries;
            }
        } catch (error) {
            console.error('Error loading data:', error);
            this.data = { files: [], entries: [] };
        }
    }

    render() {
        this.renderFiles();
        
        if (this.currentFile) {
            this.renderEntries();
            document.getElementById('addEntryBtn').style.display = 'flex';
            document.getElementById('currentFileHeader').style.display = 'flex';
            document.getElementById('currentFileName').textContent = this.currentFile.name;
            document.getElementById('emptyState').style.display = 'none';
        } else {
            document.getElementById('entriesContainer').innerHTML = '';
            document.getElementById('addEntryBtn').style.display = 'none';
            document.getElementById('currentFileHeader').style.display = 'none';
            
            if (this.data.files.length === 0) {
                document.getElementById('emptyState').style.display = 'block';
            } else {
                document.getElementById('emptyState').style.display = 'none';
            }
        }
    }

    renderFiles() {
        const container = document.getElementById('filesContainer');
        container.innerHTML = '';

        this.data.files.forEach(file => {
            const entryCount = this.data.entries.filter(e => e.file_id === file.id).length;
            const fileCard = document.createElement('div');
            fileCard.className = 'file-card';
            fileCard.style.borderTop = `4px solid ${file.color}`;
            fileCard.dataset.id = file.id;
            fileCard.innerHTML = `
                <div class="file-icon">${file.icon}</div>
                <div class="file-name">${file.name}</div>
                <div class="file-meta">
                    <span>${this.toArabicNumber(entryCount)} مدخلاً</span>
                    ${entryCount > 0 ? '<span class="file-badge">نشط</span>' : ''}
                </div>
            `;
            fileCard.addEventListener('click', () => this.openFile(file));
            container.appendChild(fileCard);
        });

        const addCard = document.createElement('div');
        addCard.className = 'file-card add-file-card';
        addCard.innerHTML = '<span>+</span><div style="font-size: 14px; font-weight: 600;">ملف جديد</div>';
        addCard.addEventListener('click', () => this.showFileModal());
        container.appendChild(addCard);
    }

    renderEntries() {
        const container = document.getElementById('entriesContainer');
        container.innerHTML = '';

        const fileEntries = this.data.entries
            .filter(e => e.file_id === this.currentFile.id)
            .sort((a, b) => new Date(b.created_at) - new Date(a.created_at));

        if (fileEntries.length === 0) {
            container.innerHTML = '<div class="empty-state"><p>📝 لا توجد مدخلات بعد<br>أضف أول مدخلة الآن!</p></div>';
            return;
        }

        fileEntries.forEach(entry => {
            const entryCard = document.createElement('div');
            entryCard.className = 'entry-card';
            entryCard.innerHTML = this.renderEntry(entry);
            
            const actions = document.createElement('div');
            actions.className = 'entry-actions';
            actions.innerHTML = `
                <button class="edit-entry" data-id="${entry.id}">✎</button>
                <button class="delete-entry" data-id="${entry.id}">🗑️</button>
            `;
            entryCard.querySelector('.entry-header').appendChild(actions);
            
            entryCard.querySelector('.edit-entry').addEventListener('click', (e) => {
                e.stopPropagation();
                this.editEntry(entry);
            });
            
            entryCard.querySelector('.delete-entry').addEventListener('click', (e) => {
                e.stopPropagation();
                this.deleteEntry(entry.id);
            });
            
            container.appendChild(entryCard);
        });
    }

    renderEntry(entry) {
        let elementsHtml = '';
        const timeStr = this.formatTime(entry.created_at);
        
        entry.elements.forEach(element => {
            switch(element.type) {
                case 'text':
                    elementsHtml += `<div class="element element-text">${element.content}</div>`;
                    break;
                case 'checklist':
                    let checklistHtml = '<div class="element-checklist">';
                    element.items.forEach(item => {
                        checklistHtml += `
                            <div class="checklist-item">
                                <input type="checkbox" ${item.checked ? 'checked' : ''} disabled>
                                <span>${item.text}</span>
                            </div>
                        `;
                    });
                    checklistHtml += '</div>';
                    elementsHtml += checklistHtml;
                    break;
                case 'highlight':
                    elementsHtml += `<div class="element element-highlight">⭐ ${element.content}</div>`;
                    break;
                case 'problem':
                    elementsHtml += `
                        <div class="element element-problem">
                            <strong>⚠️ مشكلة:</strong> ${element.problem}
                            ${element.solution ? `<div class="solution-text">✅ الحل: ${element.solution}</div>` : ''}
                        </div>
                    `;
                    break;
                case 'achievement':
                    elementsHtml += `<div class="element element-achievement"><span class="emoji">🏆</span> ${element.content}</div>`;
                    break;
            }
        });

        return `
            <div class="entry-header">
                <span class="entry-time">🕒 ${timeStr}</span>
                <span class="mood-badge">${entry.mood}</span>
            </div>
            ${elementsHtml}
        `;
    }

    formatTime(isoString) {
        const date = new Date(isoString);
        let hours = date.getHours();
        const minutes = date.getMinutes();
        const ampm = hours >= 12 ? 'مساءً' : 'صباحاً';
        hours = hours % 12;
        hours = hours ? hours : 12;
        const timeStr = `${hours}:${minutes.toString().padStart(2, '0')} ${ampm}`;
        return timeStr.replace(/\d/g, d => this.toArabicNumber(d));
    }

    openFile(file) {
        this.currentFile = file;
        this.render();
    }

    backToFiles() {
        this.currentFile = null;
        this.render();
    }

    showFileModal(file = null) {
        this.currentFileEdit = file;
        document.getElementById('fileModalTitle').textContent = file ? 'تعديل الملف' : 'ملف جديد';
        document.getElementById('fileName').value = file ? file.name : '';
        document.getElementById('fileIcon').value = file ? file.icon : '📁';
        this.selectedColor = file ? file.color : '#9d4edd';
        
        document.querySelectorAll('.color-option').forEach(opt => {
            opt.classList.remove('selected');
            if (opt.dataset.color === this.selectedColor) {
                opt.classList.add('selected');
            }
        });
        
        document.getElementById('fileModal').style.display = 'flex';
    }

    hideFileModal() {
        document.getElementById('fileModal').style.display = 'none';
    }

    async saveFile() {
        const name = document.getElementById('fileName').value.trim();
        if (!name) {
            alert('الرجاء إدخال اسم الملف');
            return;
        }

        const fileData = {
            user_id: this.user.id,
            name: name,
            icon: document.getElementById('fileIcon').value,
            color: this.selectedColor
        };

        try {
            if (this.currentFileEdit) {
                const response = await fetch(`/api/files/${this.currentFileEdit.id}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(fileData)
                });
                if (response.ok) {
                    await this.loadData();
                    if (this.currentFile && this.currentFile.id === this.currentFileEdit.id) {
                        this.currentFile = { ...this.currentFile, ...fileData };
                    }
                }
            } else {
                const response = await fetch('/api/files', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(fileData)
                });
                if (response.ok) {
                    await this.loadData();
                }
            }
            
            this.hideFileModal();
            this.render();
        } catch (error) {
            console.error('Error saving file:', error);
            alert('حدث خطأ في حفظ الملف');
        }
    }

    async deleteFile() {
        if (!this.currentFile) return;
        
        if (confirm(`هل أنت متأكد من حذف الملف "${this.currentFile.name}" وجميع مدخلاته؟`)) {
            try {
                const response = await fetch(`/api/files/${this.currentFile.id}`, {
                    method: 'DELETE'
                });
                if (response.ok) {
                    await this.loadData();
                    this.currentFile = null;
                    this.render();
                }
            } catch (error) {
                console.error('Error deleting file:', error);
                alert('حدث خطأ في حذف الملف');
            }
        }
    }

    showEntryModal(entry = null) {
        if (!this.currentFile) return;
        
        this.currentEntry = entry;
        this.selectedMood = entry ? entry.mood : '😊';
        document.getElementById('entryModalTitle').textContent = entry ? 'تعديل المدخلة' : 'مدخلة جديدة';
        
        document.querySelectorAll('.mood-option').forEach(opt => {
            opt.classList.remove('selected');
            if (opt.dataset.mood === this.selectedMood) {
                opt.classList.add('selected');
            }
        });

        const elementsContainer = document.getElementById('elementsContainer');
        elementsContainer.innerHTML = '';
        
        if (entry) {
            entry.elements.forEach(element => {
                this.addElementToEditor(element);
            });
        }

        document.getElementById('entryModal').style.display = 'flex';
    }

    hideEntryModal() {
        document.getElementById('entryModal').style.display = 'none';
        document.getElementById('elementsContainer').innerHTML = '';
    }

    addElementToEditor(element = null) {
        const container = document.getElementById('elementsContainer');
        
        const elementDiv = document.createElement('div');
        elementDiv.className = 'element-editor';
        
        const typeSelect = document.createElement('select');
        typeSelect.className = 'element-type-select';
        typeSelect.innerHTML = `
            <option value="text">📝 نص</option>
            <option value="checklist">✅ قائمة</option>
            <option value="highlight">⭐ مهم</option>
            <option value="problem">⚠️ مشكلة</option>
            <option value="achievement">🏆 إنجاز</option>
        `;
        
        if (element) {
            typeSelect.value = element.type;
        }

        const contentDiv = document.createElement('div');
        contentDiv.className = 'element-content-editor';
        
        const removeBtn = document.createElement('button');
        removeBtn.className = 'remove-element';
        removeBtn.innerHTML = '✕';
        removeBtn.onclick = () => elementDiv.remove();

        elementDiv.appendChild(typeSelect);
        elementDiv.appendChild(contentDiv);
        elementDiv.appendChild(removeBtn);

        const updateContentEditor = () => {
            const type = typeSelect.value;
            contentDiv.innerHTML = '';
            
            if (element && type === element.type) {
                switch(type) {
                    case 'text':
                    case 'highlight':
                    case 'achievement':
                        const textarea = document.createElement('textarea');
                        textarea.placeholder = 'اكتب المحتوى...';
                        textarea.value = element.content || '';
                        textarea.rows = 3;
                        contentDiv.appendChild(textarea);
                        break;
                        
                    case 'checklist':
                        const checklistDiv = document.createElement('div');
                        checklistDiv.className = 'checklist-editor';
                        
                        const items = element.items || [{ text: '', checked: false }];
                        items.forEach((item) => {
                            const itemDiv = document.createElement('div');
                            itemDiv.className = 'checklist-item-edit';
                            itemDiv.innerHTML = `
                                <input type="checkbox" ${item.checked ? 'checked' : ''}>
                                <input type="text" placeholder="عنصر القائمة" value="${item.text}">
                                <button class="remove-checklist-item">✕</button>
                            `;
                            itemDiv.querySelector('.remove-checklist-item').onclick = () => itemDiv.remove();
                            checklistDiv.appendChild(itemDiv);
                        });
                        
                        const addItemBtn = document.createElement('button');
                        addItemBtn.className = 'element-btn';
                        addItemBtn.textContent = '+ إضافة عنصر';
                        addItemBtn.onclick = () => {
                            const newItem = document.createElement('div');
                            newItem.className = 'checklist-item-edit';
                            newItem.innerHTML = `
                                <input type="checkbox">
                                <input type="text" placeholder="عنصر القائمة">
                                <button class="remove-checklist-item">✕</button>
                            `;
                            newItem.querySelector('.remove-checklist-item').onclick = () => newItem.remove();
                            checklistDiv.insertBefore(newItem, addItemBtn);
                        };
                        
                        contentDiv.appendChild(checklistDiv);
                        contentDiv.appendChild(addItemBtn);
                        break;
                        
                    case 'problem':
                        const problemDiv = document.createElement('div');
                        problemDiv.innerHTML = `
                            <textarea placeholder="المشكلة..." rows="2">${element.problem || ''}</textarea>
                            <textarea placeholder="الحل (اختياري)..." rows="2" style="margin-top: 8px;">${element.solution || ''}</textarea>
                        `;
                        contentDiv.appendChild(problemDiv);
                        break;
                }
            } else {
                switch(type) {
                    case 'text':
                    case 'highlight':
                    case 'achievement':
                        const textarea = document.createElement('textarea');
                        textarea.placeholder = 'اكتب المحتوى...';
                        textarea.rows = 3;
                        contentDiv.appendChild(textarea);
                        break;
                        
                    case 'checklist':
                        const checklistDiv = document.createElement('div');
                        checklistDiv.className = 'checklist-editor';
                        
                        const itemDiv = document.createElement('div');
                        itemDiv.className = 'checklist-item-edit';
                        itemDiv.innerHTML = `
                            <input type="checkbox">
                            <input type="text" placeholder="عنصر القائمة">
                            <button class="remove-checklist-item">✕</button>
                        `;
                        itemDiv.querySelector('.remove-checklist-item').onclick = () => itemDiv.remove();
                        checklistDiv.appendChild(itemDiv);
                        
                        const addItemBtn = document.createElement('button');
                        addItemBtn.className = 'element-btn';
                        addItemBtn.textContent = '+ إضافة عنصر';
                        addItemBtn.onclick = () => {
                            const newItem = document.createElement('div');
                            newItem.className = 'checklist-item-edit';
                            newItem.innerHTML = `
                                <input type="checkbox">
                                <input type="text" placeholder="عنصر القائمة">
                                <button class="remove-checklist-item">✕</button>
                            `;
                            newItem.querySelector('.remove-checklist-item').onclick = () => newItem.remove();
                            checklistDiv.insertBefore(newItem, addItemBtn);
                        };
                        
                        contentDiv.appendChild(checklistDiv);
                        contentDiv.appendChild(addItemBtn);
                        break;
                        
                    case 'problem':
                        const problemDiv = document.createElement('div');
                        problemDiv.innerHTML = `
                            <textarea placeholder="المشكلة..." rows="2"></textarea>
                            <textarea placeholder="الحل (اختياري)..." rows="2" style="margin-top: 8px;"></textarea>
                        `;
                        contentDiv.appendChild(problemDiv);
                        break;
                }
            }
        };

        typeSelect.addEventListener('change', updateContentEditor);
        updateContentEditor();

        container.appendChild(elementDiv);
    }

    collectElements() {
        const elements = [];
        const editors = document.querySelectorAll('.element-editor');
        
        editors.forEach(editor => {
            const type = editor.querySelector('.element-type-select').value;
            const contentEditor = editor.querySelector('.element-content-editor');
            
            switch(type) {
                case 'text':
                case 'highlight':
                case 'achievement':
                    const textarea = contentEditor.querySelector('textarea');
                    if (textarea && textarea.value.trim()) {
                        elements.push({
                            type: type,
                            content: textarea.value.trim()
                        });
                    }
                    break;
                    
                case 'checklist':
                    const items = [];
                    const checklistItems = contentEditor.querySelectorAll('.checklist-item-edit');
                    checklistItems.forEach(item => {
                        const checkbox = item.querySelector('input[type="checkbox"]');
                        const textInput = item.querySelector('input[type="text"]');
                        if (textInput.value.trim()) {
                            items.push({
                                text: textInput.value.trim(),
                                checked: checkbox.checked
                            });
                        }
                    });
                    if (items.length > 0) {
                        elements.push({
                            type: 'checklist',
                            items: items
                        });
                    }
                    break;
                    
                case 'problem':
                    const problemTextarea = contentEditor.querySelectorAll('textarea');
                    if (problemTextarea[0] && problemTextarea[0].value.trim()) {
                        elements.push({
                            type: 'problem',
                            problem: problemTextarea[0].value.trim(),
                            solution: problemTextarea[1] ? problemTextarea[1].value.trim() : ''
                        });
                    }
                    break;
            }
        });
        
        return elements;
    }

    async saveEntry() {
        if (!this.currentFile) return;
        
        const elements = this.collectElements();
        if (elements.length === 0) {
            alert('الرجاء إضافة عنصر واحد على الأقل');
            return;
        }

        const entryData = {
            user_id: this.user.id,
            file_id: this.currentFile.id,
            mood: this.selectedMood,
            elements: elements
        };

        try {
            if (this.currentEntry) {
                const response = await fetch(`/api/entries/${this.currentEntry.id}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(entryData)
                });
                if (response.ok) {
                    await this.loadData();
                }
            } else {
                const response = await fetch('/api/entries', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(entryData)
                });
                if (response.ok) {
                    await this.loadData();
                }
            }
            
            this.hideEntryModal();
            this.render();
        } catch (error) {
            console.error('Error saving entry:', error);
            alert('حدث خطأ في حفظ المدخلة');
        }
    }

    async deleteEntry(entryId) {
        if (confirm('هل أنت متأكد من حذف هذه المدخلة؟')) {
            try {
                const response = await fetch(`/api/entries/${entryId}`, {
                    method: 'DELETE'
                });
                if (response.ok) {
                    await this.loadData();
                    this.render();
                }
            } catch (error) {
                console.error('Error deleting entry:', error);
                alert('حدث خطأ في حذف المدخلة');
            }
        }
    }

    editEntry(entry) {
        this.showEntryModal(entry);
    }

    attachEvents() {
        document.getElementById('addFileBtn').addEventListener('click', () => this.showFileModal());
        document.getElementById('backToFiles').addEventListener('click', () => this.backToFiles());
        document.getElementById('editFileBtn').addEventListener('click', () => this.showFileModal(this.currentFile));
        document.getElementById('deleteFileBtn').addEventListener('click', () => this.deleteFile());

        document.getElementById('cancelFileModal').addEventListener('click', () => this.hideFileModal());
        document.getElementById('saveFileBtn').addEventListener('click', () => this.saveFile());

        document.querySelectorAll('.color-option').forEach(option => {
            option.addEventListener('click', (e) => {
                document.querySelectorAll('.color-option').forEach(opt => opt.classList.remove('selected'));
                option.classList.add('selected');
                this.selectedColor = option.dataset.color;
            });
        });

        document.getElementById('addEntryBtn').addEventListener('click', () => this.showEntryModal());
        document.getElementById('cancelEntryModal').addEventListener('click', () => this.hideEntryModal());
        document.getElementById('saveEntryBtn').addEventListener('click', () => this.saveEntry());

        document.querySelectorAll('.add-element-buttons .element-btn').forEach(btn => {
            btn.addEventListener('click', () => this.addElementToEditor());
        });

        document.querySelectorAll('.mood-option').forEach(option => {
            option.addEventListener('click', (e) => {
                document.querySelectorAll('.mood-option').forEach(opt => opt.classList.remove('selected'));
                option.classList.add('selected');
                this.selectedMood = option.dataset.mood;
            });
        });

        window.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal')) {
                this.hideFileModal();
                this.hideEntryModal();
            }
        });

        const profileBtn = document.createElement('button');
        profileBtn.className = 'profile-btn';
        profileBtn.innerHTML = '👤';
        profileBtn.style.position = 'absolute';
        profileBtn.style.top = '20px';
        profileBtn.style.left = '20px';
        profileBtn.style.width = '40px';
        profileBtn.style.height = '40px';
        profileBtn.style.borderRadius = '20px';
        profileBtn.style.background = 'rgba(157, 78, 221, 0.2)';
        profileBtn.style.border = '1px solid rgba(157, 78, 221, 0.3)';
        profileBtn.style.color = 'white';
        profileBtn.style.fontSize = '20px';
        profileBtn.style.cursor = 'pointer';
        profileBtn.style.zIndex = '100';
        profileBtn.onclick = () => window.location.href = '/profile';
        document.querySelector('.app').appendChild(profileBtn);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.app = new MindBoxApp();
});