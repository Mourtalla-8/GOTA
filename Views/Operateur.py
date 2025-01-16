"""
Fonctions d'affichage pour les opérateurs
"""

from Views.Functions import print_header, print_menu, print_message


def display_operator_menu():
    """Affiche le menu des gestionnaires."""
    print_header("Menu Gestionnaire")
    options = [
        "Créer un opérateur",
        "Renommer un opérateur",
        "Lister les opérateurs",
        "Lister les numéros d’un operateur",
        "Gérer les index",
        "Vendre un numéro",
        "Vendre du crédit",
        "État de la caisse",
    ]
    return options

def display_operators(operators: list):
    """Affiche la liste des opérateurs."""
    print_header("Liste des Opérateurs")
    for operator in operators:
        print(f"Nom: {operator['name']}")
        print(f"Index: {', '.join(operator['indexes'])}")
        print("-" * 30)

def display_numbers_for_index(operator_name: str, index: str, numbers: list):
    """Affiche les numéros associés à un index d'un opérateur."""
    print_header(f"Numéros disponibles pour l'index {index} de l'opérateur {operator_name}")
    if not numbers:
        print_message(f"Aucun numéro associé à l'index {index}.", "INFO")
    else:
        for number in numbers:
            print(number)
    print("-" * 30)

def display_index_menu():
    """Affiche le menu de gestion des index."""
    print_header("Gestion des Index")
    options = [
        "Ajouter un nouvel index",
        "Supprimer un index"
    ]
    print_menu(options)
    return options

