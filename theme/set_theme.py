        # Theme dropdown
        self.theme_combo = QComboBox()
        self.populate_themes()
        self.theme_combo.currentIndexChanged.connect(self.apply_theme)



def populate_themes(self)
        theme_dir = QDir(theme)
        if not theme_dir.exists()
            print(مجلد الثيمات غير موجود)
            return

        theme_files = theme_dir.entryList([.qss])
        if not theme_files
            print(لا توجد ملفات ثيمات في المجلد)
            return

        for theme_file in theme_files
            self.theme_combo.addItem(theme_file)

    def apply_theme(self)
        selected_theme = self.theme_combo.currentText()
        theme_path = QDir(theme).filePath(selected_theme)
        if not QFile.exists(theme_path)
            print(الملف غير موجود, theme_path)
            return

        try
            with open(theme_path, 'r') as theme_file
                stylesheet = theme_file.read()
                self.setStyleSheet(stylesheet)
        except Exception as e
            print(حدث خطأ أثناء قراءة الملف, e)


