---
layout: default
title: Home
permalink: /
---
# Penguin Class
Welcome to the International Penguin Class Dinghy Association.

- [Join the class](/class/join)
- [Upcoming regattas](/events/)
- [Documents & rules](/docs/)

## Latest News
{% for post in site.posts limit:5 %}
<article class="teaser">
  <h3><a href="{{ post.url | relative_url }}">{{ post.title }}</a></h3>
  <p class="meta">{{ post.date | date_to_long_string }}</p>
  {{ post.excerpt }}
  <p><a href="{{ post.url | relative_url }}">Read more →</a></p>
</article>
{% endfor %}

<p><a href="{{ '/news/' | relative_url }}">More news →</a></p>

Explore the full legacy site in our [Archive](/archive/).
