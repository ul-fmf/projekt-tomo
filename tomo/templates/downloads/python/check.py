class Check:
    @staticmethod
    def initialize(parts):
        Check.parts = parts
        for part in Check.parts:
            part['errors'] = []
            part['challenge'] = []
        Check.current = None
        Check.part_counter = None
        Check.user_id = {{ user.id }}

    @staticmethod
    def part():
        if Check.part_counter is None:
            Check.part_counter = 0
        else:
            Check.part_counter += 1
        Check.current = Check.parts[Check.part_counter]
        return Check.current.get('solution', '').strip() != ''

    @staticmethod
    def error(msg, *args, **kwargs):
        Check.current['errors'].append(msg.format(*args, **kwargs))

    @staticmethod
    def challenge(x, k=None):
        pair = (str(k), str(Check.canonize(x)))
        Check.current['challenge'].append(pair)

    @staticmethod
    def execute(example, env={}, use_globals=True, do_eval=False, catch_exception=False):
        local_env = {}
        local_env.update(env)
        global_env = globals() if use_globals else {}
        old_stdout, old_stderr = sys.stdout, sys.stderr
        new_stdout, new_stderr = io.StringIO(), io.StringIO()
        exec_info = {'env': local_env}
        try:
            sys.stdout, sys.stderr = new_stdout, new_stderr
            if do_eval:
                exec_info['value'] = eval(example, global_env, local_env)
            else:
                exec(example, global_env, local_env)
        except Exception as e:
            if catch_exception:
                exec_info['exception'] = e
            else:
                raise e
        finally:
            sys.stdout, sys.stderr = old_stdout, old_stderr
        exec_info['stdout'] = new_stdout.getvalue()
        exec_info['stderr'] = new_stderr.getvalue()
        return exec_info

    @staticmethod
    def run(example, state, message=None, env={}, clean=lambda x: x):
        code = "\n".join(example)
        example = "  >>> " + "\n  >>> ".join(example)
        s = {}
        s.update(env)
        exec (code, globals(), s)
        errors = []
        for (x,v) in state.items():
            if x not in s:
                errors.append('morajo nastaviti spremenljivko {0}, vendar je ne'.format(x))
            elif clean(s[x]) != clean(v):
                errors.append('morajo nastaviti {0} na {1},\nvendar nastavijo {0} na {2}'.format(x, v, s[x]))
        if errors:
            Check.error('Ukazi\n{0}\n{1}.', example,  ";\n".join(errors))
            return False
        else:
            return True

    @staticmethod
    def canonize(x, digits=6):
        if   type(x) is float:
            x = round(x, digits)
            # We want to canonize -0.0 and similar small negative numbers to 0.0
            # Since -0.0 still behaves as False, we can use the following
            return x if x else 0.0
        elif type(x) is complex: return complex(Check.canonize(x.real, digits), Check.canonize(x.imag, digits))
        elif type(x) is list: return list([Check.canonize(y, digits) for y in x])
        elif type(x) is tuple: return tuple([Check.canonize(y, digits) for y in x])
        elif type(x) is dict: return sorted([(Check.canonize(k, digits), Check.canonize(v, digits)) for (k,v) in x.items()])
        elif type(x) is set: return sorted([Check.canonize(y, digits) for y in x])
        else: return x

    @staticmethod
    def equal(example, value=None, exception=None,
                clean=lambda x: x, env={},
                precision=1.0e-6, strict_float=False, strict_list=True):
        def difference(x, y):
            if x == y: return None
            elif (type(x) != type(y) and
                 (strict_float or not (type(y) in [int, float, complex] and type(x) in [int, float, complex])) and
                 (strict_list or not (type(y) in [list, tuple] and type(x) in [list, tuple]))):
                return "različna tipa"
            elif type(y) in [int, float, complex]:
                return ("numerična napaka" if abs(x - y) > precision else None)
            elif type(y) in [tuple,list]:
                if len(y) != len(x): return "napačna dolžina seznama"
                else:
                    for (u, v) in zip(x, y):
                        msg = difference(u, v)
                        if msg: return msg
                    return None
            elif type(y) is dict:
                if len(y) != len(x): return "napačna dolžina slovarja"
                else:
                    for (k, v) in y.items():
                        if k not in x: return "manjkajoči ključ v slovarju"
                        msg = difference(x[k], v)
                        if msg: return msg
                    return None
            else: return "različni vrednosti"

        local = locals()
        local.update(env)

        if exception:
            try:
                eval(example, globals(), local)
            except Exception as e:
                if e.__class__ != exception.__class__ or e.args != exception.args:
                    Check.error("Izraz {0} sproži izjemo {1!r} namesto {2!r}.",
                                example, e, exception)
                    return False
                else:
                    return True
            else:
                Check.error("Izraz {0} vrne {1!r} namesto da bi sprožil izjemo {2}.",
                            example, returned, exception)
                return False

        else:
            returned = eval(example, globals(), local)
            reason = difference(clean(returned), clean(value))
            if reason:
                Check.error("Izraz {0} vrne {1!r} namesto {2!r} ({3}).",
                            example, returned, value, reason)
                return False
            else:
                return False

    @staticmethod
    @contextmanager
    def in_out_file(in_lines, given_lines, filename_in="_in", filename_out="_out"):
        with open(filename_in, "w") as _f:
            for line in in_lines:
                print(line, file=_f)
        yield filename_in, filename_out
        with open(filename_out) as _f:
            out_lines = _f.readlines()
        os.remove(filename_in)
        os.remove(filename_out)
        len_out, len_given = len(out_lines), len(given_lines)
        if len_out < len_given:
            out_lines += (len_given - len_out) * ["\n"]
        else:
            given_lines += (len_out - len_given) * ["\n"]
        equal = True
        line_width = max(len(out_line.rstrip()) for out_line in out_lines + ["je izhodna datoteka enaka"])
        diff = ["{0}   | namesto:".format("je izhodna datoteka enaka".ljust(line_width))]
        for out, given in zip(out_lines, given_lines):
            out, given = out.rstrip(), given.rstrip()
            if out != given:
                equal = False
            diff.append("{0} {1} {2}".format(out.ljust(line_width), "|" if out == given else "*", given))
        if not equal:
            Check.error("Pri vhodni datoteki\n  {0}\n{1}".format("\n  ".join(in_lines), "\n  ".join(diff)))

    @staticmethod
    def summarize():
        for i, part in enumerate(Check.parts):
            if not part['solution'].strip():
                print('Podnaloga {0} je brez rešitve.'.format(i + 1))
            elif part['errors']:
                print('Podnaloga {0} ni prestala vseh testov:'.format(i + 1))
                for e in part['errors']:
                    print("- {0}".format("\n  ".join(e.splitlines())))
            elif 'rejection' in part:
                print('Podnaloga {0} je zavrnjena. ({1})'.format(i + 1, part['rejection']))
            else:
                print('Podnaloga {0} je pravilno rešena.'.format(i + 1))
