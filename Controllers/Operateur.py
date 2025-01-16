"""
Contrôleur pour les opérateurs
"""

import os
from Controllers.Client import ClientController
from Models.Operateur import OperateurModel
from Views.Operateur import *
from Controllers.Functions import *


class OperateurController:
    def __init__(self):
        self.model = OperateurModel()

    def login_manager(self):
        operator_logged_in = False
        MAX_ATTEMPTS = 3 # Limite du nombre de tentatives
        attempts = 0

        # Vérifier si le fichier des gestionnaires existe avant de commencer
        file_path = os.path.join("BD", "gestionnaires.txt")
        if not os.path.exists(file_path):
            print_message("Le fichier des gestionnaires est introuvable.", "ERROR")
            return operator_logged_in, None

        print_message("Entrez 'q' pour quitter.", "INFO")
        while not operator_logged_in and attempts < MAX_ATTEMPTS:
            username = input("Nom d'utilisateur : ").strip()
            if username.lower() == 'q':
                print("\033[94mAu revoir!\033[0m")
                return None, None

            password = input("Mot de passe : ").strip()
            if password.lower() == 'q':
                print("\033[94mAu revoir!\033[0m")
                return None, None

            if self.verify_manager_credentials(username, password, file_path):
                print_message("Connexion réussie en tant que gestionnaire.", "SUCCESS")
                operator_logged_in = True
            else:
                attempts += 1
                attempts_left = MAX_ATTEMPTS - attempts  # Calculer le nombre de tentatives restantes
                print_message(f"Tentatives restantes: {attempts_left}","INFO")
                print_message("Entrez 'q' pour quitter.", "INFO")


        if attempts == MAX_ATTEMPTS:
            print_message("Nombre maximum de tentatives atteint.", "ERROR")
        return operator_logged_in, username


    def verify_manager_credentials(self, username, password, file_path):
        """Vérifie les identifiants du gestionnaire dans le fichier des gestionnaires."""
        try:
            with open(file_path, "r") as file:
                for line in file:
                    stored_username, stored_password = line.strip().split(":")
                    if stored_username == username and stored_password == password:
                        return True
                    else:
                        print_message("Nom d'utilisateur ou mot de passe incorrect. Réessayez.", "ERROR")
                        return False
        except Exception as e:
            print_message(f"Une erreur est survenue lors de l'ouverture du fichier : {str(e)}", "ERROR")
            return False


    def create_operator(self):
        """Crée un nouvel opérateur."""
        operator_name = input("Entrez le nom de l'opérateur: ")
        operator_validation_message = validate_operator_name(operator_name)
        if operator_validation_message:
            print_message(operator_validation_message, "ERROR")
            return

        index = input("Entrez l'index de l'opérateur: ").strip()
        if  if_operator_exist(operator_name):
            print_message(f"L'opérateur {operator_name} existe déjà", "INFO")
            return False
        index_validation_message = validate_index(index)
        if index_validation_message:
            print_message(index_validation_message, "ERROR")
            return
        if not self.model.is_index_unique(index):
            print_message("Cet index est déjà utilisé par un autre opérateur.", "ERROR")
            return
        if self.model.create_operator(operator_name, index):
            print_message(f"L'opérateur {operator_name} a été créé avec succès.", "SUCCESS")
            return
        print_message("Une erreur est survenue lors de la création de l'opérateur.", "ERROR")
        return

    def rename_operator(self) -> str:
        """Renomme un opérateur."""
        if not self.list_operators():
            return

        old_name = input("Entrez le nom actuel de l'opérateur: ")
        if not if_operator_exist(old_name):
            print_message(f"L'opérateur {old_name} n'existe pas.", "ERROR")
            return False

        new_name = input("Entrez le nouveau nom de l'opérateur: ")

        validation_message = validate_operator_name(new_name)
        if validation_message:
            print_message(validation_message, "ERROR")
            return
        if self.model.rename_operator(old_name, new_name):
            print_message(f"L'opérateur {old_name} a été renommé en {new_name}.", "SUCCESS")
            return
        return


    def list_operators(self):
        """Liste tous les opérateurs."""
        operators = self.model.get_all_operators()

        if not operators:
            print_message("Aucun opérateur trouvé.", "INFO")
            return False

        display_operators(operators)
        return True


    def list_numbers_for_operator(self, operator_name: str = None) -> None:
        """Lister les numéros associés à un opérateur spécifique, avec gestion des index multiples."""

        if not operator_name:  # Vérifie si operator_name est vide ou None
            if not self.list_operators():
                return
            operator_name = input("Entrez le nom de l'opérateur: ")

        # Récupérer tous les opérateurs
        operators = self.model.get_all_operators()

        # Vérifier si des opérateurs ont été récupérer
        if not operators:
            print_message("Aucun opérateur trouvé.", "ERROR")
            return False

        # Trouver l'opérateur correspondant
        for operator in operators:
            if operator["name"].lower() == operator_name.lower():
                indexes = operator.get("indexes", [])

                if isinstance(indexes, list) and len(indexes) > 1:
                    # Afficher les index et demander à l'utilisateur de choisir
                    print_message("L'opérateur a plusieurs index :", "INFO")
                    for i, index in enumerate(indexes):
                        print(f"{i + 1}. {index}")

                    choice = int(input("Choisissez un index par son numéro: ")) - 1

                    if 0 <= choice < len(indexes):
                        chosen_index = indexes[choice]
                        numbers = [num for num in operator["numbers"] if num.startswith(chosen_index)]
                        display_numbers_for_index(operator["name"], chosen_index, numbers)
                        return operator, chosen_index
                    else:
                        print_message("Choix invalide.", "INFO")
                        return None, None
                else:
                    # Si un seul index, afficher directement les numéros
                    index = indexes[0] if indexes else ""
                    display_numbers_for_index(operator["name"], index, operator["numbers"])
                return operator, index
        # Si l'opérateur n'est pas trouvé
        print_message(f"Aucun opérateur trouvé avec le nom {operator_name}.", "INFO")
        return None, None


    def manage_indexes(self):
        """Gère les index d'un opérateur."""
        if not self.list_operators():
            return

        operator_name = input("Entrez le nom de l'opérateur: ")

        if not if_operator_exist(operator_name):
            print_message(f"L'opérateur {operator_name} n'a pas été trouvé.", "ERROR")
            return False

        while True:
            display_index_menu()
            choice = input("Votre choix: ")

            if choice == '1':  # Ajouter un index
                operators = self.model.get_all_operators()
                for operator in operators:
                    if operator_name.lower() == operator['name'].lower():
                        # Vérifier si l'opérateur a déjà 3 index
                        if len(operator['indexes']) >= 3:
                            print_message(f"L'opérateur {operator_name} a déjà 3 index, il ne peut pas en ajouter un autre.", "INFO")
                            break
                        # Si l'opérateur a moins de 3 index, on peut ajouter un nouveau
                        index = input("Entrez le nouvel index: ")
                        if not self.model.is_index_unique(index):
                            print_message("Cet index est déjà utilisé par un autre opérateur.", "ERROR")
                            continue
                        index_validation_message = validate_index(index)
                        if index_validation_message:
                            print_message(index_validation_message, "ERROR")
                            continue

                        if self.model.add_index_to_operator(operator_name, index):
                            print_message(f"L'index {index} a été ajouté avec succès à l'opérateur {operator_name}.", "SUCCESS")
                        else:
                            print_message(f"Échec de l'ajout de l'index {index}.", "ERROR")
                        break
            elif choice == '2':  # Supprimer un index
                index = input("Entrez l'index à supprimer: ")
                index_validation_message = validate_index(index)
                if index_validation_message:
                    print_message(index_validation_message, "ERROR")
                    continue

                operators = self.model.get_all_operators()
                for operator in operators:
                    if operator_name.lower() == operator['name'].lower():
                        if len(operator["indexes"]) == 1:
                            if self.model.remove_index_from_operator(operator_name, index):
                                print_message(f"L'index {index} et l'opérateur {operator_name} ont été supprimés avec succès.", "SUCCESS")
                                return
                        elif self.model.remove_index_from_operator(operator_name, index):
                            print_message(f"L'index {index} a été supprimé avec succès de l'opérateur {operator_name}.", "SUCCESS")
                            continue

            elif choice == '0':  # Quitter l'opération
                print_message("Opération annulée.", "INFO")
                break
            else:
                print_message("Choix invalide, veuillez réessayer.", "INFO")


    def sell_number(self) -> bool:
        """Vente d'un numéro"""
        # Affiche l'interface pour créer un nouveau client.
        print_header("Créer un nouveau client")

        # lister tous les opérateurs.
        if not self.list_operators():
            return

        operator_name = input("Entrez le nom de l'opérateur: ").strip()
        # Lister les numéros associés à un opérateur spécifique, avec gestion des index multiples.
        operator, operator_index = self.list_numbers_for_operator(operator_name)
        if operator is None or operator_index is None:
            return False

        phone = input("Entrez le numéro de téléphone du client (9 chiffres): ").strip()
        validation_message = validate_phone_number(phone)
        if validation_message:
            print_message(validation_message, "ERROR")
            return False

        # Vérifier si le numéro appartient à l'opérateur
        print_message(f"Vérification si le numéro {phone} est disponible chez l'opérateur {operator_name} ...", "INFO")
        if not self.model.is_number_available_for_operator(phone, operator_name):
            print_message(f"Le numéro {phone} est déjà pris ou n'est pas disponible chez l'opérateur {operator_name}.", "ERROR")
            return False

        # Vérifier si le numéro commence par l'index spécifié
        if not phone.startswith(operator_index):
            print_message(f"Le numéro doit commencer par l'index {operator_index}.", "ERROR")
            return False

        pin = input("Entrez le code PIN du client (4 chiffres): ").strip()
        validation_message = validate_pin(pin)
        if validation_message:
            print_message(validation_message, "ERROR")
            return False

        print_message(f"Création du client avec le numéro {phone} ...", "INFO")
        if self.model.assign_number_to_client(phone, operator_name, pin):
            print_message(f"Client créé, assignation du numéro {phone} à l'opérateur {operator_name}.", "SUCCESS")
            return True

        print_message(f"Échec de la création du client avec le numéro {phone}.", "ERROR")
        return False


    def sell_credit_to_client(self, manager_name: str) -> bool:
        """Vente de crédit à un client spécifique."""
        operators = self.model.get_all_operators()
        if not operators:
            print_message("Aucun opérateur trouvé.", "INFO")
        else:
            print("Liste des opérateurs :")
            for operator in operators:
                print(f"{operator['name']}")
            print("-" * 30)

        phone = input("Numéro de téléphone du client: ")
        validation_message = validate_phone_number(phone)
        if validation_message:
            print_message(validation_message, "ERROR")
            return

        amount = int(input("Montant de crédit à vendre: "))
        validation_message = validate_amount(amount)
        if validation_message:
            print_message(validation_message, "ERROR")
            return

        # Vérifier si le client existe et ajouter le crédit
        client_controller = ClientController()
        success, message = client_controller.add_credit(phone, amount)

        if success:
            # Enregistrer la vente de crédit
            operator_name = get_operator_by_phone(phone)
            self.model.record_credit_sale(operator_name, amount, manager_name)
            print_message(f"Succès ! {amount}F de crédit ont été ajoutés au compte du client {phone}.", "SUCCESS")
            return True
        else:
            print_message(f"Échec de l'ajout de crédit pour le client {phone}.", "ERROR")
            print_message(f"Motif de l'échec : {message}", "INFO")
            return False


    def get_cash_state(self, manager_name: str):
        """Affiche l'état de la caisse du gestionnaire avec un détail par opérateur."""
        cashier_data = self.model._load_cashier()

        if manager_name not in cashier_data:
            print_message(f"Aucune donnée pour le gestionnaire {manager_name}.", "INFO")
            return

        print_message(f"État de la caisse pour le gestionnaire {manager_name}:", "INFO")
        for operator_name, data in cashier_data[manager_name].items():
            print(f"Opérateur {operator_name}:")
            print(f"  - État du jour : {data['daily']}F")
            print(f"  - État du mois : {data['monthly']}F")
            print(f"  - État de l'année : {data['yearly']}F")

