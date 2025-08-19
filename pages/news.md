---
layout: default
title: News
permalink: /news/
redirect_from:
  - /posts/
---

{% assign posts = site.posts %}
{% if posts.size == 0 %}
<p>No news yet.</p>
{% else %}
  {% assign current_year = nil %}
  {% for post in posts %}
    {% assign post_year = post.date | date: "%Y" %}
    {% if post_year != current_year %}
      {% if current_year != nil %}
        </ul>
      {% endif %}
      <h2>{{ post_year }}</h2>
      <ul>
      {% assign current_year = post_year %}
    {% endif %}
    <li><a href="{{ post.url | relative_url }}">{{ post.title }}</a> — {{ post.date | date_to_string }}</li>
  {% endfor %}
  {% if current_year != nil %}
    </ul>
  {% endif %}
{% endif %}