function parts = extract_parts(src)
    part_regex = '% =+@(?<part>\d+)=\s*\n';          % beginning of header
    part_regex = [part_regex '(?<description>(\s*%( [^\n]*)?\n)+?)']; % description
    part_regex = [part_regex '(\s*% ---+\s*\n'];     % optional beginning of template
    part_regex = [part_regex '(?<template>(\s*%( [^\n]*)?\n)*))?']; % solution template
    part_regex = [part_regex '\s*% =+\s*?\n'];       % end of header
    part_regex = [part_regex '(?<solution>.*?)'];    % solution
    part_regex = [part_regex '\s*check_part\s*\(\s*\)\s*;?\s*\n']; % beginning of validation
    part_regex = [part_regex '(?<validation>.*?)'];  % validation
    part_regex = [part_regex '(?=\n\s*(% )?% =+@)']; % beginning of next part
    [s, e, te, m, t, nm, sp] = regexp(src,part_regex,'dotall');
    if iscell(nm.part)
      for i=1:length(nm.part)
        parts{end+1} =  struct('part', nm.part(i),'solution', strtrim(nm.solution(i)),...
          'validation', strtrim(nm.validation(i)),...
          'description', regexprep(strtrim(nm.description(i)),'^\s*% ?','','lineanchors'),...
          'template', regexprep(regexprep(strtrim(nm.template(i)), '^\s*% -+\n', ''), '^\s*% ?','','lineanchors'));
      end
    else
      parts{1} = struct('part', nm.part,'solution', strtrim(nm.solution),...
      'validation', strtrim(nm.validation),...
      'description', regexprep(strtrim(nm.description),'^\s*% ?','','lineanchors'),...
      'template', regexprep(regexprep(strtrim(nm.template), '^\s*% -+\n', ''), '^\s*% ?','','lineanchors'));
    end
    % The last solution extends all the way to the validation code,
    % so we strip any trailing whitespace from it.
end


function parts = extract_solutions(src)
    part_regex = '% =+@(?<part>\d+)=\s*\n';          % beginning of header
    part_regex = [part_regex '(\s*%( [^\n]*)?\n)+?']; % description
    part_regex = [part_regex '\s*% =+\s*?\n'];       % end of header
    part_regex = [part_regex '(?<solution>.*?)'];    % solution
    part_regex = [part_regex '(?=\n\s*(% )?% =+@)']; % beginning of next part
    [s, e, te, m, t, nm, sp] = regexp(src,part_regex,'dotall');
    if iscell(nm.part)
      for i=1:length(nm.part)
        parts{end+1} =  struct('part', nm.part(i), 'solution', strtrim(nm.solution(i)));
      end
    else
      parts{1} = struct('part', nm.part, 'solution', strtrim(nm.solution));
    end
    % The last solution extends all the way to the validation code,
    % so we strip any trailing whitespace from it.
end


function [response,output] = submit_parts(submited_parts, url, token)
       data = savejson('',submited_parts); %.encode('utf-8')
       % test for python 3
       py_version = 'import sys; print(sys.version_info[0])';
       [r,out2] = system(['python -c "import sys; print(sys.version_info[0])"']);
       [r,out3] = system(['python3 -c "import sys; print(sys.version_info[0])"']);
       if str2num(out2) == 3
         py_cmd = 'python';
       elseif str2num(out3) == 3
         py_cmd = 'python3';
       else
         fprintf('napaka: Python ni na voljo!\nProsimo, da namestite Python 3 (www.python.org) in poskrbite, da je v sistemski poti.\n')
       end
       fprintf('Shranjujem v oblak... ')
       py_file = tempname();
       fp = fopen(py_file,'wt');
       fprintf(fp,'import json, urllib.request\n');
       fprintf(fp,'data = r"""'); 
       fwrite(fp,data); 
       fprintf(fp,'\n"""\n'); 
       fprintf(fp,'blk_data = data.encode("utf-8")\n');
       fprintf(fp,'headers = { "Authorization": "%s","content-type": "application/json" }\n',token);
       fprintf(fp,'request = urllib.request.Request("%s", data=blk_data, headers=headers)\n',url);
       fprintf(fp,'response = urllib.request.urlopen(request)\n');
       fprintf(fp,'print(response.read().decode("utf-8"))');
       fclose(fp);
       [response,output] = system([py_cmd ' ' py_file ' 2>&1']);
       if response
         disp('PRI SHRANJEVANJU SE JE ZGODILA NAPAKA! Poskusite znova.')
         disp(output)
       else
         disp('OK')
       end
end
