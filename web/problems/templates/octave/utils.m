function parts = extract_parts(src)
    part_regex = '# =+@(?<part>\d+)=\n';  # beginning of header
    part_regex = [part_regex '(?<description>(#( [^\n]*)?\n)+)']; # description
    part_regex = [part_regex '# =+\n'];           # end of header
    part_regex = [part_regex '(?<solution>.*?)']; # solution
    part_regex = [part_regex 'check_part\(\)\n']; # beginning of validation
    part_regex = [part_regex '(?<validation>.*?)']; # validation
    part_regex = [part_regex '(?=\n(# )?# =+@)']; # beginning of next part        
    [s, e, te, m, t, nm, sp] = regexp(src,part_regex,'dotall');
    if iscell(nm.part)
      for i=1:length(nm.part)
        parts{end+1} =  struct("part",nm.part(i),
          "solution", strtrim(nm.solution(i)),
          "validation", strtrim(nm.validation(i)),
          "description", regexprep(strtrim(nm.description(i)),"^#","",'lineanchors')
          );
      end
    else      
      parts{1} = struct("part",nm.part,
      "solution",strtrim(nm.solution),
      "validation",strtrim(nm.validation),
      "description", regexprep(strtrim(nm.description),"^# ","",'lineanchors')
      );
    end
    # The last solution extends all the way to the validation code,
    # so we strip any trailing whitespace from it.
endfunction


function [response,output] = submit_parts(submited_parts, url, token)
       #data = [data "]" ];
       data = savejson('',submited_parts); #.encode('utf-8')
       % test for python 3
       py_version = 'import sys; print(sys.version_info[0])';
       [r,out2] = system(["python -c '" py_version "'"]);
       [r,out3] = system(["python3 -c '" py_version "'"]);
       if str2num(out2) == 3
         py_cmd = 'python';
       elseif str2num(out3) == 3
         py_cmd = 'python3';
       else
         disp("napaka: Python ni na voljo!\nProsimo, da namestite Python 3 (www.python.org) in poskrbite, da je v sistemski poti.")
       end
       printf("Shranjujem na strežnik ... ")
       py_code = [...
       "import json, urllib.request\n",...
       'data = r"""', data, "\n",'"""',"\n",...
       'blk_data = data.encode("utf-8")',"\n"...
       'headers = { "Authorization": "' token '","content-type": "application/json" }',"\n"...
       'request = urllib.request.Request("' url '", data=blk_data, headers=headers)',"\n"...
       "response = urllib.request.urlopen(request)\n"...
       'print(response.read().decode("utf-8"))'];
       # 'response = json.loads(response.read().decode("utf-8"))',"\n",...
       # 'for part in response["attempts"]:',"\n",...
       # '  print("%s: %d" %(part["part"],part["valid"]))'];
       # TODO print feedback as well
       # disp(pycall)
       py_file = tempname();
       fp = fopen(py_file,'wt'); fwrite(fp,py_code); fclose(fp);
       #'response = post(''' url ''')'
       #'print(response.text)"']
       %[response,output] = system([py_cmd " -c '" py_code "' 2>&1"]);
       [response,output] = system([py_cmd " " py_file " 2>&1"]);
       unlink(py_file); # clean tmp file
       if response
         disp('PRI SHRANJEVANJU JE PRIŠLO DO NAPAKE! Poskusite znova.')
         disp(output)
       else
         disp('OK')
       end
       #request = urllib.request.Request(url, data=data, headers=headers)
       #response = urllib.request.urlopen(request)
       #return json.loads(response.read().decode('utf-8'))
endfunction
