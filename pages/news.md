---
layout: default
title: News
permalink: /news/
redirect_from:
  - /posts/
---

{% assign posts = site.posts %}
{% if posts.size == 0 %}No news yet.{% endif %}
<ul>
{% for post in posts %}
  <li><a href="{{ post.url | relative_url }}">{{ post.title }}</a> — {{ post.date | date_to_string }}</li>
{% endfor %}
</ul>