---
layout: events
title: Events
permalink: /events/
---

{% assign current_date = 'now' | date: '%Y-%m-%d' %}
{% assign upcoming = '' | split: '' %}
{% assign past = '' | split: '' %}

{% for event in site.events %}
  {% assign event_date = event.date | date: '%Y-%m-%d' %}
  {% if event_date >= current_date %}
    {% assign upcoming = upcoming | push: event %}
  {% else %}
    {% assign past = past | push: event %}
  {% endif %}
{% endfor %}

{% assign upcoming = upcoming | sort: "date" %}
{% assign past = past | sort: "date" | reverse %}

{% if upcoming.size > 0 %}
## Upcoming Events
{% for event in upcoming %}
  {% include event-preview.html event=event %}
{% endfor %}
{% else %}
## Upcoming Events
<p>No upcoming events yet.</p>
{% endif %}

{% if past.size > 0 %}
## Past Events
{% assign current_year = nil %}
{% for event in past %}
  {% assign event_year = event.date | date: "%Y" %}
  {% if event_year != current_year %}
    {% if current_year != nil %}
      </div>
    {% endif %}
    <h2>{{ event_year }}</h2>
    <div class="year-events">
    {% assign current_year = event_year %}
  {% endif %}
  {% include event-preview.html event=event %}
{% endfor %}
{% if current_year != nil %}
  </div>
{% endif %}
{% else %}
## Past Events
<p>No past events yet.</p>
{% endif %}

<!-- Debug Info -->
<!-- Total events: {{ site.events.size }} -->
<!-- Current date: {{ current_date }} -->
<!-- Upcoming events: {{ upcoming.size }} -->
<!-- Past events: {{ past.size }} -->