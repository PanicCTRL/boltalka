"""
chart_canvas.py — Графический холст проекта SIGNAL
Двухпанельный график на базе PyQt6 и pyqtgraph:
- Верхняя панель (plot_candles): свечи, регрессионные каналы, уровни.
- Нижняя панель (plot_macd): индикатор MACD, волны гистограммы, нулевая линия.
- Оси X панелей синхронизированы (setXLink).
"""

import pyqtgraph as pg
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPen

# Глобальные настройки pyqtgraph: тёмная палитра и сглаживание
pg.setConfigOption('background', '#111111')   # Глубокий тёмно-серый фон графика
pg.setConfigOption('foreground', '#d1d4dc')   # Светло-серый цвет осей и текста шкалы
pg.setConfigOptions(antialias=True)          # Сглаживание тонких линий


class ChartCanvas(pg.GraphicsLayoutWidget):
    """
    Класс холста с двумя синхронизированными графиками.
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        # 1. Настройка сетки холста (Layout)
        # Строка 0 (свечи) получает 70% высоты, строка 1 (MACD) — 30%
        self.ci.layout.setRowStretchFactor(0, 7)
        self.ci.layout.setRowStretchFactor(1, 3)
        self.ci.layout.setSpacing(2)  # Минимальный зазор между графиками в пикселях

        # 2. Верхняя панель: График цены и трендов
        self.plot_candles = self.addPlot(row=0, col=0)
        self.plot_candles.showGrid(x=True, y=True, alpha=0.15)  # Сетка графика
        self.plot_candles.setClipToView(True)                   # Оптимизация: рендерить только то, что в кадре
        self.plot_candles.getAxis('left').setWidth(70)          # Фиксированная ширина ценовой шкалы
        self.plot_candles.hideAxis('bottom')                    # Скрываем нижнюю ось времени у свечей

        # 3. Нижняя панель: Осциллятор MACD
        self.plot_macd = self.addPlot(row=1, col=0)
        self.plot_macd.showGrid(x=True, y=True, alpha=0.15)     # Сетка индикатора
        self.plot_macd.setClipToView(True)
        self.plot_macd.getAxis('left').setWidth(70)             # Выравниваем шкалу строго под шкалой свечей

        # 4. Намертво сцепляем ось времени X нижнего графика с верхним
        self.plot_macd.setXLink(self.plot_candles)

        # 5. Нулевая линия на графике MACD (уровень раздела холмов и впадин)
        zero_pen = pg.mkPen(color='#555555', width=1, style=Qt.PenStyle.DashLine)
        self.macd_zero_line = pg.InfiniteLine(pos=0.0, angle=0, pen=zero_pen)
        self.plot_macd.addItem(self.macd_zero_line)

    def clear_plots(self):
        """Очистить оба графика перед повторным расчетом или загрузкой нового дня."""
        self.plot_candles.clear()
        self.plot_macd.clear()
        self.plot_macd.addItem(self.macd_zero_line)  # Возвращаем нулевую линию обратно
