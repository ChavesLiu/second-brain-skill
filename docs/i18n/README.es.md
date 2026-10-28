<div align="center">

<h1>🧠 Second Brain Skill</h1>

<p><strong>Construye tu propio segundo cerebro con IA</strong></p>

<p>
  Inspirado en <a href="https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f">LLM Wiki de Karpathy</a>.<br>
  Una base ligera y extensible para crear una base de conocimiento en evolución continua.
</p>

<p>
  <a href="https://github.com/ChavesLiu/second-brain-skill/stargazers"><img src="https://img.shields.io/github/stars/ChavesLiu/second-brain-skill?style=flat-square" alt="Estrellas en GitHub"></a>
  <a href="https://github.com/ChavesLiu/second-brain-skill/network/members"><img src="https://img.shields.io/github/forks/ChavesLiu/second-brain-skill?style=flat-square" alt="Forks en GitHub"></a>
  <a href="../../LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue?style=flat-square" alt="Licencia MIT"></a>
  <img src="https://img.shields.io/badge/Claude_Code-Skill-blueviolet?style=flat-square" alt="Skill para Claude Code">
</p>

<p><a href="../../README.md">中文</a> | <a href="../../README.en.md">English</a> | <a href="README.ja.md">日本語</a> | <strong>Español</strong> | <a href="README.fr.md">Français</a> | <a href="README.ko.md">한국어</a></p>

</div>

---

## Descripción general

**Second Brain Skill** es una implementación de código abierto inspirada en el concepto [LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) de Andrej Karpathy. Convierte información personal dispersa en una wiki estructurada, interconectada y en constante evolución.

Ofrece una **base mínima, funcional y extensible** que cualquier desarrollador puede bifurcar (fork), personalizar y ampliar para construir su propio segundo cerebro.

### De la recuperación a la acumulación de conocimiento

**El RAG tradicional se parece a un intérprete; Second Brain Skill sigue un enfoque inspirado en un compilador.** Mientras que el RAG suele recuperar información relevante al consultar, aquí los LLM transforman progresivamente los materiales originales en una wiki estructurada y mantienen las relaciones entre fuentes, entidades y conceptos.

**RAG recupera conocimiento. LLM Wiki construye conocimiento.**

Tú seleccionas los materiales y planteas buenas preguntas. El LLM se encarga de resumir, crear referencias cruzadas, archivar y mantener la coherencia.

## Demostración

Observa cómo los materiales se convierten en una base de conocimiento estructurada e interconectada.

![Demostración del flujo help → init → ingest → query](https://raw.githubusercontent.com/ChavesLiu/second-brain-skill/refs/heads/main/docs/images/guide.gif)

## Arquitectura de tres capas

El proyecto separa los materiales originales, el conocimiento estructurado y las convenciones de funcionamiento.

| Capa | Ubicación | Escribe | Lee | Contenido |
| --- | --- | --- | --- | --- |
| **Materiales originales** | `raw/` | Tú | LLM | Artículos, notas, PDF, imágenes, investigaciones |
| **Base de conocimiento** | `wiki/` | LLM | Tú | Resúmenes, entidades, conceptos, análisis, enlaces |
| **Especificación** | `Skill` | Evolución conjunta | LLM | SCHEMA, flujos de trabajo, scripts |

Los materiales originales permanecen intactos mientras la wiki y sus convenciones evolucionan por separado.

## Inicio rápido

### 1. Instalación

Clona el repositorio, copia el Skill al directorio global de Claude Code e instala sus dependencias de Python:

```bash
git clone https://github.com/ChavesLiu/second-brain-skill.git
cp -r second-brain-skill/skills/wiki ~/.claude/skills/wiki
# Al actualizar una instalación existente, no sobrescribas settings.json ni registries.json locales
pip install -r ~/.claude/skills/wiki/scripts/requirements.txt
```

### 2. Inicializar una base de conocimiento

```text
/wiki init
```

La primera vez que uses cualquier función de `/wiki`, el Skill preguntará una sola vez el idioma de interacción predeterminado (`zh` / `en` / `ja` / `es` / `fr` / `ko`) y lo guardará como `interaction_language` en `<skill-dir>/settings.json`. En sesiones posteriores leerá esa configuración y no volverá a preguntar.

`/wiki init` solo pregunta la ruta y el nombre de la base de conocimiento. Las bases nuevas usan el idioma de interacción actual como idioma de contenido. Las bases existentes conservan el `language` de `registries.json` y no se traducen automáticamente; las entradas antiguas sin `language` se tratan como `zh`.

### 3. Incorporar el primer material

Coloca tus materiales en el directorio `raw/` de la base de conocimiento:

```bash
cp my-article.md ~/my-kb/raw/
```

```text
/wiki ingest
```

El LLM lee el material, genera resúmenes, extrae entidades y conceptos y mantiene referencias cruzadas. Una incorporación puede crear o actualizar entre 10 y 15 páginas, según el material.

### 4. Consultar tu conocimiento

```text
/wiki query ¿Qué es Memex?
```

```text
Compara las ventajas y desventajas de RAG frente al enfoque Wiki
```

También puedes preguntar en lenguaje natural. El LLM utiliza el conocimiento acumulado para relacionar información y responder. Las interacciones de UI y las respuestas usan el idioma de interacción actual; las páginas y registros de la wiki usan el `language` propio de esa base.

## Comandos principales

| Comando | Función |
| --- | --- |
| `/wiki help` | Mostrar la ayuda y la lista de comandos disponibles |
| `/wiki init` | Crear y registrar una base de conocimiento |
| `/wiki language` | Mostrar el idioma de interacción actual |
| `/wiki language <zh|en|ja|es|fr|ko>` | Cambiar el idioma de la UI y el idioma predeterminado de nuevas bases |
| `/wiki ingest` | Incorporar materiales (Markdown, PDF, imágenes) |
| `/wiki query <pregunta>` | Responder usando la base de conocimiento |
| `/wiki lint` | Comprobar la salud y coherencia de la wiki |
| `/wiki wipe` | Eliminar o reiniciar páginas de la wiki (recuperable desde `wiki/.trash/`) |
| `/wiki test` | Ejecutar pruebas automáticas |

Al eliminar o reiniciar contenido, las páginas se trasladan a `wiki/.trash/` y pueden recuperarse con `/wiki wipe restore`; `raw/` no se modifica. `/wiki wipe empty-trash` vacía la papelera de forma permanente: después solo puede recuperarse contenido guardado previamente en el historial de Git.

Todos los comandos también admiten instrucciones en lenguaje natural: no necesitas memorizarlos.

## Modo de lenguaje natural

El Skill reconoce tu intención y ejecuta la acción correspondiente.

| Lo que dices | Acción |
| --- | --- |
| «Incorpora este artículo» | Incorporar material |
| «¿Qué es Memex?» | Consultar la wiki |
| «Compara RAG y Wiki» | Recuperar y sintetizar conocimiento |
| «Cita siempre las fuentes» | Guardar la preferencia en `conventions.md` |
| «Revisa la base de conocimiento» | Comprobar su estado |

También funciona con interfaces conversacionales como OpenClaw, siempre que el entorno tenga acceso al Skill, a la base de conocimiento y a las herramientas necesarias.

## Integración con Obsidian

Abre la base de conocimiento Markdown en [Obsidian](https://obsidian.md/) para explorar gráficos, enlaces entrantes y páginas.

![Vista de grafo de la base de conocimiento en Obsidian](https://raw.githubusercontent.com/ChavesLiu/second-brain-skill/refs/heads/main/docs/images/obsidian.png)

Complementos recomendados:

- **Front Matter Title** — Muestra títulos en los nodos del gráfico (preconfigurado; el idioma del título sigue el de la base de conocimiento)
- **Dataview** — Consultas de metadatos mediante frontmatter
- **Web Clipper** — Guarda artículos web en `raw/`

## OpenClaw (Web)

Second Brain Skill también puede integrarse con OpenClaw para gestionar conocimiento mediante conversación, pero no funciona «de fábrica» solo por abrir OpenClaw. Debes instalar el Skill en el entorno de OpenClaw, sincronizar o exponer la base de conocimiento y registrar en su memoria las rutas y reglas de uso. `settings.json` es configuración local del entorno: la instalación global de Claude Code y el entorno de OpenClaw guardan por separado el idioma de interacción y ajustes relacionados; no hay sincronización automática entre máquinas.

Con esa memoria configurada, OpenClaw puede reconocer materiales enviados por el usuario, guardarlos en `raw/` y lanzar la incorporación. Para enlaces web, como artículos de WeChat, el entorno también necesita herramientas de descarga o navegador (por ejemplo, Playwright) disponibles para que el LLM pueda abrir, guardar e incorporar el contenido.

![Demostración de incorporación automática con OpenClaw](https://raw.githubusercontent.com/ChavesLiu/second-brain-skill/refs/heads/main/docs/images/openclaw-wiki.gif)

Consulta la [guía de usuario — Integración con OpenClaw](../user-guide.en.md#openclaw-integration) para ver los pasos detallados.

## Estructura de directorios

La base de conocimiento mantiene esta estructura de directorios:

```text
~/my-kb/
├── raw/
│   ├── assets/
│   └── *.md / *.pdf
└── wiki/
    ├── index.md
    ├── log.md
    ├── overview.md
    ├── conventions.md
    ├── sources/
    ├── entities/
    ├── concepts/
    └── analyses/
```

| Ruta | Descripción |
| --- | --- |
| `raw/` | Materiales originales: los escribes tú y el LLM solo los lee |
| `raw/assets/` | Imágenes y adjuntos |
| `wiki/` | Base de conocimiento generada y mantenida por el LLM |
| `wiki/index.md` | Índice de contenido |
| `wiki/log.md` | Registro de operaciones |
| `wiki/overview.md` | Página de resumen |
| `wiki/conventions.md` | Convenciones de uso y preferencias |
| `wiki/sources/` | Páginas de resumen de materiales |
| `wiki/entities/` | Entidades, como personas, organizaciones y herramientas |
| `wiki/concepts/` | Conceptos, como teorías, métodos y patrones |
| `wiki/analyses/` | Análisis, comparaciones y síntesis |

## Casos de uso

- **Investigación** — Incorporar artículos académicos y construir conocimiento especializado
- **Lectura** — Procesar libros por capítulos y conectar personajes, temas y conceptos
- **Desarrollo personal** — Organizar diarios, artículos y notas de pódcasts
- **Análisis competitivo** — Seguir competidores y actualizar comparaciones
- **Conocimiento de equipo** — Organizar actas y documentación de proyectos

## Haz un fork y crea tu versión

Second Brain Skill es un **punto de partida, no un producto terminado**. Adapta su estructura, flujos y convenciones a tus necesidades, ya sea para investigación, un dominio especializado o un equipo. **Haz un fork. Personalízalo. Construye tu segundo cerebro.** ¡Se agradecen comentarios y contribuciones!

## Documentación

- **[Guía de usuario](../user-guide.en.md)** — Instalación, funciones, Obsidian y OpenClaw (en inglés)
- **[Filosofía de diseño](../../skills/wiki/IDEA.md)** — Principios inspirados en LLM Wiki (en chino)
- **[Documentación técnica del Skill](../../skills/wiki/README.en.md)** — Especificaciones, flujos y estructura (en inglés)

## Agradecimientos

- [Andrej Karpathy](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) — Por presentar la idea de LLM Wiki que inspiró este proyecto.

- [Vannevar Bush](https://en.wikipedia.org/wiki/Vannevar_Bush) — Por proponer Memex en 1945, antecedente de la gestión asociativa del conocimiento.

## Historial de estrellas

[![Gráfico del historial de estrellas](https://api.star-history.com/chart?repos=chavesliu/second-brain-skill&type=date&legend=top-left)](https://www.star-history.com/?repos=chavesliu%2Fsecond-brain-skill&type=date&legend=top-left)

## Licencia

Este proyecto se distribuye bajo la [licencia MIT](../../LICENSE).
