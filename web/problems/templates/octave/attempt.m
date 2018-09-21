function {{ problem.slug|safe }}

check = struct();
% NE BRIŠI prvih dveh vrstic

%
% =============================================================================
% {{ problem.title|safe }}{% if problem.description %}
%
% {{ problem.description|indent:"% "|safe }}{% endif %}{% for part, solution_attempt in parts %}
% =====================================================================@{{ part.id|stringformat:'06d'}}=
% {{ forloop.counter }}. podnaloga
% {{ part.description|indent:"% "|safe }}
% =============================================================================
{{ solution_attempt|safe }}{% endfor %}














































































































































% ============================================================================@


% 'Če vam Octave/Matlab sporoča, da je v tej vrstici sintaktična napaka,';
% 'se napaka v resnici skriva v zadnjih vrsticah vaše kode.';

% 'Kode od tu naprej NE SPREMINJAJTE!';

% check.m
{% include 'octave/check_functions.m' %}
% check.m
% varargin2struct.m
{% include 'octave/jsonlab.m' %}

{% include 'octave/utils.m' %}


function update_attempts(response)
  valid_regex = "([0-9]+): *([01])";
  [s,e,te,m,t,nm,sp] = regexp(char(response),valid_regex);
  for i = 1:length(t)
    for j = 1:length(check.parts)
      if str2num(check.parts(j).part) == str2num(t{i}{1})
        % get validation from server response
        % TODO add feedback
        check.parts(j).valid = str2num(t{i}{2});
      end
    end
  end
end


function validation = validate_current_file(src)

%            backup_filename = '{0}.{1}'.format(filename, suffix)
%            suffix += 1
%        shutil.copy(filename, backup_filename)
%        return backup_filename
%
%
  file_parts = extract_solutions(src);
  check_initialize(file_parts);

  {% for part, _, token in parts %}
      if check_part()
        check.current_part.token = '{{ token }}';
        try
              {{ part.validation|default:"0;"|indent:"  "|safe }}
          catch err
              check_error(["Testi sprožijo izjemo\n" err.message]);
          end
      end
  {% endfor %}



submited_parts = cell(0, 0);
for part = check.parts
    part = part{1};
    if check_has_solution(part)
        part.feedback = savejson('',part.feedback);
        submited_parts{end+1} = part;
     end
end

url = "{{ submission_url }}";
token = "Token {{ authentication_token }}";

response = submit_parts(submited_parts, url, token);
update_attempts(response);
check_summarize()
end
if exist('OCTAVE_VERSION','builtin')
  src = char(fileread(mfilename('fullpathext')));
else
  % mfilename in Matlab does not return .m
  src = char(fileread(strcat(mfilename('fullpathext'),'.m')));
end

validate_current_file(src);
% attempt.m
