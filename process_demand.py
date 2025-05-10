#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
from itertools import permutations

class NetworkProcessor:
    """
    Clase para procesar demandas de redes virtuales (VN) sobre una red sustrato.
    Implementa una estrategia de asignación para maximizar el ratio de aceptación.
    """
    
    def __init__(self):
        """
        Inicializa el procesador de redes.
        """
        self.substrate_network = None
        self.demands = []
        self.accepted_demands = []
        self.rejected_demands = []
        self.allocations = {}
    
    def set_substrate_network(self, adjacency_matrix):
        """
        Establece la red sustrato mediante una matriz de adyacencia.
        Los valores representan el ancho de banda disponible en Mbps.
        
        Args:
            adjacency_matrix (numpy.ndarray): Matriz de adyacencia de la red sustrato
        """
        self.substrate_network = adjacency_matrix.copy()
        self.original_substrate = adjacency_matrix.copy()
    
    def add_demand(self, demand_id, demand_path, bandwidth_requirements):
        """
        Añade una demanda de red virtual para ser procesada.
        
        Args:
            demand_id (int): Identificador de la demanda
            demand_path (list): Lista de nodos en el camino de la demanda
            bandwidth_requirements (list): Lista de requisitos de ancho de banda entre nodos
        """
        self.demands.append({
            'id': demand_id,
            'path': demand_path,
            'bandwidth': bandwidth_requirements
        })
    
    def reset(self):
        """
        Resetea el estado del procesador de redes.
        """
        self.demands = []
        self.accepted_demands = []
        self.rejected_demands = []
        self.allocations = {}
        if self.original_substrate is not None:
            self.substrate_network = self.original_substrate.copy()
    
    def find_all_possible_allocations(self, demand):
        """
        Encuentra todas las posibles asignaciones para una demanda en la red sustrato.
        
        Args:
            demand (dict): Demanda a procesar
            
        Returns:
            list: Lista de posibles asignaciones (mapeos de nodos)
        """
        demand_nodes = len(demand['path'])
        substrate_nodes = self.substrate_network.shape[0]
        
        # Generamos todas las permutaciones posibles de nodos sustrato
        all_mappings = []
        for perm in permutations(range(1, substrate_nodes + 1), demand_nodes):
            all_mappings.append(list(perm))
        
        # Filtramos las asignaciones que cumplen con los requisitos de ancho de banda
        valid_mappings = []
        for mapping in all_mappings:
            valid = True
            
            # Verificar si cada enlace en la demanda puede ser asignado a un
            # camino en la red sustrato con suficiente ancho de banda
            for i in range(len(demand['path']) - 1):
                src_node = mapping[i] - 1  # Ajustamos índice (0-based)
                dst_node = mapping[i + 1] - 1  # Ajustamos índice (0-based)
                
                required_bandwidth = demand['bandwidth'][i]
                
                # Verificar si hay conexión directa con suficiente ancho de banda
                if self.substrate_network[src_node, dst_node] < required_bandwidth:
                    valid = False
                    break
            
            if valid:
                valid_mappings.append(mapping)
        
        return valid_mappings
    
    def allocate_demand(self, demand, mapping):
        """
        Asigna una demanda a la red sustrato según el mapeo dado.
        
        Args:
            demand (dict): Demanda a asignar
            mapping (list): Mapeo de nodos para la asignación
            
        Returns:
            bool: True si la asignación fue exitosa, False si no
        """
        # Verificar si hay suficiente ancho de banda disponible
        for i in range(len(demand['path']) - 1):
            src_node = mapping[i] - 1  # Ajustamos índice (0-based)
            dst_node = mapping[i + 1] - 1  # Ajustamos índice (0-based)
            
            required_bandwidth = demand['bandwidth'][i]
            
            if self.substrate_network[src_node, dst_node] < required_bandwidth:
                return False
        
        # Asignar recursos en la red sustrato
        for i in range(len(demand['path']) - 1):
            src_node = mapping[i] - 1  # Ajustamos índice (0-based)
            dst_node = mapping[i + 1] - 1  # Ajustamos índice (0-based)
            
            required_bandwidth = demand['bandwidth'][i]
            
            self.substrate_network[src_node, dst_node] -= required_bandwidth
        
        # Guardar la asignación
        self.allocations[demand['id']] = mapping
        
        return True
    
    def process_all_demands(self):
        """
        Procesa todas las demandas utilizando la estrategia de maximizar
        el ratio de aceptación.
        
        Returns:
            float: Ratio de aceptación (demandas aceptadas / total de demandas)
        """
        # Ordenamos las demandas según la estrategia para maximizar el ratio de aceptación
        # Primero las que requieren menos ancho de banda total
        self.demands.sort(key=lambda d: sum(d['bandwidth']))
        
        for demand in self.demands:
            print(f"\nProcesando demanda #{demand['id']}")
            
            # Encontrar todas las posibles asignaciones
            possible_allocations = self.find_all_possible_allocations(demand)
            
            print(f"Posibles asignaciones para demanda #{demand['id']}:")
            if possible_allocations:
                for i, allocation in enumerate(possible_allocations):
                    print(f"  Opción {i+1}: Mapeo de nodos virtuales a nodos sustrato: {allocation}")
            else:
                print("  No hay asignaciones posibles que cumplan los requisitos")
            
            # Intentar asignar la demanda
            if possible_allocations:
                # Seleccionamos la primera asignación válida (ya están ordenadas)
                allocation = possible_allocations[0]
                if self.allocate_demand(demand, allocation):
                    self.accepted_demands.append(demand)
                    print(f"  ✓ Demanda #{demand['id']} ACEPTADA con asignación: {allocation}")
                else:
                    self.rejected_demands.append(demand)
                    print(f"  ✗ Demanda #{demand['id']} RECHAZADA - No hay suficientes recursos disponibles")
            else:
                self.rejected_demands.append(demand)
                print(f"  ✗ Demanda #{demand['id']} RECHAZADA - No hay asignaciones posibles")
        
        return self.get_acceptance_ratio()
    
    def get_acceptance_ratio(self):
        """
        Calcula el ratio de aceptación.
        
        Returns:
            float: Ratio de aceptación (demandas aceptadas / total de demandas)
        """
        total_demands = len(self.accepted_demands) + len(self.rejected_demands)
        if total_demands == 0:
            return 0.0
        
        return len(self.accepted_demands) / total_demands
    
    def get_results(self):
        """
        Obtiene los resultados del procesamiento.
        
        Returns:
            dict: Resultados del procesamiento
        """
        return {
            "accepted_demands": self.accepted_demands,
            "rejected_demands": self.rejected_demands,
            "acceptance_ratio": self.get_acceptance_ratio(),
            "allocations": self.allocations,
            "remaining_substrate": self.substrate_network
        }
    
    def print_allocation_results(self):
        """
        Muestra los resultados de las asignaciones.
        """
        print("\nRESULTADOS DE ASIGNACIÓN:")
        print(f"Ratio de aceptación: {self.get_acceptance_ratio():.2f}")
        print(f"Demandas aceptadas: {len(self.accepted_demands)} de {len(self.demands)}")
        
        print("\nAsignaciones:")
        for demand in self.accepted_demands:
            allocation = self.allocations[demand['id']]
            print(f"Demanda #{demand['id']}: Asignada a nodos sustrato {allocation}")
        
        for demand in self.rejected_demands:
            print(f"Demanda #{demand['id']}: RECHAZADA")
        
        print("\nRecursos restantes en la red sustrato (ancho de banda):")
        print(self.substrate_network)