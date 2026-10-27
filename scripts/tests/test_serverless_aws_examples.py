"""Check that the TypeScript examples in the serverless-aws skill stay safe to copy."""

from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]

# Models copy these blocks verbatim, so the text is the code under test.
TEXT = (ROOT / "skills/serverless-aws/SKILL.md").read_text()
BLOCKS = re.findall(r"```typescript\n(.*?)```", TEXT, re.S)
CODE = re.sub(r"(?<!:)//.*$", "", re.sub(r"/\*.*?\*/", "", "\n".join(BLOCKS), flags=re.S), flags=re.M)
LOG_FIELDS = [
    "error: error instanceof Error ? error.stack : 'non-Error value thrown'",
    "requestId: event.requestContext.requestId",
    "messageId: record.messageId",
]


class ServerlessAwsExampleTests(unittest.TestCase):
    def test_all_five_examples_are_scanned(self):
        self.assertEqual(len(BLOCKS), 5, "every check below scans only ```typescript blocks")

    def test_logs_omit_headers_and_bodies(self):
        calls = re.findall(r"\.(?:error|warn|info|log|debug)\((.*?)\);", CODE, re.S)
        self.assertTrue(calls, "no log calls found to check")
        for args in calls:
            rest = re.sub(r"^\s*'[^']*'", "", args)
            for field in LOG_FIELDS:
                rest = rest.replace(field, "")
            with self.subTest(log=args.splitlines()[0]):
                self.assertFalse(re.search(r"\w", rest), f"a log call passes more than an ID and the error stack: {rest.strip()}")
        self.assertFalse("event.headers" in CODE, "an example reads event.headers, which carries tokens")

    def test_null_body_is_guarded_before_parse(self):
        guard, parse = CODE.find("if (!event.body)"), CODE.find("JSON.parse(event.body)")
        self.assertNotEqual(guard, -1, "no null guard on event.body, which API Gateway sets to null")
        self.assertNotEqual(parse, -1, "the handler no longer parses event.body")
        self.assertLess(guard, parse, "the null guard on event.body comes after JSON.parse")

    def test_sqs_reports_partial_batch_failures(self):
        self.assertFalse("Records.length" in CODE, "the SQS handler limits the batch size")
        self.assertTrue("for (const record of event.Records)" in CODE, "the SQS handler skips records")
        self.assertTrue("batchItemFailures.push({ itemIdentifier: record.messageId })" in CODE,
                        "the SQS handler doesn't report failed records")
        loop = re.search(r"for \(const record of event\.Records\) \{(.*?)\n    \}\n    return \{ batchItemFailures \};\n\}",
                         CODE, re.S)
        self.assertTrue(loop, "the SQS handler doesn't return batchItemFailures after the loop")
        self.assertFalse(re.search(r"\b(return|break|continue|throw)\b", loop.group(1)),
                         "the SQS loop skips a failed record or stops before the last one")
        self.assertTrue("ReportBatchItemFailures" in TEXT,
                        "the prose doesn't name ReportBatchItemFailures, without which Lambda ignores the response")

    def test_unknown_message_type_fails_the_record(self):
        self.assertTrue(re.search(r"default:\s*throw new Error", CODE), "an unknown message type succeeds and is deleted")
        self.assertFalse("console.warn" in CODE, "an example warns instead of failing")

    def test_deduplication_uses_a_conditional_write(self):
        self.assertFalse("new Map" in CODE, "deduplication keeps per-environment state in a Map")
        self.assertTrue("attribute_not_exists(" in CODE, "deduplication has no conditional write")
        self.assertTrue("instanceof ConditionalCheckFailedException" in CODE,
                        "deduplication doesn't treat a failed condition as a duplicate")
        self.assertTrue("CancellationReasons" in TEXT, "the prose doesn't say how to read a cancelled transaction")
        self.assertTrue("ConsistentRead" in TEXT, "the prose doesn't require a strongly consistent marker read")

    def test_no_lookalike_library_names(self):
        for name in ["trace.", "getServiceConfig", "StatusCodeError", "assert("]:
            with self.subTest(name=name):
                self.assertFalse(name in CODE, f"{name} is neither a real API nor defined in the example")

    def test_other_copy_hazards_stay_fixed(self):
        self.assertFalse(re.search(r"(?<![.\w])process\(", CODE), "an example calls Node's global process object")
        for hazard, reason in [
            ("region: '", "a hardcoded region"),
            ("response.text()", "the upstream response body in an error"),
            ("return response.json()", "an unwrapped JSON parse error that quotes the body"),
            ("JSON.parse(record.body)", "an unwrapped JSON parse error that quotes the message body"),
        ]:
            with self.subTest(hazard=hazard):
                self.assertFalse(hazard in CODE, reason)
        self.assertTrue("instanceof SyntaxError" in CODE, "the response.json() parse error isn't replaced")
        self.assertTrue("AbortSignal.timeout(" in CODE, "fetch has no timeout")
        for value in re.findall(r"AbortSignal\.timeout\(([^)]*)\)", CODE):
            with self.subTest(timeout=value):
                self.assertLess(int(value.replace("_", "")), 3000, "the fetch timeout reaches Lambda's 3-second default")


if __name__ == "__main__":
    unittest.main()
