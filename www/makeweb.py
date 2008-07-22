#!/usr/bin/env python

# Usage: run "python makeweb.py src web" to update files
# under 'web'. See "python makeweb.py --help" for more options.

import os, sys, shutil
from stat import *
from optparse import OptionParser


# how to process files that match various filename patterns
FILE_ACTION_TBL = [

    # selector_func(infilepath) -> True|False
    # output_filepath_func(outfilepath) -> outfilepath
    # cmd_line_func(opts, infilepath, outfilepath) -> cmdline|None

    ( lambda f: f.endswith('.py'),
      lambda o: o.replace('.py', '.html'),
      lambda opts, i, o: "source-highlight --input='%s' --output='%s'" \
        % (i, o) ),

    ( lambda f: f.endswith('userguide.txt'),
      lambda o: o.replace('.txt', '.html'),
      lambda opts, i, o: "asciidoc --unsafe --conf-file='%s/layout.conf' -a icons -a toc -o '%s' '%s'" \
        % (opts.srcdir, o, i) ),

    ( lambda f: f.endswith('.txt'),
      lambda o: o.replace('.txt', '.html'),
      lambda opts, i, o: "asciidoc --unsafe --conf-file='%s/layout.conf' -a icons -o '%s' '%s'" \
        % (opts.srcdir, o, i) ),

    ( lambda f: f.endswith('layout.conf') or f.endswith('.svn') or f.endswith('.inc'),
      lambda o: o,
      lambda opts, i, o: None )
]


# list of directories to skip
DIR_SKIP_TBL = [
    '.svn'
]


def _is_older(inp, outp):
    older = True
    if os.path.exists(outp):
        modin  = os.stat(inp)[ST_MTIME]
        modout = os.stat(outp)[ST_MTIME]
        older = (modin > modout)
    return older


def _rmtree_warn(fn, path, excinfo):
    print "** WARNING **: error while doing %s on %s" % (fn, path)


def _can_skip(opts, infile, outfile):
    return not _is_older(infile, outfile) and not opts.force


def process_file(opts, infile, outfile):

    for matchfn, outfilefn, cmdfn in FILE_ACTION_TBL:
        if matchfn(infile):
            outfile_actual = outfilefn(outfile)
            cmd = cmdfn(opts, infile, outfile_actual)
            if _can_skip(opts, infile, outfile_actual):
                if opts.verbose >= 2:
                    print "up to date %s -> %s" % (infile, outfile_actual)
                return
            if cmd:
                # do cmd
                if opts.verbose:
                    print "process %s -> %s" % (infile, outfile_actual)
                if opts.verbose >= 3:
                    print "command is [%s]" % cmd
                if not opts.dryrun:
                    os.system(cmd)
            # else if cmd is None, do nothing
            return

    # nothing matched, default action is to copy
    if not _can_skip(opts, infile, outfile):
        if opts.verbose:
            print "copying %s -> %s" % (infile, outfile)
        if not opts.dryrun:
            shutil.copy(infile, outfile)


def make(opts, indir, outdir):

    # does outdir exists?
    odexists = os.path.exists(outdir)

    # if it exists, it must be a dir!
    if odexists and not os.path.isdir(outdir):
        print "** WARNING **: output dir '%s' exists but is " \
            "not a dir, skipping" % outdir
        return

    # make outdir if not existing
    if not odexists:
        if opts.verbose:
            print "creating %s" % outdir
        if not opts.dryrun:
            os.mkdir(outdir)

    # process indir/* -> outdir/*
    for elem in os.listdir(indir):
        inp = os.path.join(indir, elem)
        outp = os.path.join(outdir, elem)

        # process files
        if os.path.isfile(inp):
            if os.path.exists(outp) and not os.path.isfile(outp):
                print "** WARNING **: output '%s' corresponding to " \
                    "input '%s' is not a file, skipping" % (outp, inp)
            else:
                process_file(opts, inp, outp)

        # process directories
        elif os.path.isdir(inp):
            # if dir is in skip list, silently ignore
            if elem in DIR_SKIP_TBL:
                if opts.verbose >= 3:
                    print "skipping %s" % inp
                continue
            # just recurse
            make(opts, inp, outp)

        # neither a file nor a dir
        else:
            print "** WARNING **: input '%s' is neither file nor " \
                "dir, skipping" % inp


def get_opts():
    usage = "usage: %prog [options] srcdir destdir"

    p = OptionParser(usage=usage)
    p.add_option("-f", "--force", action="store_true", dest="force", default=False, 
        help="ignore timestamps and force build of all files")
    p.add_option("-v", "--verbose", action="count", dest="verbose", default=0,
        help="be chatty (use more v's to be more friendly)")
    p.add_option("-c", "--clean-first", action="store_true", dest="clean", default=False,
        help="remove outdir and everything under it before building")
    p.add_option("-n", "--dry-run", action="store_true", dest="dryrun", default=False,
        help="just print what will happen rather than doing it")

    (opts, args) = p.parse_args()
    if len(args) != 2:
        p.error("incorrect number of arguments")
    srcdir, destdir = args

    if not os.path.exists(srcdir):
        p.error("srcdir (%s) does not exist" % srcdir)
    if not os.path.isdir(args[0]):
        p.error("srcdir (%s) is not a directory" % srcdir)
    if os.path.exists(destdir) and not os.path.isdir(destdir):
        p.error("destdir (%s) is not a directory" % destdir)

    if opts.verbose == None:
        opts.verbose = 0

    # add srcdir and destdir also to opts
    opts.srcdir = srcdir
    opts.destdir = destdir

    return (opts, srcdir, destdir)


def main():
    opts, src, dest = get_opts()
    if opts.verbose >= 3:
        print ("running with options:\nsrc = [%s]\ndest = [%s]\nverbose = [%d]\n" +\
            "dry-run = [%d]\nclean-first = [%d]\nforce = [%d]") %\
            (src, dest, opts.verbose, opts.dryrun, opts.clean, opts.force)
    if opts.dryrun and opts.verbose == 0:
        opts.verbose = 1
    if opts.clean:
        if opts.dryrun or opts.verbose:
            print "removing tree %s" % dest
        if not opts.dryrun:
            os.rmtree(dest, True, _rmtree_warn)
    make(opts, src, dest)


main()

