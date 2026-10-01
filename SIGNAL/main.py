"""
main.py — Точка входа проекта SIGNAL.
Запуск оконного приложения и отображение графического канваса.
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from chart_canvas import ChartCanvas


def main():
    # 1. Запуск оконного движка Qt (выделение памяти, системные очереди мыши)
    app = QApplication(sys.argv)

    # 2. Создаем главное окно приложения
    win = QMainWindow()
    win.setWindowTitle("SIGNAL — Visualizer & Indicator Lab")
    win.resize(1200, 800)  # Стартовый размер окна в пикселях (ширина, высота)

    # 3. Вставляем наш двухпанельный холст в центр окна
    canvas = ChartCanvas()
    win.setCentralWidget(canvas)

    # 4. Показываем окно на экране
    win.show()

    # 5. Запускаем бесконечный цикл ожидания событий (клики, зум, закрытие окна)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
