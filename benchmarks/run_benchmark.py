#!/usr/bin/python3

import sys, os, subprocess, errno
from sys import stdout, stderr, argv
from getopt import gnu_getopt

ALL_LIBS = ['nop', 'reckless', 'stdio', 'fstream', 'pantheios', 'spdlog']
ALL_TESTS = ['periodic_calls', 'call_burst', 'write_files', 'mandelbrot']

SINGLE_SAMPLE_TESTS = {'mandelbrot'}
THREADED_TESTS = {'call_burst', 'mandelbrot'}
TESTS_WITH_DRY_RUN = {'call_burst'}
MAX_THREADS = 4

# /run_benchmark.py -t mandelbrot  1448.92s user 64.87s system 208% cpu 12:04.87 total
# with SINGLE_SAMPLE_TEST_ITERATIONS=2 means we should have
# about 80 for 8 hours runtime
SINGLE_SAMPLE_TEST_ITERATIONS = 100

def main():
    opts, args = gnu_getopt(argv[1:], 'l:t:h', ['libs', 'tests', 'help'])
    libs = None
    tests = None
    show_help = len(args) != 0

    for option, value in opts:
        if option in ('-l', '--libs'):
            libs = [lib.strip() for lib in value.split(',')]
        elif option in ('-t', '--tests'):
            tests = [test.strip() for test in value.split(',')]
        elif option in ('-h', '--help'):
            show_help = True

    if show_help:
        stderr.write(
            'usage: run_benchmark.py [OPTIONS]\n'
            'where OPTIONS are:\n'
            '-t,--tests TESTS comma-separated list of tests to run\n'
            '-l,--libs  LIBS  comma-separated list of libs to benchmark\n'
            '-h,--help        show this help\n'
            'Available libraries: {}\n'
            'Available tests: {}\n'.format(
                ','.join(ALL_LIBS), ','.join(ALL_TESTS)))
        return 1

    if libs is None:
        libs = sorted(ALL_LIBS)
    if tests is None:
        tests = sorted(ALL_TESTS)

    run_tests(libs, tests)


def run_tests(libs, tests):
    for test in tests:
        stdout.write(test + ':')
        stdout.flush()
        for lib in libs:
            stdout.write(' ' + lib)
            if test in THREADED_TESTS:
                stdout.write('/')
                for threads in range(1, MAX_THREADS+1):
                    stdout.write(str(threads))
                    stdout.flush()
                    success = run_test(lib, test, threads)
            else:
                stdout.flush()
                success = run_test(lib, test)

            if not success:
                stdout.write('[F]')

        stdout.write('\n')
        stdout.flush()

def reset():
    if os.path.exists('log.txt'):
        os.unlink('log.txt')
    subprocess.call('sync')
    
def run_test(lib, test, threads = None):
    binary_name = lib + '_' + test
    if threads is not None:
        binary_name += '_' + str(threads)
        
    def run(out_file):
        try:
            p = subprocess.Popen([binary_name], executable='./' + binary_name, stdout=out)
            p.wait()
        except OSError as e:
            if e.errno == errno.ENOENT:
                return False
            else:
                raise

    if test in TESTS_WITH_DRY_RUN:
        with open(os.devnull, 'w') as out:
            run(out)
            
    txt_name = binary_name + '.txt'
    with open('results/' + txt_name, 'w') as out:
        total_iterations = 1
        if test in SINGLE_SAMPLE_TESTS:
            total_iterations = SINGLE_SAMPLE_TEST_ITERATIONS
        for i in range(0, total_iterations):
            reset()
            run(out)
    return True

if __name__ == "__main__":
    sys.exit(main())

    
