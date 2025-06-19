import sys
from PyQt6.QtWidgets import QApplication
from src.ui.main_window import MainWindow
from src.config.settings import load_settings

def main():
    """애플리케이션 메인 진입점"""
    # 설정 로드
    settings = load_settings()
    
    # Qt 애플리케이션 생성
    app = QApplication(sys.argv)
    app.setApplicationName("Rec Chart OCR")
    
    # 메인 윈도우 생성 및 표시
    window = MainWindow(settings)
    window.show()
    
    # 애플리케이션 실행
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 