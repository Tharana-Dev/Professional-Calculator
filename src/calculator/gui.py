import asyncio

import psutil
from nicegui import app
from nicegui import events
from nicegui import ui

from calculator.calculator import evaluate
from calculator.history import clear_history
from calculator.history import get_history

# ----------------------------------------------------
# Style Constants
# ----------------------------------------------------
NUMBER_BTN = (
    "bg-slate-800 text-slate-100 font-bold text-lg rounded-lg h-12 "
    "transition-transform active:scale-95 duration-75"
)
OPERATOR_BTN = (
    "bg-cyan-700 text-white font-bold text-lg rounded-lg h-12 "
    "transition-transform active:scale-95 duration-75"
)
FUNC_BTN = (
    "bg-slate-800 text-cyan-400 font-bold rounded-lg h-12 "
    "transition-transform active:scale-95 duration-75"
)
CLEAR_BTN = (
    "bg-amber-600 text-white font-bold rounded-lg h-12 "
    "transition-transform active:scale-95 duration-75"
)
BACK_BTN = (
    "bg-slate-700 text-white font-bold rounded-lg h-12 "
    "transition-transform active:scale-95 duration-75"
)
EQUAL_BTN = (
    "bg-gradient-to-r from-cyan-500 to-blue-600 text-white font-black text-xl "
    "rounded-lg row-span-2 self-stretch transition-transform active:scale-95 duration-75 shadow-md"
)

POWER_ON = (
    "bg-emerald-600 text-white font-bold rounded-lg text-xs px-2 h-7 "
    "transition-all duration-150"
)
POWER_OFF = (
    "bg-rose-600 text-white font-bold rounded-lg text-xs px-2 h-7 "
    "transition-all duration-150"
)

# ----------------------------------------------------
# Global State
# ----------------------------------------------------
is_on = False
current_expr = ""
cursor_pos = 0  # cursor position in the expression
max_length = 255

# UI references
display_label = None
scroll_area = None
error_row = None
screen_container = None
power_btn = None
battery_label = None
history_dialog = None
history_table = None
hidden_focus = None  # invisible input that always holds focus

smart_buttons = {}


# ----------------------------------------------------
# Focus helper – keeps focus away from buttons
# ----------------------------------------------------
def refocus():
    global hidden_focus
    if hidden_focus:
        hidden_focus.run_method("focus")


# ----------------------------------------------------
# Display helper – renders expression with cursor
# ----------------------------------------------------
def render_display():
    global current_expr, cursor_pos, display_label, scroll_area
    if not current_expr:
        display_label.content = "0"
    else:
        before = current_expr[:cursor_pos]
        after = current_expr[cursor_pos:]
        # Build HTML: expression with a blinking cursor span
        html = before + '<span class="cursor-blink">|</span>' + after
        display_label.content = html
    scroll_area.scroll_to(percent=100)


# ----------------------------------------------------
# Battery & Power
# ----------------------------------------------------
def get_battery_icon(percent: float) -> str:
    if percent == 100:
        return "🔋"
    elif percent >= 75:
        return "⚡"
    elif percent >= 50:
        return "🥱"
    elif percent >= 20:
        return "😟"
    else:
        return "🆘"


def update_battery():
    refocus()
    try:
        bat = psutil.sensors_battery()
        if not bat:
            battery_label.set_text("🖥️ DESKTOP")
            return

        icon = get_battery_icon(bat.percent)
        plug = "🔌" if bat.power_plugged else ""
        battery_label.set_text(f"{icon}{plug}{bat.percent}%")

        if bat.percent < 20:
            battery_label.classes("animate-pulse")
        else:
            battery_label.classes(remove="animate-pulse")
    except Exception:
        battery_label.set_text("N/A")


async def toggle_power():
    refocus()
    global is_on, current_expr, cursor_pos, power_btn, display_label, screen_container

    if is_on == False:
        power_btn.props("loading")
        display_label.content = "HELLO"
        await asyncio.sleep(0.8)
        try:
            bat = psutil.sensors_battery()
            if bat:
                percent = bat.percent
                status = "⚡ PLUGGED IN" if bat.power_plugged else "🔋 ON BATTERY"
                display_label.content = f"BATTERY: {percent}%\n{status}"
            else:
                display_label.content = "NO BATTERY"
        except Exception:
            display_label.content = "BATTERY UNKNOWN"
        await asyncio.sleep(0.7)
        current_expr = ""
        cursor_pos = 0
        render_display()  # shows "0"
        is_on = True
        power_btn.props(remove="loading")
        power_btn.classes(replace=POWER_OFF)
        screen_container.classes(remove="opacity-20 pointer-events-none")
        update_button_states()
    elif is_on == True:
        display_label.content = "GOODBYE"
        if error_row:
            error_row.clear()
        screen_container.classes("opacity-20 pointer-events-none")
        await asyncio.sleep(1.0)
        current_expr = ""
        cursor_pos = 0
        display_label.content = "SYSTEM OFF"
        is_on = False
        power_btn.classes(replace=POWER_ON)
        update_button_states()


# ----------------------------------------------------
# Action and Error Functions
# ----------------------------------------------------
def append_character(char: str):
    refocus()
    global current_expr, cursor_pos
    if not is_on:
        return
    if len(current_expr) >= max_length:
        show_error("Maximum limit of 255 characters reached", critical=False)
        return

    clear_error()

    # Smart parenthesis toggling – inspect the character just before the cursor
    if char == "()":
        # char left of cursor (if any)
        left_char = current_expr[cursor_pos - 1 : cursor_pos] if cursor_pos > 0 else ""
        if not current_expr or left_char in "+-*/^%(":
            char_to_insert = "("
        else:
            open_count = current_expr.count("(")
            close_count = current_expr.count(")")
            if open_count > close_count:
                char_to_insert = ")"
            else:
                char_to_insert = "("
    else:
        char_to_insert = char

    # Insert at cursor position
    current_expr = (
        current_expr[:cursor_pos] + char_to_insert + current_expr[cursor_pos:]
    )
    cursor_pos += len(char_to_insert)

    render_display()
    update_button_states()


def clear_display():
    refocus()
    global current_expr, cursor_pos
    if not is_on:
        return
    current_expr = ""
    cursor_pos = 0
    render_display()
    clear_error()
    update_button_states()


def step_backspace():
    refocus()
    global current_expr, cursor_pos
    if not is_on or not current_expr:
        return
    if cursor_pos > 0:
        current_expr = current_expr[: cursor_pos - 1] + current_expr[cursor_pos:]
        cursor_pos -= 1
        render_display()
        clear_error()
        update_button_states()


def process_calculation():
    refocus()
    global current_expr, cursor_pos
    if not is_on or not current_expr:
        return

    result_data = evaluate(current_expr)

    if result_data.success:
        current_expr = str(result_data.value)
        cursor_pos = len(current_expr)
        render_display()
        clear_error()
    else:
        err_msg = result_data.error or "Error"
        is_crit = (
            "zero" in err_msg.lower()
            or "overflow" in err_msg.lower()
            or "large" in err_msg.lower()
        )
        show_error(err_msg, critical=is_crit)

    scroll_area.scroll_to(percent=100)
    update_button_states()


def update_button_states():
    if not is_on:
        for btn in smart_buttons.values():
            btn.disable()
        return

    valid_ending = current_expr and (
        current_expr[-1].isdigit() or current_expr[-1] in ")%"
    )
    for btn in smart_buttons.values():
        if valid_ending:
            btn.enable()
        else:
            btn.disable()


def show_error(message: str, critical: bool):
    global error_row
    error_row.clear()
    with error_row:
        if critical:
            ui.icon("report", color="red").classes("text-sm")
            ui.label(message).classes("text-red-500 text-xs font-bold")
        else:
            ui.icon("warning", color="amber").classes("text-sm")
            ui.label(message).classes("text-amber-400 text-xs font-medium")


def clear_error():
    global error_row
    if error_row:
        error_row.clear()


def handle_global_keys(e: events.GenericEventArguments):
    if not is_on:
        return

    key = e.args.get("key")
    if not key:
        return

    # Map known key names to calculator characters / actions
    key_map = {
        "Enter": "Enter",
        "=": "=",
        "Backspace": "Backspace",
        "Escape": "Escape",
        "+": "+",
        "-": "-",
        "*": "*",
        "/": "/",
        "%": "%",
        "^": "^",
        "(": "(",
        ")": ")",
        ".": ".",
        "0": "0",
        "1": "1",
        "2": "2",
        "3": "3",
        "4": "4",
        "5": "5",
        "6": "6",
        "7": "7",
        "8": "8",
        "9": "9",
        "q": "√",
        "Q": "√",
        "r": "√",
        "R": "√",
        "NumpadAdd": "+",
        "NumpadSubtract": "-",
        "NumpadMultiply": "*",
        "NumpadDivide": "/",
        "NumpadDecimal": ".",
        "Numpad0": "0",
        "Numpad1": "1",
        "Numpad2": "2",
        "Numpad3": "3",
        "Numpad4": "4",
        "Numpad5": "5",
        "Numpad6": "6",
        "Numpad7": "7",
        "Numpad8": "8",
        "Numpad9": "9",
        "NumpadEnter": "Enter",
        "ArrowLeft": "ArrowLeft",
        "ArrowRight": "ArrowRight",
    }

    action = key_map.get(key)
    if action is None:
        return

    global cursor_pos, current_expr  # needed for arrow keys

    if action == "ArrowLeft":
        cursor_pos = max(0, cursor_pos - 1)
        render_display()
    elif action == "ArrowRight":
        cursor_pos = min(len(current_expr), cursor_pos + 1)
        render_display()
    elif action == "Enter":
        process_calculation()
    elif action == "Backspace":
        step_backspace()
    elif action == "Escape":
        clear_display()
    else:
        append_character(action)


def fetch_history_rows():
    """Fetch and format history records from the backend."""
    raw_history = get_history()
    formatted_rows = []
    for record in raw_history:
        # Trim the time to a readable format
        try:
            clean_time = (
                record.timestamp.split("T")[0]
                if "T" in record.timestamp
                else record.timestamp
            )
        except:
            clean_time = record.timestamp
        formatted_rows.append(
            {
                "expression": record.expression,
                "result": record.result,
                "time": clean_time,
            }
        )
    return formatted_rows


def open_history():
    """Open the history dialog and populate the table."""
    global history_table, history_dialog
    if history_table is None:
        return
    history_table.rows = fetch_history_rows()
    history_dialog.open()


def clear_history_records():
    """Clear history from backend and table."""
    clear_history()
    if history_table:
        history_table.rows = []
    ui.notify("History Cleared", type="info", position="bottom-left")


# ----------------------------------------------------
# Main Page
# ----------------------------------------------------
@ui.page("/")
def calculator_page():
    global display_label, scroll_area, error_row, screen_container, power_btn, battery_label, history_dialog, history_table, hidden_focus

    ui.page_title("Professional Calculator")
    ui.add_head_html("""
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&display=swap" rel="stylesheet">
        <style>
            body {
                overflow: hidden;
                height: 100vh;
                margin: 0;
                padding: 0;
                background-color: #0f172a;
            }
            .calc-font {
                font-family: 'Orbitron', monospace !important;
            }
            .cursor-blink {
                animation: blink 1s step-end infinite;
                }
            @keyframes blink {
                0%, 100% { opacity: 1; }
                50% { opacity: 0; }
}
        </style>
    """)

    # --- Hidden focus input (steals focus from buttons) ---
    hidden_focus = ui.input().classes("opacity-0 absolute w-0 h-0 pointer-events-none")
    hidden_focus.props("autofocus")
    hidden_focus.run_method("focus")

    with ui.column().classes("w-full h-screen items-center justify-center p-0 m-0"):
        with ui.card().classes(
            "w-full max-w-sm p-4 bg-slate-900 rounded-none "
            "flex flex-col justify-start gap-2"
        ):
            # ----------------------------------------------------
            # HEADER
            # ----------------------------------------------------
            with ui.row().classes("w-full justify-between items-center mb-2"):
                # Left side: power button
                power_btn = ui.button(
                    "ON/OFF", on_click=lambda: asyncio.create_task(toggle_power())
                )
                power_btn.classes(POWER_ON)

                # Right side: battery + menu
                with ui.row().classes("items-center gap-1"):
                    battery_label = ui.label("BATTERY").classes(
                        "text-xs text-slate-400"
                    )
                    update_battery()  # you can still call it here

                    # Menu button and its dropdown
                    menu_btn = (
                        ui.button(icon="more_vert", color=None)
                        .props("flat dense")
                        .classes("text-slate-400")
                    )
                    with ui.menu():
                        ui.menu_item("View History", on_click=open_history)
                        ui.menu_item("Clear History", on_click=clear_history_records)

                # ----------------------------------------------------
                # LCD Display
                # ----------------------------------------------------
                with (
                    ui.row()
                    .classes("w-full p-2 justify-end items-center")
                    .style(
                        "background-color: #052e16; border: 2px solid #064e3b; border-radius: 4px;"
                    )
                ):
                    with ui.scroll_area().classes(
                        "w-full h-24 max-h-24"
                    ) as scroll_area:
                        display_label = (
                            ui.html()
                            .classes(
                                "calc-font text-emerald-400 text-2xl font-black tracking-wider "
                                "break-all text-right w-full pr-1 whitespace-pre-wrap"
                            )
                            .style("color: #34d399;")
                        )
                        display_label.content = "SYSTEM OFF"
                # ----------------------------------------------------
                # Error Row (placed between LCD and buttons)
                # ----------------------------------------------------
                error_row = ui.row().classes("w-full h-6 items-center gap-1 mb-1")

                # ----------------------------------------------------
                # Button Grid (initially dimmed)
                # ----------------------------------------------------
                screen_container = ui.column().classes(
                    "w-full gap-3 opacity-20 pointer-events-none transition-all duration-300 pb-2"
                )
                with screen_container:
                    with ui.grid(columns=4).classes("w-full gap-2.5"):
                        # Row 1
                        ui.button("CLR", on_click=clear_display).classes(CLEAR_BTN)
                        ui.button("⌫", on_click=step_backspace).classes(BACK_BTN)
                        ui.button(
                            "( )", on_click=lambda: append_character("()")
                        ).classes(FUNC_BTN)
                        ui.button("√", on_click=lambda: append_character("√")).classes(
                            FUNC_BTN + " text-lg"
                        )

                        # Row 2
                        btn_pow = ui.button(
                            "xⁿ", on_click=lambda: append_character("^")
                        ).classes(FUNC_BTN)
                        smart_buttons["^"] = btn_pow

                        btn_mod = ui.button(
                            "%", on_click=lambda: append_character("%")
                        ).classes(FUNC_BTN)
                        smart_buttons["%"] = btn_mod

                        btn_div = ui.button(
                            "÷", on_click=lambda: append_character("/")
                        ).classes(OPERATOR_BTN + " text-lg")
                        smart_buttons["/"] = btn_div

                        btn_mul = ui.button(
                            "×", on_click=lambda: append_character("*")
                        ).classes(OPERATOR_BTN + " text-lg")
                        smart_buttons["*"] = btn_mul

                        # Row 3
                        ui.button("7", on_click=lambda: append_character("7")).classes(
                            NUMBER_BTN
                        )
                        ui.button("8", on_click=lambda: append_character("8")).classes(
                            NUMBER_BTN
                        )
                        ui.button("9", on_click=lambda: append_character("9")).classes(
                            NUMBER_BTN
                        )
                        ui.button("-", on_click=lambda: append_character("-")).classes(
                            OPERATOR_BTN + " text-xl"
                        )

                        # Row 4
                        ui.button("4", on_click=lambda: append_character("4")).classes(
                            NUMBER_BTN
                        )
                        ui.button("5", on_click=lambda: append_character("5")).classes(
                            NUMBER_BTN
                        )
                        ui.button("6", on_click=lambda: append_character("6")).classes(
                            NUMBER_BTN
                        )

                        btn_plus = ui.button(
                            "+", on_click=lambda: append_character("+")
                        ).classes(OPERATOR_BTN + " text-xl")
                        smart_buttons["+"] = btn_plus

                        # Row 5 & 6 (with row-span =)
                        ui.button("1", on_click=lambda: append_character("1")).classes(
                            NUMBER_BTN
                        )
                        ui.button("2", on_click=lambda: append_character("2")).classes(
                            NUMBER_BTN
                        )
                        ui.button("3", on_click=lambda: append_character("3")).classes(
                            NUMBER_BTN
                        )
                        ui.button("=", on_click=process_calculation).classes(
                            EQUAL_BTN + " col-start-4 row-start-5 row-span-2"
                        )

                        ui.button("0", on_click=lambda: append_character("0")).classes(
                            NUMBER_BTN + " col-start-1 row-start-6 col-span-2"
                        )
                        ui.button(".", on_click=lambda: append_character(".")).classes(
                            NUMBER_BTN + " text-xl col-start-3 row-start-6"
                        )
    # ----------------------------------------------------
    # History Dialog
    # ----------------------------------------------------
    columns = [
        {
            "name": "expression",
            "label": "Expression",
            "field": "expression",
            "align": "left",
        },
        {"name": "result", "label": "Result", "field": "result", "align": "right"},
        {"name": "time", "label": "Time", "field": "time", "align": "center"},
    ]

    with ui.dialog() as history_dialog:
        with ui.card().classes("w-96 max-w-lg p-4"):
            ui.label("Calculation History").classes(
                "text-lg font-bold text-cyan-500 mb-2"
            )
            history_table = ui.table(columns=columns, rows=[], row_key="time").classes(
                "w-full mb-4"
            )
            with ui.row().classes("w-full justify-between"):
                ui.button(
                    "Clear Logs", on_click=clear_history_records, color="red"
                ).props("flat")
                ui.button("Close", on_click=history_dialog.close, color="cyan")
    # ----------------------------------------------------
    # Battery timer & keyboard listener
    # ----------------------------------------------------
    ui.timer(30, update_battery)
    ui.on("keydown", handle_global_keys)


# ----------------------------------------------------
# Window Configuration & Run
# ----------------------------------------------------
app.native.window_args["resizable"] = False
ui.run(title="Professional Calculator", window_size=(380, 640), native=True)
