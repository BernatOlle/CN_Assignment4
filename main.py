#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
from process_demand import NetworkProcessor

def main():
    """
    Función principal que implementa el ejemplo de validación proporcionado.
    """
    # Crear instancia del procesador de redes
    processor = NetworkProcessor()
    
    # Definir la red sustrato usando matriz de adyacencia
    # Los valores representan el ancho de banda disponible en Mbps
    # 0 indica que no hay conexión entre nodos
    substrate_network = np.array([
        # 1    2    3    4    5
        [  0,  12,   0,   0,   0 ],  # Nodo 1
        [  0,   0,  10,   7,   0 ],  # Nodo 2
        [  0,   0,   0,   0,   8 ],  # Nodo 3
        [  0,   0,   0,   0,   6 ],  # Nodo 4
        [  0,   0,   0,   0,   0 ]   # Nodo 5
    ])
    
    # Establecer la red sustrato
    processor.set_substrate_network(substrate_network)
    
    # Añadir demandas según el ejemplo
    # Demanda #1: Camino de 4 nodos con requerimientos de ancho de banda [8, 8, 5]
    processor.add_demand(
        demand_id=1,
        demand_path=[1, 2, 3, 4],  # 4 nodos virtuales
        bandwidth_requirements=[8, 8, 5]  # Ancho de banda entre los nodos
    )
    
    # Demanda #2: Camino de 4 nodos con requerimientos de ancho de banda [4, 6, 2]
    processor.add_demand(
        demand_id=2,
        demand_path=[1, 2, 3, 4],  # 4 nodos virtuales
        bandwidth_requirements=[4, 6, 2]  # Ancho de banda entre los nodos
    )
    
    # Procesar todas las demandas
    acceptance_ratio = processor.process_all_demands()
    
    # Mostrar resultados de asignación
    processor.print_allocation_results()
    
    print(f"\nResumen final: Ratio de aceptación = {acceptance_ratio:.2f}")

if __name__ == "__main__":
    main()