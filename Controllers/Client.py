"""
Contrôleur pour les clients
"""

from Models.Client import ClientModel
from Views.Client import *
from Controllers.Functions import *

class ClientController:
    def __init__(self):
        self.model = ClientModel()

    def login_client(self) -> bool:
        """Effectue la connexion du client avec 3 tentatives possibles."""
        client_logged_in = False
        MAX_ATTEMPTS = 3  # Limite du nombre de tentatives
        attempts = 0

        print_message("Entrez 'q' pour quitter.", "INFO")
        while not client_logged_in and attempts < MAX_ATTEMPTS:
            phone = input("Numéro de téléphone: ").strip()

            if phone.lower() == 'q':
                print_message("Quitter la connexion.", "INFO")
                return None, None

            pin = input("Code PIN: ").strip()

            if pin.lower() == 'q':
                print_message("Quitter la connexion.", "INFO")
                return None, None

            client = self.model.get_client_by_phone(phone)
            if not client:
                print_message("Numéro de téléphone invalide.", "ERROR")
            elif client["pin"] != pin:
                print_message("PIN incorrect.", "ERROR")
            else:
                # Si la connexion réussit
                client_logged_in = True
                return True, client

            attempts += 1
            attempts_left = MAX_ATTEMPTS - attempts  # Calculer le nombre de tentatives restantes
            print_message(f"Tentatives restantes: {attempts_left}", "INFO")
            print_message("Entrez 'q' pour quitter.", "INFO")

        if attempts == MAX_ATTEMPTS:
            print_message("Nombre maximum de tentatives atteint.", "ERROR")
        return False, None


    def check_credit(self, client_logged):
        """Consulte le crédit d'un client."""
        pin = input("Entrez votre code pin : ")
        if not client_logged or client_logged["pin"] != pin:
            print_message("Code pin incorrecte", "ERROR")
            return

        client = self.model.get_client_by_phone(client_logged['phone'])

        print_message(f"Votre crédit actuel est de {client['credit']}F.", "INFO")
        return

    def get_call_rate(self, phone1: str, phone2: str) -> int:
        """Retourne le tarif de l'appel entre deux numéros en fonction de leur opérateur."""
        # On récupère les préfixes des deux numéros
        index1 = phone1[:2]  # Les 2 premiers chiffres
        index2 = phone2[:2]

        operateur_model = OperateurModel()
        operators = operateur_model.get_all_operators()
        operator1 = None
        operator2 = None

        # Trouver l'opérateur pour chaque téléphone
        for operator in operators:
            if index1 in operator["indexes"]:
                operator1 = operator
            if index2 in operator["indexes"]:
                operator2 = operator

        # Si les deux numéros sont du même opérateur
        if operator1 and operator2:
            if operator1["name"] == operator2["name"]:
                return operator1["rates"]["same_operator"]
            else:
                return operator1["rates"]["different_operator"]
        return 2

    def request_call(self, client_logged):
        """Permet au client de passer un appel si son crédit est suffisant."""
        target_number = input("Numéro à appeler : ")

        if client_logged['phone'] == target_number:
            print_message("", "ERROR")
            return

        # Vérification si le client a suffisamment de crédit
        client = self.model.get_client_by_phone(client_logged['phone'])
        if client['credit'] <= 0:
            print_message("Pas assez de crédit pour appeler.", "ERROR")
            return

        # Validation du numéro de téléphone
        validation_message = validate_phone_number(target_number)
        if validation_message:
            print_message(validation_message, "ERROR")
            return

        # Vérifier si le numéro cible existe
        target_client = self.model.get_client_by_phone(target_number)
        if not target_client:
            print_message("Numéro de téléphone introuvable.", "ERROR")
            return

        # Recherche du nom du contact dans les contacts du client
        contact_name = next((c["name"] for c in client.get("contacts", []) if c["number"] == target_number), None)
        display_name = contact_name if contact_name else target_number

        # Calcul du tarif d'appel
        rate = self.get_call_rate(client['phone'], target_number)
        self.model.make_call(client, display_name, target_number, rate)


    def add_credit(self, phone: str, amount: float) -> bool:
        """Ajoute du crédit à un client."""
        client = self.model.get_client_by_phone(phone)
        if client:
            # Utiliser la méthode update_credit pour ajouter du crédit
            success = self.model.update_credit(phone, amount)
            if success:
                return True, f"Crédit de {amount} ajouté au {phone} avec succès."
            else:
                return False, "Erreur lors de l'ajout du crédit."

        return False, "Client non trouvé."


    def get_call_history(self, client_logged) -> None:
        """Obtenir et afficher l'historique des appels d'un client."""
        client = self.model.get_client_by_phone(client_logged["phone"])
        if client and client.get("call_history"):
            display_call_history(client)
        else:
            print_message("Aucun appel trouvé dans l'historique.", "INFO")

