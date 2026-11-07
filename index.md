---
layout: default
title: Home
permalink: /
---
# Welcome to the<br />International Penguin Class Dinghy Association

{% include highlight-slideshow.html config="/assets/data/highlight-home.json" %}

<nav class="jump-nav" aria-label="Jump to section">
  <a class="jump-btn" href="#results">Results</a>
  <a class="jump-btn" href="#events">Events</a>
  <a class="jump-btn" href="#news">News</a>
  <a class="jump-btn" href="#classifieds">Classifieds</a>
</nav>

{% include home/results.html %}

{% include home/events.html %}

{% include home/news.html %}

{% include home/classifieds.html %}

<section class="home-cta" aria-label="Get involved">
  <a class="home-cta-card" href="{{ '/penguin/plans/' | relative_url }}">
    <span class="home-cta-title">Build a Penguin</span>
    <span class="home-cta-text">Plans, specs and suppliers for building your own boat.</span>
  </a>
  <a class="home-cta-card" href="{{ '/archive/' | relative_url }}">
    <span class="home-cta-title">Explore the Archives</span>
    <span class="home-cta-text">Documents, photos, results, yearbooks and the legacy website.</span>
  </a>
</section>
