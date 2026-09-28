import tkinter as tk
from tkinter import ttk, messagebox
import math
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

class RectificationCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Расчет эффективности ректификационных тарелок")
        self.root.geometry("655x700")
        
        # Создаем основную структуру
        self.create_widgets()
        
    def create_widgets(self):
        # Основной фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Заголовок
        title_label = ttk.Label(main_frame, 
                               text="Расчет эффективности решетчатых тарелок провального типа",
                               font=("Arial", 14, "bold"))
        title_label.grid(row=0, column=0, columnspan=4, pady=(0, 20))
        
        # Фрейм для входных параметров
        input_frame = ttk.LabelFrame(main_frame, text="Входные параметры", padding="10")
        input_frame.grid(row=1, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Параметры для верхней секции
        ttk.Label(input_frame, text="Верхняя секция (укрепляющая):").grid(row=0, column=0, columnspan=4, sticky=tk.W, pady=(0, 10))
        
        self.create_input_fields(input_frame, "в", 1)
        
        # Параметры для нижней секции
        ttk.Label(input_frame, text="Нижняя секция (исчерпывающая):").grid(row=6, column=0, columnspan=4, sticky=tk.W, pady=(20, 10))
        
        self.create_input_fields(input_frame, "н", 7)
        
        # Кнопки расчета
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=4, pady=10)
        
        ttk.Button(button_frame, text="Рассчитать", command=self.calculate).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Очистить", command=self.clear_fields).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Построить график", command=self.plot_results).pack(side=tk.LEFT, padx=5)
        
        # Фрейм для результатов
        results_frame = ttk.LabelFrame(main_frame, text="Результаты расчета", padding="10")
        results_frame.grid(row=3, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Создаем таблицу для результатов
        self.create_results_table(results_frame)
        
    def create_input_fields(self, parent, suffix, start_row):
        """Создает поля ввода для указанной секции"""
        # Рабочая скорость пара
        ttk.Label(parent, text=f"w_p,{suffix} (м/с):").grid(row=start_row, column=0, sticky=tk.W, padx=(0, 5))
        self.vars[f"w_p_{suffix}"] = tk.DoubleVar(value=1.0)
        ttk.Entry(parent, textvariable=self.vars[f"w_p_{suffix}"], width=10).grid(row=start_row, column=1, padx=(0, 10))
        
        # Высота газо-жидкостного слоя
        ttk.Label(parent, text=f"h_г-ж,{suffix} (м):").grid(row=start_row, column=2, sticky=tk.W, padx=(0, 5))
        self.vars[f"h_gj_{suffix}"] = tk.DoubleVar(value=0.12)
        ttk.Entry(parent, textvariable=self.vars[f"h_gj_{suffix}"], width=10).grid(row=start_row, column=3, padx=(0, 10))
        
        # Коэффициент диффузии в паре
        ttk.Label(parent, text=f"D_y,{suffix} (м²/с):").grid(row=start_row+1, column=0, sticky=tk.W, padx=(0, 5))
        self.vars[f"D_y_{suffix}"] = tk.DoubleVar(value=6.7e-6)
        ttk.Entry(parent, textvariable=self.vars[f"D_y_{suffix}"], width=10).grid(row=start_row+1, column=1, padx=(0, 10))
        
        # Приведенная плотность орошения
        ttk.Label(parent, text=f"U_{suffix} (м³/м²·с):").grid(row=start_row+1, column=2, sticky=tk.W, padx=(0, 5))
        self.vars[f"U_{suffix}"] = tk.DoubleVar(value=0.001)
        ttk.Entry(parent, textvariable=self.vars[f"U_{suffix}"], width=10).grid(row=start_row+1, column=3, padx=(0, 10))
        
        # Коэффициент диффузии в жидкости
        ttk.Label(parent, text=f"D_x,{suffix} (м²/с):").grid(row=start_row+2, column=0, sticky=tk.W, padx=(0, 5))
        self.vars[f"D_x_{suffix}"] = tk.DoubleVar(value=4.4e-9)
        ttk.Entry(parent, textvariable=self.vars[f"D_x_{suffix}"], width=10).grid(row=start_row+2, column=1, padx=(0, 10))
        
        # Тангенс угла наклона рабочей линии
        ttk.Label(parent, text=f"l_{suffix}:").grid(row=start_row+2, column=2, sticky=tk.W, padx=(0, 5))
        self.vars[f"l_{suffix}"] = tk.DoubleVar(value=0.436 if suffix == "в" else 1.941)
        ttk.Entry(parent, textvariable=self.vars[f"l_{suffix}"], width=10).grid(row=start_row+2, column=3, padx=(0, 10))
        
        # Тангенс угла наклона равновесной линии
        ttk.Label(parent, text=f"m_{suffix}:").grid(row=start_row+3, column=0, sticky=tk.W, padx=(0, 5))
        self.vars[f"m_{suffix}"] = tk.DoubleVar(value=0.5 if suffix == "в" else 0.96)
        ttk.Entry(parent, textvariable=self.vars[f"m_{suffix}"], width=10).grid(row=start_row+3, column=1, padx=(0, 10))
    
    def create_results_table(self, parent):
        """Создает таблицу для отображения результатов"""
        # Заголовки столбцов
        headers = ["Параметр", "Верхняя секция", "Нижняя секция", "Единицы измерения"]
        
        for i, header in enumerate(headers):
            ttk.Label(parent, text=header, font=("Arial", 10, "bold")).grid(row=0, column=i, padx=5, pady=5)
        
        # Параметры для отображения
        parameters = [
            ("Число Пекле (пар)", "Pe_y", ""),
            ("Число Пекле (жидкость)", "Pe_x", ""),
            ("Коэф. массоотдачи (пар)", "beta_yf", "м/с"),
            ("Коэф. массоотдачи (жидкость)", "beta_xf", "м/с"),
            ("Число единиц переноса (пар)", "n_y", ""),
            ("Число единиц переноса (жидкость)", "n_x", ""),
            ("Общее число единиц переноса", "n_0y", ""),
            ("Эффективность тарелки", "E_0", "")
        ]
        
        self.result_labels = {}
        
        for i, (name, key, unit) in enumerate(parameters):
            ttk.Label(parent, text=name).grid(row=i+1, column=0, sticky=tk.W, padx=5)
            
            for j, suffix in enumerate(["в", "н"], 1):
                label = ttk.Label(parent, text="-", background="white", relief="solid", width=15)
                label.grid(row=i+1, column=j, padx=5, pady=2)
                self.result_labels[f"{key}_{suffix}"] = label
            
            ttk.Label(parent, text=unit).grid(row=i+1, column=3, padx=5)
    
    def calculate_pe(self, w_p, h_gj, D, phase='y'):
        """Расчет числа Пекле (формулы 7 и 9)"""
        try:
            return (w_p * h_gj) / D
        except ZeroDivisionError:
            messagebox.showerror("Ошибка", f"Коэффициент диффузии D_{phase} не может быть равен нулю")
            return 0
    
    def calculate_beta_yf(self, Pe_y, h_gj, w_p):
        """Расчет коэффициента массоотдачи по паровой фазе (формула 6)"""
        return 1.77e3 * (Pe_y ** -0.5) * (h_gj ** 1.2) * w_p
    
    def calculate_beta_xf(self, Pe_x, U, h_gj):
        """Расчет коэффициента массоотдачи по жидкой фазе (формула 8)"""
        return 1.26e5 * (Pe_x ** -0.5) * U * (h_gj ** 1.9)
    
    def calculate_n_y(self, beta_yf, w_p):
        """Расчет числа единиц переноса по паровой фазе (формула 4)"""
        try:
            return beta_yf / w_p
        except ZeroDivisionError:
            return 0
    
    def calculate_n_x(self, beta_xf, U):
        """Расчет числа единиц переноса по жидкой фазе (формула 5)"""
        try:
            return beta_xf / U
        except ZeroDivisionError:
            return 0
    
    def calculate_n_0y(self, n_y, n_x, m, l):
        """Расчет общего числа единиц переноса (формула 2)"""
        try:
            denominator = l * n_x + m * n_y
            if denominator == 0:
                return 0
            return (n_x * n_y * l) / denominator
        except ZeroDivisionError:
            return 0
    
    def calculate_E_0(self, n_0y):
        """Расчет эффективности тарелки (формула 1)"""
        return 1 - math.exp(-n_0y)
    
    def calculate(self):
        """Основная функция расчета"""
        try:
            results = {}
            
            for suffix in ["в", "н"]:
                # Получаем значения из полей ввода
                w_p = self.vars[f"w_p_{suffix}"].get()
                h_gj = self.vars[f"h_gj_{suffix}"].get()
                D_y = self.vars[f"D_y_{suffix}"].get()
                U = self.vars[f"U_{suffix}"].get()
                D_x = self.vars[f"D_x_{suffix}"].get()
                l = self.vars[f"l_{suffix}"].get()
                m = self.vars[f"m_{suffix}"].get()
                
                # Выполняем расчеты по формулам
                Pe_y = self.calculate_pe(w_p, h_gj, D_y, 'y')
                Pe_x = self.calculate_pe(U, h_gj, D_x, 'x')
                
                beta_yf = self.calculate_beta_yf(Pe_y, h_gj, w_p)
                beta_xf = self.calculate_beta_xf(Pe_x, U, h_gj)
                
                n_y = self.calculate_n_y(beta_yf, w_p)
                n_x = self.calculate_n_x(beta_xf, U)
                
                n_0y = self.calculate_n_0y(n_y, n_x, m, l)
                E_0 = self.calculate_E_0(n_0y)
                
                # Сохраняем результаты
                results.update({
                    f"Pe_y_{suffix}": Pe_y,
                    f"Pe_x_{suffix}": Pe_x,
                    f"beta_yf_{suffix}": beta_yf,
                    f"beta_xf_{suffix}": beta_xf,
                    f"n_y_{suffix}": n_y,
                    f"n_x_{suffix}": n_x,
                    f"n_0y_{suffix}": n_0y,
                    f"E_0_{suffix}": E_0
                })
            
            # Обновляем интерфейс с результатами
            self.update_results(results)
            
        except Exception as e:
            messagebox.showerror("Ошибка расчета", f"Произошла ошибка при расчете: {str(e)}")
    
    def update_results(self, results):
        """Обновляет таблицу с результатами"""
        for key, value in results.items():
            if key in self.result_labels:
                if isinstance(value, float):
                    display_value = f"{value:.4f}"
                else:
                    display_value = str(value)
                self.result_labels[key].config(text=display_value)
    
    def clear_fields(self):
        """Очищает все поля ввода и результаты"""
        for var in self.vars.values():
            if isinstance(var, tk.DoubleVar):
                var.set(0.0)
        
        for label in self.result_labels.values():
            label.config(text="-")
    
    def plot_results(self):
        """Строит график эффективности тарелок"""
        try:
            # Получаем значения эффективности
            E_0_v = self.result_labels["E_0_в"].cget("text")
            E_0_n = self.result_labels["E_0_н"].cget("text")
            
            if E_0_v == "-" or E_0_n == "-":
                messagebox.showwarning("Предупреждение", "Сначала выполните расчет")
                return
            
            E_0_v = float(E_0_v)
            E_0_n = float(E_0_n)
            
            # Создаем график
            fig, ax = plt.subplots(figsize=(8, 6))
            
            sections = ['Верхняя\n(укрепляющая)', 'Нижняя\n(исчерпывающая)']
            efficiencies = [E_0_v * 100, E_0_n * 100]  # в процентах
            
            bars = ax.bar(sections, efficiencies, color=['skyblue', 'lightcoral'], alpha=0.7)
            
            # Добавляем подписи значений
            for bar, efficiency in zip(bars, efficiencies):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                       f'{efficiency:.1f}%', ha='center', va='bottom', fontsize=12)
            
            ax.set_ylabel('Эффективность тарелки, %', fontsize=12)
            ax.set_title('Эффективность ректификационных тарелок\nпо секциям колонны', fontsize=14, fontweight='bold')
            ax.set_ylim(0, 100)
            ax.grid(True, alpha=0.3, axis='y')
            
            plt.tight_layout()
            
            # Показываем график в отдельном окне
            plt.show()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось построить график: {str(e)}")
    
    @property
    def vars(self):
        if not hasattr(self, '_vars'):
            self._vars = {}
        return self._vars

def main():
    root = tk.Tk()
    app = RectificationCalculator(root)
    root.mainloop()

if __name__ == "__main__":
    main()