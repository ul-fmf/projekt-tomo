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

function parts = extract_parts(filename)
    f = fopen(filename, 'r');
    source = '';
    while (s = fgets(f)) > -1
      source = [source s];
    end
    fclose(f)
    part_regex = '# =+@(?<part>\d+)=\n';  # beginning of header
    part_regex = [part_regex '(#( [^\n]*)?\n)+']; # description
    part_regex = [part_regex '# =+\n'];           # end of header
    part_regex = [part_regex '(?<solution>.*?)'];# solution
    part_regex = [part_regex '(?=\n# =+@)'];     # beginning of next part

    [s, e, te, m, t, nm, sp] = regexp(source,part_regex,'dotall');
    if iscell(nm.part)
      parts = [];
      for i=1:length(nm.part)
        parts = [parts struct("part",nm.part(i),"solution", strtrim(nm.solution(i)))];
      end
    else
      parts = [struct("part",nm.part,"solution",strtrim(nm.solution))];
    end
    # The last solution extends all the way to the validation code,
    # so we strip any trailing whitespace from it.
endfunction

function [response,output] = submit_parts(parts, url, token)
       submited_parts = cell();
       for part = parts
           if check_has_solution(part)
               #data = [data '{ "secret":'
               part.feedback = savejson('',part.feedback);
               submited_parts(end+1) = part;
               #submited_parts(end).feedback = savejson(submited_parts(end).feedback);
            end
        end
       #data = [data "]" ];
       data = savejson('',submited_parts); #.encode('utf-8')
       pycall = [...
       'python3 - 2>&1 << EOF',"\n",...
       'import json, urllib.request',"\n",...
       'data = r"""' data '"""',"\n",...
       'blk_data = data.encode("utf-8")',"\n",...
       'headers = { "Authorization": "' token '","content-type": "application/json" }',"\n",...
       'request = urllib.request.Request("' url '", data=blk_data, headers=headers)',"\n",...
       'response = urllib.request.urlopen(request)',"\n",...
       'response = json.loads(response.read().decode("utf-8"))',"\n",...
       'for part in response["attempts"]:',"\n",...
       '  print("%s: %d" %(part["part"],part["valid"]))',"\n",...
       'EOF'];
       # TODO print feedback as well
       # disp(pycall)

       #'response = post(''' url ''')'
       #'print(response.text)"']
       [response,output] = system(pycall);
       if response
         disp('PRI SHRANJEVANJU JE PRIŠLO DO NAPAKE! Poskusite znova.')
         disp(output)
       else
         disp('rešitve so shranjene.')
       end
       #request = urllib.request.Request(url, data=data, headers=headers)
       #response = urllib.request.urlopen(request)
       #return json.loads(response.read().decode('utf-8'))
endfunction
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
%  filename = argv()(end) # current filename
  filename = which("{{ problem_title }}");
  file_parts = extract_parts(filename);
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

printf('Shranjujem rešitve na strežnik... ');
url = "{{ submission_url }}"; #'https://www.projekt-tomo.si/api/attempts/submit/';
token = "Token {{ authentication_token }}"; #'Token 0779d82c83d98c1e4a5480e4e6f57b906598f5ee';
response = submit_parts(check.parts, url, token);
update_attempts(response);
check_summarize()
endfunction

validate_current_file();
# attempt.m
