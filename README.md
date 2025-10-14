# 30 Minute Vibe Coding Challenge Projekter

Dette repository indeholder projekter skabt under **30 Minute Vibe Coding Challenge** på [Kasper Junges YouTube-kanal](https://www.youtube.com/@KasperJunge).

## Om Udfordringen

30 Minute Vibe Coding Challenge er en serie, hvor projekter bygges fra bunden på kun 30 minutter, der demonstrerer hurtig prototyping og AI-assisteret udviklingsteknikker.

## Sådan Virker Det

Dette repository tilbyder et simpelt script til at bootstrap nye projekter med prækonfigurerede kommandoskabeloner til AI-assistenter (Claude og Cursor).

### Struktur

- `context-engineering/` - Context engineering filer til AI-assistenter
  - `commands/` - Template markdown filer der definerer AI-assistent kommandoer
    - `sdd/` - Spec-Driven Development workflow (til greenfield projekter)
    - `rpi/` - Research-Plan-Implement workflow (til eksisterende codebases)
  - `rules/` - Tilpassede regler for AI-adfærd
- `templates/` - Projekt skabeloner der kan bruges til at initialisere nye projekter
- `projects/` - Her oprettes nye projekter
- `cli.py` - CLI script til at oprette nye projekter

### AI-Assistent Workflows

Dette projekt inkluderer to forskellige workflows til forskellige scenarier:

#### 🌱 Spec-Driven Development (SDD)
**Hvornår:** Når du bygger nye projekter fra bunden (greenfield)

**Kommandoer:**
1. `clarify_requirements.md` - Afklarer projektkrav gennem spørgsmål
2. `clarify_design.md` - Afklarer teknisk design og arkitektur
3. `create_plan.md` - Skaber detaljeret implementeringsplan
4. `implement_plan.md` - Implementerer planen med tests

**Flow:** Requirements → Design → Plan → Implement

#### 🔍 Research-Plan-Implement (RPI)
**Hvornår:** Når du modificerer eller udvider eksisterende codebases (brownfield)

**Kommandoer:**
1. `research_codebase.md` - Undersøger og forstår eksisterende kodebase
2. `create_plan.md` - Skaber plan for ændringer baseret på research
3. `implement_plan.md` - Implementerer ændringerne

**Flow:** Research → Plan → Implement

### Opsætning

Installer først dependencies med `uv`:

```bash
uv sync
```

### Brug

CLI'en tilbyder to hovedkommandoer:

**Opret et nyt projekt:**

```bash
uv run vibe new <projekt-navn>
```

**Opret et nyt projekt fra en skabelon:**

```bash
uv run vibe new <projekt-navn> --template <skabelon-navn>
```

**Vis tilgængelige skabeloner:**

```bash
uv run vibe list
```

**Yderligere muligheder:**

```bash
# Åbn ikke projektet i Cursor automatisk
uv run vibe new <projekt-navn> --no-open

# Vis version
uv run vibe --version

# Vis hjælp
uv run vibe --help
```

Dette vil:
1. Oprette en ny mappe under `projects/<projekt-navn>/`
2. Kopiere skabelonfiler hvis `--template` er angivet
3. Oprette `.claude/commands/` og `.cursor/commands/` undermapper
4. Kopiere begge workflow sets (sdd + rpi) fra `context-engineering/commands/` til begge undermapper
5. Åbne projektet i Cursor (medmindre `--no-open` er angivet)

### Eksempler

Opret et tomt projekt:
```bash
uv run vibe new min-fede-app
```

Opret et projekt fra FastAPI skabelonen:
```bash
uv run vibe new min-fede-app --template fastapi-sqlite-jinja2
```

Vis tilgængelige skabeloner:
```bash
uv run vibe list
```

Opret et projekt uden at åbne det i Cursor:
```bash
uv run vibe new min-fede-app --no-open
```

### Tilgængelige Skabeloner

- **fastapi-sqlite-jinja2** - FastAPI web app med SQLite database og Jinja2 templates

Nu kan du starte din 30-minutters kodningsudfordring med AI-assistent kommandoer klar til brug! 🎵
