# IA Musical Inteligente — Protótipo de Análise de Áudio

Protótipo web em **Python + Flask** para análise técnica de arquivos de áudio, combinando extração de características com `librosa`, processamento com `pydub` e experimentos simples de Machine Learning com `scikit-learn`.

**Autor:** Tiago Cunha de Souza

> **Status:** projeto experimental de portfólio. Não é uma ferramenta de masterização profissional e o componente atual de Machine Learning utiliza dados sintéticos/de demonstração, portanto suas classificações não devem ser tratadas como modelo validado.

---

## Objetivo

Explorar como técnicas de análise de sinal e Machine Learning podem apoiar produtores musicais na leitura de características de uma faixa.

O sistema recebe arquivos de áudio e gera informações e sugestões baseadas em métricas extraídas do próprio sinal.

---

## Recursos implementados

A implementação atual inclui experimentos com:

- upload de arquivos MP3 e WAV;
- duração, canais, sample rate e bit depth;
- volume médio em dBFS;
- detecção de BPM;
- análise cromática para estimativa de tonalidade;
- análise espectral por faixas de frequência;
- comparação de energia entre graves, médios e agudos;
- heurísticas para sugestões de mixagem;
- análise básica de transientes/onsets;
- protótipo de classificação de equilíbrio de graves usando regressão logística.

---

## Stack

- Python
- Flask
- Librosa
- Pydub
- NumPy
- scikit-learn
- SoundFile
- Gunicorn
- HTML/CSS/JavaScript no frontend do protótipo

---

## Arquitetura simplificada

```text
Arquivo de áudio
      ↓
Upload Flask
      ↓
Validação do arquivo
      ↓
Pydub + Librosa
      ↓
Extração de características
      ├── BPM
      ├── tonalidade estimada
      ├── volume
      ├── espectro
      └── energia por bandas
      ↓
Heurísticas + experimento ML
      ↓
Relatório para o usuário
```

---

## Executando localmente

### Pré-requisitos

- Python 3
- `ffmpeg` disponível no sistema para compatibilidade com formatos processados pelo Pydub

### Instalação

```bash
git clone "https://github.com/tiagolif/ia-musical-inteligente..git"
cd "ia-musical-inteligente."
python -m venv .venv
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Windows:

```powershell
.venv\Scripts\activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

Execute:

```bash
python app.py
```

---

## Sobre o componente de Machine Learning

O código contém uma regressão logística utilizada para experimentar o pipeline completo:

```text
features → treinamento → predição → interpretação
```

Neste estágio, o dataset de treinamento é **fictício e muito pequeno**, criado apenas para aprendizado e prova de conceito.

Isso significa que métricas ou classificações como “graves dominantes” **não possuem validade estatística suficiente para uso profissional**.

Uma evolução correta exigiria:

1. dataset real e suficientemente grande;
2. definição objetiva de labels;
3. separação treino/validação/teste;
4. normalização das features;
5. métricas de avaliação;
6. validação em músicas de diferentes gêneros;
7. versionamento do modelo.

---

## Heurísticas x IA

Parte das sugestões atuais é produzida por regras determinísticas baseadas em valores de volume, BPM e energia espectral.

Exemplo conceitual:

```text
SE energia_graves estiver muito acima dos médios
ENTÃO sugerir revisão de equilíbrio espectral
```

Essas regras são úteis para prototipação, mas não devem ser confundidas com inferência de um modelo treinado em produção.

---

## Melhorias planejadas

- separar análise de áudio da camada web;
- transformar features em estrutura JSON estável;
- adicionar testes automatizados;
- criar dataset real para experimentação;
- avaliar modelos de classificação/regressão adequados;
- adicionar visualizações de espectro e waveform;
- melhorar gestão de arquivos temporários;
- implementar limites de upload e segurança de produção;
- documentar métricas e resultados de avaliação.

---

## O que este projeto demonstra

Este projeto faz parte do meu portfólio e demonstra experiência prática com:

- Python;
- Flask;
- processamento de áudio;
- extração de features;
- integração frontend/backend;
- prototipação de Machine Learning;
- transformação de dados técnicos em uma experiência compreensível para o usuário.

---

## Nota sobre arquivos de demonstração

Arquivos de áudio presentes no repositório são utilizados apenas como material de teste do protótipo. Antes de reutilizar ou redistribuir qualquer mídia, verifique os direitos aplicáveis ao arquivo específico.
