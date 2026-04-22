import os, time, threading, requests, subprocess
import speech_recognition as sr
import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
import edge_tts
import asyncio

# --- CONFIGURAÇÕES ---
# ⚠️ COLOQUE SUA CHAVE ABAIXO ⚠️
CHAVE_GROQ = "COLOQUE_SUA_CHAVE_AQUI" 
NOME_USUARIO = "Senhor Matheus"
AUDIO_BOOT = "iniciar.mp3"

async def gerar_voz(texto):
    communicate = edge_tts.Communicate(texto, "pt-BR-AntonioNeural")
    await communicate.save("fala.mp3")

def falar(texto):
    print(f"\nJARVIS: {texto}")
    asyncio.run(gerar_voz(texto))
    if os.path.exists("fala.mp3"):
        caminho = os.path.abspath("fala.mp3")
        tempo_estimado = (len(texto) // 10) + 3
        cmd = f'powershell -c "Add-Type -AssemblyName PresentationCore; $m = New-Object System.Windows.Media.MediaPlayer; $m.Open(\'{caminho}\'); $m.Play(); Start-Sleep -s {tempo_estimado}"'
        subprocess.run(cmd, shell=True)
        try: os.remove("fala.mp3")
        except: pass

def tocar_inicio():
    caminho_inicio = os.path.abspath(AUDIO_BOOT)
    if os.path.exists(caminho_inicio):
        print(f"Executando sequência de boot...")
        subprocess.Popen(['start', 'wmplayer', caminho_inicio], shell=True)
        def fechar_player():
            time.sleep(26)
            os.system("taskkill /f /im wmplayer.exe >nul 2>&1")
        threading.Thread(target=fechar_player, daemon=True).start()
        time.sleep(2) 
    else:
        print("Aviso: iniciar.mp3 não encontrado.")

def perguntar_ia(pergunta):
    if CHAVE_GROQ == "COLOQUE_SUA_CHAVE_AQUI":
        return "Senhor, a chave da API não foi configurada. Por favor, adicione-a no código."
        
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {CHAVE_GROQ}", "Content-Type": "application/json"}
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": f"Você é o sistema JARVIS. Responda de forma curta e heróica ao {NOME_USUARIO}."},
            {"role": "user", "content": pergunta}
        ],
        "temperature": 0.7
    }
    try:
        res = requests.post(url, json=payload, headers=headers, timeout=12)
        return res.json()['choices'][0]['message']['content']
    except:
        return "Senhor, houve uma falha de conexão."

def ouvir():
    fs = 16000
    segundos = 7 
    try:
        print("\n[ Ouvindo... ]")
        gravacao = sd.rec(int(segundos * fs), samplerate=fs, channels=1)
        sd.wait()
        write("input.wav", fs, np.int16(gravacao * 32767))
        rec = sr.Recognizer()
        with sr.AudioFile("input.wav") as source:
            audio = rec.record(source)
            texto = rec.recognize_google(audio, language="pt-BR").lower()
            return texto
    except:
        return ""

def main():
    print(f"\n" + "="*55)
    print(f"      J.A.R.V.I.S. MARK 85 - PROTOCOLO GROQ")
    print("="*55)
    while True:
        comando = ouvir()
        if "acorda" in comando or "crianças" in comando:
            tocar_inicio() 
            falar(f"Protocolos iniciados. Estou online, {NOME_USUARIO}.")
            while True:
                pergunta = ouvir()
                if any(n in pergunta for n in ["jarvis", "chaves"]):
                    p_limpa = pergunta.replace("jarvis", "").strip()
                    falar(perguntar_ia(p_limpa) if p_limpa else "Sim, senhor?")
                elif "dormir" in pergunta:
                    falar("Hibernando sistemas.")
                    break

if __name__ == "__main__":
    main()