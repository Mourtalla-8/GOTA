"""
Modèle pour la gestion des clients
"""

import os
import json
from typing import Dict, List, Optional
import pygame
from Views.Functions import print_message
import time
from datetime import datetime
import threading
import locale
import sounddevice as sd
import wavio
import numpy as np


class ClientModel:
    def __init__(self):
        self.clients_file = "BD/clients.txt"
        if not os.path.exists("BD"):
            os.makedirs("BD")

    def create_client(self, phone: str, pin: str) -> bool:
        """Créer un client avec un numéro de téléphone et un code PIN."""
        clients = self.get_all_clients()

        # Vérifier si le client avec ce numéro existe déjà
        if any(client["phone"] == phone for client in clients):
            print_message(f"Le numéro {phone} est déjà attribué à un client.", "ERROR")
            return False

        client = {
            "phone": phone,
            "pin": pin,
            "credit": 0,
            "contacts": [],
            "call_history": [],
            "blocked_contacts": []
        }

        clients.append(client)
        self._save_clients(clients)
        return True

    def get_client_by_phone(self, phone: str) -> Optional[Dict]:
        """Obtenir les détails d'un client via son numéro de téléphone."""
        clients = self.get_all_clients()
        for client in clients:
            if client["phone"] == phone:
                return client
        return None

    def get_all_clients(self) -> List[Dict]:
        """Obtenir tous les clients."""
        if not os.path.exists(self.clients_file):
            return []
        try:
            with open(self.clients_file, "r", encoding="utf-8") as f:
                content = f.read().strip()
                data = json.loads(content)
                return data
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print_message(f"Erreur lors de la lecture du fichier : {e}", "ERROR")
            return []


    def _save_clients(self, clients: List[Dict]):
        """Sauvegarder la liste des clients dans un fichier."""
        # Sauvegarde explicite pour s'assurer que les données sont bien enregistrées
        try:
            with open(self.clients_file, "w") as f:
                json.dump(clients, f, indent=4)
        except Exception as e:
            print_message(f"Erreur lors de la sauvegarde des clients : {e}", "ERROR")

    def update_credit(self, phone: str, amount: float) -> bool:
        """Mettre à jour le crédit du client."""
        clients = self.get_all_clients()
        for client in clients:
            if client["phone"] == phone:
                client["credit"] += amount
                self._save_clients(clients)
                return True
        print_message("Client introuvable.", "ERROR")
        return False


    def add_call_to_history(self, phone: str, call_details: dict):
        """Ajouter un appel à l'historique d'un client."""
        clients = self.get_all_clients()
        for client in clients:
            if client["phone"] == phone:
                client["call_history"].insert(0, call_details)
                self._save_clients(clients)
                return True
        return False


    def update_call_status(self, phone: str, call_index: int, new_status: str) -> bool:
        """Mettre à jour le statut d'un appel dans l'historique du client."""
        clients = self.get_all_clients()

        for client in clients:
            if client["phone"] == phone:
                call_history = client.get("call_history", [])

                if 0 <= call_index < len(call_history):
                    # Mettre à jour le statut de l'appel
                    call_history[call_index]["status"] = new_status
                    # Sauvegarder les modifications dans le fichier
                    self._save_clients(clients)
                    return True
                else:
                    print_message("Erreur : Indice d'appel invalide.", "ERROR")
                    return False

        print_message("Client introuvable.", "ERROR")
        return False


    def make_call(self, caller, target_name: str, target_number, rate: int):
        """Effectuer un appel, jouer la sonnerie et gérer la fin de l'appel par crédit ou entrée utilisateur."""
        print(f"Appel en cours vers {target_name}...")

        # Fonction pour jouer un son
        def play_sound(sound_file):
            """Jouer un fichier sonore."""
            pygame.mixer.init()
            sound_path = os.path.join("BD", "sounds", sound_file)
            if os.path.exists(sound_path):
                pygame.mixer.music.load(sound_path)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    time.sleep(1)
            pygame.mixer.quit()

        # Fonction d'attente d'entrée utilisateur avec timeout
        def get_user_input(timeout):
            """Obtenir l'entrée utilisateur avec un timeout."""
            action = [None]

            def wait_for_input():
                action[0] = input().lower()

            input_thread = threading.Thread(target=wait_for_input)
            input_thread.start()
            input_thread.join(timeout)
            if input_thread.is_alive():
                return None
            return action[0]

        # Démarrer la sonnerie dans un thread
        ringtone_thread = threading.Thread(target=play_sound, args=("ring-tone.mp3",))
        ringtone_thread.start()

        # Attendre l'action de l'utilisateur ou la fin de la sonnerie (timeout de 20 secondes)
        print("ça sonne ....")
        print("Appuyez sur [d] pour parler ou [Entrée] pour raccrocher.")
        action = get_user_input(20)

        # Arrêter la sonnerie si l'utilisateur répond ou si la sonnerie est terminée
        pygame.mixer.music.stop()
        ringtone_thread.join()

        if action != 'd':
            play_sound("end-call.mp3")
            print_message("Appel annulé.", "INFO")
            return False

        audio_dir = os.path.join("BD", "calls")
        if not os.path.exists(audio_dir):
            os.makedirs(audio_dir)

        audio_filename = os.path.join(audio_dir, f"call_{caller['phone']}_{target_number}_{int(time.time())}.wav")

        initial_credit = caller['credit']
        max_duration = initial_credit // rate  # Durée maximale en secondes que le client peut appeler
        recording_duration = 0
        cost = 0
        call_ended = False
        call_interrupted = False
        samplerate = sd.default.samplerate or 44100
        recorded_data = []

        locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
        call_time = datetime.now()
        formatted_date = call_time.strftime("%d %B %Y %H:%M:%S")

        # Fonction de callback pour enregistrer l'audio et gérer la durée de l'appel
        def callback(indata, frames, time, status):
            nonlocal recording_duration, call_ended, call_interrupted, cost
            duration_in_seconds = frames / samplerate
            recording_duration += duration_in_seconds
            recorded_data.append(indata.copy())

            if recording_duration >= max_duration:
                call_ended = True
                cost = caller['credit']
                print_message(f"Crédit épuisé. Durée : {int(recording_duration)} seconde(s). Coût : {cost}F.", "INFO")
                self.update_credit(caller['phone'], -cost)
                raise sd.CallbackStop  # Arrêter l'appel si la durée maximale atteinte (crédit épuisé)

        # Enregistrer l'appel
        try:
            with sd.InputStream(callback=callback, samplerate=samplerate):
                print_message("Enregistrement en cours... Parlez maintenant.", "INFO")
                print("Appuyer sur [r] pour raccrocher.")
                while not call_ended and not call_interrupted:
                    action = get_user_input(max_duration)
                    if action == 'r':
                        cost = rate * int(recording_duration)
                        print_message(f"Appel raccroché. Durée : {int(recording_duration)} seconde(s). Coût : {cost}F.", "INFO")
                        self.update_credit(caller['phone'], -cost)
                        call_interrupted = True
                        break
                    time.sleep(1)  # Attente passive pour permettre à l'appel de se dérouler
        except Exception as e:
            print(f"Erreur pendant l'appel : {e}")

        # Enregistrer l'audio dans un fichier
        print_message("Sauvegarde du fichier audio en cours...", "INFO")
        recorded_array = np.concatenate(recorded_data, axis=0)
        wavio.write(audio_filename, recorded_array, samplerate, sampwidth=2)
        print_message(f"Fichier audio sauvegardé sous {audio_filename}", "INFO")

        # Préparer les détails de l'appel pour l'appelant
        call_details_for_caller = {
            "direction": "outgoing",
            "number": target_number,
            "name": target_name if target_name != target_number else "inconnu",
            "status": "unread",
            "duration": int(recording_duration),
            "cost": cost,
            "date": formatted_date,
            "audio_file": audio_filename
        }

        # Récupérer les informations du client cible
        client_target = self.get_client_by_phone(target_number)
        contact_caller_name = next((c["name"] for c in client_target.get("contacts", []) if c["number"] == caller['phone']), "inconnu")
        caller_name = contact_caller_name

        # Préparer les détails de l'appel pour le destinataire
        call_details_for_target = {
            "direction": "incoming",
            "number": caller['phone'],
            "name": caller_name,
            "status": "unread",
            "duration": int(recording_duration),
            "cost": cost,
            "date": formatted_date,
            "audio_file": audio_filename
        }

        # Ajouter les détails à l'historique de l'appel pour l'appelant et le destinataire
        self.add_call_to_history(caller['phone'], call_details_for_caller)
        self.add_call_to_history(target_number, call_details_for_target)
        return True

