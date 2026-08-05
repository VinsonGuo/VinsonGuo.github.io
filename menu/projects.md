---
layout: page
title: Projects
permalink: /projects
body_class: projects
---

<div class="projects-head">
  <p>Apps I've designed, built, and shipped.</p>
</div>

<div class="projects-grid">
  {% assign projects = site.projects | sort: "order" %}
  {% for project in projects %}
    <a class="projects-card" href="{{ site.github.url }}{{ project.url }}">
      <div class="projects-card-top">
        <img class="projects-card-logo" src="{{ site.github.url }}{{ project.logo }}" alt="{{ project.title }} logo">
        <div class="projects-card-info">
          <h2>{{ project.title }}</h2>
          <p>{{ project.tagline }}</p>
        </div>
        <span class="projects-card-arrow">→</span>
      </div>
      <div class="projects-card-chips">
        {% for p in project.platforms %}
          <span class="projects-chip">{{ p }}</span>
        {% endfor %}
      </div>
    </a>
  {% endfor %}
</div>
