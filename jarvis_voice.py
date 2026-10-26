"""
jarvis_voice.py - Live Speech Recognition & Audio Response Loop
Pushes live status + chat to the holographic HUD via jarvis_state_store.
Assistant name: Jack (for Shaik Mohammad Sohail)
"""

import sys
import os
import subprocess
import time
import speech_recognition as sr
import jarvis_brain
import jarvis_state_store as store


def speak(text):
    """Speak output and update HUD."""
    if not text:
        return
    print(f"\n[JACK]: {text}\n")
    store.add_chat("jarvis", text)  # HUD still uses key "jarvis" for styling
    store.set_state("speaking", "Responding…")

    if sys.platform == "darwin":
        subprocess.run(["say", "-v", "Samantha", text])
    else:
        try:
            import pyttsx3
            engine = pyttsx3.init()
            try:
                rate = engine.getProperty("rate")
                engine.setProperty("rate", int(rate * 0.95))
            except Exception:
                pass
            engine.say(text)
            engine.runAndWait()
        except Exception:
            pass

    store.set_state("listening", "Listening for command…")


def listen_loop():
    recognizer = sr.Recognizer()
    recognizer.dynamic_energy_threshold = True
    recognizer.pause_threshold = 0.8
    recognizer.non_speaking_duration = 0.5

    store.set_state("starting", "Calibrating microphone…")
    store.add_chat("sys", "Jack is online. Say a command.")

    try:
        mic = sr.Microphone()
    except Exception as e:
        print(f"Error accessing microphone: {e}")
        print("Falling back to text console input mode.")
        store.set_state("idle", "Text mode (no mic)")
        store.add_chat("sys", f"Mic unavailable: {e}. Type in the terminal.")
        while True:
            try:
                user_input = input("You: ")
                if user_input.strip():
                    store.add_chat("you", user_input.strip())
                    store.set_state("thinking", "Processing…")
                    t0 = time.time()
                    reply = jarvis_brain.think(user_input)
                    store.set_timings(t_think=time.time() - t0)
                    speak(reply)
            except (KeyboardInterrupt, EOFError):
                break
        store.set_state("off", "Offline")
        return

    with mic as source:
        print("\n" + "=" * 50)
        print("  JACK AI ASSISTANT IS ACTIVE AND LISTENING")
        print("  Open HUD:  python jarvis_server.py")
        print("  Say commands like:")
        print("    - 'Jack, open VS Code'")
        print("    - 'Open Chrome' / 'Open Gmail' / 'Open GitHub'")
        print("    - 'Open Notepad'")
        print("    - 'Play lofi on YouTube'")
        print("    - 'Stock market report'")
        print("=" * 50 + "\n")
        recognizer.adjust_for_ambient_noise(source, duration=1.0)

    store.set_state("listening", "Listening for command…")
    store.add_chat("sys", "Microphone calibrated. Ready.")

    while True:
        try:
            with mic as source:
                print("Listening... ", end="", flush=True)
                store.set_state("listening", "Listening…")
                for _ in range(3):
                    store.push_mic_level(0.15 + 0.1 * (_ % 3))
                audio = recognizer.listen(source, timeout=10, phrase_time_limit=8)

            print("Processing... ", end="", flush=True)
            store.set_state("recognizing", "Recognizing speech…")
            t_rec0 = time.time()

            query = recognizer.recognize_google(audio).strip()
            t_rec = time.time() - t_rec0
            print(f'\nYou said: "{query}"')
            store.add_chat("you", query)
            store.set_timings(t_rec=t_rec)

            q_clean = query.lower()
            # Accept both "jack" and "jarvis" as wake words
            for wake in ("jack", "jarvis"):
                if wake in q_clean:
                    q_clean = q_clean.replace(wake, "").strip(" ,.!?")

            if not q_clean:
                speak("Yes Sohail, I'm listening.")
                continue

            store.set_state("thinking", "Thinking…")
            t0 = time.time()
            response = jarvis_brain.think(q_clean)
            store.set_timings(t_think=time.time() - t0)
            store.bump_tools("action")
            speak(response)
            store.clear_tool_active()

        except sr.WaitTimeoutError:
            continue
        except sr.UnknownValueError:
            continue
        except KeyboardInterrupt:
            print("\nShutting down Jack. Goodbye!")
            store.set_state("off", "Offline")
            store.add_chat("sys", "Voice agent stopped.")
            break
        except Exception as e:
            print(f"\n[Notice]: {e}")
            store.add_chat("sys", f"Notice: {e}")
            time.sleep(0.5)


if __name__ == "__main__":
    listen_loop()