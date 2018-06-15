\documentclass[arhiv]{../izpit}
\usepackage{fouriernc}
\usepackage{xcolor}
\usepackage{tikz}

\begin{document}

\izpit{ {{ problem_set.course.title }}: {{ problem_set.title }} }{???}{
  {{ problem_set.description|safe }}
}

{% for problem in problem_set.problems.all %}
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\naloga[{{ problem.title }}]
{{ problem.description|safe }}

{% for part in problem.parts.all %}
\podnaloga
{{ part.description|safe }}
{% endfor %}

{% endfor %}

\end{document}
