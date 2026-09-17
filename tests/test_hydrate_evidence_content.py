"""Mode and date safety checks for the trusted evidence hydrator.

The hydrator writes retrieval provenance, so a wrong date is not a cosmetic
defect: it can record today's fetch under an earlier date and pass validation.
These tests pin the two supported modes and prove every unsafe variant is
refused rather than defaulted. Network retrieval itself is covered by
``tests/test_evidence_content.py``; here the fetch boundary is stubbed so the
date and mode logic is what gets exercised.
"""

import importlib.util
from pathlib import Path
import subprocess
import sys

import pytest
import yaml

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
SCRIPT = ROOT / "scripts" / "hydrate-evidence-content.py"


def load_script(name):
    path = ROOT / "scripts" / name
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


HYDRATE = load_script("hydrate-evidence-content.py")
SEARCH_DATE = "2026-07-10"


def evidence_document(entry_count=2):
    """Return a published document whose entries are already hydrated."""
    return {
        "schema_version": 2,
        "provenance_status": "complete",
        "slug": "example-pattern",
        "last_checked": SEARCH_DATE,
        "search": {"run_id": "github-actions:123", "checked_at": SEARCH_DATE},
        "evidence": [
            {
                "url": f"https://vendor-{index}.example/docs",
                "mechanism_quote": "The product ships the mechanism.",
                "resolved_url": f"https://vendor-{index}.example/docs",
                "content_sha256": "0" * 64,
                "retrieved": SEARCH_DATE,
            }
            for index in range(entry_count)
        ],
    }


def write_document(tmp_path, document):
    path = tmp_path / "example-pattern.yaml"
    path.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
    return path


def install_fake_fetch(monkeypatch, *, moved_to=None, quote_present=True):
    """Replace only the network boundary, keeping hydrate's own semantics."""
    def fake_fetch(url, quote=None):
        return {
            "resolved_url": moved_to or url,
            "content_sha256": "a" * 64,
            "mechanism_quote_present": quote_present,
        }

    monkeypatch.setattr(HYDRATE, "fetch", fake_fetch)


def read_back(path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_neither_mode_is_refused_instead_of_defaulted(tmp_path, monkeypatch):
    """No mode has a safe default, so the hydrator must not pick one."""
    install_fake_fetch(monkeypatch)
    path = write_document(tmp_path, evidence_document())

    with pytest.raises(ValueError, match="select a mode"):
        HYDRATE.hydrate(path)

    assert read_back(path) == evidence_document(), "a refused run must not write"


def test_recheck_rejects_a_caller_supplied_date(tmp_path, monkeypatch):
    """A recheck dates itself; accepting a date would reopen the backdating hole."""
    install_fake_fetch(monkeypatch)
    path = write_document(tmp_path, evidence_document())

    with pytest.raises(ValueError, match="derives its own date"):
        HYDRATE.hydrate(path, retrieved_date="2026-09-17", recheck=True)


def test_recheck_advances_the_check_date_and_leaves_the_search_pinned(
        tmp_path, monkeypatch):
    """Re-verification advances 'last_checked'; no search reran, so 'checked_at' holds."""
    install_fake_fetch(monkeypatch, moved_to="https://vendor-0.example/docs/new")
    path = write_document(tmp_path, evidence_document(entry_count=1))

    count, notes = HYDRATE.hydrate(path, recheck=True)
    document = read_back(path)

    today = HYDRATE.today_utc().isoformat()
    assert count == 1
    assert document["last_checked"] == today
    assert document["evidence"][0]["retrieved"] == today
    assert document["search"]["checked_at"] == SEARCH_DATE
    assert document["evidence"][0]["resolved_url"] == "https://vendor-0.example/docs/new"
    assert any("no search reran" in note for note in notes)


def test_recheck_reports_only_sources_that_moved(tmp_path, monkeypatch):
    """A stable address produces no move note, so a real redirect stays visible."""
    install_fake_fetch(monkeypatch)
    path = write_document(tmp_path, evidence_document(entry_count=1))

    _, notes = HYDRATE.hydrate(path, recheck=True)

    assert not any("resolved_url ->" in note for note in notes)


def test_run_mode_leaves_the_document_check_dates_untouched(tmp_path, monkeypatch):
    """Inside an approved run the caller owns the document dates, not the hydrator."""
    install_fake_fetch(monkeypatch)
    path = write_document(tmp_path, evidence_document(entry_count=1))

    HYDRATE.hydrate(path, retrieved_date="2026-09-17")
    document = read_back(path)

    assert document["evidence"][0]["retrieved"] == "2026-09-17"
    assert document["last_checked"] == SEARCH_DATE
    assert document["search"]["checked_at"] == SEARCH_DATE


def test_a_retrieval_date_earlier_than_the_recorded_one_is_refused(
        tmp_path, monkeypatch):
    """Backdating a fresh digest validated cleanly before; it must now fail."""
    install_fake_fetch(monkeypatch)
    path = write_document(tmp_path, evidence_document(entry_count=1))

    with pytest.raises(ValueError, match="refusing to backdate"):
        HYDRATE.hydrate(path, retrieved_date="2026-06-01")

    assert read_back(path)["evidence"][0]["content_sha256"] == "0" * 64


def test_a_withdrawn_quote_writes_nothing_at_all(tmp_path, monkeypatch):
    """One absent quote must abort the whole file, not half-update it."""
    install_fake_fetch(monkeypatch, quote_present=False)
    original = evidence_document()
    path = write_document(tmp_path, original)

    with pytest.raises(ValueError, match="absent from fetched content"):
        HYDRATE.hydrate(path, recheck=True)

    assert read_back(path) == original


def test_none_found_document_is_never_marked_freshly_checked(tmp_path, monkeypatch):
    """With no admitted source, a recheck proves nothing and must claim nothing."""
    install_fake_fetch(monkeypatch)
    document = evidence_document()
    document["evidence"] = "none found"
    path = write_document(tmp_path, document)

    count, _ = HYDRATE.hydrate(path, recheck=True)

    assert count == 0
    assert read_back(path)["last_checked"] == SEARCH_DATE


HEADER = (
    "schema_version: 2\n"
    "provenance_status: complete\n"
    "slug: example-pattern\n"
    "last_checked: 2026-07-10\n"
    "search:\n"
    '  run_id: "github-actions:123"\n'
    "  checked_at: 2026-07-10\n"
    "  modes:\n"
    "    name:\n"
    "      queries:\n"
    '        - "example query"\n'
)


def fixture_entries(pad):
    """Render two hydrated evidence entries at the given list indent."""
    return "".join(
        f"{pad}- tier: T1\n"
        f"{pad}  mechanism_quote: The product ships the mechanism.\n"
        f"{pad}  url: https://vendor-{index}.example/docs\n"
        f"{pad}  resolved_url: https://vendor-{index}.example/docs\n"
        f'{pad}  content_sha256: "{"0" * 64}"\n'
        f"{pad}  retrieved: 2026-07-10\n"
        for index in range(2)
    )


def fixture_text(*, nested_list):
    """Render the fixture with the evidence list nested or at its key's indent."""
    pad = "  " if nested_list else ""
    return (
        f"{HEADER}"
        "terminology_variants:\n"
        f"{pad}- term: Example\n"
        f"{pad}  used_by: Vendor\n"
        f"{pad}  url: https://vendor-9.example/naming\n"
        "evidence:\n"
        f"{fixture_entries(pad)}"
        "verdict: verified\n"
    )


NESTED = fixture_text(nested_list=True)
LAYOUTS = pytest.mark.parametrize("nested_list", [True, False], ids=["nested", "column-zero"])


def recheck_fixture(tmp_path, monkeypatch, *, nested_list=True, **fetch_options):
    """Recheck one fixture layout and return its original and resulting text."""
    install_fake_fetch(monkeypatch, **fetch_options)
    original = fixture_text(nested_list=nested_list)
    path = tmp_path / "example-pattern.yaml"
    path.write_text(original, encoding="utf-8")
    HYDRATE.hydrate(path, recheck=True)
    return original, path.read_text(encoding="utf-8")


@LAYOUTS
def test_recheck_touches_only_the_lines_it_changes(tmp_path, monkeypatch, nested_list):
    """A reviewer must see the changed fields, not a reformatted file.

    YAML lets a block list sit at its parent key's indent, which is how most of
    the evidence corpus is written, so both layouts must resolve entry indices.
    """
    original, text = recheck_fixture(
        tmp_path, monkeypatch, nested_list=nested_list)

    before, after = original.splitlines(), text.splitlines()
    changed = [b for b, a in zip(before, after) if b != a]
    assert len(before) == len(after), "a recheck must not add or remove lines"
    # last_checked, then content_sha256 and retrieved for each of two entries.
    assert len(changed) == 5, changed


def test_in_place_update_preserves_existing_quoting(tmp_path, monkeypatch):
    """Rewriting a value must not silently restyle the line around it."""
    _, text = recheck_fixture(tmp_path, monkeypatch)
    today = HYDRATE.today_utc().isoformat()

    assert f'    content_sha256: "{"a" * 64}"' in text, "a quoted value stays quoted"
    assert f"    retrieved: {today}" in text, "an unquoted value stays unquoted"
    assert '  run_id: "github-actions:123"' in text, "untouched lines stay byte-identical"
    assert '        - "example query"' in text, "unrelated blocks keep their style"


@LAYOUTS
def test_url_outside_the_evidence_list_is_never_rewritten(
        tmp_path, monkeypatch, nested_list):
    """A terminology 'url' shares its key with an entry field but is not one."""
    _, text = recheck_fixture(
        tmp_path, monkeypatch, nested_list=nested_list,
        moved_to="https://moved.example/docs")

    assert "url: https://vendor-9.example/naming" in text


def test_in_place_update_is_rejected_when_it_would_change_meaning():
    """The writer proves its own output reparses to the intended document."""
    assert HYDRATE.apply_updates(NESTED, [(0, "retrieved", "2026-09-17")]) is not None
    assert HYDRATE.apply_updates(NESTED, [(0, "absent_field", "x")]) is None


def test_cli_refuses_to_run_without_an_explicit_mode(tmp_path):
    """The command line makes the unsafe invocation unrepresentable."""
    path = tmp_path / "example-pattern.yaml"
    path.write_text(NESTED, encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(path)],
        capture_output=True, text=True, cwd=ROOT, timeout=30, check=False)

    assert result.returncode != 0
    assert "--recheck" in result.stderr
