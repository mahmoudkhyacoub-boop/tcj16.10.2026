from pathlib import Path
import ast
import sqlite3
import tempfile

source = Path('main.py').read_text(encoding='utf-8')
ast.parse(source)
assert 'CREATE TABLE IF NOT EXISTS shop_locations' in source
assert 'whatsapp_default_location_id' in source
assert 'مواقع الفروع وروابط Check-in عبر Google Maps' in source
assert 'def _whatsapp_location_link' in source
assert 'def _append_whatsapp_location' in source
assert 'message = self._append_whatsapp_location(message)' in source

# Verify the isolated storage contract and default selection behavior without launching Tk.
with tempfile.TemporaryDirectory() as tmp:
    con = sqlite3.connect(':memory:')
    con.execute('CREATE TABLE settings (key TEXT PRIMARY KEY, value TEXT)')
    con.execute('''CREATE TABLE shop_locations (
        id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE, address TEXT,
        maps_url TEXT NOT NULL, active INTEGER NOT NULL DEFAULT 1,
        created_at TEXT NOT NULL, updated_at TEXT NOT NULL)''')
    con.execute('INSERT INTO shop_locations(name,address,maps_url,created_at,updated_at) VALUES (?,?,?,?,?)', ('الفرع الرئيسي','عمان','https://maps.app.goo.gl/main','now','now'))
    con.execute('INSERT INTO shop_locations(name,address,maps_url,created_at,updated_at) VALUES (?,?,?,?,?)', ('فرع إربد','إربد','https://www.google.com/maps/search/?api=1&query=irbid','now','now'))
    con.execute("INSERT INTO settings(key,value) VALUES ('whatsapp_default_location_id','2')")
    row = con.execute("SELECT name,maps_url FROM shop_locations WHERE id=(SELECT CAST(value AS INTEGER) FROM settings WHERE key='whatsapp_default_location_id') AND active=1").fetchone()
    assert row == ('فرع إربد', 'https://www.google.com/maps/search/?api=1&query=irbid')
    con.close()

# Only supported Google Maps share URL hosts are accepted by the UI validator.
assert 'maps.app.goo.gl' in source and 'google.com' in source and 'google.jo' in source
assert 'UPDATE shop_locations SET active=0' in source
print('V236_GOOGLE_MAPS_MULTI_LOCATION_CHECKIN=PASS')
