"""Run the model-check worked example through quint and pin each step's verdict."""

from pathlib import Path
import re
import shutil
import subprocess
import unittest

SPEC = Path(__file__).resolve().parents[2] / "skills/model-check/references/example-queue-consumer.qnt"
SAMPLES = 20000
RUN = ["--main=queue_consumer", f"--max-samples={SAMPLES}", "--max-steps=30", "--seed=7"]
VERDICT = re.compile(r"^\[(ok|violation)\]", re.M)
WITNESS = re.compile(r"^(\w+) was witnessed in \d+ trace\(s\) out of (\d+) explored \(([\d.]+)%\)$", re.M)


def quint(*args):
    return subprocess.run(["quint", *args], capture_output=True, text=True, timeout=300)


@unittest.skipUnless(shutil.which("quint"), "quint is not installed")
class ExampleVerdicts(unittest.TestCase):
    def check(self, step, *invariants):
        """Returns the verdict and {witness: (explored, percent)} for one run."""
        result = quint("run", str(SPEC), *RUN, f"--step={step}", "--invariants", *invariants,
                       "--witnesses", "orphanClaim", "settled")
        output = result.stdout + result.stderr
        verdict = VERDICT.search(output)
        self.assertIsNotNone(verdict, output)
        witnesses = {name: (int(explored), float(percent)) for name, explored, percent in WITNESS.findall(output)}
        return verdict.group(1), witnesses

    def test_typecheck(self):
        result = quint("typecheck", str(SPEC))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_current_code_loses_messages(self):
        self.assertEqual(self.check("step", "noLostMessages")[0], "violation")

    def test_design_passes_and_reaches_failure_and_finish(self):
        verdict, witnesses = self.check("stepDesign", "noLostMessages", "atMostOnce", "oneOwner")
        self.assertEqual(verdict, "ok")
        self.assertEqual(witnesses["settled"][0], SAMPLES)
        self.assertGreater(witnesses["orphanClaim"][1], 0)
        self.assertGreater(witnesses["settled"][1], 0)

    def test_no_lease_mutant_allows_two_owners(self):
        self.assertEqual(self.check("stepMutNoLease", "oneOwner")[0], "violation")

    def test_ack_live_lease_mutant_loses_messages(self):
        self.assertEqual(self.check("stepMutAckLiveLease", "noLostMessages")[0], "violation")


if __name__ == "__main__":
    unittest.main()
