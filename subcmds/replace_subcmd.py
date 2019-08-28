
import os

from topics import KrepXmlConfigFile, RaiseExceptionIfOptionMissed, \
  SubCommand, XmlConfigFile

class ReplaceSubcmd(SubCommand):
  COMMAND = 'replace'

  help_summary = 'Replace file contexts with XML value-sets elements'
  help_usage = """\
%prog [options] --xml-file value-sets.xml [--output saved-filename] file-to-replace ...

Handle the git-repo project git commits diff and generate the reports in
purposed formats."""

  def options(self, optparse):
    SubCommand.options(self, optparse)

    options = optparse.add_option_group('Pattern options')
    options.add_option(
      '--simple-substitute',
      dest='simple_subst', action='store_true',
      help='Define to use simple variable in option "from" and "to"')
    options.add_option(
      '--group',
      dest='group', action='store',
      help='The set name in value-set file')
    options.add_option(
      '--from',
      dest='fr', action='store', metavar="FROM",
      help='The referred "from" attr in referred elements')
    options.add_option(
      '--to',
      dest='to', action='store',
      help='The referred "to" attr in referred elements')

    options = optparse.add_option_group('File options')
    options.add_option(
      '--xml-file',
      dest='xml_file', action='store',
      help='Set the xml file as import value-sets')
    options.add_option(
      '--inplace',
      dest='inplace', action='store_true',
      help='Update the file in the place')
    options.add_option(
      '--postfix',
      dest='postfix', action='store',
      help='Output the files with specific extension postfix')
    options.add_option(
      '--output',
      dest='output', action='store',
      help='Output the replaced content to the file')

  def execute(self, options, *args, **kws):
    RaiseExceptionIfOptionMissed(
      options.xml_file, 'XML file isn\'t defined')
    RaiseExceptionIfOptionMissed(
      not (options.output and len(args) != 1), "output works only for one file")

    valueset = XmlConfigFile(options.xml_file)
    if not options.group:
      sets = valueset.value_sets()
      if len(sets) == 1:
        options.group = sets.keys()[0]

    RaiseExceptionIfOptionMissed(
      options.group, 'group referred in XML file is undefined')
    RaiseExceptionIfOptionMissed(
      args, 'No files to substitue')

    for name in args:
      if not os.path.exists(name):
        print('Error: %s not existed' % name)
        continue

      context = ''
      with open(name, 'r') as fp:
        context = fp.read()

      substitue = context
      for var in valueset.foreach(options.group):
        if options.simple_subst:
          if var.get(options.fr) and var.get(options.to):
            vfr = var.get(options.fr)
            vto = var.get(options.to)
            substitue = substitue.replace(vfr, vto)
        else:
          vfr, ra = valueset.escape_attr(options.fr, var)
          vto, rb = valueset.escape_attr(options.to, var)
          if ra and rb:
            substitue = substitue.replace(vfr, vto)

      oname = ''
      if options.inplace:
        oname = name
      else:
        if options.output:
          oname = options.output
        else:
          oname = name

        if options.postfix:
          oname += options.postfix

      with open(oname, 'w') as fp:
        fp.write(substitue)

    return True
