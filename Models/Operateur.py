"""
Modèle pour la gestion des opérateurs
"""

import os
import json
from typing import List, Dict
from Models.Client import ClientModel
from Views.Functions import print_message


class OperateurModel:
    def __init__(self):
        self.operators_file = "BD/operators.txt"
        self.cashier_file = "BD/caisses.txt"

        if not os.path.exists("BD"):
            os.makedirs("BD")

    def create_operator(self, name: str, index: str) -> bool:
        """Créer un opérateur avec un nom et un index."""
        operator = {
            "name": name,
            "indexes": [index],
            "numbers": self._generate_numbers(index),
            "rates": {
                "same_operator": 1,  # 1F par seconde
                "different_operator": 2
            }
        }

        operators = self.get_all_operators()
        operators.append(operator)
        self._save_operators(operators)
        return True

    def _generate_numbers(self, index: str) -> List[str]:
        """Génère 100 numéros pour un index donné."""
        return [f"{index}{str(i).zfill(7)}" for i in range(100)]

    def get_all_operators(self) -> List[Dict]:
        """Récupère la liste de tous les opérateurs."""
        if not os.path.exists(self.operators_file):
            return []
        with open(self.operators_file, "r") as f:
            return json.load(f)

    def _save_operators(self, operators: List[Dict]):
        """Sauvegarde la liste des opérateurs dans le fichier."""
        with open(self.operators_file, "w") as f:
            json.dump(operators, f, indent=2)

    def rename_operator(self, old_name: str, new_name: str) -> bool:
        """Renommer un opérateur."""
        operators = self.get_all_operators()
        for operator in operators:
            if operator["name"] == old_name:
                operator["name"] = new_name
                self._save_operators(operators)
                return True
        return False

    def add_index_to_operator(self, operator_name: str, index: str) -> bool:
        operators = self.get_all_operators()
        for operator in operators:
            if operator["name"].lower() == operator_name.lower():
                operator["indexes"].append(index)
                operator["numbers"].extend(self._generate_numbers(index))
                self._save_operators(operators)
                return True
        return False

    def remove_index_from_operator(self, name: str, index: str) -> bool:
        """Supprimer un index d'un opérateur si possible."""
        operators = self.get_all_operators()
        for operator in operators:
            if operator["name"] == name:
                if index in operator["indexes"]:
                    if not self._can_remove_index(operator, index):
                        print_message(f"Impossible de supprimer l'index {index} car il est encore utilisé par des clients.", "INFO")
                        return False
                    if len(operator["indexes"]) == 1:
                        print_message(f"L'opérateur {name} n'a qu'un seul index {index}.\nSupprimer cet index entraînera également la suppression de l'opérateur.", "INFO")
                        r_confirm = input("Entrez 'oui' pour confirmer la suppression : ").strip().lower()
                        if r_confirm != "oui" :
                            print("Suppression annulée.")
                            return False

                        operators = [op for op in operators if op["name"] != name]
                        self._save_operators(operators)
                        return True

                    operator["indexes"].remove(index)
                    operator["numbers"] = [num for num in operator["numbers"] if not num.startswith(index)]
                    self._save_operators(operators)
                    return True
                print_message(f"L'index {index} n'existe pas pour l'opérateur {name}.", "INFO")
                return False
        return False

    def _can_remove_index(self, operator, index: str) -> bool:
        """Vérifie si un index peut être supprimé en fonction des clients existants."""
        client_model = ClientModel()

        # Vérifiez si des clients utilisent cet index
        for client in client_model.get_all_clients():
            if client["phone"].startswith(index):
                return False  # L'index est encore utilisé par un client
        return True

    def is_index_unique(self, index: str) -> bool:
        """Vérifie si l'index est unique parmi tous les opérateurs."""
        operators = self.get_all_operators()
        return not any(index in operator["indexes"] for operator in operators)

    def _save_cashier(self, cashier_data: Dict):
        """Sauvegarde les informations de caisse dans un fichier."""
        with open(self.cashier_file, "w") as f:
            json.dump(cashier_data, f, indent=2)

    def _load_cashier(self) -> Dict:
        """Charge les informations de caisse du gestionnaire."""
        if not os.path.exists(self.cashier_file):
            return {}

        with open(self.cashier_file, "r") as f:
            return json.load(f)

    def record_credit_sale(self, operator_name: str, amount: float, manager_name: str):
        """Vendre du crédit à un client et enregistrer la vente dans la caisse du gestionnaire."""
        # Enregistrer la vente dans la caisse du gestionnaire
        cashier_data = self._load_cashier()

        if manager_name not in cashier_data:
            cashier_data[manager_name] = {}

        # Ajouter ou mettre à jour les informations de caisse pour l'opérateur
        if operator_name not in cashier_data[manager_name]:
            cashier_data[manager_name][operator_name] = {"daily": 0, "monthly": 0, "yearly": 0}

        # Ajouter la vente au jour, mois et année pour cet opérateur
        cashier_data[manager_name][operator_name]["daily"] += amount
        cashier_data[manager_name][operator_name]["monthly"] += amount
        cashier_data[manager_name][operator_name]["yearly"] += amount

        self._save_cashier(cashier_data)
        print_message(f"Crédit de {amount}F vendu. Vente enregistrée dans la caisse du gestionnaire {manager_name} pour l'opérateur {operator_name}.", "SUCCESS")


    def is_number_available_for_operator(self, phone: str, operator_name: str) -> bool:
        """Vérifie si un numéro est disponible pour un opérateur donné."""
        operators = self.get_all_operators()
        for operator in operators:
            if operator["name"] == operator_name:
                if phone in operator["numbers"]:
                    return True
                else:
                    return False
        return False

    def assign_number_to_client(self, phone: str, operator_name: str, pin: str) -> bool:
        operators = self.get_all_operators()
        for operator in operators:
            if operator["name"] == operator_name and phone in operator["numbers"]:
                operator["numbers"].remove(phone)
                client_model = ClientModel()
                client_model.create_client(phone, pin)
                self._save_operators(operators)
                return True
        return False
