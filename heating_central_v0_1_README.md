# Centrálne riadenie kúrenia v0.1

Riadi zatiaľ obývačku; ďalšie izby sa dopĺňajú do zoznamu `rooms` v balíku. Najvyššia platná požiadavka >= 5 % povoľuje teplotu z existujúcej ekvitermiky (30–60 °C). Pri vonkajšej teplote >= 17 °C, neplatnom vonkajšom údaji/krivke, vypnutom centrálnom riadení alebo chýbajúcej platnej požiadavke zapisuje 0 do `number.boiler_selflowtemp`.

Požiadavka izby sa započíta iba s číselnou izbovou teplotou a aspoň jedným dostupným ventilom tej istej izby s hlásenou polohou > 0,5 %. Pri PID miestnosti sa navyše vyžaduje dostupný zapnutý PID. Zadané okenné kontakty musia byť off; neplatný kontakt blokuje izbu. Hlásená poloha nie je meranie prietoku ani potvrdenie dostatočného minimálneho prietoku kotlom.

Obnovuje požiadavku každú minútu, pri zmenách vstupov, po štarte HA a po skončení TÚV. `switch.boiler_heatingactivated` zapína pri potrebe kúrenia; pri nulovej potrebe posiela iba nulovú teplotu. TÚV nemení. Nedostupný kotol nemôže ovládať, ďalší pokus nastane pri minútovom obnovení. Nezavádza minimálnu dobu horenia ani meranie čerstvosti senzorov; tieto vlastnosti treba vyhodnotiť pri reálnom kúrení.

## Nasadenie
1. Ulož `heating_central_v0_1.yaml` do `packages/heating_central_v0_1.yaml` vedľa svojho `configuration.yaml`.
2. Ak ešte nepoužívaš packages, doplň do configuration.yaml:
   ```yaml
   homeassistant:
     packages: !include_dir_named packages
   ```
   Ak už existuje `homeassistant:`, vlož len `packages:` pod neho. Nevytváraj druhý kľúč. Ak už používaš iný spôsob načítania packages, prispôsob umiestnenie existujúcemu spôsobu; nenahrádzaj ho naslepo.
3. Skontroluj konfiguráciu v HA. Pred reštartom vypni starú automatizáciu **Kotol - Ekvitermická regulácia**. Táto automatizácia musí byť jediným pravidelným zapisovateľom požiadavky kotlu. PID, ventily, model v0.5 a senzor ekvitermiky ponechaj aktívne.
4. Reštartuj HA. Nový hlavný prepínač je pri prvom vytvorení vypnutý; pri ďalších reštartoch obnoví svoj stav. Simulácia sa pri každom štarte vypne a jej požiadavka sa nastaví na 0.
5. Skontroluj nové entity a zapni `input_boolean.heating_central_enabled`.

Toto je package, nie blueprint. Neimportuje sa cez obrazovku Blueprinty.

## Simulácia
`input_boolean.heating_simulation_enabled` nahrádza požiadavku obývačky hodnotou `input_number.heating_simulated_demand`. Neotvára ventily a nemení setpoint ani výstup PID. Môže reálne zapnúť kúrenie, keď je centrálne riadenie zapnuté a ostatné podmienky platia. Pri zatvorených ventiloch ostane vyhodnotená požiadavka 0. Letný limit 17 °C a ekvitermika platia aj počas simulácie.

Postup testu: pri vypnutom centrálnom riadení môžeš overiť vyhodnotenú požiadavku bez kladného príkazu kotlu. Zvýš setpoint obývačky, aby PID otvoril ventily. Zapni simuláciu a nastav napr. 40 %. Vyhodnotená požiadavka má byť 40 %. Po zapnutí centrálneho riadenia sa pri platnej zimnej krivke vypočítaná teplota vody nastaví podľa ekvitermiky. Zníženie simulácie na 0 musí poslať 0 kotlu. Nakoniec vypni simuláciu a vráť pôvodný setpoint.

Prepínač centrálneho riadenia off znamená posielať nulovú požiadavku, nie prestať komunikovať s kotlom. Diagnostické input_number sú výstupy; ich ručná zmena neovláda kotol. Vypočítaná teplota vody nie je potvrdenie, že ju kotol prijal; over aj `number.boiler_selflowtemp` a `sensor.boiler_curflowtemp`.

## Karta do dashboardu
```yaml
type: entities
title: Centrálne kúrenie
show_header_toggle: false
entities:
  - input_boolean.heating_central_enabled
  - input_boolean.heating_simulation_enabled
  - input_number.heating_simulated_demand
  - input_number.heating_effective_demand
  - input_number.heating_flow_target
  - sensor.ekvitermika_pozadovana_teplota_vody
  - number.boiler_selflowtemp
  - sensor.boiler_curflowtemp
```

## Pridanie izby
Do `variables.rooms` doplň ďalšiu položku s reálnymi ID:
```yaml
- name: Dalsia izba
  demand: input_number.dalsia_izba_potreba_tepla
  temperature: sensor.dalsia_izba_teplota
  simulate: false
  valves:
    - sensor.dalsia_izba_ventil_percenta
  windows: []
```
Pre domectrl PID doplň `pid: number.pid_dalsia_izba`. Pre Homematic ho vynechaj. Polohy musia byť v percentách 0–100, nie 0–1. Po úprave znovu načítaj automatizácie. Zoznam sledovaných vstupov sa zostaví automaticky. Každá izba potrebuje vlastný funkčný model a ovládanie ventilov. Ostatné, zatiaľ nepridané izby nemôžu zapnúť kotol.

## Overenie
YAML sa úspešne načítal a 18 scenárov prešlo vykonaním skutočných Jinja šablón s náhradami funkcií HA: normálna požiadavka, nulová požiadavka, zatvorené/nedostupné ventily, vypnutý PID, neplatná teplota a ekvitermika, hlavný vypínač, letný limit, horný limit vody, simulácia vrátane nuly, malá požiadavka a ďalšia miestnosť s oknom.
Home Assistant runtime, fyzický kotol a časovanie udalostí neboli v tomto prostredí testované. Pred nasadením vykonaj kontrolu konfigurácie HA a pozri stopu novej automatizácie.
