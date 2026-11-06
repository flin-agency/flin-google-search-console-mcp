# Einreichung: flin Search Console 0.1.5

Vorbereiteter Stand vom 15. Oktober 2026. Noch nicht eingereicht oder veröffentlicht.

## Ziel und Grenzen

Eingereicht wird ein **Plugin bundle** für **Claude Code** aus dem Ordner `plugin/`.
Es enthält denselben lokalen Python-Server wie die Desktop-Erweiterung, mit festen
Abhängigkeiten. Es wird kein öffentlicher MCP-Server betrieben.

Die nötige Eingabe eigener Google-OAuth-Zugangsdaten über `userConfig` wird derzeit
von Claude Code unterstützt. Cowork fragt diese Werte nicht ab; im normalen Chat
werden lokale Plugin-Server nicht geladen. Deshalb wird dieser Stand nicht als
Cowork- oder Chat-Plugin angeboten. Für den bisherigen Desktop-Chat bleibt das
separate `.mcpb` verfügbar. Eine bestehende `.mcpb`-Installation wird durch einen
Verzeichniseintrag nicht migriert oder automatisch aktualisiert.

## Fertige Angaben fürs Portal

| Feld | Wert |
| --- | --- |
| Typ | Plugin bundle |
| Repository | `https://github.com/flin-agency/flin-google-search-console-mcp` |
| Plugin path | `plugin` |
| Branch | Standardbranch verwenden; erst nach geprüfter Veröffentlichung verbinden |
| Name | `flin-search-console` |
| Anzeigename | flin Search Console |
| Version | 0.1.5 |
| Anbieter | flin GmbH |
| Website | `https://flin.agency` |
| Anschrift | Weinbergstrasse 31, 8006 Zürich, Schweiz |
| Kontakt | `flin@flin.agency` |
| Datenschutzkontakt | Nicolas Glauser, `flin@flin.agency` |
| Dokumentation | `https://github.com/flin-agency/flin-google-search-console-mcp/blob/main/plugin/README.md` |
| Datenschutzerklärung | `https://github.com/flin-agency/flin-google-search-console-mcp/blob/main/PRIVACY.md` |
| Support | `https://github.com/flin-agency/flin-google-search-console-mcp/issues` |
| Lizenz | MIT |
| Symbol | `plugin/icon.svg` |

Firmenangaben wurden aus dem [Impressum](https://flin.agency/impressum/) und der
[Datenschutzseite](https://flin.agency/privacy-policy/) übernommen. Die beiden
neuen GitHub-Dokumentationslinks funktionieren erst, wenn die Dateien auf dem
angegebenen Branch veröffentlicht sind.

Kurzbeschreibung für die englische Auflistung:

> Read Google Search Console performance and URL indexing status in Claude Code. Requires your own Google Desktop OAuth client.

Beschreibung und mindestens drei ausführbare Beispielanfragen stehen in
[plugin/README.md](../plugin/README.md). Die technische Datenschutzerklärung liegt
in [PRIVACY.md](../PRIVACY.md), Supportinformationen in [SUPPORT.md](../SUPPORT.md).

## Angaben zur Datenverarbeitung

- **Eigene oder fremde API:** unabhängige Integration mit der Google Search Console
  API. Keine Behauptung, Google oder die Google-API zu besitzen oder zu vertreten.
  Zugriff nur auf Properties, für die das angemeldete Konto Berechtigungen hat.
- **Authentifizierung:** Nutzer stellen einen eigenen Google-OAuth-Client vom Typ
  Desktop-App bereit und melden sich über Googles Browser-Dialog an. Scope:
  `https://www.googleapis.com/auth/webmasters.readonly`.
- **Personendaten:** können in Suchanfragen, URLs und Property-Daten vorkommen;
  daher nicht pauschal „keine Personendaten“ angeben.
- **Übermittlung:** OAuth und Suchparameter an Google; Ergebnisse an den vom Nutzer
  verwendeten MCP-Client, bei Claude entsprechend an Anthropic. Keine eigene
  flin-Telemetrie oder Übermittlung der Ergebnisdaten an flin-Server.
- **Speicherung:** lokale OAuth-Token-Dateien bleiben bis zur Löschung erhalten;
  der Server speichert keine Ergebnisdatenbank. Client-Verlauf und Backups werden
  separat verwaltet. Tokens sind nicht vom Server verschlüsselt.
- **Schreibzugriffe:** keine Änderungen an Search Console oder Websites. Der lokale
  Anmeldevorgang speichert und erneuert Token-Dateien.
- **Zielgruppe:** Fachanwender für SEO und Website-Analyse; keine speziell an
  Minderjährige gerichtete Anwendung.
- **Finanztransaktionen, Werbung, Mediengenerierung:** keine solchen Funktionen.

Die Angaben müssen vor dem Absenden mit der finalen Version übereinstimmen.
Verbindliche Erklärungen und die Directory Terms bestätigt der zuständige
flin-Verantwortliche im Portal selbst.

## Prüferzugang vorbereiten

Die automatische Prüfung verwendet ausschließlich Dummy-Zugangsdaten. Sie ersetzt
keinen Test von Google-Anmeldung, Berechtigungen und echten Ergebnisdaten.

Für Anthropic fehlt noch ein bereitgestellter Testzugang mit einer eigenen,
nicht vertraulichen Search-Console-Testproperty und vorhandenen Leistungsdaten.
Der Eigentümer richtet ihn in Google ein und übermittelt Zugangsinformationen
ausschließlich im vorgesehenen privaten Reviewer-Kanal, niemals im Repository.

Bereitzustellen sind:

1. Exakter Property-Identifier, eine URL innerhalb der Property und ein Zeitraum
   mit vorhandenen Daten, die zur Prüfung freigegeben sind.
2. Ein Google-OAuth-Client vom Typ Desktop-App mit aktivierter Search Console API.
3. Ein Verfahren, mit dem die Prüfer sich anmelden können; bei OAuth-Testing die
   betreffenden Testnutzer zulassen. Keine privaten Mitarbeiter-Logins weitergeben.
4. Die Schritte aus [directory-review-tests.md](directory-review-tests.md).

Eine lokale Beispieldatei allein wäre kein voll funktionsfähiger Search-Console-
Testzugang. Nach dem Review nicht mehr benötigte Berechtigungen widerrufen.

## Einreichung durchführen

1. Lokale Änderungen einschließlich `plugin/runtime/` prüfen, committen und auf
   GitHub veröffentlichen. Die generierten Dateien gehören ins Repository, da
   Anthropic den Ordner direkt liest und keinen Build ausführt.
2. CI auf den vorgesehenen Plattformen bestehen lassen. Plugin mit einer aktuellen
   Claude-Code-Version und echtem Google-Zugriff testen. Der erfolgreiche Test der
   Desktop-Version 0.1.4 ist wertvoll, ersetzt aber nicht diesen Plugin-Test.
3. Datenschutzerklärung und Supportangaben freigeben; die öffentlichen URLs prüfen.
4. Mit dem Claude-Konto der langfristig verantwortlichen Organisation das
   [Entwicklerportal](https://claude.ai/directory/manage) öffnen. Ein bezahlter
   Claude-Tarif und entsprechende Organisationsrechte sind erforderlich.
5. GitHub verbinden: Das Konto benötigt Schreibzugriff auf das Repository.
6. **Submit new → Plugin bundle** wählen, Repository und `plugin` als Pfad eingeben.
   Das Repository darf zur Prüfung privat sein, muss vor Aufnahme öffentlich sein.
7. **Validate** ausführen, blockierende Funde beheben und erneut prüfen.
8. Angaben, Testzugang und Erklärungen vervollständigen; **Submit for review**.
   Nach erfolgreicher Prüfung die Veröffentlichung im Portal veranlassen.

Mit `uv run --locked` und Python-Code in einem Unterordner ist nach der aktuellen
Checkliste eine manuelle Prüfung zu erwarten. Das ist kein Beleg für einen Fehler
und keine Zusage der Aufnahme. Auch die Nutzung der fremden Google-API wird offen
deklariert; mögliche Rückfragen sind im Portal zu klären.

## Update-Einstellungen

Zunächst manuelle Veröffentlichung bestandener Versionen verwenden. Optional
GitHub-Push-Webhook aktivieren, damit Anthropic neue Commits schneller erkennt.
Das benötigt Administratorrechte im Repository. Automatische Veröffentlichung
erst aktivieren, wenn Anthropic sie für diesen Eintrag ermöglicht und der
gewünschte Freigabeprozess feststeht. Ein GitHub-Release allein ist keine
Veröffentlichung im Claude-Verzeichnis.

## Nachweis und noch offene Schritte

Lokal auf macOS geprüft:

| Prüfung | Ergebnis |
| --- | --- |
| Python-Tests | 102 bestanden |
| Offizieller Claude-Plugin-Validator 2.1.300, strenger Modus | Bestanden; unverbindlicher Hinweis zur Marketplace-Installationszeile |
| Offizieller MCPB-Validator 2.1.2 | Bestanden |
| Plugin-ZIP starten, acht Tools und Fehlerantworten prüfen | Bestanden, isolierte Dummy-Zugangsdaten |
| Desktop-Paket starten, acht Tools und Fehlerantworten prüfen | Bestanden, isolierte Dummy-Zugangsdaten |
| Python-Wheel und Quelldistribution | Erstellt |
| GitHub-Workflows | YAML geprüft; noch kein Lauf auf GitHub |

Die vorhandene globale Claude-Code-Installation ist Version 2.1.186. Für die
Manifestprüfung wurde isoliert der aktuelle Validator 2.1.300 eingesetzt;
deine installierte Anwendung wurde nicht aktualisiert. Für den Live-Test eine
aktuelle Claude-Code-Version mit den beschriebenen Konfigurationsfeldern verwenden.

- [x] Firmen- und Kontaktdaten aus der Website übernommen.
- [x] Plugin-Konfiguration, Beschreibung, Symbol, Lizenz und Datenschutztext vorbereitet.
- [x] Acht Tools als lesend und nicht destruktiv gekennzeichnet.
- [x] Paketbau, Versionsabgleich und isolierte Starttests in CI vorbereitet.
- [ ] Finalen Plugin-Test in Claude Code mit Google-Anmeldung durchführen.
- [ ] Testproperty und Reviewer-Zugang bereitstellen.
- [ ] Inhalte freigeben und GitHub-Veröffentlichung einschließlich CI abschließen.
- [ ] Portalvalidierung, Bedingungen und eigentliche Einreichung durchführen.

## Offizielle Grundlagen

- [Einreichung und Updates](https://claude.com/docs/plugins/submit)
- [Plugin-Prüfkriterien](https://claude.com/docs/plugins/pre-submission-checklist)
- [Unterstützung je Anwendung](https://claude.com/docs/plugins/platform-support)
- [Software Directory Policy](https://support.claude.com/en/articles/13145358-anthropic-software-directory-policy)
