```markdown
# Professional Calculator

A fully‑featured desktop calculator application built with Python and NiceGUI.  
It combines a hand‑written expression engine (tokenizer → parser → evaluator) with a polished graphical interface that mimics a real Casio‑style device.

---

## Features

### Core Engine (Backend)
- **Tokenizer** – converts a raw string into tokens (numbers, operators, parentheses, functions).
- **Parser** – transforms infix tokens into Reverse Polish Notation (RPN) using the shunting‑yard algorithm.
- **Evaluator** – computes the RPN result with `Decimal` precision, catching division‑by‑zero, overflow, and other math errors.
- **History** – last 10 calculations stored as JSON, with clear and persistence.
- **Result namedtuple** – every evaluation returns `(success, value, error)` for clean error handling.

### Graphical Interface (GUI)
- **LCD Display** – styled `ui.scroll_area` with dark green phosphor‑glow text, right‑aligned, monospace font (Orbitron), and automatic scrolling.
- **Blinking Cursor** – a movable `|` cursor (arrow keys) that allows editing anywhere in the expression without clearing everything.
- **Button Grid** – 24 buttons arranged in a Casio‑style 6×4 grid with distinct colors:
  - Numbers (slate)
  - Operators (cyan)
  - Clear / Backspace (amber / slate)
  - Equals (cyan gradient, spans 2 rows)
- **Smart Operator Lock (CDM)** – binary operators are disabled until a valid digit or `)` is entered. Prevents malformed expressions like `++` or `*/`.
- **ON / OFF Ritual** – animated startup with `"HELLO"` and battery status; shutdown with `"GOODBYE"`. Buttons are dimmed and frozen when OFF.
- **Keyboard Support** – global key listener handles digits, operators, Enter, Backspace, Escape, and even `q`/`r` for √. A hidden focus‑input prevents ghost clicks.
- **Error Display** – inline error row below the LCD shows amber warnings (syntax errors) and red critical errors (division by zero, overflow).
- **Battery Indicator** – live battery percentage with expressive emoji (🔋⚡😟🆘) and plug‑in detection. Updates every 30 seconds. Desktops show `🖥️ DESKTOP`.
- **History Modal** – click the menu button (⋮) to view past calculations in a table; option to clear the log.
- **Fixed Native Window** – opens as a desktop window (no browser chrome), non‑resizable, 380×640px.

### Architecture & Testing
- **Modular backend** (`tokenizer.py`, `parser.py`, `evaluator.py`, `calculator.py`, `history.py`, `cli.py`, `definitions.py`)
- **91 unit tests** covering all layers with `pytest`.
- **Professional quality pipeline** – `black`, `isort`, `flake8`, `mypy`, `bandit` (all passing).
- **Double‑defense design**:
  - **CDM (Defensive Midfielder)** – GUI blocks bad input (smart buttons, length limit).
  - **CB (Center‑Back)** – Backend validates everything.
  - **GK (Goalkeeper)** – Evaluator catches math impossibilities.

---

## Running the Calculator

### From Source

1. **Clone the repository**
   ```bash
   git clone https://github.com/Tharana-Dev/professional-calculator.git
   cd professional-calculator
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   set PYTHONPATH=src && python -m calculator.gui
   ```
   (On PowerShell: `$env:PYTHONPATH="src"; python -m calculator.gui`)

4. **Run the backend tests**
   ```bash
   pytest tests/
   ```

### As a Standalone Executable (Windows)

The calculator is already packaged as an `.exe` using PyInstaller.  
Double‑click `Professional Calculator.exe` to launch without any terminal or Python installation.

---

## Project Structure

```
Calculator/
├── src/
│   └── calculator/
│       ├── __init__.py
│       ├── calculator.py      # Facade entry point
│       ├── cli.py             # Rich‑based CLI (alternative interface)
│       ├── definitions.py     # TokenType, Token, Operator, Result, HistoryRecord
│       ├── evaluator.py       # RPN evaluator (Decimal)
│       ├── history.py         # JSON persistence (10 records)
│       ├── parser.py          # Shunting‑yard to RPN
│       ├── tokenizer.py       # String → list[Token]
│       └── gui.py             # NiceGUI interface (all features)
├── tests/
│   ├── test_calculator.py
│   ├── test_cli.py
│   ├── test_evaluator.py
│   ├── test_history.py
│   ├── test_integration.py
│   ├── test_parser.py
│   └── test_tokenizer.py
├── pyproject.toml
├── requirements.txt
├── README.md
└── .gitignore
```

---

## Quality Pipeline

All checks pass with zero errors:

| Tool   | Command                        | Status |
|--------|--------------------------------|--------|
| black  | `black src/calculator/`        | ✅ |
| isort  | `isort src/calculator/`        | ✅ |
| flake8 | `flake8 src/calculator/`       | ✅ |
| mypy   | `mypy -p calculator`           | ✅ |
| bandit | `bandit -r src/calculator/`    | ✅ |
| pytest | `pytest tests/`                | 91 passed |

---

## Built With

- [Python 3.12](https://python.org)
- [NiceGUI](https://nicegui.io) – web‑based GUI framework
- [Rich](https://rich.readthedocs.io) – terminal formatting for the CLI
- [psutil](https://pypi.org/project/psutil/) – battery status
- [darkdetect](https://pypi.org/project/darkdetect/) – OS theme detection

---

## Author

**Tharana Dev** (Kalehe Waththgage Tharana Nimsara)  
- GitHub: [@Tharana-Dev](https://github.com/Tharana-Dev)  
- Built from scratch as part of a 150+ day self‑taught Python journey.

> *"The same mind that built a tokenizer can build anything."*

---

## License

This project is open source. You are free to use, modify, and share it.  
A formal license will be added soon.
```