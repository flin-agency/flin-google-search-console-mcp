# flin Search Console 0.1.4 in Claude prüfen

Stand: 15. Oktober 2026. Das Paket ist lokal vorbereitet; es wurde noch kein
GitHub Release veröffentlicht.

## 1. Installieren

Paket: `flin-google-search-console-mcp-0.1.4.mcpb`

1. Öffne die aktuelle **Claude Desktop-App**.
2. Gehe zu **Einstellungen → Erweiterungen / Extensions → Erweiterte
   Einstellungen / Advanced settings → Install Extension…** und wähle das
   Paket aus. Je nach Sprache und App-Version können die Bezeichnungen abweichen.
3. Trage deine **Google OAuth Client ID** und das dazugehörige **Client Secret**
   ein. Verwende bei einer bestehenden Installation denselben Google-OAuth-Client
   vom Typ „Desktop-App“. Die optionale Standard-Property kannst du zunächst leer lassen.
4. Aktiviere die Erweiterung **flin Search Console** für einen neuen Chat.

Das Paket gehört in die Desktop-Erweiterungen. Das Fenster „Benutzerdefinierten
Connector hinzufügen“ mit einer HTTPS-URL aus deinem Screenshot ist für einen
gehosteten Server gedacht.

Beim ersten Start braucht Claude eine Internetverbindung, um Python und die
festgelegten Abhängigkeiten zu laden. Falls dir die Google-Zugangsdaten noch
fehlen, stehen die Einrichtungsschritte im [README](../README.md#claude-desktop-quickstart).
Trage das Client Secret nur im Einstellungsformular ein.

Wenn die bisherige manuelle Installation ebenfalls aktiv ist, wähle für diese
Tests ausdrücklich die neue Erweiterung. Falls du die beiden nicht unterscheiden
kannst, deaktiviere den bisherigen Eintrag vorübergehend und starte Claude neu.

## 2. Diese Anfragen nacheinander testen

### Verbindung prüfen

> Führe health_check mit der Erweiterung „flin Search Console“ aus und zeige mir den Status.

**Erwartet:** `oauth_required` vor der ersten Anmeldung oder `ready` / `refreshable`
bei einer bereits vorhandenen Anmeldung. `oauth_required` ist an dieser Stelle
normal. `missing_configuration` bedeutet, dass die Zugangsdaten im Formular fehlen.

### Google-Anmeldung und Properties prüfen

> Liste mit der Erweiterung „flin Search Console“ meine Search-Console-Properties auf.

**Erwartet:** Falls erforderlich, öffnet sich die Google-Anmeldung im Browser.
Danach erscheinen die Properties, auf die dein gewähltes Konto Zugriff hat.
Eine vorhandene Anmeldung am üblichen Speicherort kann wiederverwendet werden;
ein eigener Token-Pfad aus der manuellen Konfiguration wird nicht automatisch übernommen.

### Echte Leistungsdaten abrufen

Ersetze `[PROPERTY]` durch einen exakten Wert aus der Liste, einschließlich
`sc-domain:` beziehungsweise `https://` und gegebenenfalls abschließendem `/`.

> Zeige für [PROPERTY] vom 01.09.2026 bis 30.09.2026 die Klicks, Impressionen, CTR und durchschnittliche Position. Verwende get_site_summary mit search_type="web" und data_state="final".

> Zeige für dieselbe Property und denselben Zeitraum die zehn wichtigsten Suchanfragen und die zehn wichtigsten Seiten. Verwende get_top_queries und get_top_pages jeweils mit row_limit=10.

**Erwartet:** Ergebnisse für die gewählte Property. Vergleiche die Zusammenfassung
mit Search Console bei gleichem Zeitraum, Suchtyp und ohne zusätzliche Filter.
Nutze einen anderen abgeschlossenen Zeitraum, falls September keine Daten enthält.
Die Summe der zehn Einzelzeilen muss nicht der Gesamtsumme entsprechen.

### URL-Prüfung testen

Ersetze `[URL]` durch eine echte URL innerhalb der gewählten Property.

> Prüfe mit inspect_url den Indexierungsstatus von [URL] in [PROPERTY].

**Erwartet:** Googles Indexierungsinformationen oder eine verständliche Meldung zu
fehlender Berechtigung beziehungsweise nicht verfügbaren Informationen. Die
Prüfung beantragt keine Indexierung und verändert die Website nicht.

### Anmeldung nach Neustart prüfen

Beende Claude vollständig, öffne es erneut und wiederhole die Property-Liste.

**Erwartet:** Die gespeicherte Anmeldung funktioniert weiter, sofern Google sie
nicht widerrufen hat. Es sollte nicht bei jedem Neustart eine Anmeldung nötig sein.

## 3. Ergebnis festhalten

- [ ] Paket lässt sich installieren; die drei Einstellungsfelder erscheinen.
- [ ] Erweiterung startet und health_check liefert einen nachvollziehbaren Status.
- [ ] Anmeldung und Property-Liste funktionieren.
- [ ] Zusammenfassung, Suchanfragen und Seiten liefern passende Daten.
- [ ] URL-Prüfung funktioniert für eine eigene URL.
- [ ] Anmeldung bleibt nach Neustart nutzbar.

Bei einem Fehler notiere den betroffenen Schritt, Claude-Version, Betriebssystem
und die angezeigte Fehlermeldung. Keine Tokens oder Client Secrets mitsenden.

## Bereits geprüft und noch offen

**Automatisch geprüft:** 94 Tests bestanden; Manifest mit dem offiziellen MCPB-Werkzeug
validiert; das entpackte Paket erfolgreich gestartet; alle acht Tools sowie
Konfiguration und Fehlerantworten geprüft. Der Test verwendet Dummy-Zugangsdaten.
Das Paket enthält keine lokalen `.env`-Dateien oder Google-Tokens.

**Noch offen:** Installation in deiner Claude-Version und die obigen Tests mit
echtem Google-Zugriff. Der GitHub-Release-Ablauf ist vorbereitet, aber noch nicht
auf GitHub ausgeführt. Windows ist in CI vorgesehen und lokal nicht geprüft.

Das Paket ist unsigniert. Die beiliegende Datei `SHA256SUMS` dient der
Integritätsprüfung. Neue private Paketversionen werden aus GitHub Releases
heruntergeladen und manuell installiert; automatische Updates sind nicht eingerichtet.

Offizielle [Claude-Anleitung für lokale Erweiterungen](https://support.claude.com/en/articles/10949351-getting-started-with-local-mcp-servers-on-claude-desktop).
