#!/usr/bin/env python3
"""
Attack Shark R1 Driver GUI - GTK4 Version (Complete)
"""

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib, Gio

import subprocess
import json
import os
import threading

class AttackSharkWindow(Gtk.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app)

        # Load config file path
        self.config_path = os.path.expanduser("~/.config/attack-shark/config.json")

        # Create variables
        self.create_variables()

        # Build UI
        self.build_ui()

        # Set window properties
        self.set_default_size(700, 850)
        self.set_title("Attack Shark R1 Driver")

        # Try to load existing config
        self.load_config()

    def create_variables(self):
        """Create variables for settings"""
        self.active_dpi = 1
        self.angle_snap = False
        self.deep_sleep_time = 5
        self.dpi_values = {i: 800 if i == 1 else 0 for i in range(1, 7)}
        self.key_response_time = 8
        self.polling_rate = 1000
        self.ripple_control = False
        self.sleep_time = 2.0
        self.reapply_config = False

    def build_ui(self):
        """Build the GTK4 UI"""
        # Main vertical box
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.set_child(main_box)

        # Header bar
        header_bar = Gtk.HeaderBar()
        main_box.append(header_bar)

        # Title
        title = Gtk.Label(label="Attack Shark R1 Driver")
        title.get_style_context().add_class("title")
        header_bar.set_title_widget(title)

        # Create scrolled window
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        main_box.append(scrolled)

        # Main content box
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        content_box.set_margin_top(10)
        content_box.set_margin_bottom(10)
        content_box.set_margin_start(10)
        content_box.set_margin_end(10)
        scrolled.set_child(content_box)

        # Format info section
        self.create_format_info_section(content_box)

        # Configuration section
        self.create_config_section(content_box)

        # Polling Rate section
        self.create_polling_rate_section(content_box)

        # DPI section
        self.create_dpi_section(content_box)

        # Performance section
        self.create_performance_section(content_box)

        # Power section
        self.create_power_section(content_box)

        # Buttons section
        self.create_button_section(content_box)

        # Status bar
        self.create_status_bar(main_box)

    def create_format_info_section(self, parent):
        """Create format information section"""
        frame = Gtk.Frame()
        frame.set_margin_top(5)
        frame.set_margin_bottom(5)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        box.set_margin_top(10)
        box.set_margin_bottom(10)
        box.set_margin_start(10)
        box.set_margin_end(10)
        frame.set_child(box)

        label = Gtk.Label(label="<b>Argument Format</b>")
        label.set_use_markup(True)
        label.set_halign(Gtk.Align.START)
        box.append(label)

        info_text = "Based on error messages, the correct format is:\n• Regular flags: -flag=value  (e.g., -polling-rate=500)\n• DPI flag (map type): -dpi:key=value  (e.g., -dpi:1=800)\n• Standalone flags: -flag  (e.g., -query-charge, -reapply-config)"

        info_label = Gtk.Label(label=info_text)
        info_label.set_wrap(True)
        info_label.set_halign(Gtk.Align.START)
        info_label.set_margin_top(5)
        box.append(info_label)

        parent.append(frame)

    def create_config_section(self, parent):
        """Create config file section"""
        frame = Gtk.Frame()
        frame.set_margin_top(5)
        frame.set_margin_bottom(5)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_margin_top(10)
        box.set_margin_bottom(10)
        box.set_margin_start(10)
        box.set_margin_end(10)
        frame.set_child(box)

        label = Gtk.Label(label="<b>Configuration</b>")
        label.set_use_markup(True)
        label.set_halign(Gtk.Align.START)
        box.append(label)

        # Config path
        config_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        config_label = Gtk.Label(label="Config Path:")
        config_label.set_halign(Gtk.Align.START)
        config_box.append(config_label)

        self.config_entry = Gtk.Entry()
        self.config_entry.set_text(self.config_path)
        self.config_entry.set_hexpand(True)
        config_box.append(self.config_entry)

        browse_button = Gtk.Button(label="Browse")
        browse_button.connect("clicked", self.on_browse_config)
        config_box.append(browse_button)

        box.append(config_box)

        # Reapply config
        reapply_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        reapply_label = Gtk.Label(label="Reapply entire config on save:")
        reapply_label.set_halign(Gtk.Align.START)
        reapply_box.append(reapply_label)

        self.reapply_switch = Gtk.Switch()
        self.reapply_switch.set_active(self.reapply_config)
        self.reapply_switch.connect("state-set", self.on_reapply_changed)
        reapply_box.append(self.reapply_switch)

        box.append(reapply_box)

        # Query charge button
        query_button = Gtk.Button(label="Query Battery Charge")
        query_button.connect("clicked", self.on_query_charge)
        query_button.set_halign(Gtk.Align.CENTER)
        query_button.set_margin_top(10)
        box.append(query_button)

        parent.append(frame)

    def create_polling_rate_section(self, parent):
        """Create polling rate section"""
        frame = Gtk.Frame()
        frame.set_margin_top(5)
        frame.set_margin_bottom(5)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        box.set_margin_top(10)
        box.set_margin_bottom(10)
        box.set_margin_start(10)
        box.set_margin_end(10)
        frame.set_child(box)

        label = Gtk.Label(label="<b>Polling Rate (Hz)</b>")
        label.set_use_markup(True)
        label.set_halign(Gtk.Align.START)
        box.append(label)

        rates = [125, 250, 500, 1000]
        self.polling_buttons = {}

        for rate in rates:
            rate_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            rate_label = Gtk.Label(label=f"{rate} Hz")
            rate_label.set_halign(Gtk.Align.START)
            rate_box.append(rate_label)

            radio = Gtk.CheckButton()
            if not self.polling_buttons:
                radio.set_active(rate == self.polling_rate)
            else:
                radio.set_group(self.polling_buttons[rates[0]])
                radio.set_active(rate == self.polling_rate)
            radio.connect("toggled", self.on_polling_rate_changed, rate)
            self.polling_buttons[rate] = radio
            rate_box.append(radio)

            box.append(rate_box)

        parent.append(frame)

    def create_dpi_section(self, parent):
        """Create DPI settings section"""
        frame = Gtk.Frame()
        frame.set_margin_top(5)
        frame.set_margin_bottom(5)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        box.set_margin_top(10)
        box.set_margin_bottom(10)
        box.set_margin_start(10)
        box.set_margin_end(10)
        frame.set_child(box)

        label = Gtk.Label(label="<b>DPI Settings</b>")
        label.set_use_markup(True)
        label.set_halign(Gtk.Align.START)
        box.append(label)

        # Active DPI
        active_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        active_label = Gtk.Label(label="Active DPI Slot:")
        active_label.set_halign(Gtk.Align.START)
        active_box.append(active_label)

        self.active_dpi_combo = Gtk.DropDown.new_from_strings([str(i) for i in range(1, 7)])
        self.active_dpi_combo.set_selected(self.active_dpi - 1)
        self.active_dpi_combo.connect("notify::selected", self.on_active_dpi_changed)
        active_box.append(self.active_dpi_combo)

        box.append(active_box)

        # DPI values for each slot
        self.dpi_entries = {}
        self.dpi_switches = {}

        for i in range(1, 7):
            dpi_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            dpi_label = Gtk.Label(label=f"Slot {i} DPI:")
            dpi_label.set_halign(Gtk.Align.START)
            dpi_box.append(dpi_label)

            # Entry for DPI value
            entry = Gtk.Entry()
            entry.set_text(str(self.dpi_values[i]))
            entry.set_width_chars(8)
            entry.connect("changed", self.on_dpi_entry_changed, i)
            self.dpi_entries[i] = entry
            dpi_box.append(entry)

            # Switch for enabled/disabled
            switch = Gtk.Switch()
            switch.set_active(self.dpi_values[i] > 0)
            switch.connect("state-set", self.on_dpi_switch_changed, i)
            self.dpi_switches[i] = switch
            dpi_box.append(switch)

            box.append(dpi_box)

        parent.append(frame)

    def create_performance_section(self, parent):
        """Create performance settings section"""
        frame = Gtk.Frame()
        frame.set_margin_top(5)
        frame.set_margin_bottom(5)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_margin_top(10)
        box.set_margin_bottom(10)
        box.set_margin_start(10)
        box.set_margin_end(10)
        frame.set_child(box)

        label = Gtk.Label(label="<b>Performance Settings</b>")
        label.set_use_markup(True)
        label.set_halign(Gtk.Align.START)
        box.append(label)

        # Key response time
        response_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        response_label = Gtk.Label(label="Key Response Time (4-50ms, even):")
        response_label.set_halign(Gtk.Align.START)
        response_box.append(response_label)

        self.response_spin = Gtk.SpinButton.new_with_range(4, 50, 2)
        self.response_spin.set_value(self.key_response_time)
        self.response_spin.connect("value-changed", self.on_response_time_changed)
        response_box.append(self.response_spin)

        unit_label = Gtk.Label(label="ms")
        response_box.append(unit_label)

        box.append(response_box)

        # Angle snap
        angle_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        angle_label = Gtk.Label(label="Angle Snap:")
        angle_label.set_halign(Gtk.Align.START)
        angle_box.append(angle_label)

        self.angle_switch = Gtk.Switch()
        self.angle_switch.set_active(self.angle_snap)
        self.angle_switch.connect("state-set", self.on_angle_snap_changed)
        angle_box.append(self.angle_switch)

        box.append(angle_box)

        # Ripple control
        ripple_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        ripple_label = Gtk.Label(label="Ripple Control:")
        ripple_label.set_halign(Gtk.Align.START)
        ripple_box.append(ripple_label)

        self.ripple_switch = Gtk.Switch()
        self.ripple_switch.set_active(self.ripple_control)
        self.ripple_switch.connect("state-set", self.on_ripple_control_changed)
        ripple_box.append(self.ripple_switch)

        box.append(ripple_box)

        parent.append(frame)

    def create_power_section(self, parent):
        """Create power settings section"""
        frame = Gtk.Frame()
        frame.set_margin_top(5)
        frame.set_margin_bottom(5)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_margin_top(10)
        box.set_margin_bottom(10)
        box.set_margin_start(10)
        box.set_margin_end(10)
        frame.set_child(box)

        label = Gtk.Label(label="<b>Power Settings</b>")
        label.set_use_markup(True)
        label.set_halign(Gtk.Align.START)
        box.append(label)

        # Sleep time
        sleep_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        sleep_label = Gtk.Label(label="Sleep Time (0.5-30ms):")
        sleep_label.set_halign(Gtk.Align.START)
        sleep_box.append(sleep_label)

        self.sleep_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0.5, 30.0, 0.1)
        self.sleep_scale.set_value(self.sleep_time)
        self.sleep_scale.set_draw_value(True)
        self.sleep_scale.set_hexpand(True)
        self.sleep_scale.connect("value-changed", self.on_sleep_time_changed)
        sleep_box.append(self.sleep_scale)

        box.append(sleep_box)

        # Deep sleep time
        deep_sleep_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        deep_sleep_label = Gtk.Label(label="Deep Sleep Time (1-60ms):")
        deep_sleep_label.set_halign(Gtk.Align.START)
        deep_sleep_box.append(deep_sleep_label)

        self.deep_sleep_spin = Gtk.SpinButton.new_with_range(1, 60, 1)
        self.deep_sleep_spin.set_value(self.deep_sleep_time)
        self.deep_sleep_spin.connect("value-changed", self.on_deep_sleep_time_changed)
        deep_sleep_box.append(self.deep_sleep_spin)

        unit_label = Gtk.Label(label="ms")
        deep_sleep_box.append(unit_label)

        box.append(deep_sleep_box)

        parent.append(frame)

    def create_button_section(self, parent):
        """Create action buttons section"""
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        button_box.set_halign(Gtk.Align.CENTER)
        button_box.set_margin_top(20)
        button_box.set_margin_bottom(20)

        # Load button
        load_button = Gtk.Button(label="Load Config")
        load_button.connect("clicked", self.on_load_config)
        button_box.append(load_button)

        # Save button
        save_button = Gtk.Button(label="Save Config")
        save_button.connect("clicked", self.on_save_config)
        button_box.append(save_button)

        # Apply button
        apply_button = Gtk.Button(label="Apply Settings")
        apply_button.get_style_context().add_class("suggested-action")
        apply_button.connect("clicked", self.on_apply_settings)
        button_box.append(apply_button)

        # Reset button
        reset_button = Gtk.Button(label="Reset to Defaults")
        reset_button.connect("clicked", self.on_reset_defaults)
        button_box.append(reset_button)

        parent.append(button_box)

    def create_status_bar(self, parent):
        """Create status bar"""
        self.status_bar = Gtk.Statusbar()
        self.status_context = self.status_bar.get_context_id("status")
        self.status_bar.push(self.status_context, "Ready")
        parent.append(self.status_bar)

    # Event handlers
    def on_browse_config(self, button):
        """Handle browse config button click"""
        dialog = Gtk.FileChooserNative(
            title="Select Config File",
            transient_for=self,
            action=Gtk.FileChooserAction.SAVE
        )

        # Create filter
        filter_json = Gtk.FileFilter()
        filter_json.set_name("JSON files")
        filter_json.add_pattern("*.json")
        dialog.add_filter(filter_json)

        dialog.set_current_name("config.json")

        def on_response(dialog, response):
            if response == Gtk.ResponseType.ACCEPT:
                file = dialog.get_file()
                if file:
                    filename = file.get_path()
                    self.config_entry.set_text(filename)
                    self.config_path = filename
            dialog.destroy()

        dialog.connect("response", on_response)
        dialog.show()

    def on_reapply_changed(self, switch, state):
        """Handle reapply config switch change"""
        self.reapply_config = state

    def on_query_charge(self, button):
        """Handle query charge button click"""
        def query_in_thread():
            try:
                result = subprocess.run(
                    ['attack-shark-r1-driver', '-query-charge'],
                    capture_output=True,
                    text=True,
                    check=True
                )
                GLib.idle_add(self.show_message_dialog, "Battery Charge", result.stdout)
                GLib.idle_add(self.update_status, "Battery charge queried successfully")
            except subprocess.CalledProcessError as e:
                GLib.idle_add(self.show_error_dialog, "Failed to query charge", e.stderr)
                GLib.idle_add(self.update_status, "Error querying battery charge")
            except FileNotFoundError:
                GLib.idle_add(self.show_error_dialog, "Driver not found",
                             "Make sure attack-shark-r1-driver is in your PATH.")
                GLib.idle_add(self.update_status, "Driver command not found")

        threading.Thread(target=query_in_thread, daemon=True).start()

    def on_polling_rate_changed(self, button, rate):
        """Handle polling rate change"""
        if button.get_active():
            self.polling_rate = rate

    def on_active_dpi_changed(self, combo, pspec):
        """Handle active DPI change"""
        self.active_dpi = combo.get_selected() + 1

    def on_dpi_entry_changed(self, entry, slot):
        """Handle DPI entry change"""
        try:
            value = int(entry.get_text())
            self.dpi_values[slot] = value
            self.dpi_switches[slot].set_active(value > 0)
        except ValueError:
            pass

    def on_dpi_switch_changed(self, switch, state, slot):
        """Handle DPI switch change"""
        if not state:
            self.dpi_values[slot] = 0
            self.dpi_entries[slot].set_text("0")

    def on_response_time_changed(self, spin):
        """Handle key response time change"""
        self.key_response_time = spin.get_value_as_int()

    def on_angle_snap_changed(self, switch, state):
        """Handle angle snap change"""
        self.angle_snap = state

    def on_ripple_control_changed(self, switch, state):
        """Handle ripple control change"""
        self.ripple_control = state

    def on_sleep_time_changed(self, scale):
        """Handle sleep time change"""
        self.sleep_time = scale.get_value()

    def on_deep_sleep_time_changed(self, spin):
        """Handle deep sleep time change"""
        self.deep_sleep_time = spin.get_value_as_int()

    def on_load_config(self, button):
        """Handle load config button click"""
        config_file = self.config_entry.get_text()

        if not os.path.exists(config_file):
            self.show_error_dialog("Config file not found", config_file)
            self.update_status(f"Config file not found: {config_file}")
            return

        try:
            with open(config_file, 'r') as f:
                config = json.load(f)

            # Load values from config
            self.active_dpi = config.get('active_dpi', 1)
            self.angle_snap = config.get('angle_snap', False)
            self.deep_sleep_time = config.get('deep_sleep_time', 5)
            self.key_response_time = config.get('key_response_time', 8)
            self.polling_rate = config.get('polling_rate', 1000)
            self.ripple_control = config.get('ripple_control', False)
            self.sleep_time = config.get('sleep_time', 2.0)

            # Load DPI values
            dpi_config = config.get('dpi', {})
            for i in range(1, 7):
                self.dpi_values[i] = dpi_config.get(str(i), 800 if i == 1 else 0)

            # Update UI
            self.update_ui_from_config()

            self.update_status(f"Config loaded from {config_file}")

        except Exception as e:
            self.show_error_dialog("Failed to load config", str(e))
            self.update_status("Error loading config")

    def update_ui_from_config(self):
        """Update UI elements from loaded config"""
        # Update polling rate
        for rate, button in self.polling_buttons.items():
            button.set_active(rate == self.polling_rate)

        # Update active DPI
        self.active_dpi_combo.set_selected(self.active_dpi - 1)

        # Update DPI values
        for i in range(1, 7):
            self.dpi_entries[i].set_text(str(self.dpi_values[i]))
            self.dpi_switches[i].set_active(self.dpi_values[i] > 0)

        # Update response time
        self.response_spin.set_value(self.key_response_time)

        # Update switches
        self.angle_switch.set_active(self.angle_snap)
        self.ripple_switch.set_active(self.ripple_control)

        # Update sleep times
        self.sleep_scale.set_value(self.sleep_time)
        self.deep_sleep_spin.set_value(self.deep_sleep_time)

    def on_save_config(self, button):
        """Handle save config button click"""
        config_file = self.config_entry.get_text()

        if not config_file:
            self.show_error_dialog("Error", "Please specify a config file path")
            return

        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(config_file)), exist_ok=True)

        # Prepare config dictionary
        config = {
            'active_dpi': self.active_dpi,
            'angle_snap': self.angle_snap,
            'deep_sleep_time': self.deep_sleep_time,
            'key_response_time': self.key_response_time,
            'polling_rate': self.polling_rate,
            'ripple_control': self.ripple_control,
            'sleep_time': self.sleep_time,
            'dpi': {str(i): self.dpi_values[i] for i in range(1, 7)}
        }

        try:
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)

            self.update_status(f"Config saved to {config_file}")

            # If reapply is checked, apply after saving
            if self.reapply_config:
                self.on_apply_settings(None)

        except Exception as e:
            self.show_error_dialog("Failed to save config", str(e))
            self.update_status("Error saving config")

    def on_apply_settings(self, button):
        """Handle apply settings button click"""
        def apply_in_thread():
            try:
                cmd = self._build_command()

                # Execute command
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)

                if result.stdout:
                    GLib.idle_add(self.show_message_dialog, "Success", result.stdout)
                GLib.idle_add(self.update_status, "Settings applied successfully")

            except subprocess.CalledProcessError as e:
                error_msg = f"Failed to apply settings:\n\nError: {e.stderr}"
                GLib.idle_add(self.show_error_dialog, "Error", error_msg)
                GLib.idle_add(self.update_status, "Error applying settings")
            except FileNotFoundError:
                GLib.idle_add(self.show_error_dialog, "Driver not found",
                             "Make sure attack-shark-r1-driver is in your PATH.")
                GLib.idle_add(self.update_status, "Driver command not found")
            except Exception as e:
                GLib.idle_add(self.show_error_dialog, "Unexpected error", str(e))
                GLib.idle_add(self.update_status, "Unexpected error")

        threading.Thread(target=apply_in_thread, daemon=True).start()

    def _build_command(self):
        """Build the command list for subprocess with mixed format"""
        cmd = ['attack-shark-r1-driver']

        # Add config path with = format
        config_file = self.config_entry.get_text()
        if config_file:
            cmd.append(f'-config-path={config_file}')

        # Add reapply config flag (standalone, no value)
        if self.reapply_config:
            cmd.append('-reapply-config')

        # Add polling rate with = format
        cmd.append(f'-polling-rate={self.polling_rate}')

        # Add active DPI with = format
        cmd.append(f'-active-dpi={self.active_dpi}')

        # Add DPI values with : format (special for map type!)
        for i in range(1, 7):
            dpi_value = self.dpi_values[i]
            if dpi_value > 0:
                cmd.append(f'-dpi:{i}={dpi_value}')

        # Add key response time with = format
        cmd.append(f'-key-response-time={self.key_response_time}')

        # Add angle snap with = format
        cmd.append(f'-angle-snap={str(self.angle_snap).lower()}')

        # Add ripple control with = format
        cmd.append(f'-ripple-control={str(self.ripple_control).lower()}')

        # Add sleep time with = format
        cmd.append(f'-sleep-time={self.sleep_time}')

        # Add deep sleep time with = format
        cmd.append(f'-deep-sleep-time={self.deep_sleep_time}')

        return cmd

    def on_reset_defaults(self, button):
        """Handle reset to defaults button click"""
        dialog = Gtk.MessageDialog(
            transient_for=self,
            modal=True,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text="Reset Settings",
            secondary_text="Are you sure you want to reset all settings to defaults?"
        )

        def on_response(dialog, response):
            if response == Gtk.ResponseType.YES:
                self.reset_to_defaults()
            dialog.destroy()

        dialog.connect("response", on_response)
        dialog.show()

    def reset_to_defaults(self):
        """Reset all settings to defaults"""
        self.active_dpi = 1
        self.angle_snap = False
        self.deep_sleep_time = 5
        self.dpi_values = {i: 800 if i == 1 else 0 for i in range(1, 7)}
        self.key_response_time = 8
        self.polling_rate = 1000
        self.ripple_control = False
        self.sleep_time = 2.0

        self.update_ui_from_config()
        self.update_status("Settings reset to defaults")

    def load_config(self):
        """Load initial config"""
        config_file = self.config_path
        if os.path.exists(config_file):
            self.on_load_config(None)

    # UI helper methods
    def show_message_dialog(self, title, message):
        """Show a message dialog"""
        dialog = Gtk.MessageDialog(
            transient_for=self,
            modal=True,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text=title,
            secondary_text=message
        )
        dialog.connect("response", lambda d, r: d.destroy())
        dialog.show()

    def show_error_dialog(self, title, message):
        """Show an error dialog"""
        dialog = Gtk.MessageDialog(
            transient_for=self,
            modal=True,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text=title,
            secondary_text=message
        )
        dialog.connect("response", lambda d, r: d.destroy())
        dialog.show()

    def update_status(self, message):
        """Update status bar"""
        self.status_bar.remove_all(self.status_context)
        self.status_bar.push(self.status_context, message)

class AttackSharkApp(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="com.github.attackshark.r1driver")

    def do_activate(self):
        win = AttackSharkWindow(self)
        win.present()

def main():
    app = AttackSharkApp()
    app.run()

if __name__ == "__main__":
    main()
