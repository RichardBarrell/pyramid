import optparse
import sys

from pyramid.interfaces import ITweens

from pyramid.tweens import MAIN
from pyramid.tweens import INGRESS
from pyramid.paster import bootstrap

from pyramid.compat import print_

def main(argv=sys.argv, quiet=False):
    command = PTweensCommand(argv, quiet)
    command.run()

class PTweensCommand(object):
    """Print all implicit and explicit :term:`tween` objects used by a
    Pyramid application.  The handler output includes whether the system is
    using an explicit tweens ordering (will be true when the
    ``pyramid.tweens`` setting is used) or an implicit tweens ordering (will
    be true when the ``pyramid.tweens`` setting is *not* used).

    This command accepts one positional argument:

    ``config_uri`` -- specifies the PasteDeploy config file to use for the
    interactive shell. The format is ``inifile#name``. If the name is left
    off, ``main`` will be assumed.

    Example::

        $ ptweens myapp.ini#main

    """
    summary = "Print all tweens related to a Pyramid application"
    stdout = sys.stdout

    parser = optparse.OptionParser()

    bootstrap = (bootstrap,) # testing

    def __init__(self, argv, quiet=False):
        self.quiet = quiet
        self.options, self.args = self.parser.parse_args(argv[1:])

    def _get_tweens(self, registry):
        from pyramid.config import Configurator
        config = Configurator(registry = registry)
        return config.registry.queryUtility(ITweens)

    def out(self, msg): # pragma: no cover
        if not self.quiet:
            print_(msg)

    def show_chain(self, chain):
        fmt = '%-10s  %-65s'
        self.out(fmt % ('Position', 'Name'))
        self.out(fmt % ('-'*len('Position'), '-'*len('Name')))
        self.out(fmt % ('-', INGRESS))
        for pos, (name, _) in enumerate(chain):
            self.out(fmt % (pos, name))
        self.out(fmt % ('-', MAIN))

    def run(self):
        if not self.args:
            self.out('Requires a config file argument')
            return
        config_uri = self.args[0]
        env = self.bootstrap[0](config_uri)
        registry = env['registry']
        tweens = self._get_tweens(registry)
        if tweens is not None:
            explicit = tweens.explicit
            if explicit:
                self.out('"pyramid.tweens" config value set '
                         '(explicitly ordered tweens used)')
                self.out('')
                self.out('Explicit Tween Chain (used)')
                self.out('')
                self.show_chain(tweens.explicit)
                self.out('')
                self.out('Implicit Tween Chain (not used)')
                self.out('')
                self.show_chain(tweens.implicit())
            else:
                self.out('"pyramid.tweens" config value NOT set '
                         '(implicitly ordered tweens used)')
                self.out('')
                self.out('Implicit Tween Chain')
                self.out('')
                self.show_chain(tweens.implicit())
