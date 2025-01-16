"""
Fonctions d'affichage pour les clients
"""

from Views.Functions import print_header, print_menu, print_message, play_audio
from Models.Client import ClientModel
from prettytable import PrettyTable


def display_client_menu():
    """Affiche le menu des clients."""
    print_header("Menu Client")
    options = [
        "Consulter mon crédit",
        "Effectuer un appel",
        "Voir l'historique des appels",
        "Gérer les contacts",
        "Transférer du crédit",
    ]
    return options

def display_call_history(client):
    """Afficher l'historique des appels du client."""
    while True:  # Ajout d'une boucle pour maintenir la vue de l'historique active
        client_model = ClientModel()
        client = client_model.get_client_by_phone(client["phone"])
        call_history = client["call_history"]

        # Affichage de l'historique dans un tableau avec PrettyTable
        table = PrettyTable()
        cyan_background = "\033[46m"
        black_text = "\033[30m"
        reset_color = "\033[0m"

        # Noms de colonnes
        table.field_names = [
            f"{cyan_background}{black_text} {'Status'.center(10)} {reset_color}",
            f"{cyan_background}{black_text} {'Index'.center(10)} {reset_color}",
            f"{cyan_background}{black_text} {'Direction'.center(10)} {reset_color}",
            f"{cyan_background}{black_text} {'Nom'.center(10)} {reset_color}",
            f"{cyan_background}{black_text} {'Numéro'.center(10)} {reset_color}",
            f"{cyan_background}{black_text} {'Durée'.center(10)} {reset_color}",
            f"{cyan_background}{black_text} {'Coût'.center(10)} {reset_color}",
            f"{cyan_background}{black_text} {'Date'.center(10)} {reset_color}"
        ]

        table.hrules = True  # séparation entre les lignes

        for idx, call in enumerate(call_history):
            status = "Lu" if call["status"] == "read" else "Non lu"
            color_read_unread = "\033[42m\033[30m" if call["status"] == "read" else "\033[41m\033[30m"
            direction = "Sortant" if call["direction"] == "outgoing" else "Entrant"
            color_in_out = "\033[32m" if call["direction"] == "outgoing" else "\033[31m"

            # Ajouter une ligne au tableau avec les couleurs appropriées
            table.add_row([
                f"{color_read_unread} {status} {reset_color}",
                f"{idx}",
                f"{color_in_out}{direction}{reset_color}",
                f"{color_in_out}{call['name']}{reset_color}",
                f"{color_in_out}{call['number']}{reset_color}",
                f"{color_in_out}{call['duration']}{reset_color}",
                f"{color_in_out}{call['cost']}{reset_color}",
                f"{color_in_out}{call['date']}{reset_color}"
            ])

        print_header("Historique des appels")
        print(table)

        # Sélectionner un appel pour plus de détails
        print("\nEntrez position d'un appel pour voir plus de détails (ou appuyez sur [Entrée] pour quitter) : ")
        index = input().strip()
        if index == "":
            break

        if index.isdigit():
            index = int(index)
            if index >= 0 and index < len(call_history):
                display_call_details(call_history[index], client, index)
            else:
                if len(call_history) > 1:
                    print_message(f"Veuillez entrer un numéro valide (entre 0 et {len(call_history) - 1}).", "ERROR")
                else:
                    print_message(f"Veuillez entrer un numéro valide.", "ERROR")
        else:
            print_message(f"Veuillez entrer un numéro valide.", "ERROR")

def display_call_details(call, client, call_index):
    """Afficher les détails d'un appel"""
    while True:
        print("\033[94mDétails de l'appel :\033[0m")
        if call["direction"] == "outgoing":
            print(f"Appel : \033[32mSortant\033[0m")
        else:
            print(f"Appel : \033[31mEntrant\033[0m")
        if call["name"] != call["number"] and call["name"] != "inconnu":
            print(f"Nom du contact : {call['name']}")
        if call["name"] == "inconnu":
            print(f"Nom du contact : --")
        print(f"Numéro : {call['number']}")
        print(f"Durée : {call['duration']} secondes")
        print(f"Coût : {call['cost']}F")
        print(f"Date de l'appel : {call['date']}")
        if call["status"] == "unread":
            print(f"Status : \033[41m\033[30m Non lu \033[0m")
        else:
            print(f"Status : \033[42m\033[30m Lu \033[0m")
        print("-" * 40)
        print("")

        choix = input("Que souhaitez-vous faire ?\n"
                      "- [o] Écouter le message vocal\n"
                      "- [Entrée] Revenir à l'historique\n"
                      "Votre choix : ").strip()
        if choix.lower() == 'o':
            if play_audio(call['audio_file']):
                call["status"] = "read"
                client_model = ClientModel()
                client_model.update_call_status(client["phone"], call_index, "read")
                print(f"Statut de l'appel mis à jour à : Lu")
        elif choix == '':
            return
        else:
            print_message("Veuillez entrer 'o', ou 'Entrée'.", "ERROR")

