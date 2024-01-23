#!/usr/bin/python3
import pathlib
import tkinter as tk
import pprint as pp
import pygubu

import pygubudesigner.services.designersettingsbase as dsbase
from pygubudesigner.preferences import (
    options,
    DATA_DIR,
    get_option,
    save_from_dict,
)
from pygubudesigner.util import get_ttk_style
from pygubudesigner.i18n import translator as _


dsbase.PROJECT_PATH = DATA_DIR / "ui"
dsbase.PROJECT_UI = dsbase.PROJECT_PATH / "designer_settings.ui"


class DesignerSettings(dsbase.DesignerSettingsBase):
    def __init__(self, master=None, translator=None):
        super().__init__(master, translator)
        self.app_master = master
        self.dialog_toplevel = self.mainwindow.toplevel
        self.frm_settings = self.builder.get_object("frm_settings")

        self.separator_keys = {
            "NONE": _("No separator (e.g. button1)"),
            "UNDERSCORE": _("""Use "_" as separator (e.g. button_1)"""),
        }
        field = self.builder.get_object("widget_naming_separator")
        field.configure(values=self.separator_keys.items())

        fieldlist = ("widget_set", "default_layout_manager")
        for fname in fieldlist:
            field = self.builder.get_object(fname)
            field.configure(values=options[fname]["values"])

        # setup theme values
        s = get_ttk_style()
        styles = s.theme_names()
        themelist = []
        for name in styles:
            themelist.append((name, name))
        themelist.sort()
        field = self.builder.get_object("ttk_theme")
        field.configure(values=themelist)

    def run(self):
        self.edit_settings()
        self.mainwindow.run()

    def on_dialog_close(self, event=None):
        self._deselect_combobox_text()
        self.mainwindow.close()

    def edit_settings(self):
        # set defaults
        defaults = {}
        for key in options:
            defaults[key] = options[key]["default"]

        # Load user options
        user_settings = {}
        # General
        for key in options:
            user_settings[key] = get_option(key)
        self.frm_settings.edit(user_settings, defaults)

    def btn_cancel_cliced(self):
        self.on_dialog_close()

    def btn_apply_clicked(self):
        form = self.frm_settings
        form.submit()
        valid = form.is_valid()
        if valid:
            save_from_dict(form.cleaned_data)
            self.app_master.event_generate("<<PygubuDesignerPreferencesSaved>>")
            self.on_dialog_close()
        else:
            # FIXME
            pp.pprint(form.errors)

    def _deselect_combobox_text(self):
        """
        Deselect all text in all combo boxes.

        If we don't do this, the next time the preference window opens,
        One of the combo boxes may have all its text selected.
        """
        for field in self.frm_settings.fields.values():
            if field.winfo_class() == "TCombobox":
                field.select_clear()


if __name__ == "__main__":
    root = tk.Tk()
    app = DesignerSettings(root)
    app.run()
