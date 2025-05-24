import sys
import time
import ctypes
import os
import validators  # ✅ Helps check if URL is valid
import requests
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QTabWidget, QPushButton, QListWidget, QLineEdit, QWidget, QSplashScreen
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile
from PyQt5.QtWebEngineCore import QWebEngineUrlScheme, QWebEngineUrlSchemeHandler, QWebEngineUrlRequestJob
from PyQt5.QtCore import QUrl, QByteArray
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import QTimer  # ✅ This fixes the missing QTimer error

# ✅ Function for logging errors to a file
def log_error(message):
    """Logs errors to error_log.txt."""
    with open("error_log.txt", "a") as log_file:
        log_file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - ERROR: {message}\n")

# ✅ Ensure Windows recognizes the app separately from Python
my_app_id = "com.bananabrowser.app"
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(my_app_id)

# ✅ Initialize QApplication BEFORE any widgets
app = QApplication(sys.argv)
app.setWindowIcon(QIcon("favicon.ico"))

# ✅ Load splash screen image correctly
splash_pix = QPixmap("logo.png").scaled(500, 500)
splash = QSplashScreen(splash_pix)
splash.show()

# ✅ Simulate loading time without freezing UI
time.sleep(2)

class CustomBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Banana Browser")
        self.setGeometry(100, 100, 1000, 700)
        self.setWindowIcon(QIcon("favicon.ico"))

        # ✅ Create URL Bar
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Enter a URL...")
        self.url_bar.returnPressed.connect(self.load_url)  # Load URL when Enter is pressed

        # ✅ Sidebar (Tab List)
        self.sidebar = QListWidget()
        self.sidebar.itemClicked.connect(self.switch_tab)

        # ✅ Add New Tab Button
        self.new_tab_button = QPushButton("New Tab")
        self.new_tab_button.clicked.connect(self.create_new_tab)

        # ✅ Theme Toggle Button
        self.theme_button = QPushButton("Toggle Dark Mode")
        self.theme_button.clicked.connect(self.toggle_theme)

        # ✅ Tab Widget (Multiple Tabs)
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)

        # ✅ Layout setup
        sidebar_layout = QVBoxLayout()
        sidebar_layout.addWidget(self.theme_button)
        sidebar_layout.addWidget(self.new_tab_button)
        sidebar_layout.addWidget(self.sidebar)

        browser_layout = QVBoxLayout()
        browser_layout.addWidget(self.url_bar)  # ✅ Add URL bar
        browser_layout.addWidget(self.tabs)

        main_layout = QHBoxLayout()
        main_layout.addLayout(sidebar_layout, 2)
        main_layout.addLayout(browser_layout, 8)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # ✅ Open Default Tab with `bna://games` Homepage
        self.create_new_tab("https://www.google.com")  # ✅ New tabs now start with your custom page
        self.light_mode = True
        splash.finish(self)

    def create_new_tab(self, url="https://www.google.com"):
        """Creates a new browser tab with custom homepage."""
        if not isinstance(url, str):  # ✅ Ensure URL is a valid string
            log_error(f"Invalid URL type received: {url}")
            url = "https://www.google.com"  # ✅ Default to built-in page

        new_browser = QWebEngineView()
        new_browser.setUrl(QUrl(url))  # ✅ Load `bna://games` instead of Google

        tab_index = self.tabs.addTab(new_browser, "Loading...")
        self.sidebar.addItem("Loading...")

        new_browser.loadFinished.connect(lambda: self.update_tab_name(new_browser, tab_index))
        new_browser.loadFinished.connect(lambda: self.apply_theme(new_browser))

        self.tabs.setCurrentIndex(tab_index)

        sidebar_layout = QVBoxLayout()  # ✅ Creates sidebar layout for buttons & history
        sidebar_layout.addWidget(self.theme_button)
        sidebar_layout.addWidget(self.new_tab_button)
        sidebar_layout.addWidget(self.sidebar)

        browser_layout = QVBoxLayout()  # ✅ Creates browser layout for URL bar & tabs
        browser_layout.addWidget(self.url_bar)
        browser_layout.addWidget(self.tabs)


        # ✅ Create History Panel (Right-Side List)
        self.history_panel = QListWidget()
        self.history_panel.setMaximumWidth(300)  # ✅ Set width for layout consistency

        # ✅ Define Main Layout First
        main_layout = QHBoxLayout()

        # ✅ Add Sidebar & Browser Layouts
        main_layout.addLayout(sidebar_layout, 2)
        main_layout.addLayout(browser_layout, 6)

        # ✅ Now Add History Panel (Fixing Undefined Issue)
        main_layout.addWidget(self.history_panel, 2)  # ✅ Right-side history panel

        # ✅ Set Main Layout for the Window
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def auto_complete_url(self, url):
        """Ensures valid URLs by intelligently checking if 'www.' is needed."""
        if not url.startswith(("http://", "https://")):  
            test_https = f"https://{url}"
            test_http = f"http://{url}"
            
            # ✅ Check if the URL works without 'www.'
            if self.url_works(test_https):
                url = test_https
            elif self.url_works(test_http):
                url = test_http
            else:
                # ✅ If neither works, try with 'www.'
                url = f"https://www.{url}" if self.url_works(f"https://www.{url}") else f"http://www.{url}"
        
        return url

    def update_tab_name(self, browser, index):
        QTimer.singleShot(500, lambda: self.tabs.setTabText(index, browser.page().title()))  # ✅ Directly update after delay

    def load_url(self):
        """Loads corrected URL into the active tab and logs history."""
        url = self.url_bar.text()
        corrected_url = self.auto_complete_url(url)

        if url:
            try:
                self.tabs.currentWidget().setUrl(QUrl(corrected_url))
                self.url_bar.setText(corrected_url)
                self.history_panel.addItem(corrected_url)  # ✅ Adds URL to history panel

                # ✅ Log history to a file immediately upon navigation
                with open("history.txt", "a") as log_file:
                    log_file.write(corrected_url + "\n")
            except Exception as e:
                log_error(f"Failed to load URL: {corrected_url} - {e}")


    # ✅ Save History When Closing the Browser
    def closeEvent(self, event):
        """Logs session history into a file when closing."""
        with open("browser_history.txt", "a") as log_file:
            for index in range(self.history_panel.count()):
                log_file.write(self.history_panel.item(index).text() + "\n")


    def close_tab(self, index):
        """Closes the selected tab."""
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)
            if index < self.sidebar.count():
                self.sidebar.takeItem(index)

    def switch_tab(self, item):
        """Switches to the selected tab from the sidebar."""
        tab_index = self.sidebar.row(item)
        self.tabs.setCurrentIndex(tab_index)

    def toggle_theme(self):
        """Switches between light and dark mode."""
        self.light_mode = not self.light_mode  # ✅ Toggles mode each time button is clicked

        if self.light_mode:
            light_style = """
                QMainWindow { background-color: white; color: black; }
                QTabWidget::pane { background: #F5F5F5; }
                QPushButton { background-color: #DDD; color: black; border-radius: 5px; }
                QListWidget { background-color: white; color: black; }
            """
            self.setStyleSheet(light_style)
            self.theme_button.setText("Toggle Dark Mode")
        else:
            dark_style = """
                QMainWindow { background-color: #2E2E2E; color: white; }
                QTabWidget::pane { background: #3E3E3E; }
                QPushButton { background-color: #555; color: white; border-radius: 5px; }
                QListWidget { background-color: #3E3E3E; color: white; }
            """
            self.setStyleSheet(dark_style)
            self.theme_button.setText("Toggle Light Mode")

    def apply_theme(self, browser):
        if self.light_mode:
            browser.setStyleSheet("background-color: white; color: black;")
        else:
            browser.setStyleSheet("background-color: #2E2E2E; color: white;")

            for index in range(self.tabs.count()):
                self.apply_theme(self.tabs.widget(index))

# ✅ Launch the browser
window = CustomBrowser()
window.show()

# ✅ Ensure the application runs without crashing
sys.exit(app.exec_())
