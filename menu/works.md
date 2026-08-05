---
layout: page
title: Works
permalink: /works
body_class: works
---

<div class="works-head">
  <p>Apps I've designed, built, and shipped.</p>
</div>

<div class="works-grid">
  {% assign works = site.works | sort: "order" %}
  {% for work in works %}
    <a class="works-card" href="{{ site.github.url }}{{ work.url }}">
      <div class="works-card-top">
        <img class="works-card-logo" src="{{ site.github.url }}{{ work.logo }}" alt="{{ work.title }} logo">
        <div class="works-card-info">
          <h2>{{ work.title }}</h2>
          <p>{{ work.tagline }}</p>
        </div>
        <span class="works-card-arrow">→</span>
      </div>
      <div class="works-card-chips">
        {% for p in work.platforms %}
          <span class="works-chip">{{ p }}</span>
        {% endfor %}
      </div>
    </a>
  {% endfor %}
</div>
