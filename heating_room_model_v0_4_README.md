# Kúrenie – model miestnosti v0.4

Upravené z originálu `C:\Users\maros\Desktop\Kúrenie\heating_room_model_v0_3.yaml`. Originál zostal nezmenený.

## Použitie

Súbor heating_room_model_v0_4.yaml ulož do `/config/blueprints/automation/Marlo461/`. Pri existujúcej automatizácii zmeň cestu blueprintu z v0_3 na v0_4 a zachovaj jej vstupy. Nové vstupy majú predvolené hodnoty. Existujúce štyri výstupné helpery sa nemenia.

| Nastavenie | Homematic | Shelly PID |
|---|---|---|
| setpoint_mode | climate (predvolené) | number |
| thermostat_entity | pôvodná climate entita | môže zostať prázdne; iba záložná meraná teplota |
| setpoint_number_entity | prázdne | number.pid_izba |
| room_temperature_entity | externý senzor alebo pôvodný fallback | externý izbový senzor |
| pid_demand_entity | voliteľné | voliteľný výstup PID 0–100 % |

Blueprint iba číta vstupy a zapisuje štyri výstupné helpery. Nezapisuje setpoint ani polohu ventilov. Pri režime number ignoruje HVAC režim Shelly. Externá číselná izbová teplota má prioritu pred current_temperature. Bez platnej izbovej teploty alebo setpointu vráti nulovú potrebu a vodu a pozastaví učenie.

## Zachovaná logika

Výpočet potreby ostáva 70 % teplotná zložka + 30 % ventilová zložka, s pôvodnými teplotnými prahmi, blokovaním oknom a váhou miestnosti. Ak je zadaný platný PID demand, nahradí iba ventilovú zložku. Výstup modelu preto nemusí byť rovný PID demand. Nezadaný/nečíselný demand použije pôvodné ventily; číselný demand sa obmedzí na 0–100 %.

Vzorce radiátora, učenie W/K, dôvera, päťminútový interval učenia a výpočet požadovanej vody zostávajú zachované. PID demand nenahrádza fyzické otvorenie ventilov pri učení. Pri Shelly s fyzickým rozsahom 0–20 % sa pôvodný prah učenia 85 % bežne nedosiahne; táto verzia nezavádza neoverený prepočet prietoku. Bez ventilových vstupov sa W/K neučí.

Zmeny externého senzora, PID setpointu, PID demand a okien vyvolajú prepočet. Voliteľné vstupy sleduje state_changed udalosť s filtrom pred akciami; ostatné udalosti sa odmietnu. Učenie sa vykonáva iba na pôvodnom päťminútovom spúšťači.

Pôvodné správanie výstupu potrebnej vody zostáva zachované: pri vypnutom HmIP alebo otvorenom okne môže byť vypočítaná voda nenulová, kým potreba tepla je nula. Centrálna regulácia musí rešpektovať potrebu tepla.

## Overenie

Overené načítanie YAML, syntax všetkých Jinja šablón, 18 porovnaní HmIP proti v0.3, priorita externého senzora, režim number nezávislý od HVAC, limity a fallback demand, učenie iba pri periodickom spúšťači a zápisy iba do helperov. Lokálna simulácia nenahrádza kontrolu konfigurácie a skúšku priamo v Home Assistante; tam verzia zatiaľ nebola nasadená.

Schéma vychádza z [dokumentácie blueprintov Home Assistant](https://www.home-assistant.io/docs/blueprint/schema/) a [spúšťačov automatizácií](https://www.home-assistant.io/docs/automation/trigger/).
