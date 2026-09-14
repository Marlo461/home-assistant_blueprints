import math
import yaml
from jinja2.nativetypes import NativeEnvironment

cfg = yaml.safe_load(open('heating_central_v0_1.yaml'))
a = cfg['automation'][0]
env = NativeEnvironment()
def numeric(x):
    try:
        return math.isfinite(float(x))
    except (ValueError, TypeError):
        return False

base = {
 'input_boolean.heating_central_enabled': 'on',
 'input_boolean.heating_simulation_enabled': 'off',
 'input_number.heating_simulated_demand': '60',
 'input_number.obyvacka_potreba_tepla_0_100': '38',
 'sensor.senzor_obyvacka_air_temperature': '24',
 'number.pid_obyvacka': '26',
 'number.trv1_valve_position': '7.81',
 'number.trv2_valve_position': '7.82',
 'sensor.ekvitermika_pozadovana_teplota_vody': '35',
 'sensor.boiler_outdoortemp': '10',
}
def evaluate(changes=None, enabled=True, extra=None):
    states = base | (changes or {})
    context = dict(
      rooms=a['variables']['rooms'] + (extra or []),
      states=lambda e: states.get(e, 'unavailable'),
      is_state=lambda e,v: states.get(e) == v,
      state_attr=lambda e,k: enabled if k == 'pid_enable' else None,
      is_number=numeric,
    )
    demand = env.from_string(a['actions'][0]['variables']['effective_demand']).render(**context)
    target = env.from_string(a['actions'][1]['variables']['flow_target']).render(**context, effective_demand=demand)
    watched = env.from_string(a['variables']['watched_entities']).render(**context)
    assert 'number.trv2_valve_position' in watched
    assert 'input_number.heating_effective_demand' not in watched
    return float(demand), float(target)

assert evaluate() == (38,35)
assert evaluate({'input_number.obyvacka_potreba_tepla_0_100':'0'}) == (0,0)
assert evaluate({'number.trv1_valve_position':'0','number.trv2_valve_position':'0'}) == (0,0)
assert evaluate({'number.trv1_valve_position':'unavailable'}) == (38,35)
assert evaluate(enabled=False) == (0,0)
assert evaluate({'sensor.senzor_obyvacka_air_temperature':'unavailable'}) == (0,0)
assert evaluate({'input_boolean.heating_central_enabled':'off'}) == (38,0)
assert evaluate({'sensor.boiler_outdoortemp':'17'}) == (38,0)
assert evaluate({'sensor.boiler_outdoortemp':'unavailable'}) == (38,0)
assert evaluate({'sensor.ekvitermika_pozadovana_teplota_vody':'unavailable'}) == (38,0)
assert evaluate({'sensor.ekvitermika_pozadovana_teplota_vody':'75'}) == (38,60)
assert evaluate({'input_boolean.heating_simulation_enabled':'on'}) == (60,35)
assert evaluate({'input_boolean.heating_simulation_enabled':'on','input_number.heating_simulated_demand':'0'}) == (0,0)
assert evaluate({'input_boolean.heating_simulation_enabled':'on','number.trv1_valve_position':'0','number.trv2_valve_position':'0'}) == (0,0)
assert evaluate({'input_number.obyvacka_potreba_tepla_0_100':'4'}) == (4,0)
room = dict(name='Test', demand='input_number.test', temperature='sensor.test', valves=['number.test'], windows=['binary_sensor.window'])
extra_states={'input_number.test':'70','sensor.test':'20','number.test':'50','binary_sensor.window':'off'}
assert evaluate(extra_states, extra=[room]) == (70,35)
assert evaluate(extra_states | {'binary_sensor.window':'on'}, extra=[room]) == (38,35)
assert evaluate(extra_states | {'binary_sensor.window':'unavailable'}, extra=[room]) == (38,35)
print('PASS: YAML parsed; 18 Jinja scenarios including simulation, valves, faults, second room, window and flow limits.')
