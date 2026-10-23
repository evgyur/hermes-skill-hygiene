import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import stat
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('hygiene_audit', ROOT / 'scripts/audit.py')
a = importlib.util.module_from_spec(spec)
spec.loader.exec_module(a)
GOOD = '---\nname: sample\ndescription: "Use when testing a synthetic skill."\n---\n\n# Sample\n'

class AuditTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.skill = self.root / 'sample'
        self.skill.mkdir()
        self.path = self.skill / 'SKILL.md'
        self.path.write_text(GOOD)
    def run_audit(self, text=None, deep=False, **kwargs):
        if text is not None:
            self.path.write_text(text)
        return a.audit([{'path': str(self.path)}], deep=deep, **kwargs)
    def test_valid(self):
        r = self.run_audit()
        self.assertEqual(r['findings'], [])
        self.assertEqual(r['readable_roots'], 1)
    def test_duplicate_yaml_key(self):
        r = self.run_audit(GOOD.replace('name: sample', 'name: sample\nname: other'))
        self.assertEqual(r['findings'][0]['detail'], 'DuplicateKey')
    def test_missing_frontmatter(self):
        self.assertEqual(self.run_audit('# Not a skill')['counts'], {'invalid_root': 1})
    def test_invalid_yaml(self):
        self.assertIn('invalid_root', self.run_audit('---\nname: [\n---\n')['counts'])
    def test_missing_name(self):
        self.assertIn('missing_name', self.run_audit(GOOD.replace('name: sample\n', ''))['counts'])
    def test_missing_description(self):
        text = GOOD.replace('description: "Use when testing a synthetic skill."\n', '')
        self.assertIn('missing_description', self.run_audit(text)['counts'])
    def test_valid_local_link(self):
        (self.skill / 'references').mkdir()
        (self.skill / 'references/guide.md').write_text('# Guide\n')
        self.assertFalse(self.run_audit(GOOD + '[Guide](references/guide.md)\n')['findings'])
    def test_broken_local_link(self):
        r = self.run_audit(GOOD + '[Guide](references/missing.md)\n')
        self.assertEqual(r['counts'], {'broken_relative_link': 1})
    def test_duplicate_link_is_one_assertion(self):
        r = self.run_audit(GOOD + '[X](missing.md) [X](missing.md)\n')
        self.assertEqual(r['counts'], {'broken_relative_link': 1})
    def test_code_and_inline_examples_ignored(self):
        text = GOOD + '```md\n[Example](absent.md)\n```\n`[Other](absent-two.md)`\n'
        self.assertFalse(self.run_audit(text)['findings'])
    def test_nested_fence_does_not_close_outer(self):
        text = GOOD + '````md\n```sh\n[Example](absent.md)\n```\n````\n'
        self.assertFalse(self.run_audit(text)['findings'])
    def test_web_urls_and_fragments_ignored(self):
        text = GOOD + '[Web](https://example.org/a) [Anchor](#sample)\n'
        self.assertFalse(self.run_audit(text)['findings'])
    def test_web_root_relative_is_not_host_filesystem(self):
        r = self.run_audit(GOOD + '[Web](/guide/page.md)\n')
        self.assertFalse(r['findings'])
        self.assertEqual(r['advisories'][0]['kind'], 'web_root_relative_link')
    def test_placeholder_path_not_executable_artifact(self):
        text = GOOD + '[Example](path/to/output.md) [Variable](<project>/file.md)\n'
        self.assertFalse(self.run_audit(text)['findings'])
    def test_large_root_is_not_deletion_verdict(self):
        r = self.run_audit(GOOD + ('generic text\n' * 2500))
        self.assertFalse(r['findings'])
        self.assertEqual(r['advisories'][0]['kind'], 'large_root_review')
        self.assertEqual(r['records'][0]['disposition'], 'retain-owner-workflow')
    def test_finite_read_budget(self):
        r = self.run_audit(GOOD + ('x' * (a.MAX_BYTES + 1)))
        self.assertEqual(r['readable_roots'], 0)
        self.assertIn('invalid_root', r['counts'])
    def test_deep_reads_refs_and_signature_changes(self):
        ref = self.skill / 'references/guide.md'; ref.parent.mkdir(); ref.write_text('# First\n')
        first = self.run_audit(deep=True)
        ref.write_text('# Second\n')
        second = self.run_audit(deep=True)
        self.assertEqual(first['documents_read'], 2)
        self.assertNotEqual(first['signature'], second['signature'])
    def test_shared_realpath_scanned_once_profiles_preserved(self):
        alias = self.root / 'alias'; alias.symlink_to(self.skill, target_is_directory=True)
        r = a.audit([{'path': str(self.path), 'effective_profiles': ['alpha']},
                     {'path': str(alias / 'SKILL.md'), 'effective_profiles': ['beta']}])
        self.assertEqual(r['unique_roots'], 1)
        self.assertEqual(r['records'][0]['effective_profiles'], ['alpha', 'beta'])
    def test_repo_owner_detected(self):
        (self.root / '.git').mkdir()
        self.assertEqual(self.run_audit()['records'][0]['owner'], 'repository-bound')
    def test_physical_fallback_prunes_support_and_vendor(self):
        for rel in ['references/nested', 'vendor/other']:
            p = self.skill / rel; p.mkdir(parents=True); (p / 'SKILL.md').write_text(GOOD)
        self.assertEqual(len(a.physical_entries([self.root])), 1)
    def test_physical_fallback_does_not_follow_external_symlink(self):
        link = self.root / 'outside'; link.symlink_to(self.skill, target_is_directory=True)
        self.assertEqual(len(a.physical_entries([self.root])), 1)
    def test_review_retains_original_evidence(self):
        r = self.run_audit(GOOD + '[Example](missing.md)\n')
        decision = {'id': r['findings'][0]['id'], 'decision': 'template', 'reason': 'Synthetic expected output, not a shipped dependency.'}
        review = a.evaluate_reviews(r, [decision])
        self.assertEqual(len(r['findings']), 1)
        self.assertEqual(len(review['reviewed']), 1)
        self.assertFalse(review['unreviewed'])
    def test_changed_source_invalidates_review(self):
        first = self.run_audit(GOOD + '[Example](missing.md)\n')
        decision = {'id': first['findings'][0]['id'], 'decision': 'historical', 'reason': 'Synthetic retained source.'}
        second = self.run_audit(GOOD + '# Changed\n[Example](missing.md)\n')
        review = a.evaluate_reviews(second, [decision])
        self.assertEqual(len(review['unreviewed']), 1)
        self.assertEqual(review['stale_decision_ids'], [decision['id']])
    def test_blanket_or_unexplained_reviews_rejected(self):
        for decision in [{'id': 'x', 'decision': 'ignore_all', 'reason': 'ignore'},
                         {'id': 'x', 'decision': 'template', 'reason': ''}]:
            with self.assertRaises(ValueError): a.evaluate_reviews({'findings': []}, [decision])
    def test_duplicate_reviews_rejected(self):
        d = {'id': 'x', 'decision': 'template', 'reason': 'Synthetic'}
        with self.assertRaises(ValueError): a.evaluate_reviews({'findings': []}, [d, d])
    def test_partition_complete(self):
        left = self.root / 'left.md'; right = self.root / 'right.md'
        left.write_bytes(b'prefix abc'); right.write_bytes(b'def suffix')
        self.assertTrue(a.verify_partition(b'abcdef', [{'start': 0, 'end': 3, 'path': str(left)}, {'start': 3, 'end': 6, 'path': str(right)}]))
    def test_partition_gap_and_overlap_rejected(self):
        p = self.root / 'part.md'; p.write_bytes(b'abcdef')
        for parts in [[{'start': 1, 'end': 6, 'path': str(p)}],
                      [{'start': 0, 'end': 4, 'path': str(p)}, {'start': 3, 'end': 6, 'path': str(p)}]]:
            with self.assertRaises(ValueError): a.verify_partition(b'abcdef', parts)
    def test_partition_loss_rejected(self):
        p = self.root / 'part.md'; p.write_bytes(b'abc')
        with self.assertRaises(ValueError): a.verify_partition(b'abcdef', [{'start': 0, 'end': 6, 'path': str(p)}])
    def test_cli_strict_private_report(self):
        out = self.root / 'report.json'
        self.path.write_text(GOOD + '[Missing](missing.md)\n')
        with contextlib.redirect_stdout(io.StringIO()):
            code = a.main(['--root', str(self.skill), '--out', str(out), '--strict'])
        self.assertEqual(code, 1)
        self.assertEqual(stat.S_IMODE(out.stat().st_mode), 0o600)
        self.assertEqual(len(json.loads(out.read_text())['review']['unreviewed']), 1)

if __name__ == '__main__':
    unittest.main()
