"""
Fonctions d'affichage communes
"""

import wave
import pyaudio


def print_header(title: str):
    """Affiche un en-tête avec le titre centré."""
    print("\n" + "=" * 70)
    print(f"{title:^50}")
    print("=" * 70 + "\n")


def print_menu(options: list, zero_option_text: str = "Quitter"):
    """Affiche un menu avec une liste d'options et une option zéro personnalisable."""
    for i, option in enumerate(options, 1):
        print(f"{i}. {option}")
    print(f"0. {zero_option_text}")


def print_message(message: str, message_type: str = "INFO"):
    """Affiche un message de type spécifié."""
    colors = {
        "ERROR": "\033[91m",
        "SUCCESS": "\033[92m",
        "INFO": "\033[94m"
    }
    color = colors.get(message_type.upper(), "\033[94m")
    print(f"\n{color}[{message_type.upper()}] {message}\033[0m\n")


def play_audio(file_path):
    # Ouvrir le fichier audio en mode lecture
    try:
        # Ouvrir le fichier audio en mode lecture
        with wave.open(file_path, 'rb') as wf:
            # Initialiser PyAudio
            p = pyaudio.PyAudio()

            # Ouvrir un flux de lecture avec PyAudio
            stream = p.open(format=pyaudio.paInt16,
                            channels=wf.getnchannels(),
                            rate=wf.getframerate(),
                            output=True)

            duration = wf.getnframes() / wf.getframerate()
            duration = int(duration)
            print("")
            print_message(f"Durée du fichier : {duration} seconde(s)", "INFO")
            print("Lecture en cours...")

            # Lire et jouer le fichier audio
            data = wf.readframes(1024)
            while data:
                stream.write(data)
                data = wf.readframes(1024)

            # Fermer le flux après la lecture
            stream.stop_stream()
            stream.close()

            # Terminer PyAudio
            p.terminate()

            # Message après la lecture
            print("")
            print_message("Lecture terminée.", "INFO")
            print("")
            return True
    except FileNotFoundError:
        print_message("Le fichier audio est introuvable.", "ERROR")
    except wave.Error:
        print_message("Erreur lors de l'ouverture du fichier audio. Vérifiez le format du fichier.", "ERROR")
    except Exception as e:
        print_message(f"Une erreur imprévue est survenue : {e}", "ERROR")
