---
layout: default
title: Classifieds
permalink: /classifieds/
---

## Classifieds

Buy, sell, or trade Penguin boats, parts, and equipment within the class community.

### Recent Listings

{%- for classified in site.classifieds reversed -%}
<article class="classified-preview">
  <h3><a href="{{ classified.url }}">{{ classified.title }}</a></h3>
  <p class="meta">
    <strong>Posted:</strong> {{ classified.date | date_to_long_string }}
    {%- if classified.contact %}
    • <strong>Contact:</strong> {{ classified.contact }}
    {%- endif %}
  </p>
  <p class="excerpt">{{ classified.content | strip_html | truncatewords: 30 }}</p>
</article>
{%- endfor -%}

### Submit a Classified Ad

To submit a classified ad, please contact the Class Secretary with the following information:

- **Title:** Brief description of the item
- **Description:** Detailed description with photos (if available)
- **Contact Information:** Name, email, and/or phone number
- **Price:** If applicable

Classified ads are free for class members and help keep Penguins sailing in the community.

### Guidelines

- Classified ads are for Penguin-related items only
- Ads are reviewed before posting
- Contact information is required
- Photos are encouraged but not required
- Ads are typically removed after 6 months or when item is sold

*For questions about classified ads, please contact the [Class Secretary](/class/officers/).* 