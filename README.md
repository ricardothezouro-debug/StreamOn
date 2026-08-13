# Stream Ligar

App companheiro do **Streamer Sidekick** que prepara tudo para a live: abre o
**NVIDIA Broadcast**, o **OBS**, o **Streamer Sidekick** e os painéis de
transmissão (**YouTube Studio** + **Twitch Dashboard** no Chrome, perfil Ricardo)
— na ordem certa e com um clique.

Visual alinhado ao Streamer Sidekick (paleta neon, painéis de canto cortado,
tipografia Bahnschrift) e estrutura preparada para, no futuro, ser acoplado como
um plugin do Sidekick.

## Dois executáveis

| Executável | Para quê |
|------------|----------|
| **Stream Ligar.exe** | O launcher. Botão **LIGAR LIVE** abre a sequência e mostra o progresso ao vivo. |
| **Config.exe** | Editor: escolha quais apps/links abrir, a ordem, e o **delay** entre eles. |

O launcher também tem o botão **Configurar**, que abre a mesma tela do `Config.exe`.

## Configuração padrão (já vem pronta)

1. NVIDIA Broadcast — delay 4s
2. OBS Studio — delay 5s
3. Streamer Sidekick — delay 3s
4. Chrome (perfil **Ricardo** / `Profile 2`) abrindo YouTube Studio + Twitch

### Tipos de item

- **Programa (.exe)** — caminho do executável, argumentos opcionais e pasta de
  trabalho opcional (vazio = pasta do próprio `.exe`, importante para o OBS).
- **Chrome (perfil + abas)** — escolhe um perfil do Chrome (detectados
  automaticamente pelo nome, ex.: *Ricardo*) e uma lista de URLs, cada uma vira
  uma aba na mesma janela.
- **Link (navegador padrão)** — abre uma URL no navegador padrão do Windows.

Cada item tem um **delay (segundos)** aplicado *depois* de abri-lo, dando tempo do
programa carregar antes do próximo. Itens podem ser reordenados (↑/↓),
duplicados, desativados ou removidos.

A configuração fica em `%APPDATA%\StreamLigar\config.json`.

## Rodar do código-fonte

```bash
pip install -r requirements.txt
# launcher
python -m stream_ligar            # (a partir de src no PYTHONPATH)
# ou:
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

## Acoplar ao Streamer Sidekick (futuro)

O Sidekick carrega ferramentas como *módulos* descritos por
`ModuleInfo(module_id, title, subtitle, status, accent)` e mostrados como cards
no hub, cada um com sua página no `QStackedWidget`.

O arquivo [`src/stream_ligar/module.py`](src/stream_ligar/module.py) é a costura:

- `module_info()` devolve o card (usa a classe `ModuleInfo` do próprio Sidekick
  quando ele está importável, senão uma cópia local compatível).
- `build_page(config)` devolve o `LauncherPage` (a mesma página usada no app
  standalone) pronto para ser inserido no hub.

Para plugar, no `app.py` do Sidekick bastaria:

```python
from stream_ligar.module import module_info, build_page
modules.register(module_info())
# e adicionar build_page(config) como página "launcher" no hub
```

Como o tema é aplicado no `QApplication` inteiro, a página assume o visual do
Sidekick automaticamente.

## Estrutura

```
src/stream_ligar/
  core/        config, launcher (thread + delays), chrome profiles, paths
  ui/          theme, components (NeonPanel…), launcher_window, config_window
  module.py    adaptador de plugin para o Streamer Sidekick
  launcher_main.py / config_main.py   entradas dos dois executáveis
packaging/stream_ligar.spec           PyInstaller (2 exes, pasta compartilhada)
scripts/                              make_icon.py, build_exe.ps1
```
