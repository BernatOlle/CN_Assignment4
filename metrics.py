#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk

class MetricasVN:
    """
    Clase para calcular y visualizar métricas de asignación de redes virtuales.
    """
    
    def __init__(self, processor=None):
        """
        Inicializa el analizador de métricas.
        
        Args:
            processor: Instancia de NetworkProcessor para analizar
        """
        self.processor = processor
        self.metrics_history = {
            'acceptance_ratio': [],
            'bandwidth_utilization': [],
            'node_utilization': []
        }
    
    def set_processor(self, processor):
        """
        Establece el procesador de redes a analizar.
        
        Args:
            processor: Instancia de NetworkProcessor
        """
        self.processor = processor
    
    def calculate_bandwidth_utilization(self):
        """
        Calcula el porcentaje de utilización del ancho de banda disponible.
        
        Returns:
            float: Porcentaje de utilización del ancho de banda
        """
        if self.processor is None or self.processor.original_substrate is None:
            return 0.0
        
        total_bandwidth = np.sum(self.processor.original_substrate)
        used_bandwidth = total_bandwidth - np.sum(self.processor.substrate_network)
        
        if total_bandwidth == 0:
            return 0.0
            
        return (used_bandwidth / total_bandwidth) * 100
    
    def calculate_node_utilization(self):
        """
        Calcula el porcentaje de utilización de nodos.
        
        Returns:
            float: Porcentaje de nodos del sustrato utilizados
        """
        if self.processor is None or self.processor.allocations is None:
            return 0.0
            
        total_nodes = self.processor.substrate_network.shape[0]
        
        # Obtener todos los nodos utilizados (aplanando la lista de asignaciones)
        used_nodes = set()
        for demand_id, allocation in self.processor.allocations.items():
            for node in allocation:
                used_nodes.add(node)
        
        if total_nodes == 0:
            return 0.0
            
        return (len(used_nodes) / total_nodes) * 100
    
    def update_metrics(self):
        """
        Actualiza las métricas calculadas.
        
        Returns:
            dict: Diccionario con las métricas actualizadas
        """
        if self.processor is None:
            return {}
            
        # Calcular métricas actuales
        acceptance_ratio = self.processor.get_acceptance_ratio() * 100
        bandwidth_util = self.calculate_bandwidth_utilization()
        node_util = self.calculate_node_utilization()
        
        # Actualizar historial
        self.metrics_history['acceptance_ratio'].append(acceptance_ratio)
        self.metrics_history['bandwidth_utilization'].append(bandwidth_util)
        self.metrics_history['node_utilization'].append(node_util)
        
        return {
            'acceptance_ratio': acceptance_ratio,
            'bandwidth_utilization': bandwidth_util,
            'node_utilization': node_util
        }
    
    def get_metrics_summary(self):
        """
        Obtiene un resumen de las métricas actuales.
        
        Returns:
            str: Resumen de métricas en formato de texto
        """
        metrics = self.update_metrics()
        
        summary = (
            f"Ratio de Aceptación: {metrics['acceptance_ratio']:.2f}%\n"
            f"Utilización de Ancho de Banda: {metrics['bandwidth_utilization']:.2f}%\n"
            f"Utilización de Nodos: {metrics['node_utilization']:.2f}%\n"
        )
        
        # Información adicional sobre demandas
        if self.processor:
            total_demands = len(self.processor.demands)
            accepted = len(self.processor.accepted_demands)
            rejected = len(self.processor.rejected_demands)
            
            summary += (
                f"\nDemandas Totales: {total_demands}\n"
                f"Demandas Aceptadas: {accepted}\n"
                f"Demandas Rechazadas: {rejected}\n"
            )
            
        return summary
    
    def plot_metrics(self, figure=None):
        """
        Genera gráficos de las métricas.
        
        Args:
            figure: Figura de matplotlib para dibujar (opcional)
            
        Returns:
            Figure: Figura con los gráficos de métricas
        """
        if figure is None:
            figure = plt.figure(figsize=(10, 8))
            
        # Convertir listas a arrays para facilitar operaciones
        iterations = np.arange(1, len(self.metrics_history['acceptance_ratio']) + 1)
        acc_ratio = np.array(self.metrics_history['acceptance_ratio'])
        bw_util = np.array(self.metrics_history['bandwidth_utilization'])
        node_util = np.array(self.metrics_history['node_utilization'])
        
        # Crear subplots
        ax1 = figure.add_subplot(211)
        ax1.plot(iterations, acc_ratio, 'b-', marker='o', label='Ratio de Aceptación (%)')
        ax1.set_title('Rendimiento de Asignación VN')
        ax1.set_ylabel('Porcentaje (%)')
        ax1.set_xlabel('Iteración')
        ax1.legend(loc='upper left')
        ax1.grid(True)
        
        ax2 = figure.add_subplot(212)
        ax2.plot(iterations, bw_util, 'r-', marker='s', label='Utilización de Ancho de Banda (%)')
        ax2.plot(iterations, node_util, 'g-', marker='^', label='Utilización de Nodos (%)')
        ax2.set_ylabel('Porcentaje (%)')
        ax2.set_xlabel('Iteración')
        ax2.legend(loc='upper left')
        ax2.grid(True)
        
        figure.tight_layout()
        return figure
    
    def create_metrics_widget(self, parent):
        """
        Crea un widget para mostrar métricas en una interfaz Tkinter.
        
        Args:
            parent: Widget padre de Tkinter
            
        Returns:
            tuple: (frame, actualizar_funcion)
        """
        frame = tk.Frame(parent)
        
        # Texto para métricas
        metrics_label = tk.Label(frame, text="Métricas de Rendimiento:", font=('Arial', 12, 'bold'))
        metrics_label.pack(pady=(10, 5), anchor='w')
        
        metrics_text = tk.Text(frame, height=10, width=50, font=('Courier', 10))
        metrics_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        metrics_text.insert(tk.END, "No hay métricas disponibles aún")
        
        # Gráfico para métricas
        fig = Figure(figsize=(6, 6))
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        def update_metrics_display():
            # Actualizar texto
            metrics_summary = self.get_metrics_summary()
            metrics_text.delete(1.0, tk.END)
            metrics_text.insert(tk.END, metrics_summary)
            
            # Actualizar gráfico
            fig.clear()
            self.plot_metrics(fig)
            canvas.draw()
        
        return frame, update_metrics_display