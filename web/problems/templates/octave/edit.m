function {{ problem.slug|safe }}_edit
check = struct();
if exist('OCTAVE_VERSION','builtin')
  src = char(fileread(mfilename('fullpathext')));
else
  src = char(fileread(strcat(mfilename('fullpathext'),'.m')));
end

file_parts = extract_parts(src);
check_initialize(file_parts);
{% load i18n %}
% NE SPREMINJAJ prvih vrstic

% =============================================================================
% {{ problem.title|safe }}{% if problem.description %}
%
% {{ problem.description|indent:'% '|safe }}{% endif %}{% for part in problem.parts.all %}
% =====================================================================@{{ part.id|stringformat:'06d'}}=
% {{ part.description|indent:'% '|safe }}{% if part.template %}
% -----------------------------------------------------------------------------
% {{ part.template|indent:'% '|safe }}{% endif %}
% =============================================================================
{{ part.solution|safe }}

check_part();
{{ part.validation|safe }}

{% endfor %}
% % =====================================================================@000000=
% % {% blocktrans %}  This is a template for a new problem part. To create a new part, uncomment
% % the template and fill in your content.
% %
% % Define a function `multiply(x, y)` that returns the product of `x` and `y`.
% % For example:
% %
% %     octave> multiply(3, 7)
% %     ans = 21
% %     octave> multiply(6, 7)
% %     ans = 42{% endblocktrans %}
% % =============================================================================
%
% function p = {% trans 'multiply' %}(x, y)
%     p =  x * y;
% end
%
% check_part();
%
% check_equal('{% trans 'multiply' %}(3, 7)', 21);
% check_equal('{% trans 'multiply' %}(6, 7)', 42);
% check_equal('{% trans 'multiply' %}(10, 10)', 100);
% check_secret({% trans 'multiply' %}(100, 100));
% check_secret({% trans 'multiply' %}(500, 123));


% ===========================================================================@=
% {% trans 'Do not change this line or anything below it.' %}
% =============================================================================

validate_current_edit_file(src,check.parts);

% =L=I=B=R=A=R=Y=@=

% "Ce vam Octave/Matlab javi, da je v tej vrstici napaka,
% se napaka v resnici skriva v zadnjih vrsticah va"se kode.

% Kode od tu naprej NE SPREMINJAJTE!

% check.m
{% include 'octave/check_functions.m' %}
% check.m
% varargin2struct.m
{% include 'octave/jsonlab.m' %}

{% include 'octave/utils.m' %}

function validation = validate_current_edit_file(src,parts)
  n = length(parts);
  valid = [];
  for i=1:n
    parts{i}.problem = {{ problem.id }};
    parts{i}.solution = parts{i}.solution;
    parts{i}.validation = parts{i}.validation;
    if str2num(parts{i}.part) != 0
      parts{i}.id = str2num(parts{i}.part);
    end
    valid  = [valid parts{i}.valid];
    parts{i} = rmfield(rmfield(rmfield(parts{i},'valid'),'feedback'),'part');
  end
  problem_regex = ['% =+\s*\n',...               % beginning of header
      '\s*% (?<title>[^\n]*)\n',...              % title
      '(?<description>(\s*%( [^\n]*)?\n)*?)',... % description
      '(?=\s*(% )?% =+@)',];                     % beginning of first part
  [s, e, te, m, t, nm, sp] = regexp(src,problem_regex,'dotall');
  if isempty(parts)
    parts = {}
  end
  problem = struct(
    'parts',{parts},
    'title',strtrim(nm.title),
    'description',regexprep(strtrim(nm.description),'^\s*% ?','','lineanchors'),
    'id', {{ problem.id }},
    'problem_set', {{ problem.problem_set.id }}
  );
  check_summarize()
  if all(valid)
    shranim = input('Ali nalogo shranim na "stre"znik? (da/ne) ','s');
    if strtrim(shranim) == 'da'
      printf('Shranjujem nalogo... ');
      url = '{{ submission_url }}';
      token = 'Token {{ authentication_token }}';
      response = submit_parts(problem, url, token);
    end
  else
    disp('Problem ni dobro formuliran!');
  end
end

end	% edit.m
