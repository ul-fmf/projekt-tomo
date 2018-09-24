function b = check_has_solution(part)
  b = length(strtrim(part.solution))>0;
end

function check_initialize(parts)
  check.parts = parts;
  for i =1:length(parts)
    check.parts{i}.valid = 1;
    check.parts{i}.feedback = cell();
    check.parts{i}.secret = cell();
  end
  check.part_counter = 0;
end

function r = check_part()
  check.part_counter = check.part_counter + 1;
  check.current_part = check.parts{check.part_counter};
  r = check_has_solution(check.current_part);
end

function check_error(message)
  check.parts{check.part_counter}.valid = 0;
  check_feedback(message);
end

function check_feedback(message)
	% append feedbact
  check.parts{check.part_counter}.feedback(end+1) = {message};
end

function res = check_equal(koda, rezultat)
  res = 0;
  actual_result = eval(koda);
  if any(size(actual_result) ~= size(rezultat)) || (norm(actual_result - rezultat) > 1e-6) || any(isnan(actual_result) ~= isnan(rezultat))
    check_error(['Izraz ', koda, ' vrne ', mat2str(actual_result), ' namesto ', mat2str(rezultat)]);
    res = 1;
  end
end

function check_secret(x,hint)
  if nargin<2, hint=''; end  
  check.parts{check.part_counter}.secret{end+1} = x;
end

function check_summarize()
  for i=1:check.part_counter
    if not(check_has_solution(check.parts{i}))
      fprintf('%d. podnaloga je brez rešitve.\n', i);
    elseif not(check.parts{i}.valid)
      fprintf('%d. podnaloga nima veljavne rešitve.\n',i);
    else
      fprintf('%d. podnaloga ima veljavno rešitev.\n', i);
    end
    for j = 1:length(check.parts{i}.feedback)
      fprintf('  - %d ',j);
      disp(char(check.parts{i}.feedback(j)));
    end
  end
end
