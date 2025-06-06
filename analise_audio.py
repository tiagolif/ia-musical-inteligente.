import librosa
import librosa.display # Para visualização, embora não vamos usar agora, é bom importar
import numpy as np
from pydub import AudioSegment
import os

# --- CONFIGURAÇÃO ---
NOME_ARQUIVO_AUDIO = "ilusi.mp3.mp3" # O seu arquivo de áudio para análise

# --- CARREGAR O ÁUDIO E PROCESSAR COM PYDUB E LIBROSA ---
try:
    # --- Pydub: Carregar e obter informações básicas ---
    audio_pydub = AudioSegment.from_file(NOME_ARQUIVO_AUDIO)
    print(f"Arquivo de áudio '{NOME_ARQUIVO_AUDIO}' carregado com sucesso pelo pydub!")

    duracao_ms = len(audio_pydub)
    duracao_seg = duracao_ms / 1000.0
    duracao_min = duracao_seg / 60.0
    canais = audio_pydub.channels
    sample_rate_pydub = audio_pydub.frame_rate
    bits_por_amostra = audio_pydub.sample_width * 8
    volume_dbfs = audio_pydub.dBFS

    print(f"\n--- Informações do Áudio (Pydub) ---")
    print(f"Duração: {duracao_seg:.2f} segundos ({duracao_min:.2f} minutos)")
    print(f"Canais: {canais} (1=Mono, 2=Estéreo)")
    print(f"Taxa de Amostragem (Sample Rate): {sample_rate_pydub} Hz")
    print(f"Bits por Amostra: {bits_por_amostra} bits")
    print(f"Volume Médio (dBFS): {volume_dbfs:.2f} dBFS")

    # --- Librosa: Preparar áudio para análise ---
    y, sr = librosa.load(NOME_ARQUIVO_AUDIO, sr=None) # sr=None mantém a taxa de amostragem original
    print(f"Áudio carregado com sucesso pelo librosa. Sample Rate: {sr} Hz")

    # Adicionando o cálculo de onset_env aqui para que esteja disponível para as seções futuras
    # onset_frames é mais apropriado aqui, pois onset_detect retorna os quadros dos onsets
    onset_frames = librosa.onset.onset_detect(y=y, sr=sr)


    # --- ANÁLISE DE BPM (com Librosa) ---
    print(f"\n--- Análise de Ritmo (Librosa) ---")
    # Estimar o BPM
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)

    # Corrigido: Usar .item() para extrair o valor escalar do array NumPy
    print(f"BPM Detectado: {tempo.item():.2f}")

    # --- EXEMPLO DE UM FEEDBACK MAIS DETALHADO (Nossa "IA" avançando) ---
    print(f"\n--- Sugestões da IA (Volume e BPM) ---")
    
    # Feedback de Volume
    if volume_dbfs < -20:
        print(f"Volume: O volume geral está um pouco baixo ({volume_dbfs:.2f} dBFS). Considere aumentar o ganho da faixa em aproximadamente 3-6 dB para melhor impacto.")
    elif volume_dbfs > -5:
        print(f"Volume: O volume geral está alto ({volume_dbfs:.2f} dBFS). Pode haver saturação ou clipping. Sugiro abaixar o ganho da faixa em aproximadamente 2-4 dB e verificar o headroom.")
    else:
        print(f"Volume: O volume parece adequado ({volume_dbfs:.2f} dBFS). Bom trabalho!")

    # Feedback de BPM
    if tempo.item() < 120:
        print(f"BPM: O ritmo detectado ({tempo.item():.2f} BPM) é mais lento. Adequado para gêneros como Deep House, Chillout ou Downtempo. Se busca mais energia, um BPM entre 125-130 pode ser ideal.")
    elif tempo.item() > 140:
        print(f"BPM: O ritmo detectado ({tempo.item():.2f} BPM) é rápido. Bom para Drum and Bass, Hardstyle ou Trance acelerado. Verifique se essa velocidade é a intenção artística, pois pode ser desafiador para a pista de dança.")
    else:
        print(f"BPM: O ritmo detectado ({tempo.item():.2f} BPM) está em uma faixa comum (120-140 BPM) para muitos gêneros de música eletrônica, como House, Techno e Trance.")

    # --- ANÁLISE DE HARMONIA/CHAVE MUSICAL (com Librosa) ---
    print(f"\n--- Análise Harmônica (Librosa) ---")

    # Calcula as características cromáticas (chroma features)
    chroma = librosa.feature.chroma_stft(y=y, sr=sr)

    # Nomes das notas
    keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

    # Gerar o perfil cromático médio do áudio
    chroma_means = np.mean(chroma, axis=1)

    # Normalizar o perfil cromático médio
    chroma_means_norm = chroma_means / np.sum(chroma_means)

    # Matrizes de correlação para chaves maiores e menores (Krumhansl-Schmuckler)
    major_template = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
    minor_template = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])

    # Normalizar os templates
    major_template_norm = major_template / np.sum(major_template)
    minor_template_norm = minor_template / np.sum(minor_template)

    # Calcular a correlação com todas as 24 chaves
    best_correlation = -1 # Começa com um valor bem baixo
    detected_key = "Não detectada"

    for i in range(12): # Para cada uma das 12 notas (C, C#, ..., B) como tônica
        root_note = keys[i]
        
        # Shiftar o perfil cromático para testar todas as 12 rotações de tônica
        shifted_chroma = np.roll(chroma_means_norm, -i) # Rola para a esquerda para alinhar a tônica com C

        # Correlacionar com os templates maior e menor
        major_corr = np.dot(shifted_chroma, major_template_norm)
        minor_corr = np.dot(shifted_chroma, minor_template_norm)

        # Atualizar se encontramos uma correlação melhor para Maior
        if major_corr > best_correlation:
            best_correlation = major_corr
            detected_key = f"{root_note} Major"
        
        # Atualizar se encontramos uma correlação melhor para Menor
        if minor_corr > best_correlation:
            best_correlation = minor_corr
            detected_key = f"{root_note} Minor"

    print(f"Chave Musical Detectada: {detected_key}")

    # --- Sugestões Adicionais da IA (baseadas na Chave) ---
    print(f"\n--- Sugestões Adicionais da IA (Harmonia) ---")
    if detected_key != "Não detectada":
        print(f"Sugestão de Harmonia: A chave detectada é {detected_key}. Considere construir sua melodia e acordes dentro dessa chave para garantir a coesão harmônica.")
        if "Major" in detected_key:
            print("Essa é uma chave maior, geralmente associada a sensações mais alegres e brilhantes.")
        elif "Minor" in detected_key:
            print("Essa é uma chave menor, frequentemente associada a sensações mais melancólicas ou dramáticas.")
    else:
        print("Sugestão de Harmonia: Não foi possível detectar uma chave musical clara. Isso pode acontecer com áudios complexos ou atonais. Se for uma faixa melódica, tente simplificar ou focar em uma progressão mais clara.")

    # --- ANÁLISE DE ESPECTRO/FREQUÊNCIAS (com Librosa) ---
    print(f"\n--- Análise de Frequências (Librosa) ---")

    # Calcula o Espectrograma de Curta Duração (STFT)
    D = librosa.stft(y, n_fft=2048, hop_length=512)
    S_db = librosa.amplitude_to_db(np.abs(D), ref=np.max)

    # Faixas de frequência para análise
    freqs = librosa.fft_frequencies(sr=sr, n_fft=2048)

    idx_graves = np.where((freqs >= 20) & (freqs < 250))[0]
    idx_medios = np.where((freqs >= 250) & (freqs < 4000))[0]
    idx_agudos = np.where((freqs >= 4000) & (freqs <= 20000))[0]

    energia_graves = np.mean(S_db[idx_graves]) if len(idx_graves) > 0 else -np.inf
    energia_medios = np.mean(S_db[idx_medios]) if len(idx_medios) > 0 else -np.inf
    energia_agudos = np.mean(S_db[idx_agudos]) if len(idx_agudos) > 0 else -np.inf

    print(f"Energia Média em Graves (20-250Hz): {energia_graves:.2f} dB")
    print(f"Energia Média em Médios (250Hz-4kHz): {energia_medios:.2f} dB")
    print(f"Energia Média em Agudos (4kHz-20kHz): {energia_agudos:.2f} dB")

    # --- Sugestões Adicionais da IA (Mixagem/Equalização) ---
    print(f"\n--- Sugestões Adicionais da IA (Mixagem/Equalização) ---")

    if energia_graves > (energia_medios + 5):
        print("Sugestão de Mixagem: Os graves parecem muito dominantes. Considere um pouco de 'sidechain compression' no baixo ou kick, ou ajuste a equalização para dar mais espaço aos médios.")
    elif energia_medios < (energia_graves - 10) and energia_medios < (energia_agudos - 10):
        print("Sugestão de Mixagem: A faixa pode estar 'oca' ou sem corpo. Verifique a energia nas frequências médias. Talvez alguns sintetizadores ou vocais precisem de mais presença nessa faixa.")
    elif energia_agudos > (energia_medios + 7):
        print("Sugestão de Mixagem: Há muita energia nos agudos. Isso pode causar fadiga auditiva. Considere um 'high-shelf EQ' suave ou um 'de-esser' em elementos como hi-hats ou pratos.")
    else:
        print("Sugestão de Mixagem: A distribuição de frequências gerais parece equilibrada. Bom trabalho na mixagem!")

    # --- IDENTIFICAÇÃO BÁSICA DE INSTRUMENTOS/SONS (Heurística) ---
    print(f"\n--- Identificação de Sons Básicos (Heurística) ---")

    # Reutilizando freqs, S_db calculados anteriormente
    # Reutilizando beat_frames (detectados na análise de BPM) como uma proxy para onsets rítmicos

    # Encontrar a frequência de pico (mais forte) no espectro médio dos graves
    if len(idx_graves) > 0 and S_db[idx_graves,:].size > 0:
        mean_spectrum_graves = np.mean(S_db[idx_graves, :], axis=1)
        peak_freq_idx_graves = np.argmax(mean_spectrum_graves)
        peak_freq_graves = freqs[idx_graves[peak_freq_idx_graves]]
    else:
        peak_freq_graves = 0

    # --- Sugestões baseadas em Instrumentos ---
    print(f"\n--- Sugestões da IA (Instrumentos Básicos) ---")

    # Tentativa de identificar Kick
    if tempo.item() > 60 and energia_graves > -40 and peak_freq_graves > 40 and peak_freq_graves < 100:
        print("Elemento: Parece haver um **Kick Drum** proeminente. Para um 'punch' ideal, assegure que não haja conflito de fase com o baixo e que as frequências de sub-graves (30-60Hz) estejam bem controladas.")
    elif tempo.item() > 60 and energia_graves > -50:
        print("Elemento: Há uma boa presença de graves. Revise a clareza e definição do seu **Kick/Bassline** para evitar 'embolamento' nessa faixa de frequência.")

    # Tentativa de identificar Snare/Clap
    if energia_medios > -60 and len(onset_frames) / duracao_seg > 1.5:
        print("Elemento: É provável que haja um **Snare/Clap** presente. Concentre-se no ataque (transientes) e no corpo desse elemento (200-500Hz) para que ele corte bem na mix.")
    elif energia_medios > -70:
        print("Elemento: Existe uma presença de médios. Considere a definição de seus elementos percussivos ou melódicos (sintetizadores, vocais) nessa faixa (250Hz-4kHz).")

    # Tentativa de identificar Hi-Hats
    if energia_agudos > -70 and len(onset_frames) / duracao_seg > 2.5:
        print("Elemento: Parece haver **Hi-Hats** ou **Pratos** ativos. Verifique se eles não estão excessivamente estridentes ou 'chiantes'. Um 'high-shelf' levemente atenuado acima de 10kHz pode suavizar.")
    elif energia_agudos > -80:
        print("Elemento: Há alguma informação nos agudos. Garanta que seus elementos de alta frequência (pads, arps, ruídos) não estejam competindo negativamente com a percussão ou vocais.") 


except FileNotFoundError:
    print(f"Erro: O arquivo '{NOME_ARQUIVO_AUDIO}' não foi encontrado na mesma pasta do script.")
    print("Verifique se o nome do arquivo está correto e se ele está na pasta certa.")
except Exception as e:
    print(f"Ocorreu um erro ao processar o áudio: {e}")
    print("Certifique-se de que o FFmpeg está instalado e no PATH, e que o arquivo de áudio não está corrompido.")
    print(f"Detalhes do erro: {e}")