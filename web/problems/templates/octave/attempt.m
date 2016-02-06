global check;
check = struct();
# NE BRIŠI prvih dveh vrstic

#
# =============================================================================
# {{ problem.title|safe }}{% if problem.description %}
#
# {{ problem.description|indent:"# "|safe }}{% endif %}{% for part, solution_attempt in parts %}
# =====================================================================@{{ part.id|stringformat:'06d'}}=
# {{ forloop.counter }}. podnaloga
# {{ part.description|indent:"# "|safe }}
# =============================================================================
{{ solution_attempt|safe }}{% endfor %}














































































































































# ============================================================================@


'Če vam Octave sporoča, da je v tej vrstici sintaktična napaka,';
'se napaka v resnici skriva v zadnjih vrsticah vaše kode.';

'Kode od tu naprej NE SPREMINJAJTE!';

# check.m
{% include 'octave/check_functions.m' %}
# check.m
# varargin2struct.m
{% include 'octave/jsonlab.m' %}

{% include 'octave/utils.m' %}


function update_attempts(response)
  global check
  valid_regex = "([0-9]+): *([01])";
  [s,e,te,m,t,nm,sp] = regexp(char(response),valid_regex);
  for i = 1:length(t)
    for j = 1:length(check.parts)
      if str2num(check.parts(j).part) == str2num(t{i}{1})
        # get validation from server response
        # TODO add feedback
        check.parts(j).valid = str2num(t{i}{2});
      end
    end
  end
endfunction


function validation = validate_current_file()
  global check;

#    def backup(filename):
#        backup_filename = None
#        suffix = 1
#        while not backup_filename or os.path.exists(backup_filename):
%            backup_filename = '{0}.{1}'.format(filename, suffix)
%            suffix += 1
%        shutil.copy(filename, backup_filename)
%        return backup_filename
%
%
  src = char(fileread(mfilename("fullpathext")));
  fclose(fp);
  file_parts = extract_parts(src);
  check_initialize(file_parts);

  {% for part, _ in parts %}
      if check_part()
          try
              {{ part.validation|default:"0;"|indent:"  "|safe }}
          catch err
              check_error(["Testi sprožijo izjemo\n" err.message]);
          end
      end
  {% endfor %}



submited_parts = cell();
for part = check.parts
    if check_has_solution(part)
        #data = [data '{ "secret":'
        part.feedback = savejson('',part.feedback);
        submited_parts(end+1) = part;
        #submited_parts(end).feedback = savejson(submited_parts(end).feedback);
     end
end

url = "{{ submission_url }}";
token = "Token {{ authentication_token }}";

response = submit_parts(submited_parts, url, token);
update_attempts(response);
check_summarize()
endfunction

validate_current_file();
# attempt.m
