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

`node --test tests/*.test.mjs`: isolamento da troca de kick e stems idênticos, bloqueios, duração/arranjo, WAV, MIDI, validação e autenticação/origem. 14 testes automatizados aprovados. QA visual pelo navegador de teste, incluindo renderização, substituição, aprovação, criação de pistas e persistência. O fluxo com login real na nuvem ainda precisa ser validado pelo titular. WebMCP não foi disponibilizado pelo navegador local de teste.
SQL de criação em database.sql. Mudanças são aditivas, sem tocar tabelas do CRM. Credenciais privilegiadas não são necessárias.
