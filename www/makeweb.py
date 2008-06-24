#!/usr/bin/env python

import os, sys, shutil
from stat import *
from string import Template
from optparse import OptionParser

# files in src dir that should not be copied to web dir
SKIP_FILES = [ 'layout.conf', '.svn', 'instrset.inc' ]

# asciidoc command line
ASCIIDOC = 'asciidoc --unsafe --conf-file=${srcdir}/layout.conf -a icons -o ${outfile} ${infile}'

# specialized ASCIIDOC for certain files
# - this is a hack trying to look generic
ASCIIDOC_PERFILE = {
    'userguide.txt': ASCIIDOC.replace('-a icons', '-a icons -a toc')
}


def _is_older(inp, outp):
    older = True
    if os.path.exists(outp):
        modin  = os.stat(inp)[ST_MTIME]
        modout = os.stat(outp)[ST_MTIME]
        older = (modin > modout)
    return older


def _rmtree_warn(fn, path, excinfo):
    print "** WARNING **: error while doing %s on %s" % (fn, path)


def asciidoc(opts, srcdir, inp, outp):
    if _is_older(inp, outp) or opts.force:
        if opts.verbose:
            print "asciidoc %s -> %s" % (inp, outp)
        asciidoc = ASCIIDOC_PERFILE.get(os.path.split(inp)[-1], ASCIIDOC)
        cmd = Template(asciidoc).substitute(srcdir=srcdir, infile=inp, outfile=outp)
        if opts.verbose >= 3:
            print "asciidoc command is [%s]" % cmd
        if not opts.dryrun:
            os.system(cmd)
    else:
        if opts.verbose >= 2:
            print "up to date %s -> %s" % (inp, outp)


def copy(opts, inp, outp):
    if os.path.isdir(inp):
        if os.path.exists(outp) and not os.path.isdir(outp):
            print "** ERROR **: cannot copy directory ('%s') to file ('%s')" % (inp, outp)
            sys.exit(1)
        if not os.path.exists(outp):
            if opts.verbose:
                print "creating %s" % (outp)
            if not opts.dryrun:
                os.mkdir(outp)
        for file in os.listdir(inp):
            if file not in SKIP_FILES:
                copy(opts, os.path.join(inp, file), os.path.join(outp, file))
    else:
        if _is_older(inp, outp) or opts.force:
            if opts.verbose:
                print "copying %s -> %s" % (inp, outp)
            if not opts.dryrun:
                shutil.copy(inp, outp)
        else:
            if opts.verbose >= 2:
                print "up to date %s -> %s" % (inp, outp)


def make(opts, indir, outdir):
    # make output dir if it does not exist
    if not os.path.exists(outdir):
        if opts.verbose:
            print "creating %s" % outdir
        if not opts.dryrun:
            os.mkdir(outdir)
    # process all files/dirs under input directory
    for elem in os.listdir(indir):
        inp = os.path.join(indir, elem)
        if elem.endswith('.txt'):
            outp = os.path.join(outdir, elem[:-4] + '.html')
            asciidoc(opts, indir, inp, outp)
        elif elem not in SKIP_FILES:
            outp = os.path.join(outdir, elem)
            copy(opts, inp, outp)


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

