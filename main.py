"""
Point d'entrée principal de l'application
"""

from Controllers.Functions import get_user_choice, handle_operator_menu, handle_client_menu
from Views.Functions import print_header, print_menu
from Controllers.Client import ClientController
from Controllers.Operateur import OperateurController


def main():
    try:
        while True:
            print_header("Système de Gestion Télécom")

            options = ["Gestionnaire", "Client"]
            print_menu(options)

            choice = get_user_choice(len(options), options)
            if choice == 0:
                print("\033[94mAu revoir!\033[0m")
                break
            while True:
                if choice == 1:
                    # Menu Gestionnaire
                    operator_controller = OperateurController()
                    if not handle_operator_menu(operator_controller):
                        return
                    break
                elif choice == 2:
                    # Menu Client
                    client_controller = ClientController()
                    if not handle_client_menu(client_controller):
                        return
                    break

    except Exception as e:
        print(f"Une erreur s'est produite: {str(e)}")
        import traceback
        print(traceback.format_exc())


if __name__ == "__main__":
    main()
