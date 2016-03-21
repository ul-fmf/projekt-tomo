function b = check_has_solution(part)
  b = length(strtrim(part.solution))>0;
endfunction

function check_initialize(parts)
  global check;
  check.parts = parts;
  for i =1:length(parts)
    check.parts{i}.valid = 1;
    check.parts{i}.feedback = cell();
    check.parts{i}.secret = cell();
  end
  check.part_counter = 0;
endfunction

function r = check_part()
  global check;
  check.part_counter = check.part_counter + 1;
  r = check_has_solution(check.parts{check.part_counter});
endfunction

function check_error(message)
  global check;
  check.parts{check.part_counter}.valid = 0;
  check_feedback(message);
endfunction

function check_feedback(message)
  global check;
	% append feedbact
  check.parts{check.part_counter}.feedback(end+1) = {message};
endfunction

function res = check_equal(koda, rezultat)
  global check;
  res = 0;
  actual_result = eval(koda);
  if abs(actual_result - rezultat) > 1e-15
    check_error(["Izraz ", koda, " vrne ", mat2str(actual_result), " namesto ", mat2str(rezultat)]);
    res = 1;
  end
endfunction

function check_secret(x,hint="")
  global check;
  check.parts{check.part_counter}.secret{end+1} = x;
endfunction

function check_summarize()
  global check;
  for i=1:check.part_counter
    if not(check_has_solution(check.parts{i}))
      printf('%d. podnaloga je brez rešitve.\n', i);
    elseif not(check.parts{i}.valid)
      printf('%d. podnaloga nima veljavne rešitve.\n',i);
    else
      printf('%d. podnaloga ima veljavno rešitev.\n', i);
    end
    for j = 1:length(check.parts{i}.feedback)
      printf('  - %d ',j);
      disp(char(check.parts{i}.feedback(j)));
    end
  end
endfunction
