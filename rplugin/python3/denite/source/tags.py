# ============================================================================
# FILE: tags.py
# AUTHOR: Yasumasa Tamura (tamura.yasumasa _at_ gmail.com)
# License: MIT license
# ============================================================================

from .base import Base
from subprocess import check_output, CalledProcessError
from denite.util import parse_tagline
import re
import tempfile

OUTLINE_HIGHLIGHT_SYNTAX = [
    {'name': 'Name', 'link': 'Identifier', 're': '\s\S\+\%(\s\+\[\)\@='},
    {'name': 'Type', 'link': 'Type',       're': '\[.\{-}\]'},
    {'name': 'Ref',  'link': 'Comment',    're': '\s\s.\+'}
]


class Source(Base):

    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'tags'
        self.kind = 'file'
        self.vars = {
            'command': ['ctags'],
            'options': ['-R', '-o'],
            'ignore_types': [],
            'encoding': 'utf-8'
        }

    def on_init(self, context):
        context['__cwd'] = context['args'][0] if len(
            context['args']) > 0 else self.vim.call('getcwd')

    def highlight(self):
        for syn in OUTLINE_HIGHLIGHT_SYNTAX:
            self.vim.command(
                'syntax match {0}_{1} /{2}/ contained containedin={0}'.format(
                    self.syntax_name, syn['name'], syn['re']))
            self.vim.command(
                'highlight default link {0}_{1} {2}'.format(
                    self.syntax_name, syn['name'], syn['link']))

    def gather_candidates(self, context):
        with tempfile.NamedTemporaryFile(mode='w') as tf:
            command = []
            command += self.vars['command']
            command += self.vars['options']
            command += [tf.name, context['__cwd']]

            try:
                check_output(command).decode(self.vars['encoding'])
            except CalledProcessError:
                return []

            candidates = []
            with open(tf.name) as f:
                for line in f:
                    if re.match('!', line) or not line:
                        continue
                    info = parse_tagline(line.rstrip())
                    if info['type'] in self.vars['ignore_types']:
                        continue
                    info['file'] = self.vim.call(
                        'fnamemodify', info['file'], ':~:.')

                    candidates.append({
                        'word': '{file} {name} [{type}]  {ref}'.format(**info),
                        'action__path': info['file'],
                        'action__pattern': info['pattern'],
                        '__type': info['type']
                    })
        return sorted(
            candidates,
            key=lambda item: (item['action__path'], item['__type'])
        )
