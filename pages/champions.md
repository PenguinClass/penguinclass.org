---
layout: default
title: Champions & History
permalink: /champions/
---

# Champions & History

The International Penguin Class Dinghy Association maintains records of championship results and honors our champions across different series.

## International Champions

The Penguin International Championship is the premier event of the class, held annually to determine the world champion.

<table>
  <thead>
    <tr><th>Year</th><th>Champion</th><th>Crew</th><th>Club</th><th>Location</th><th>Boat</th><th>Results</th></tr>
  </thead>
  <tbody>
  {%- assign intl_champs = site.data.champions | where_exp: "c", "c.result_id contains 'international-'" | sort: "year" | reverse -%}
  {%- for c in intl_champs -%}
    {%- assign r = site.results | where: "id", c.result_id | first -%}
    <tr>
      <td>{% if r %}<a href="{{ r.url }}">{{ c.year }}</a>{% else %}{{ c.year }}{% endif %}</td>
      <td>{{ c.skipper }}</td>
      <td>{{ c.crew }}</td>
      <td>{{ c.club }}</td>
      <td>{{ c.location }}</td>
      <td>{{ c.boat }}</td>
      <td>
        {%- if c.results_url -%}
          <a href="{{ c.results_url }}">view</a>
        {%- elsif r and r.results_url -%}
          <a href="{{ r.results_url }}">view</a>
        {%- else -%}
          —
        {%- endif -%}
      </td>
    </tr>
  {%- endfor -%}
  </tbody>
</table>

## North American Champions

The North American Championship is a prestigious regional event that showcases top talent across the continent.

<table>
  <thead>
    <tr><th>Year</th><th>Champion</th><th>Crew</th><th>Club</th><th>Location</th><th>Boat</th><th>Results</th></tr>
  </thead>
  <tbody>
  {%- assign na_champs = site.data.champions | where_exp: "c", "c.result_id contains 'north-american-'" | sort: "year" | reverse -%}
  {%- for c in na_champs -%}
    {%- assign r = site.results | where: "id", c.result_id | first -%}
    <tr>
      <td>{% if r %}<a href="{{ r.url }}">{{ c.year }}</a>{% else %}{{ c.year }}{% endif %}</td>
      <td>{{ c.skipper }}</td>
      <td>{{ c.crew }}</td>
      <td>{{ c.club }}</td>
      <td>{{ c.location }}</td>
      <td>{{ c.boat }}</td>
      <td>
        {%- if c.results_url -%}
          <a href="{{ c.results_url }}">view</a>
        {%- elsif r and r.results_url -%}
          <a href="{{ r.results_url }}">view</a>
        {%- else -%}
          —
        {%- endif -%}
      </td>
    </tr>
  {%- endfor -%}
  </tbody>
</table>

## Championship History

### International Championship
The International Championship has been held annually since 1941, with the exception of 1942-1944 during World War II, and in 2020 for COVID-19. This prestigious event brings together the world's best Penguin sailors to compete for the title of International Champion.

### North American Championship
The North American Championship was first sailed in 1965 and held only in years when the Internationals were in South America.

## Hall of Fame

The Penguin Class honors outstanding sailors and contributors through various recognition programs:

- **International Champions** - All-time winners of the premier event
- **North American Champions** - Regional championship winners
- **Class Officers** - Past and present leadership
- **Fleet Champions** - Regional and local fleet champions
- **Special Recognition** - Outstanding contributions to the class

## Historical Records

For comprehensive historical results, championship records, and detailed regatta reports, please visit our [Archive](/archive/legacy-website/) which contains:

- Complete championship histories
- Annual regatta results
- Historical photos and reports
- Fleet championship records
- Regional event outcomes

*Detailed historical records and championship information are maintained in the [Archive](/archive/legacy-website/).*
