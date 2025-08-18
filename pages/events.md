---
layout: default
title: Events
permalink: /events/
---

{% assign upcoming = site.events | where_exp:"e","e.date >= site.time" | sort: "date" %}
{% assign past = site.events | where_exp:"e","e.date < site.time" | sort: "date" | reverse %}

## Upcoming
{% if upcoming.size == 0 %}No upcoming events yet.{% endif %}
{% for e in upcoming %}
- [{{ e.title }}]({{ e.url }}) — {{ e.date | date_to_string }}{% if e.venue %}, {{ e.venue }}{% endif %}
{% endfor %}

## Past
{% if past.size == 0 %}No past events yet.{% endif %}
{% for e in past %}
- [{{ e.title }}]({{ e.url }}) — {{ e.date | date_to_string }}
{% endfor %}

<!-- Debug Info -->
<!-- Total events: {{ site.events.size }} -->
<!-- Current time: {{ site.time }} -->
<!-- Upcoming events: {{ upcoming.size }} -->
<!-- Past events: {{ past.size }} -->