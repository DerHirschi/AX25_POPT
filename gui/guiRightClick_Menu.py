"""
by Grok3 AI
"""
import tkinter as tk


class ContextMenu:
    def __init__(self, widget):
        self._widget = widget
        self._root = widget.winfo_toplevel()
        self._menu = tk.Menu(widget, tearoff=0)
        self.is_menu_active = False  # Flag, um den Menüstatus zu verfolgen
        self._original_menu = None  # Speichert die ursprüngliche Menüleiste
        self._bind_context_menu()

    def add_item(self, label, command):
        """Fügt ein Menüelement hinzu"""
        self._menu.add_command(label=label, command=lambda: [command(), self._cleanup()])

    def add_separator(self):
        """Fügt einen Separator hinzu"""
        self._menu.add_separator()

    def add_submenu(self, label):
        """Fügt ein Untermenü hinzu und gibt das Untermenü-Objekt zurück"""
        submenu = tk.Menu(self._menu, tearoff=0)
        self._menu.add_cascade(label=label, menu=submenu)
        return submenu

    def _show(self, event):
        """Zeigt das Kontextmenü an der Mausposition"""
        try:
            # Speichere und deaktiviere die Menüleiste
            self._original_menu = self._root.cget("menu")
            if self._original_menu:
                try:
                    # Deaktiviere Menüleisten-Einträge statt Entfernen
                    for i in range(self._original_menu.index("end") + 1):
                        self._original_menu.entryconfig(i, state="disabled")
                except ValueError:
                    pass

            # Öffne das Kontextmenü
            self._menu.tk_popup(event.x_root, event.y_root)
            self.is_menu_active = True

            # Bindungen für Linksklick und Fokusverlust
            self._root.bind("<Button-1>", self._close_on_left_click)
            self._root.bind("<FocusOut>", self._close_on_focus_out)
        except ValueError:
            self._cleanup()

    def _close_on_left_click(self, event):
        """Schließt das Menü bei einem Linksklick außerhalb"""
        if not self.is_menu_active:
            return

        try:
            # Prüfe, ob der Klick außerhalb des Menüs erfolgt
            menu_x = self._menu.winfo_rootx()
            menu_y = self._menu.winfo_rooty()
            menu_width = self._menu.winfo_width()
            menu_height = self._menu.winfo_height()

            click_x = event.x_root
            click_y = event.y_root

            # Wenn der Klick außerhalb des Menübereichs liegt, Menü schließen
            if not (menu_x <= click_x <= menu_x + menu_width and
                    menu_y <= click_y <= menu_y + menu_height):
                self._menu.unpost()  # Menü schließen
                self._cleanup()
        except ValueError:
            # print(f"Fehler in _close_on_left_click: {e}")
            self._cleanup()

    def _close_on_focus_out(self, event):
        """Schließt das Menü, wenn das Fenster den Fokus verliert"""
        if not self.is_menu_active:
            return

        # Verzögere die Prüfung, um Fokuswechsel beim Öffnen zu vermeiden
        self._root.after(100, self._check_focus_out)

    def _check_focus_out(self):
        """Prüft, ob das Menü geschlossen werden soll"""
        if not self.is_menu_active:
            return

        # Prüfe, ob das Root-Fenster den Fokus hat
        try:
            if self._root.focus_get() is None:
                self._menu.unpost()  # Menü schließen
                self._cleanup()
        except KeyError:
            self._menu.unpost()  # Menü schließen
            self._cleanup()

    def _cleanup(self):
        """Entfernt Bindings, stellt Menüleiste wieder her und setzt Status zurück"""
        if not self.is_menu_active:
            return

        self.is_menu_active = False
        try:
            # Stelle die Menüleisten-Einträge wieder her
            if self._original_menu:
                for i in range(self._original_menu.index("end") + 1):
                    self._original_menu.entryconfig(i, state="normal")
            # Entferne Bindings
            self._root.unbind("<Button-1>")
            self._root.unbind("<FocusOut>")
        except ValueError:
            pass

    def _bind_context_menu(self):
        """Bindet das Rechtsklick-Event an das Widget"""
        # Plattformunabhängige Rechtsklick-Bindung
        self._widget.bind("<Button-3>", self._show)  # Windows & Linux
        self._widget.bind("<Control-Button-1>", self._show)  # MacOS