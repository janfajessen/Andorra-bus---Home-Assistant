<div align="center">

# Andorra Bus <br> Home Assistant Integration

<img src="brands/logo@2x.png" width="450"/>

![Version](https://img.shields.io/badge/version-1.5.24-blue?style=for-the-badge)
![HA](https://img.shields.io/badge/Home%20Assistant-2024.1+-orange?style=for-the-badge&logo=home-assistant)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python)
![HACS](https://img.shields.io/badge/HACS-Custom-41BDF5?style=for-the-badge&logo=homeassistantcommunitystore&logoColor=white)
[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-Donate-yellow?style=for-the-badge&logo=buymeacoffee)](https://www.buymeacoffee.com/janfajessen)
[![Patreon](https://img.shields.io/badge/Patreon-Support-red?style=for-the-badge&logo=patreon)](https://www.patreon.com/janfajessen)
<!--[![Ko-Fi](https://img.shields.io/badge/Ko--Fi-Support-teal?style=for-the-badge&logo=ko-fi)](https://ko-fi.com/janfajessen)
[![GitHub Sponsors](https://img.shields.io/badge/GitHub%20Sponsors-Support-pink?style=for-the-badge&logo=githubsponsors)](https://github.com/sponsors/janfajessen)
[![PayPal](https://img.shields.io/badge/PayPal-Donate-blue?style=for-the-badge&logo=paypal)](https://paypal.me/janfajessen)-->

</div>

<p align="center">
  <b>Horaris de bus en temps real d'Andorra per a Home Assistant</b><br/>
  <sub>Powered by FEDA Mou-te · feda.hafas.cloud</sub>
</p>

---


<details>
<summary>🇪🇸 Español </summary>

## Andorra Bus para Home Assistant

Integración personalizada para obtener los horarios en tiempo real de los autobuses públicos de Andorra (FEDA Mou-te) directamente en Home Assistant.

### Características

- Tiempo real — horarios actualizados cada minuto desde la API oficial HAFAS de FEDA
- Cualquier parada — busca por nombre, navega todas las paradas de Andorra o filtra por línea
- Sensores automáticos por línea — un sensor por cada línea que pasa por la parada
- Buses nocturnos — incluye líneas BN
- Retrasos en tiempo real — muestra adelantos y retrasos cuando la API los proporciona
- Sin servicio silencioso — los días sin servicio no genera errores en el log

### Sensores creados

| Sensor | Estado | Descripción |
|--------|--------|-------------|
| `bus_[parada]_propera_sortida` | `11 min L2` | Próxima salida con línea y minutos |
| `bus_[parada]_l2` | `11:16` | Próxima salida de la línea L2 |
| `bus_[parada]_bn2` | `Mañana 23:57` | Próxima salida del bus nocturno |

### Instalación via HACS (recomendada)

1. Abre **HACS → Integraciones → ⋮ → Repositorios personalizados**
2. Añade `https://github.com/janfajessen/andorra_bus` como **Integración**
3. Busca **Andorra Bus** e instala
4. Reinicia Home Assistant
5. Ve a **Configuración → Integraciones → Añadir integración** y busca **Andorra Bus**
<img src="brands/icon@2x.png" width="150"/>

### Instalación manual

1. Descarga los archivos de este repositorio
2. Copia la carpeta `andorra_bus` a `/config/custom_components/andorra_bus/`
3. Reinicia Home Assistant

### Configuración

| Método | Descripción |
|--------|-------------|
| Por nombre | Escribe el nombre de la parada (ej: `Valira Nova`) |
| Todas las paradas | Navega la lista completa de paradas de Andorra |
| Por línea | Filtra por número de línea (ej: `L2`, `BN2`) |

### Ejemplo de automatización

```yaml
automation:
  alias: "Aviso bus en 10 minutos"
  trigger:
    - platform: template
      value_template: >
        {% set mins = state_attr('sensor.bus_valira_nova_213_propera_sortida', 'minutes_until') %}
        {{ mins is not none and mins | int <= 10 and mins | int > 9 }}
  action:
    - service: notify.mobile_app_telefon
      data:
        message: >
          El bus sale en
          {{ state_attr('sensor.bus_valira_nova_213_propera_sortida', 'minutes_until') }} minutos —
          {{ state_attr('sensor.bus_valira_nova_213_propera_sortida', 'line') }}
```

### Notas técnicas

- Usa la API HAFAS de `feda.hafas.cloud` (la misma que la app oficial FEDA Mou-te)
- No requiere ninguna clave de API ni registro
- Intervalo de actualización: **60 segundos** — Ventana de tiempo: **24 horas**

</details>

---

<details>
<summary>🇫🇷 Français </summary>

## Andorra Bus pour Home Assistant

Intégration personnalisée pour obtenir les horaires en temps réel des bus publics d'Andorre (FEDA Mou-te) directement dans Home Assistant.

### Fonctionnalités

- Temps réel — horaires mis à jour chaque minute depuis l'API officielle HAFAS de FEDA
- N'importe quel arrêt — recherche par nom, liste complète ou par ligne
- Capteurs automatiques par ligne — un capteur pour chaque ligne desservant l'arrêt
- Bus de nuit — inclut les lignes BN
- Retards en temps réel — affiche les avances et retards quand l'API les fournit
- Sans service silencieux — pas d'erreurs dans le log les jours sans service

### Capteurs créés

| Capteur | État | Description |
|---------|------|-------------|
| `bus_[arret]_propera_sortida` | `11 min L2` | Prochain départ avec ligne et minutes |
| `bus_[arret]_l2` | `11:16` | Prochain départ de la ligne L2 |
| `bus_[arret]_bn2` | `Demain 23:57` | Prochain départ du bus de nuit |

### Installation via HACS (recommandée)

1. Ouvrez **HACS → Intégrations → ⋮ → Dépôts personnalisés**
2. Ajoutez `https://github.com/janfajessen/andorra_bus` comme **Intégration**
3. Cherchez **Andorra Bus** et installez
4. Redémarrez Home Assistant
<img src="brands/icon@2x.png" width="150"/>

### Installation manuelle

1. Téléchargez les fichiers de ce dépôt
2. Copiez le dossier `andorra_bus` dans `/config/custom_components/andorra_bus/`
3. Redémarrez Home Assistant

### Configuration

| Méthode | Description |
|---------|-------------|
| Par nom | Tapez le nom de l'arrêt (ex : `Valira Nova`) |
| Tous les arrêts | Parcourez la liste complète des arrêts d'Andorre |
| Par ligne | Filtrez par numéro de ligne (ex : `L2`, `BN2`) |

### Notes techniques

- Utilise l'API HAFAS de `feda.hafas.cloud` (même backend que l'app officielle FEDA Mou-te)
- Aucune clé API ni inscription requise
- Intervalle de mise à jour : **60 secondes** — Fenêtre de temps : **24 heures**

</details>

---

<details>
<summary>🇬🇧 English </summary>

## Andorra Bus for Home Assistant

Custom integration to get real-time public bus schedules for Andorra (FEDA Mou-te) directly in Home Assistant.

### Features

- Real-time — schedules updated every minute from the official FEDA HAFAS API
- Any stop — search by name, browse all stops in Andorra, or filter by line
- Automatic sensors per line — one sensor for each line serving the selected stop
- Night buses — includes BN lines
- Real-time delays — shows early arrivals and delays when provided by the API
- Silent no-service — no log errors on days with no service

### Created sensors

| Sensor | State | Description |
|--------|-------|-------------|
| `bus_[stop]_propera_sortida` | `11 min L2` | Next departure with line and minutes |
| `bus_[stop]_l2` | `11:16` | Next departure for line L2 |
| `bus_[stop]_bn2` | `Tomorrow 23:57` | Next night bus departure |

### HACS installation (recommended)

1. Open **HACS → Integrations → ⋮ → Custom repositories**
2. Add `https://github.com/janfajessen/andorra_bus` as an **Integration**
3. Search for **Andorra Bus** and install
4. Restart Home Assistant
5. Go to **Settings → Integrations → Add integration** and search **Andorra Bus**
<img src="brands/icon@2x.png" width="150"/>

### Manual installation

1. Download the files from this repository
2. Copy the `andorra_bus` folder to `/config/custom_components/andorra_bus/`
3. Restart Home Assistant

### Configuration

| Method | Description |
|--------|-------------|
| By name | Type the stop name (e.g. `Valira Nova`) |
| All stops | Browse the full list of stops in Andorra |
| By line | Filter by line number (e.g. `L2`, `BN2`) |

### Technical notes

- Uses the HAFAS API at `feda.hafas.cloud` (same backend as the official FEDA Mou-te app)
- No API key or registration required
- Update interval: **60 seconds** — Time window: **24 hours**
- Coverage: all urban and interurban lines in Andorra (L1-L5, BN1-BN3...)

</details>

---

<details>
<summary>🇵🇹 Português </summary>

## Andorra Bus para Home Assistant

Integração personalizada para obter os horários em tempo real dos autocarros públicos de Andorra (FEDA Mou-te) diretamente no Home Assistant.

### Funcionalidades

- Tempo real — horários atualizados a cada minuto a partir da API oficial HAFAS da FEDA
- Qualquer paragem — pesquise por nome, navegue por todas as paragens ou filtre por linha
- Sensores automáticos por linha — um sensor para cada linha que serve a paragem
- Autocarros noturnos — inclui linhas BN
- Atrasos em tempo real — mostra antecipações e atrasos quando a API os fornece
- Sem serviço silencioso — sem erros no log nos dias sem serviço

### Sensores criados

| Sensor | Estado | Descrição |
|--------|--------|-----------|
| `bus_[paragem]_propera_sortida` | `11 min L2` | Próxima partida com linha e minutos |
| `bus_[paragem]_l2` | `11:16` | Próxima partida da linha L2 |
| `bus_[paragem]_bn2` | `Amanhã 23:57` | Próxima partida do autocarro noturno |

### Instalação via HACS (recomendada)

1. Abra **HACS → Integrações → ⋮ → Repositórios personalizados**
2. Adicione `https://github.com/janfajessen/andorra_bus` como **Integração**
3. Procure **Andorra Bus** e instale
4. Reinicie o Home Assistant
<img src="brands/icon@2x.png" width="150"/>

### Instalação manual

1. Descarregue os ficheiros deste repositório
2. Copie a pasta `andorra_bus` para `/config/custom_components/andorra_bus/`
3. Reinicie o Home Assistant

### Configuração

| Método | Descrição |
|--------|-----------|
| Por nome | Escreva o nome da paragem (ex: `Valira Nova`) |
| Todas as paragens | Navegue pela lista completa de paragens de Andorra |
| Por linha | Filtre por número de linha (ex: `L2`, `BN2`) |

### Notas técnicas

- Utiliza a API HAFAS de `feda.hafas.cloud` (o mesmo backend que a app oficial FEDA Mou-te)
- Não requer chave de API nem registo
- Intervalo de atualização: **60 segundos** — Janela de tempo: **24 horas**

</details>


## Andorra Bus per a Home Assistant

Integració personalitzada per obtenir els horaris en temps real dels autobusos públics d'Andorra (FEDA Mou-te) directament a Home Assistant, sense cap clau d'API ni registre.

### Característiques

- Temps real — horaris actualitzats cada minut des de l'API oficial HAFAS de FEDA
- Qualsevol parada — cerca per nom, navega totes les parades d'Andorra o filtra per línia
- Sensors automàtics per línia — un sensor per cada línia que passa per la parada
- Busos nocturns — inclou línies BN (Bus Nocturn)
- Retards en temps real — mostra avanços i retards quan l'API els proporciona
- Sense servei silenciós — els dies sense servei no genera errors al log
- Multilingüe — interfície en català, castellà, anglès, francès i portuguès

### Sensors creats

Per a cada parada configurada, la integració crea automàticament:

| Sensor | Estat | Descripció |
|--------|-------|------------|
| `bus_[parada]_propera_sortida` | `11 min L2` | Pròxima sortida amb línia i minuts |
| `bus_[parada]_l2` | `11:16` | Pròxima sortida de la línia L2 |
| `bus_[parada]_l4` | `Demà 08:00` | Pròxima sortida de la línia L4 |
| `bus_[parada]_bn2` | `Dl 23:57` | Pròxima sortida del bus nocturn |

Els sensors de línia es creen **dinàmicament** segons les línies que l'API retorna. Els dies de cap de setmana amb menys servei simplement no mostren algunes línies.

#### Atributs dels sensors

**`propera_sortida`**
```yaml
stop_id: "1002"
stop_name: Valira Nova - 213
line: Bus L2
direction: Andorra la Vella
minutes_until: 11
delay_minutes: 0
planned_departure: "2026-03-16T19:16:00+00:00"
realtime_departure: "2026-03-16T19:16:00+00:00"
upcoming_departures:
  - line: Bus L2
    direction: Andorra la Vella
    time: "20:16"
    minutes_until: 11
    delay_minutes: 0
  - line: Bus L4
    direction: Andorra la Vella
    time: "20:32"
    minutes_until: 27
    delay_minutes: 0
```

**Sensors de linia**
```yaml
stop_id: "1002"
stop_name: Valira Nova - 213
line: Bus L2
direction: Andorra la Vella
minutes_until: 11
delay_minutes: 0
next_departures:
  - time: "20:16"
    minutes_until: 11
    direction: Andorra la Vella
    delay_minutes: 0
```

---

### Installació via HACS (recomanada)

1. Obre **HACS → Integracions → ⋮ → Repositoris personalitzats**
2. Afegeix `https://github.com/janfajessen/andorra_bus` com a **Integració**
3. Busca **Andorra Bus** i instal·la
4. Reinicia Home Assistant
5. Ves a **Configuració → Integracions → Afegir integració** i cerca **Andorra Bus**
<img src="brands/icon@2x.png" width="150"/>

### Instal·lació manual

1. Baixa els fitxers d'aquest repositori
2. Copia la carpeta `andorra_bus` a `/config/custom_components/andorra_bus/`
3. Reinicia Home Assistant
4. Ves a **Configuració → Integracions → Afegir integració** i cerca **Andorra Bus**

### Configuració

Durant la installacio pots cercar la teva parada de tres maneres:

| Metode | Descripció |
|--------|------------|
| Per nom | Escriu el nom de la parada (ex: `Valira Nova`) |
| Totes les parades | Navega la llista completa de parades d'Andorra |
| Per linia | Filtra per número de línia (ex: `L2`, `BN2`) |

---

### Targetes per a Home Assistant

#### 1. Taulell de sortides complet (Markdown Card)

> Requereix [card-mod](https://github.com/thomasloven/lovelace-card-mod) per als estils de fons. Sense card-mod funciona igualment pero sense el fons fosc.

```yaml
type: markdown
card_mod:
  style: |
    ha-card {
      background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
      border-radius: 16px;
      border: 1px solid rgba(255,255,255,0.08);
    }
    ha-markdown { padding: 16px !important; }
content: >
  {% set entity = 'sensor.bus_valira_nova_213_propera_sortida' %}
  {% set attrs = state_attr(entity, 'upcoming_departures') or [] %}
  {% set mins = state_attr(entity, 'minutes_until') | int(0) %}
  {% set delay = state_attr(entity, 'delay_minutes') | int(0) %}
  {% set line = state_attr(entity, 'line') %}

  Parada: **{{ state_attr(entity, 'stop_name') }}** → {{ state_attr(entity, 'direction') }}

  {% if mins <= 0 %}
  **ARA** — {{ line }}
  {% elif mins <= 5 %}
  **{{ mins }} min** — {{ line }}
  {% else %}
  **{{ mins }} min** — {{ line }}
  {% endif %}
  {% if delay < 0 %}(avanc {{ delay }} min)
  {% elif delay > 0 %}(retard +{{ delay }} min){% endif %}

  | Hora | Linia | Min | Retard |
  |:----:|:------|----:|:-------|
  {% for d in attrs %}
  {% set dm = d.minutes_until | int(0) %}
  {% set dl = d.delay_minutes | int(0) %}
  | **{{ d.time }}** | {{ d.line | replace('Bus ','') }} | {{ dm }}' | {% if dl < 0 %}+{{ dl }}m{% elif dl > 0 %}+{{ dl }}m{% else %}-{% endif %} |
  {% endfor %}
```

#### 2. Dues parades en una sola targeta

```yaml
type: markdown
content: >
  {% set parades = [
    'sensor.bus_valira_nova_213_propera_sortida',
    'sensor.bus_valira_nova_214_propera_sortida'
  ] %}
  {% for entity in parades %}
  {% if states(entity) not in ('unknown','unavailable') %}
  {% set attrs = state_attr(entity, 'upcoming_departures') or [] %}
  {% set mins = state_attr(entity, 'minutes_until') | int(0) %}
  {% set line = state_attr(entity, 'line') %}
  {% set delay = state_attr(entity, 'delay_minutes') | int(0) %}

  **{{ state_attr(entity, 'stop_name') }}**

  {% if mins <= 0 %}ARA — {{ line }}
  {% elif mins <= 5 %}{{ mins }} min — {{ line }}
  {% else %}{{ mins }} min — {{ line }}{% endif %}
  {% if delay != 0 %}({% if delay > 0 %}+{% endif %}{{ delay }} min){% endif %}

  {% for d in attrs[:4] %}
  `{{ d.time }}` {{ d.line | replace('Bus ','') }} — {{ d.minutes_until }} min
  {% endfor %}
  {% if not loop.last %}---{% endif %}
  {% else %}
  Sense dades
  {% endif %}
  {% endfor %}
```

#### 3. Targeta Entities classica

```yaml
type: entities
title: Bus Valira Nova
entities:
  - entity: sensor.bus_valira_nova_213_propera_sortida
    name: Proxima sortida
    icon: mdi:bus-clock
  - entity: sensor.bus_valira_nova_213_l2
    name: Linia L2
    icon: mdi:bus
  - entity: sensor.bus_valira_nova_213_l4
    name: Linia L4
    icon: mdi:bus
  - entity: sensor.bus_valira_nova_213_bn2
    name: Bus Nocturn BN2
    icon: mdi:weather-night
```

#### 4. Targeta Glance compacta

```yaml
type: glance
title: Bus Valira Nova
columns: 3
entities:
  - entity: sensor.bus_valira_nova_213_propera_sortida
    name: Proxima
  - entity: sensor.bus_valira_nova_213_l2
    name: L2
  - entity: sensor.bus_valira_nova_213_l4
    name: L4
  - entity: sensor.bus_valira_nova_213_bn2
    name: BN2
  - entity: sensor.bus_valira_nova_214_propera_sortida
    name: Dir. 214
```

---

### Automatitzacions

#### Avís quan el bus surt en menys de 10 minuts

```yaml
automation:
  alias: "Avis bus en 10 minuts"
  trigger:
    - platform: template
      value_template: >
        {% set mins = state_attr('sensor.bus_valira_nova_213_propera_sortida', 'minutes_until') %}
        {{ mins is not none and mins | int <= 10 and mins | int > 9 }}
  condition:
    - condition: time
      after: "07:00:00"
      before: "22:00:00"
  action:
    - service: notify.telegram_jan
      data:
        message: >
          El bus surt en {{ state_attr('sensor.bus_valira_nova_213_propera_sortida', 'minutes_until') }} minuts!
          Linia: {{ state_attr('sensor.bus_valira_nova_213_propera_sortida', 'line') }}
          Desti: {{ state_attr('sensor.bus_valira_nova_213_propera_sortida', 'direction') }}
```

#### Avís si el bus porta retard

```yaml
automation:
  alias: "Avis retard bus"
  trigger:
    - platform: template
      value_template: >
        {{ state_attr('sensor.bus_valira_nova_213_propera_sortida', 'delay_minutes') | int(0) >= 5 }}
  action:
    - service: notify.telegram_jan
      data:
        message: >
          El bus {{ state_attr('sensor.bus_valira_nova_213_propera_sortida', 'line') }}
          porta {{ state_attr('sensor.bus_valira_nova_213_propera_sortida', 'delay_minutes') }} minuts de retard.
          Nova hora: {{ state_attr('sensor.bus_valira_nova_213_propera_sortida', 'upcoming_departures')[0].time }}
```

#### Recordatori matinal amb el primer bus del dia

```yaml
automation:
  alias: "Bon dia - primer bus"
  trigger:
    - platform: time
      at: "07:00:00"
  condition:
    - condition: not
      conditions:
        - condition: state
          entity_id: sensor.bus_valira_nova_213_propera_sortida
          state: "unavailable"
  action:
    - service: notify.telegram_jan
      data:
        message: >
          Bon dia! Primer bus disponible:
          {{ state_attr('sensor.bus_valira_nova_213_propera_sortida', 'line') }}
          a les {{ state_attr('sensor.bus_valira_nova_213_propera_sortida', 'upcoming_departures')[0].time }}
          cap a {{ state_attr('sensor.bus_valira_nova_213_propera_sortida', 'direction') }}
```

#### Avís intel·ligent només dies laborables

```yaml
automation:
  alias: "Avis bus intel·ligent"
  trigger:
    - platform: template
      value_template: >
        {% set mins = state_attr('sensor.bus_valira_nova_213_propera_sortida', 'minutes_until') %}
        {{ mins is not none and mins | int == 8 }}
  condition:
    - condition: time
      after: "07:30:00"
      before: "21:00:00"
    - condition: time
      weekday:
        - mon
        - tue
        - wed
        - thu
        - fri
  action:
    - service: notify.telegram_jan
      data:
        message: "Bus en 8 minuts — {{ state_attr('sensor.bus_valira_nova_213_propera_sortida', 'line') }}"
```

---

### Notes tècniques

- Utilitza l'API HAFAS de `feda.hafas.cloud` — la mateixa que l'app oficial FEDA Mou-te
- No requereix cap clau d'API ni registre
- Interval d'actualització predeterminat: **60 segons**
- Finestra de temps consultada: **24 hores** (inclou busos de l'endemà)
- Cobertura: totes les línies urbanes i interurbanes (L1-L5, BN1-BN3...)
- Dies sense servei: la integració retorna llista buida silenciosament, sense errors al log

---

---

<p align="center">
  Fet amb carinyo a Andorra · Hecho con cariño en Andorra · Fait avec amour en Andorre · Made with love in Andorra · Feito com carinho em Andorra
  <br/><br/>
  <a href="https://github.com/janfajessen/andorra_bus/issues">Reportar un error</a> ·
  <a href="https://github.com/janfajessen/andorra_bus/discussions">Discussions</a>
</p>
