from flask import Flask, render_template, request, jsonify, send_from_directory  # Incluído send_from_directory
import os
import librosa
import numpy as np
from pydub import AudioSegment
from sklearn.model_selection import train_test_split  # Para dividir dados em treino/teste
from sklearn.linear_model import LogisticRegression   # Um modelo de classificação simples
from sklearn.metrics import accuracy_score            # Para avaliar o modelo
from werkzeug.utils import secure_filename  # Adicione esta importação no topo
import traceback



app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/' # Pasta onde os arquivos serão temporariamente salvos
app.config['ALLOWED_EXTENSIONS'] = {'mp3', 'wav'} # Extensões de áudio permitidas

# Garante que a pasta de uploads exista
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Função para analisar o arquivo de áudio
def analyze_audio_file(filepath):
    # --- Início do Bloco de Treinamento do Modelo ML (Passo 2) ---
    # 1. Criando um dataset fictício (bem simples para começar)
    # Features: [energia_graves, energia_medios, energia_agudos]
    # Labels: 0 para 'graves OK', 1 para 'graves dominantes'
    
    X_ficticio = np.array([
        [0.6, 0.3, 0.1],  # Exemplo 1: Graves altos, médios ok, agudos baixos -> Graves Dominantes (1)
        [-5, -8, -7],     # Exemplo 2: Graves moderados, médios ok, agudos ok -> Graves OK (0)
        [2, -3, -5],      # Exemplo 3: Graves muito altos -> Graves Dominantes (1)
        [-10, -12, -10],  # Exemplo 4: Todos baixos, mas equilibrados -> Graves OK (0)
        [-2, -15, -18],   # Exemplo 5: Graves mais presentes que outros muito baixos -> Graves Dominantes (1)
        [-8, -7, -9]      # Exemplo 6: Equilibrado -> Graves OK (0)
    ])
    y_ficticio = np.array([
        1,  # Graves Dominantes
        0,  # Graves OK
        1,  # Graves Dominantes
        0,  # Graves OK
        1,  # Graves Dominantes
        0   # Graves OK
    ])

    # 2. Treinando um modelo de Regressão Logística simples
    # Em um projeto real, você dividiria em treino/teste (ex: com train_test_split)
    # e usaria um dataset muito maior e mais realista.
    model = LogisticRegression(solver='liblinear') # 'liblinear' é bom para datasets pequenos
    try:
        model.fit(X_ficticio, y_ficticio)
        print("Modelo de ML treinado com sucesso (dataset fictício).") # Log para o terminal do servidor
    except Exception as e:
        print(f"Erro ao treinar o modelo de ML: {e}")
        # Lidar com o erro, talvez não fazer a predição se o treino falhar
    # --- Fim do Bloco de Treinamento do Modelo ML ---
    results = []
    try:
        # --- Pydub: Carregar e obter informações básicas ---
        audio_pydub = AudioSegment.from_file(filepath)
        results.append(f"Arquivo de áudio '{os.path.basename(filepath)}' carregado com sucesso pelo pydub!")

        duracao_ms = len(audio_pydub)
        duracao_seg = duracao_ms / 1000.0
        duracao_min = duracao_seg / 60.0
        canais = audio_pydub.channels
        sample_rate_pydub = audio_pydub.frame_rate
        bits_por_amostra = audio_pydub.sample_width * 8
        volume_dbfs = audio_pydub.dBFS

        results.append(f"\n--- Informações do Áudio (Pydub) ---")
        results.append(f"Duração: {duracao_seg:.2f} segundos ({duracao_min:.2f} minutos)")
        results.append(f"Canais: {canais} (1=Mono, 2=Estéreo)")
        results.append(f"Taxa de Amostragem (Sample Rate): {sample_rate_pydub} Hz")
        results.append(f"Bits por Amostra: {bits_por_amostra} bits")
        results.append(f"Volume Médio (dBFS): {volume_dbfs:.2f} dBFS")

        # --- Librosa: Preparar áudio para análise ---
        # Força o resample para 22050 Hz para economizar memória no servidor
        y, sr = librosa.load(filepath, sr=22050)
        results.append(f"Áudio carregado com sucesso pelo librosa. Sample Rate: {sr} Hz")

        onset_frames = librosa.onset.onset_detect(y=y, sr=sr)

        # --- ANÁLISE DE BPM (com Librosa) ---
        results.append(f"\n--- Análise de Ritmo (Librosa) ---")
        tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
        results.append(f"BPM Detectado: {tempo.item():.2f}")

        # --- Sugestões da IA (Volume e BPM) ---
        results.append(f"\n--- Sugestões da IA (Volume e BPM) ---")
        if volume_dbfs < -20:
            results.append(f"Volume: O volume geral está um pouco baixo ({volume_dbfs:.2f} dBFS). Considere aumentar o ganho da faixa em aproximadamente 3-6 dB para melhor impacto.")
        elif volume_dbfs > -5:
            results.append(f"Volume: O volume geral está alto ({volume_dbfs:.2f} dBFS). Pode haver saturação ou clipping. Sugiro abaixar o ganho da faixa em aproximadamente 2-4 dB e verificar o headroom.")
        else:
            results.append(f"Volume: O volume parece adequado ({volume_dbfs:.2f} dBFS). Bom trabalho!")

        if tempo.item() < 120:
            results.append(f"BPM: O ritmo detectado ({tempo.item():.2f} BPM) é mais lento. Adequado para gêneros como Deep House, Chillout ou Downtempo. Se busca mais energia, um BPM entre 125-130 pode ser ideal.")
        elif tempo.item() > 140:
            results.append(f"BPM: O ritmo detectado ({tempo.item():.2f} BPM) é rápido. Bom para Drum and Bass, Hardstyle ou Trance acelerado. Verifique se essa velocidade é a intenção artística, pois pode ser desafiador para a pista de dança.")
        else:
            results.append(f"BPM: O ritmo detectado ({tempo.item():.2f} BPM) está em uma faixa comum (120-140 BPM) para muitos gêneros de música eletrônica, como House, Techno e Trance.")

        # --- ANÁLISE DE HARMONIA/CHAVE MUSICAL (com Librosa) ---
        results.append(f"\n--- Análise Harmônica (Librosa) ---")
        chroma = librosa.feature.chroma_stft(y=y, sr=sr)
        keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        chroma_means = np.mean(chroma, axis=1)
        chroma_means_norm = chroma_means / np.sum(chroma_means)
        major_template = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
        minor_template = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])
        major_template_norm = major_template / np.sum(major_template)
        minor_template_norm = minor_template / np.sum(minor_template)
        best_correlation = -1
        detected_key = "Não detectada"
        for i in range(12):
            root_note = keys[i]
            shifted_chroma = np.roll(chroma_means_norm, -i)
            major_corr = np.dot(shifted_chroma, major_template_norm)
            minor_corr = np.dot(shifted_chroma, minor_template_norm)
            if major_corr > best_correlation:
                best_correlation = major_corr
                detected_key = f"{root_note} Major"
            if minor_corr > best_correlation:
                best_correlation = minor_corr
                detected_key = f"{root_note} Minor"
        results.append(f"Chave Musical Detectada: {detected_key}")

        # --- Sugestões Adicionais da IA (baseadas na Chave) ---
        results.append(f"\n--- Sugestões Adicionais da IA (Harmonia) ---")
        if detected_key != "Não detectada":
            results.append(f"Sugestão de Harmonia: A chave detectada é {detected_key}. Considere construir sua melodia e acordes dentro dessa chave para garantir a coesão harmônica.")
            if "Major" in detected_key:
                results.append("Essa é uma chave maior, geralmente associada a sensações mais alegres e brilhantes.")
            elif "Minor" in detected_key:
                results.append("Essa é uma chave menor, frequentemente associada a sensações mais melancólicas ou dramáticas.")
        else:
            results.append("Sugestão de Harmonia: Não foi possível detectar uma chave musical clara. Isso pode acontecer com áudios complexos ou atonais. Se for uma faixa melódica, tente simplificar ou focar em uma progressão mais clara.")

        # --- ANÁLISE DE ESPECTRO/FREQUÊNCIAS (com Librosa) ---
        results.append(f"\n--- Análise de Frequências (Librosa) ---")
        D = librosa.stft(y, n_fft=2048, hop_length=512)
        S_db = librosa.amplitude_to_db(np.abs(D), ref=np.max)
        freqs = librosa.fft_frequencies(sr=sr, n_fft=2048)
        idx_graves = np.where((freqs >= 20) & (freqs < 250))[0]
        idx_medios = np.where((freqs >= 250) & (freqs < 4000))[0]
        idx_agudos = np.where((freqs >= 4000) & (freqs <= 20000))[0]
        energia_graves = np.mean(S_db[idx_graves]) if len(idx_graves) > 0 else -np.inf
        energia_medios = np.mean(S_db[idx_medios]) if len(idx_medios) > 0 else -np.inf
        energia_agudos = np.mean(S_db[idx_agudos]) if len(idx_agudos) > 0 else -np.inf
        # --- Início do Bloco de Predição do Modelo ML (Passo 3) ---
        try:
            # 1. Criar o vetor de features para o áudio atual
            # Certifique-se que 'energia_graves', 'energia_medios', 'energia_agudos' já foram calculados
            # e estão disponíveis neste ponto do código.
            # Os valores podem precisar de alguma normalização ou escalonamento em um projeto real
            # para corresponder à escala dos dados de treinamento. Para nosso exemplo simples, usamos direto.
            feature_atual = np.array([[energia_graves, energia_medios, energia_agudos]])

            # 2. Fazer a predição com o modelo treinado
            predicao_ml = model.predict(feature_atual)
            probabilidade_predicao = model.predict_proba(feature_atual)

            # 3. Interpretar e exibir o resultado da predição
            resultado_predicao_texto = "Graves OK (segundo ML)" if predicao_ml[0] == 0 else "Graves Dominantes (segundo ML)"
            
            results.append(f"\n--- Análise de Machine Learning (Equilíbrio de Graves) ---")
            results.append(f"Predição do Modelo: {resultado_predicao_texto}")
            results.append(f"Probabilidades (0: OK, 1: Dominante): {np.round(probabilidade_predicao[0], 2)}")
            print(f"Predição ML para áudio atual: {resultado_predicao_texto}, Probabilidades: {probabilidade_predicao[0]}") # Log

        except NameError as ne:
            results.append(f"\n--- Análise de Machine Learning (Equilíbrio de Graves) ---")
            results.append(f"Aviso: Não foi possível fazer a predição ML. Variável não encontrada: {ne}")
            print(f"Erro na predição ML (NameError): {ne}")
        except Exception as e:
            results.append(f"\n--- Análise de Machine Learning (Equilíbrio de Graves) ---")
            results.append(f"Aviso: Erro durante a predição do modelo de ML: {e}")
            print(f"Erro na predição ML: {e}")
        # --- Fim do Bloco de Predição do Modelo ML ---
        results.append(f"Energia Média em Graves (20-250Hz): {energia_graves:.2f} dB")
        results.append(f"Energia Média em Médios (250Hz-4kHz): {energia_medios:.2f} dB")
        results.append(f"Energia Média em Agudos (4kHz-20kHz): {energia_agudos:.2f} dB")

        # --- Sugestões Adicionais da IA (Mixagem/Equalização) ---
        results.append(f"\n--- Sugestões Adicionais da IA (Mixagem/Equalização) ---")
        if energia_graves > (energia_medios + 5):
            results.append("Sugestão de Mixagem: Os graves parecem muito dominantes. Considere um pouco de 'sidechain compression' no baixo ou kick, ou ajuste a equalização para dar mais espaço aos médios.")
        elif energia_medios < (energia_graves - 10) and energia_medios < (energia_agudos - 10):
            results.append("Sugestão de Mixagem: A faixa pode estar 'oca' ou sem corpo. Verifique a energia nas frequências médias. Talvez alguns sintetizadores ou vocais precisem de mais presença nessa faixa.")
        elif energia_agudos > (energia_medios + 7):
            results.append("Sugestão de Mixagem: Há muita energia nos agudos. Isso pode causar fadiga auditiva. Considere um 'high-shelf EQ' suave ou um 'de-esser' em elementos como hi-hats ou pratos.")
        else:
            results.append("Sugestão de Mixagem: A distribuição de frequências gerais parece equilibrada. Bom trabalho na mixagem!")

        # --- IDENTIFICAÇÃO BÁSICA DE INSTRUMENTOS/SONS (Heurística) ---
        results.append(f"\n--- Identificação de Sons Básicos (Heurística) ---")
        if len(idx_graves) > 0 and S_db[idx_graves,:].size > 0:
            mean_spectrum_graves = np.mean(S_db[idx_graves, :], axis=1)
            peak_freq_idx_graves = np.argmax(mean_spectrum_graves)
            peak_freq_graves = freqs[idx_graves[peak_freq_idx_graves]]
        else:
            peak_freq_graves = 0

        results.append(f"\n--- Sugestões da IA (Instrumentos Básicos) ---")
        if tempo.item() > 60 and energia_graves > -40 and peak_freq_graves > 40 and peak_freq_graves < 100:
            results.append("Elemento: Parece haver um **Kick Drum** proeminente. Para um 'punch' ideal, assegure que não haja conflito de fase com o baixo e que as frequências de sub-graves (30-60Hz) estejam bem controladas.")
        elif tempo.item() > 60 and energia_graves > -50:
            results.append("Elemento: Há uma boa presença de graves. Revise a clareza e definição do seu **Kick/Bassline** para evitar 'embolamento' nessa faixa de frequência.")

        if energia_medios > -60 and len(onset_frames) / duracao_seg > 1.5:
            results.append("Elemento: É provável que haja um **Snare/Clap** presente. Concentre-se no ataque (transientes) e no corpo desse elemento (200-500Hz) para que ele corte bem na mix.")
        elif energia_medios > -70:
            results.append("Elemento: Existe uma presença de médios. Considere a definição de seus elementos percussivos ou melódicos (sintetizadores, vocais) nessa faixa (250Hz-4kHz).")

        if energia_agudos > -70 and len(onset_frames) / duracao_seg > 2.5:
            results.append("Elemento: Parece haver **Hi-Hats** ou **Pratos** ativos. Verifique se eles não estão excessivamente estridentes ou 'chiantes'. Um 'high-shelf' levemente atenuado acima de 10kHz pode suavizar.")
        elif energia_agudos > -80:
            results.append("Elemento: Há alguma informação nos agudos. Garanta que seus elementos de alta frequência (pads, arps, ruídos) não estejam competindo negativamente com a percussão ou vocais.")

        return "\n".join(results)
    except FileNotFoundError:
        print(f"Erro em analyze_audio_file: Arquivo não encontrado - {filepath}")
        print(traceback.format_exc())  # Adicionado para debug
        return "Erro: O arquivo de áudio não foi encontrado no servidor (dentro da análise).", 404
    except Exception as e:
        print(f"Erro em analyze_audio_file: {e} - filepath: {filepath}")
        print("--- TRACEBACK (analyze_audio_file) ---")  # Marcador
        print(traceback.format_exc())  # LINHA IMPORTANTE PARA ADICIONAR
        print("--------------------------------------")
        return f"Ocorreu um erro inesperado ao processar o áudio: {str(e)}", 500

def allowed_file(filename):
    """
    Verifica se o arquivo possui uma extensão permitida.
    Retorna True se permitido, False caso contrário.
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    # Renderiza a página inicial
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """
    Rota para upload e análise de arquivo de áudio.
    Retorna JSON com resultado ou mensagem de erro.
    """
    # Verifica se o campo do arquivo está presente na requisição
    if 'audio_file' not in request.files:
        return jsonify(error='Nenhum arquivo enviado!'), 400

    file = request.files['audio_file']

    # Verifica se algum arquivo foi selecionado
    if file.filename == '':
        return jsonify(error='Nenhum arquivo selecionado!'), 400

    # Verifica se o arquivo é permitido e processa o upload
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        try:
            file.save(filepath)
            resultado_analise = analyze_audio_file(filepath)

            # Se a análise retornar erro, responde com mensagem e status apropriado
            if isinstance(resultado_analise, tuple):
                mensagem_erro, codigo_status_erro = resultado_analise
                return jsonify(error=mensagem_erro), codigo_status_erro
            else:
                # Sucesso: retorna resultado da análise E O NOME DO ARQUIVO
                return jsonify(success=True, results=resultado_analise, filename=filename), 200

        except Exception as e:
            # Log detalhado para debug em caso de erro inesperado
            print(f"Erro no upload_file antes da análise ou erro inesperado: {e}")
            print("--- TRACEBACK (upload_file) ---")
            print(traceback.format_exc())
            print("-------------------------------")
            return jsonify(error=f"Ocorreu um erro no servidor durante o upload ou preparação: {str(e)}"), 500
    else:
        # Arquivo não permitido ou inválido
        return jsonify(error='Tipo de arquivo não permitido ou falha no arquivo.'), 400

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    """
    Rota para servir os arquivos que foram enviados para a pasta UPLOAD_FOLDER.
    """
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)  # Mude para False