# AI Music Studio 0.3

Continuação do projeto Vercel `ai-music-studio-tiagolif` (prj_AmnUsxJgSaNGLZsfH0q7s7nTRXSc).
Este diretório é independente do app Python existente no repositório e não o substitui.

## Executar

Node 24, sem dependências externas. `npm test` e `npm run dev -- --port 4173`.
Deploy: raiz deste diretório, framework Other, output `public`, sem build/install command.
Vercel empacota `api/*.js` como Functions Node; arquivos compartilhados em public e lib.

## Implementado

- Seis pistas iniciais, criação/remoção até 16 pistas independentes; 15 presets originais, substituição com preservação de ritmo.
- Mixer por pista (volume/pan/filtro/decay/transposição/mute/solo), swing, BPM e tonalidade.
- Arranjo por seções até 64 compassos e seleção de instrumentos por seção.
- Edição de notas relativas; export MIDI multitrack (sons e efeitos não são incorporados ao MIDI).
- Import samples até 8s/10MB, áudio mono interno; origem/licença informada pelo usuário.
- IndexedDB com áudio, backups JSON completos, migração da versão anterior, histórico/desfazer/refazer.
- A/B por referência salva, bloqueio explícito de pistas aprovadas e marcos com avaliação.
- WAV estéreo 44.1k/16-bit e stems, renderização em Web Worker; proteção de pico e medição RMS.
- Supabase: tabelas exclusivas music_studio_projects/music_studio_versions e bucket privado music-studio no projeto ativo existente; RLS por auth.uid, nenhum service role no app.
- API com JWT de usuário, concorrência otimista por revisão, marcos e renderização remota com upload privado.
- MCP remoto stateless autenticado e ferramentas WebMCP condicionais na página.

## Autenticação e limitações

A nuvem usa conta de usuário Supabase existente (e-mail/senha). Não usa credenciais da conta administrativa do Supabase. Não existe signup na interface, para não interferir nas regras do CRM existente.
Tokens ficam somente no sessionStorage da aba e o refresh é validado pela API. A chave publishable é pública por definição; acesso aos dados depende das políticas RLS. Logout remove a sessão local; não revoga outros dispositivos.
MCP remoto aceita JWT de usuário e exige cliente que renove a sessão. Ainda não há fluxo OAuth dedicado ao ChatGPT; disponibilizar o endpoint não configura o conector automaticamente.
WebMCP funciona somente onde document.modelContext é fornecido pelo navegador do assistente.
Não há geração de canto, modelo Suno/Stable Audio contratado, VST, timestretch, compressor/sidechain ou masterização LUFS. Samples/loops licenciados comerciais não foram incorporados.
Render remoto é síncrono, não fila durável. Arranjos longos geram arquivos grandes e usam cotas de Storage/Functions existentes.

## Testes

`node --test tests/*.test.mjs`: isolamento da troca de kick e stems idênticos, bloqueios, duração/arranjo, WAV, MIDI, validação e autenticação/origem. 14 testes automatizados aprovados. QA visual pelo navegador de teste, incluindo renderização, substituição, aprovação, criação de pistas e persistência. O fluxo com login real na nuvem ainda precisa ser validado pelo titular. WebMCP foi verificado no endereço HTTPS publicado: leitura, marco e substituição isolada de kick preservaram as outras cinco pistas. Na prévia HTTP local o registro não é disponibilizado.
SQL de criação em database.sql. Mudanças são aditivas, sem tocar tabelas do CRM. Credenciais privilegiadas não são necessárias.

## 0.3.1 — reprodução e diagnóstico

O transporte principal agora reproduz o WAV renderizado em um elemento HTML audio nativo, sem precisar iniciar um AudioContext em tempo real. A sessão é pré-renderizada após o carregamento e alterações; Ouvir seção, comparação A/B e testes individuais também usam o player nativo. Pistas e arquivos de exportação continuam usando o mesmo motor.

A interface só informa reprodução após o evento playing, apresenta erros de decodificação/autoplay, detecta render silencioso e mostra posição real do arquivo. A preparação não inicia reprodução automaticamente. Em navegadores que exigem gesto após a preparação, o usuário pode tocar no controle nativo visível.

/api/sound-test fornece um MP3 mono de 500 Hz por 2 segundos, com suporte a Range/HEAD, independente de sessão, mixer, banco de dados e Web Audio. Esse teste não mede a saída física do aparelho: a confirmação de audibilidade ainda depende de quem está ouvindo.

21 testes automatizados aprovados. QA no navegador confirma WAV carregado (readyState 4), relógio avançando e muted=false. Não foi possível testar o alto-falante do celular do usuário.

A inicialização tolera IndexedDB bloqueado, negado ou sem resposta: o estúdio continua em sessão temporária, com aviso para exportar backup, em vez de deixar todos os controles inativos.

## 0.4.0 — samples reais e padrões por seção

Sete samples acústicos VCSL CC0 são distribuídos localmente, sob demanda, com commit de origem, URL e hashes SHA-256 no catálogo. Preview não altera a sessão; Adicionar preserva o áudio no backup e no armazenamento já existente. A importação verifica integridade. São gravações acústicas, não um pack eletrônico profissional. Reconstrução: `python scripts/prepare-library.py` (Python, ffmpeg e rede); o commit realmente usado consta no catálogo.

Seções aceitam `patterns: { [trackId]: steps }`, opcional e compatível com sessões schemaVersion 3 existentes. `set_section_steps` altera apenas os 16 passos da pista na seção indicada; `clear_section_steps` restaura herança do padrão base. Render, MIDI, API e WebMCP usam os mesmos eventos. Aprovação impede alterações por seção. Timbre e mixer continuam globais por pista.

Novas sessões iniciam o baixo duas oitavas abaixo. Sessões salvas são preservadas. Clap tight e wide agora têm envelopes diferentes. Não há GPU, nova assinatura, serviço pago ou inferência generativa adicionada.

Cada pista permite registrar `soundBrief` (até 500 caracteres) para orientar escolhas de timbre. É memória explícita do projeto, incluída no backup, versões e comandos do assistente; não retreina um modelo.

## 0.4.1 — revisão de síntese e Primeiro Groove B

Novos projetos usam `engineVersion: 2`. Projetos sem essa propriedade mantêm o motor anterior para preservar o áudio de referência. Samples gravados usam o mesmo caminho nos dois motores. A revisão sintetizada adiciona fade de ataque/release até zero, bloqueio DC, kick com sweep mais rápido, baixo aditivo com harmônicos e hi-hat de ruído em banda. Harmônicos acima do limite de Nyquist são omitidos. Não inclui sidechain, reverb, masterização ou julgamento perceptivo automatizado.

Acordes do motor 2 usam `chordIntervals` explícito (até oito intervalos) e são exportados como notas no MIDI; renomear uma pista não muda sua síntese. Projetos antigos mantêm o comportamento de acordes anterior.

`lib/revise-first-groove.js` corrige terças maiores do baixo e cria viradas de um compasso sem mudar a duração total. `scripts/render-groove-revision.mjs` recebe backup de entrada e diretório de saída opcionais; preserva a fonte e inclui a versão A no backup B. Os ganhos de A/B não são normalizados separadamente. A revisão continua aguardando avaliação auditiva.

O botão Abrir Primeiro Groove B carrega o exemplo e os três samples locais. A sessão anterior é guardada separadamente no mesmo armazenamento do navegador e pode ser restaurada pelo botão de retorno. Em modo de armazenamento temporário esse retorno só dura enquanto a aba estiver aberta. A comparação A/B usa a posição em compassos para alinhar as seções subdivididas.

## 0.5.0 — Maré de Dentro

Produção instrumental de 42 compassos, 122 BPM, Lá menor, 12 pistas, 16 seções. Piano Kawai A4 e conga VCSL CC0 adicionados ao catálogo, com fontes e hashes; piano monossample, não um instrumento multiamostrado. `scripts/prepare-production-samples.py` reproduz a conversão. `scripts/create-mare-production.mjs [output]` gera backup, MIDI e WAV usando o mesmo motor do site.

`productionMix: true` habilita o mixer local: corte de graves por pista, ducking com envoltória suave disparado pelos kicks ativos, ambiente de comb filters amortecidos e delay ping-pong a 3/16. Os controles de corte, ambiente, delay e ducking ficam nas pistas e em `set_track.fx`. A sessão usa ganho global fixo `productionGain`, não normalização independente de stems.

`gateBeats` limita a duração do sample, com fade final, e define note-off no MIDI. Notas do piano foram escritas para a amostra A4 e tonalidade A menor; o sampler ainda não faz mapeamento automático de várias amostras nem acompanha alterações do tom global. Efeitos são impressos no WAV; não são incorporados ao MIDI.

39 testes Node cobrem regressões, mixagem aditiva de stems, ducking condicionado ao kick, gate e notas da composição. A produção continua aguardando avaliação auditiva humana; os testes não certificam qualidade artística. Nenhum servidor pago, VST ou API generativa foi contratado.
