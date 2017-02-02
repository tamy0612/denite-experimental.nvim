# ============================================================================
# FILE: quickfix.py
# AUTHOR: Yasumasa Tamura (tamura.yasumasa __at__ gmail.com)
# License: MIT license
# ============================================================================

from .base import Base
import json

QUICKFIX_HIGHLIGHT_SYNTAX = [
    {'name': 'FileName', 'link': 'Function', 're': r'[^/ \[\]]\+\s'},
    {'name': 'Location', 'link': 'Comment',  're': r'|\d\+-\d\+|'},
    {'name': 'Info',     'link': 'Normal',   're': r'\(|\_s\+\)\@<=.\{}'},
]


class Source(Base):

    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'quickfix'
        self.kind = 'file'

    def highlight(self):
        for syn in QUICKFIX_HIGHLIGHT_SYNTAX:
            self.vim.command(
                'syntax match {0}_{1} /{2}/ contained containedin={0}'.format(
                    self.syntax_name, syn['name'], syn['re']))
            self.vim.command(
                'highlight default link {0}_{1} {2}'.format(
                    self.syntax_name, syn['name'], syn['link']))

    def gather_candidates(self, context):
        return [
            {
                'word': "{0} |{1}-{2}| {3}".format(
                    self.vim.call('bufname', item['bufnr']),
                    item['lnum'],
                    item['col'],
                    item['text']
                ),
                'action__path': self.vim.call(
                    'fnamemodify',
                    self.vim.call('bufname', item['bufnr']),
                    ':p'
                ),
                'action__line': item['lnum'],
                'action__col': item['col']
            } for item in self.vim.call('getqflist') if item['valid'] != 0
        ]
