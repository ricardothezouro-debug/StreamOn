# StreamOn

App companheiro do **Streamer Sidekick** que prepara tudo para a live: abre seus
programas e painéis de transmissão **na ordem certa e com um clique** — por
exemplo OBS, um software de câmera/áudio e os dashboards do YouTube/Twitch no
Chrome. Você define o que abrir; o StreamOn dispara a sequência com os delays
que você configurar.

Visual alinhado ao Streamer Sidekick (paleta neon, painéis de canto cortado,
tipografia Bahnschrift). Funciona standalone **ou** como plugin do Sidekick.

## Instalar como plugin do Streamer Sidekick

No Streamer Sidekick, seção **Plugins**, clique no card **"+"** e instale o
**StreamOn**. Ele é baixado direto deste repositório e passa a aparecer como um
card no hub, com sua própria página. Nenhuma configuração vem preenchida — você
monta a sua.

## Dois executáveis (modo standalone)

| Executável | Para quê |
|------------|----------|
| **Stream Ligar.exe** | O launcher. Botão **LIGAR LIVE** abre a sequência e mostra o progresso ao vivo. |
| **Config.exe** | Editor: escolha quais apps/links abrir, a ordem, e o **delay** entre eles. |

O launcher também tem o botão **Configurar**, que abre a mesma tela do `Config.exe`.

## Começa zerado

O StreamOn **não vem com nenhum item pré-configurado**. Na primeira vez, abra a
tela de configuração e adicione os seus. Cada item pode ser reordenado (↑/↓),
duplicado, desativado ou removido.

### Tipos de item

- **Programa (.exe)** — caminho do executável, argumentos opcionais e pasta de
  trabalho opcional (vazio = pasta do próprio `.exe`, importante para o OBS).
- **Chrome (perfil + abas)** — escolhe um perfil do Chrome (detectados
  automaticamente pelo nome) e uma lista de URLs, cada uma vira uma aba na mesma
  janela.
- **Link (navegador padrão)** — abre uma URL no navegador padrão do Windows.

Cada item tem um **delay (segundos)** aplicado *depois* de abri-lo, dando tempo do
programa carregar antes do próximo.

A configuração fica em `%APPDATA%\StreamLigar\config.json`.

## Rodar do código-fonte

```bash
pip install -r requirements.txt
# launcher
set PYTHONPATH=src && python -m stream_ligar
# editor
set PYTHONPATH=src && python -c "from stream_ligar.config_main import run; run()"
```

## Gerar os executáveis

```powershell
pip install -r requirements-build.txt
powershell -ExecutionPolicy Bypass -File scripts\build_exe.ps1
```

Saída em `dist\StreamLigar\` contendo **Stream Ligar.exe**, **Config.exe** e a
pasta compartilhada `_internal\`. É portátil — pode copiar a pasta inteira.

## Contrato de plugin do Sidekick

O Sidekick carrega ferramentas como *módulos* descritos por
`ModuleInfo(module_id, title, subtitle, status, accent)` e mostrados como cards
no hub, cada um com sua página no `QStackedWidget`.

O arquivo [`src/stream_ligar/module.py`](src/stream_ligar/module.py) é a costura:

- `module_info()` devolve o card (usa a classe `ModuleInfo` do próprio Sidekick
  quando ele está importável, senão uma cópia local compatível).
- `build_page(config=None)` devolve o `LauncherPage` pronto para ser inserido no
  hub. Standalone ele cria o próprio `ConfigStore`.

Como o tema é aplicado no `QApplication` inteiro, a página assume o visual do
Sidekick automaticamente.

## Estrutura

```
src/stream_ligar/
  core/        config, launcher (thread + delays), chrome profiles, paths
  ui/          theme, components (NeonPanel…), launcher_window, config_window
  module.py    adaptador de plugin para o Streamer Sidekick
  assets/brand/app_icon.png   ícone (power button) exibido no card do plugin
  launcher_main.py / config_main.py   entradas dos dois executáveis
packaging/stream_ligar.spec           PyInstaller (2 exes, pasta compartilhada)
scripts/                              make_icon.py, build_exe.ps1
```
