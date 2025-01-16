"""
Fonctions communes aux contrôleurs
"""

from Views.Client import display_client_menu
from Views.Functions import print_menu, print_message
from Views.Operateur import display_operator_menu
from consts import *
from Models.Operateur import OperateurModel


def handle_operator_menu(controller):
    """Gestion du menu opérateur."""
    operator_logged_in, username = controller.login_manager()
    if not operator_logged_in:
        return False

    while True:
        # Affichage du menu une seule fois après la connexion
        options = display_operator_menu()
        print_menu(options, "Se déconnecter")
        choice = get_user_choice(len(options), options)
        if choice == 0:
            print("\033[94mDéconnecté\033[0m")
            return True

        if choice == 1:
            # Créer un opérateur
            controller.create_operator()

        elif choice == 2:
            # Renommer un opérateur
            controller.rename_operator()

        elif choice == 3:
            # Lister les opérateurs
            controller.list_operators()

        if choice == 4:
            # lister tous les opérateurs.
            controller.list_numbers_for_operator()

        elif choice == 5:
            # Gérer les index
            controller.manage_indexes()

        elif choice == 6:
            # Créer un client avec la vente d'un numéro
            controller.sell_number()

        elif choice == 7:
            # Vendre du crédit
            controller.sell_credit_to_client(username)


        elif choice == 8:
            # Afficher l'état de la caisse
            controller.get_cash_state(username)


def handle_client_menu(controller):
    """Gestion du menu client."""
    client_logged_in, client_logged = controller.login_client()
    if not client_logged_in:
        return False

    if client_logged_in:
        print_message("Authentification réussie.", "SUCCESS")
        while True:
            options = display_client_menu()
            print_menu(options, "Se déconnecter")
            choice = get_user_choice(len(options), options)

            if choice == 0:
                print("\033[94mDéconnecté\033[0m")
                return True

            if choice == 1:
                # Consulter le crédit
                controller.check_credit(client_logged)

            elif choice == 2:
                # Effectuer un appel
                controller.request_call(client_logged)

            elif choice == 3:
                # Voir l'historique des appels
                controller.get_call_history(client_logged)

            elif choice == 4:
                # Gérer les contacts
                print_message("En maintenance ...", "INFO")


            elif choice == 5:
                # Transférer du crédit
                print_message("En maintenance ...", "INFO")


def validate_operator_name(name: str) -> str:
    """Valide le nom de l'opérateur."""
    if len(name) < MIN_OPERATOR_NAME_LENGTH:
        return f"Le nom de l'opérateur doit comporter au moins {MIN_OPERATOR_NAME_LENGTH} caractères."
    elif len(name) > MAX_OPERATOR_NAME_LENGTH:
        return f"Le nom de l'opérateur doit comporter au maximum {MAX_OPERATOR_NAME_LENGTH} caractères."

    # Récupère les opérateurs
    operateur_model = OperateurModel()
    existing_operators = operateur_model.get_all_operators()

    # Vérifier l'unicité du nom
    for operator in existing_operators:
        if operator["name"].lower() == name.lower():
            return "Un opérateur avec ce nom existe déjà. Veuillez choisir un nom différent."
    return ""

def validate_phone_number(number: str) -> str:
    """Valide le numéro de téléphone."""
    if len(number) != PHONE_NUMBER_LENGTH or not number.isdigit():
        return f"Le numéro de téléphone doit être composé de {PHONE_NUMBER_LENGTH} chiffres."
    return ""


def validate_pin(pin: str) -> str:
    """Valide le code PIN."""
    if len(pin) != PIN_LENGTH or not pin.isdigit():
        return f"Le code PIN doit être composé de {PIN_LENGTH} chiffres."
    return ""

def validate_amount(amount: float) -> str:
    """Valide un montant de crédit ou de vente."""
    if amount < MIN_CREDIT_AMOUNT:
        return f"Le montant doit être d'au moins {MIN_CREDIT_AMOUNT}."
    return ""

def validate_index(index: str) -> str:
    """Valide un index pour l'opérateur."""
    if len(index) != INDEX_LENGTH or not index.isdigit():
        return f"L'index doit être composé de {INDEX_LENGTH} chiffres."
    return ""

def if_operator_exist(operator_name):
    operateur_model = OperateurModel()
    operators = operateur_model.get_all_operators()
    for operator in operators:
        if operator_name.lower() == operator['name'].lower():
            return True
    return False

def get_user_choice(max_choice: int, options) -> int:
    """Demande à l'utilisateur de faire un choix dans un menu."""
    while True:
        try:
            choice = int(input("\nVotre choix: "))
            if 0 <= choice <= max_choice:
                return choice
            print_message(f"Veuillez entrer un nombre entre 0 et {max_choice}", "ERROR")
            print_menu(options)
        except ValueError:
            print_message("Veuillez entrer un nombre valide", "ERROR")
            print_menu(options)


def get_operator_by_phone(phone: str) -> str:
    """Récupère le nom de l'opérateur à partir du numéro de téléphone."""
    # Récupère l'index
    index = phone[:2]
    operateur_model = OperateurModel()

    # Vérification si les index des opérateurs sont bien définis
    for operator in operateur_model.get_all_operators():
        if index in operator["indexes"]:
            return operator["name"]

    # Si aucun opérateur n'est trouvé, afficher un message explicite
    return f"Aucun opérateur trouvé pour le préfixe {index} du numéro {phone}."

