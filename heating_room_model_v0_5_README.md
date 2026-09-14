# Kúrenie – model miestnosti v0.5

## Dôvod zmeny
Vo v0.4 zostávala pri setpointe a nulovom PID potreba tepla približne 8,2 %.
Pri nedokúrení aspoň 1,5 °C model požadoval 100 % aj pri menšom alebo nulovom PID.
Verzia v0.5 v režime number používa priamo normalizovaný výstup PID.

## Správanie
- Režim number vyžaduje číselný setpoint z domectrl PID Controller, atribút pid_enable true, izbovú teplotu a číselný pid_demand_entity.
- Potreba tepla = PID demand × room_weight, obmedzená na 0–100 %.
- Vypnutý PID, neplatný alebo chýbajúci demand: potreba 0 %. Nepoužíva sa náhrada polohou ventilu.
- Otvorené zadané okno, chýbajúca izbová teplota/setpoint a setpoint ≤ 5 °C: potreba 0 %.
- Pri heat_need 0 je aj required_supply 0, pre oba režimy.
- Režim climate zachováva pôvodný výpočet potreby tepla v0.4.
- Výpočet sa spustí aj pri štarte HA. Zmena atribútu pid_enable sa zachytí existujúcim state_changed filtrom.
- PID bez kladnej platnej požiadavky sa nepoužíva na učenie W/K.
- Model zapisuje iba štyri pomocníky; neovláda ventily ani kotol.

## Obývačka – migrácia
Importuj heating_room_model_v0_5.yaml z tejto vetvy pomocou jeho GitHub URL.
V existujúcej automatizácii zmeň iba alias a use_blueprint.path na:
```yaml
alias: Kúrenie – Obývačka – model v0.5
use_blueprint:
  path: Marlo461/heating_room_model_v0_5.yaml
```
Celú existujúcu sekciu input zachovaj. Nevytváraj druhú aktívnu automatizáciu zapisujúcu do tých istých helperov.
Ak HA pri importe uloží inú cestu, použi cestu z importovaného blueprintu.
Všetky štyri výstupné helpery musia povoľovať hodnotu 0.

## Kontrola v HA (váha 1)
| Scenár | Potreba tepla |
|---|---:|
| PID 0 %, teplota presne na setpointe | 0 % |
| PID 0 %, miestnosť 2 °C pod setpointom | 0 % |
| PID 40 %, miestnosť 2 °C pod setpointom | 40 % |
| PID 40 %, teplota na setpointe | 40 % |
| PID vypnutý, helper zostal na 40 % | 0 % |
| Demand unavailable/unknown alebo nezadaný | 0 % |
| Otvorené nakonfigurované okno | 0 % |

Pri nulovej potrebe musí required_supply zostať 0 aj s predtým naučeným W/K.
Over tiež climate režim s existujúcou konfiguráciou a aktualizáciu po reštarte HA.

## Rozsah overenia a obmedzenia
Zmeny boli skontrolované oproti zdrojovému v0.4; v tomto prostredí nie je dostupný beh Home Assistanta ani YAML/Jinja runtime. Tabuľka je postup overenia, nie tvrdenie o vykonanom teste v HA.
Učenie W/K stále vyžaduje výkon radiátorov, prívod, spiatočku a splnenie pôvodných podmienok; prah 85 % fyzickej polohy nie je prispôsobený Shelly rozsahu 0–20 %.
Kladný PID sám nepotvrdzuje otvorený ventil ani prietok. Centrálne riadenie musí zohľadniť dostupnosť ventilov, ich otvorenie, zaokrúhlenie pri prepočte 0–100 % na 0–20 % a požiadavky ostatných miestností.
Číselný zastaraný údaj sa automaticky neoznačí ako neplatný. Detekcia zastaveného PID a čerstvosti snímača nie je súčasťou tejto zmeny.
Naučená teplota prívodu nie je zatiaľ pripravená na priame riadenie kotla bez pravidiel dôvery a limitov. Existujúca ekvitermická automatizácia kotla sa touto zmenou nemení.
